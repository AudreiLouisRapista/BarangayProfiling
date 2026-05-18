from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.security import check_password_hash
from app import app, login_required
from extensions import db
from models import User, Employee, Residence
from models.finance import FiscalYear, Transaction, TransactionType


@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():

    # ── Employees ─────────────────────────────────────────────────────────────
    total_employees  = Employee.query.filter(Employee.deleted_at == None).count()
    recent_employees = Employee.query.filter(
        Employee.deleted_at == None
    ).order_by(Employee.id.desc()).limit(3).all()

    # ── Residents ─────────────────────────────────────────────────────────────
    total_residents = Residence.query.filter(Residence.deleted_at == None).count()

    # ── Finances ──────────────────────────────────────────────────────────────
    active_fy           = FiscalYear.query.filter_by(fiscal_status_id=2).first()
    current_balance     = 0.00
    total_collections   = 0.00
    total_disbursements = 0.00
    approved_budget     = 0.00
    pending_count       = 0

    if active_fy:
        approved_budget = float(active_fy.total_approved_budget)

        transactions = Transaction.query.filter_by(
            fiscal_year_id=active_fy.id
        ).all()

        for t in transactions:
            if t.transaction_type.transaction_types == 'Collection':
                total_collections += float(t.transaction_amount)
            else:
                total_disbursements += float(t.transaction_amount)

        current_balance = total_collections - total_disbursements

        # Pending transactions count
        pending_count = Transaction.query.filter_by(
            fiscal_year_id=active_fy.id
        ).join(Transaction.transaction_status).filter(
            db.text("transaction_status.status_type = 'Pending'")
        ).count()

    # ── Recent Transactions (last 5) ──────────────────────────────────────────
    recent_transactions = []
    if active_fy:
        recent_transactions = Transaction.query.filter_by(
            fiscal_year_id=active_fy.id
        ).order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc()
        ).limit(5).all()

    return render_template(
        'BarangayAdmin/dashboard.html',
        segment             = 'dashboard',
        total_employees     = total_employees,
        recent_employees    = recent_employees,
        total_residents     = total_residents,
        active_fy           = active_fy,
        approved_budget     = approved_budget,
        current_balance     = current_balance,
        total_collections   = total_collections,
        total_disbursements = total_disbursements,
        pending_count       = pending_count,
        recent_transactions = recent_transactions,
        today               = datetime.now(timezone.utc),
    )


@app.route('/login', methods=['POST'])
def login():
    user_email    = request.form.get('user_email')
    user_password = request.form.get('user_password')

    if not user_email or not user_password:
        flash('Please fill in all fields.', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(user_email=user_email).first()
    if user and check_password_hash(user.user_password, user_password):
        session['user_id']    = user.id
        session['user_email'] = user.user_email
        session['user_role']  = user.user_role.role_type
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    flash('Invalid email or password.', 'danger')
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    response = make_response(redirect(url_for('login_page')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma']        = 'no-cache'
    return response