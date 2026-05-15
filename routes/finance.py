from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, session
from app import app, login_required
from extensions import db
from models.finance import (
    Transaction, TransactionType, DocumentType,
    CategoryType, TransactionStatus, FiscalYear, BudgetAllocation
)
from models.user import Admin


# ── Helper: Auto-generate Document Number ────────────────────────────────────

def generate_doc_number(doc_type, fiscal_year_label):
    """
    Generates the next document number for a given doc type and fiscal year.
    Format: OR-2026-0001, DV-2026-0001, etc.
    """
    last = Transaction.query.filter(
        Transaction.transaction_docuNumber.like(f'{doc_type}-{fiscal_year_label}-%')
    ).order_by(Transaction.id.desc()).first()

    if last:
        last_num = int(last.transaction_docuNumber.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{doc_type}-{fiscal_year_label}-{new_num:04d}"


# ── Helper: Recalculate Running Balance ──────────────────────────────────────

def recalculate_running_balance(fiscal_year_id):
    """
    Recalculates and updates the running balance for all transactions
    in a fiscal year, ordered by date then id.
    """
    transactions = Transaction.query.filter_by(
        fiscal_year_id=fiscal_year_id
    ).order_by(
        Transaction.transaction_date.asc(),
        Transaction.id.asc()
    ).all()

    balance = 0.00
    for t in transactions:
        t_type = t.transaction_type.transaction_types  # 'Collection' or 'Disbursement'
        if t_type == 'Collection':
            balance += float(t.transaction_amount)
        else:
            balance -= float(t.transaction_amount)
        t.transaction_running_balance = round(balance, 2)

    db.session.commit()


# ── Finances Dashboard ────────────────────────────────────────────────────────

@app.route('/finances')
@login_required
def finances():
    # Get active fiscal year
    active_fiscal_year = FiscalYear.query.filter_by(status='active').first()

    transactions        = []
    budget_allocations  = []
    total_collections   = 0.00
    total_disbursements = 0.00
    current_balance     = 0.00

    if active_fiscal_year:
        transactions = Transaction.query.filter_by(
            fiscal_year_id=active_fiscal_year.id
        ).order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc()
        ).all()

        budget_allocations = BudgetAllocation.query.filter_by(
            fiscal_year_id=active_fiscal_year.id
        ).all()

        # KPI calculations
        for t in transactions:
            t_type = t.transaction_type.transaction_types
            if t_type == 'Collection':
                total_collections += float(t.transaction_amount)
            else:
                total_disbursements += float(t.transaction_amount)

        current_balance = total_collections - total_disbursements

    # Dropdown data for the modal
    transaction_types   = TransactionType.query.all()
    document_types      = DocumentType.query.all()
    category_types      = CategoryType.query.all()
    transaction_statuses = TransactionStatus.query.all()
    all_fiscal_years    = FiscalYear.query.order_by(FiscalYear.fiscal_year.desc()).all()

    return render_template(
        'BarangayAdmin/finances.html',
        segment              = 'finances',
        active_fiscal_year   = active_fiscal_year,
        transactions         = transactions,
        budget_allocations   = budget_allocations,
        total_collections    = total_collections,
        total_disbursements  = total_disbursements,
        current_balance      = current_balance,
        transaction_types    = transaction_types,
        document_types       = document_types,
        category_types       = category_types,
        transaction_statuses = transaction_statuses,
        all_fiscal_years     = all_fiscal_years,
    )


# ── Add Transaction ───────────────────────────────────────────────────────────

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    try:
        fiscal_year_id          = request.form.get('fiscal_year_id')
        transaction_type_id     = request.form.get('transaction_type_id')
        transaction_category_id = request.form.get('transaction_category_id')
        transaction_status_id   = request.form.get('transaction_status_id')
        transaction_amount      = request.form.get('transaction_amount')
        transaction_date        = request.form.get('transaction_date')
        transaction_description = request.form.get('transaction_description')
        deposited_date          = request.form.get('deposited_date') or None
        is_deposited            = 1 if request.form.get('is_deposited') else 0

        # Validate required fields
        if not all([fiscal_year_id, transaction_type_id, transaction_category_id,
                    transaction_status_id, transaction_amount, transaction_date,
                    transaction_description]):
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('finances'))

        # Get fiscal year label for doc number (e.g. '2026')
        fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)

        # Get document type — determined by transaction type
        transaction_type = TransactionType.query.get_or_404(transaction_type_id)
        if transaction_type.transaction_types == 'Collection':
            doc_type_label = 'OR'
        else:
            doc_type_label = 'DV'

        doc_type = DocumentType.query.filter_by(document_types=doc_type_label).first()
        if not doc_type:
            flash(f'Document type {doc_type_label} not found in database.', 'danger')
            return redirect(url_for('finances'))

        # Auto-generate document number
        doc_number = generate_doc_number(doc_type_label, fiscal_year.fiscal_year)

        # Get admin id from session
        admin = Admin.query.filter_by(id=session.get('user_id')).first()
        admin_id = admin.id if admin else 1  # fallback

        # Create transaction (running balance calculated after insert)
        new_transaction = Transaction(
            admin_id                = admin_id,
            transaction_type_id     = transaction_type_id,
            transaction_docuType_id = doc_type.id,
            transaction_category_id = transaction_category_id,
            fiscal_year_id          = fiscal_year_id,
            transaction_status_id   = transaction_status_id,
            transaction_amount      = transaction_amount,
            transaction_docuNumber  = doc_number,
            transaction_running_balance = 0.00,  # will be updated below
            is_deposited            = is_deposited,
            deposited_date          = deposited_date,
            transaction_date        = transaction_date,
            transaction_description = transaction_description,
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Recalculate running balance for the entire fiscal year
        recalculate_running_balance(fiscal_year_id)

        flash(f'Transaction {doc_number} recorded successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error recording transaction: {str(e)}', 'danger')

    return redirect(url_for('finances'))


# ── Edit Transaction ──────────────────────────────────────────────────────────

@app.route('/edit_transaction/<int:id>')
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)

    transactions        = Transaction.query.filter_by(
        fiscal_year_id=transaction.fiscal_year_id
    ).order_by(Transaction.transaction_date.desc()).all()

    transaction_types    = TransactionType.query.all()
    document_types       = DocumentType.query.all()
    category_types       = CategoryType.query.all()
    transaction_statuses = TransactionStatus.query.all()
    all_fiscal_years     = FiscalYear.query.order_by(FiscalYear.fiscal_year.desc()).all()
    active_fiscal_year   = FiscalYear.query.filter_by(status='active').first()

    return render_template(
        'BarangayAdmin/finances.html',
        segment              = 'finances',
        edit_transaction     = transaction,
        transactions         = transactions,
        active_fiscal_year   = active_fiscal_year,
        transaction_types    = transaction_types,
        document_types       = document_types,
        category_types       = category_types,
        transaction_statuses = transaction_statuses,
        all_fiscal_years     = all_fiscal_years,
    )


# ── Update Transaction ────────────────────────────────────────────────────────

@app.route('/update_transaction', methods=['POST'])
@login_required
def update_transaction():
    try:
        transaction_id = request.form.get('transaction_id')
        transaction    = Transaction.query.get_or_404(transaction_id)

        transaction.transaction_type_id     = request.form.get('transaction_type_id')
        transaction.transaction_category_id = request.form.get('transaction_category_id')
        transaction.transaction_status_id   = request.form.get('transaction_status_id')
        transaction.transaction_amount      = request.form.get('transaction_amount')
        transaction.transaction_date        = request.form.get('transaction_date')
        transaction.transaction_description = request.form.get('transaction_description')
        transaction.deposited_date          = request.form.get('deposited_date') or None
        transaction.is_deposited            = 1 if request.form.get('is_deposited') else 0
        transaction.updated_at              = datetime.now(timezone.utc)

        db.session.commit()

        # Recalculate running balance after update
        recalculate_running_balance(transaction.fiscal_year_id)

        flash(f'Transaction {transaction.transaction_docuNumber} updated successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating transaction: {str(e)}', 'danger')

    return redirect(url_for('finances'))


# ── Delete Transaction ────────────────────────────────────────────────────────

@app.route('/delete_transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    try:
        fiscal_year_id = transaction.fiscal_year_id
        doc_number     = transaction.transaction_docuNumber

        db.session.delete(transaction)
        db.session.commit()

        # Recalculate running balance after deletion
        recalculate_running_balance(fiscal_year_id)

        flash(f'Transaction {doc_number} deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting transaction: {str(e)}', 'danger')

    return redirect(url_for('finances'))


# ── Fiscal Year Management ────────────────────────────────────────────────────

@app.route('/fiscal_year/add', methods=['POST'])
@login_required
def add_fiscal_year():
    try:
        fiscal_year      = request.form.get('fiscal_year')
        approved_budget  = request.form.get('total_approved_budget')
        ordinance_number = request.form.get('ordinance_number')
        ordinance_date   = request.form.get('ordinance_date')

        if not all([fiscal_year, approved_budget, ordinance_number, ordinance_date]):
            flash('Please fill in all fiscal year fields.', 'warning')
            return redirect(url_for('finances'))

        existing = FiscalYear.query.filter_by(fiscal_year=fiscal_year).first()
        if existing:
            flash(f'Fiscal Year {fiscal_year} already exists.', 'warning')
            return redirect(url_for('finances'))

        # Set all existing active years to closed before adding new active one
        FiscalYear.query.filter_by(status='active').update({'status': 'closed'})

        new_fy = FiscalYear(
            fiscal_year            = fiscal_year,
            total_approved_budget  = approved_budget,
            ordinance_number       = ordinance_number,
            ordinance_date         = ordinance_date,
            status                 = 'active',
        )
        db.session.add(new_fy)
        db.session.commit()

        flash(f'Fiscal Year {fiscal_year} created successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating fiscal year: {str(e)}', 'danger')

    return redirect(url_for('finances'))