from datetime import datetime, timezone
from extensions import db


# ── Lookup Tables ────────────────────────────────────────────────────────────

class TransactionType(db.Model):
    __tablename__ = 'transaction_type'
    id                  = db.Column(db.Integer, primary_key=True)
    transaction_types   = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    transactions = db.relationship('Transaction', backref='transaction_type')


class DocumentType(db.Model):
    __tablename__ = 'document_type'
    id              = db.Column(db.Integer, primary_key=True)
    document_types  = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    transactions = db.relationship('Transaction', backref='document_type')


class CategoryType(db.Model):
    __tablename__ = 'category_type'
    id              = db.Column(db.Integer, primary_key=True)
    category_type   = db.Column(db.String(50), nullable=False, unique=True)  # e.g. 'IRA', 'Utilities'
    type_nature     = db.Column(db.String(10), nullable=False)               # 'income' or 'expense'

    # Relationships
    transactions       = db.relationship('Transaction', backref='category_type')
    budget_allocations = db.relationship('BudgetAllocation', backref='category_type')


class TransactionStatus(db.Model):
    __tablename__ = 'transaction_status'
    id          = db.Column(db.Integer, primary_key=True)
    status_type = db.Column(db.String(50), nullable=False, unique=True)  # 'Deposited', 'Paid', 'Pending', 'Cancelled'

    # Relationship
    transactions = db.relationship('Transaction', backref='transaction_status')


# ── Fiscal Year ───────────────────────────────────────────────────────────────

class FiscalYear(db.Model):
    __tablename__ = 'fiscal_year'
    id                      = db.Column(db.Integer, primary_key=True)
    fiscal_year             = db.Column(db.String(4), nullable=False, unique=True)  # e.g. '2026'
    total_approved_budget   = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    ordinance_number        = db.Column(db.String(100), nullable=False)             # e.g. 'Ordinance No. 2026-01'
    ordinance_date          = db.Column(db.Date, nullable=False)
    status                  = db.Column(db.String(20), nullable=False, default='active')  # 'draft', 'active', 'closed'

    # Relationships
    transactions       = db.relationship('Transaction', backref='fiscal_year')
    budget_allocations = db.relationship('BudgetAllocation', backref='fiscal_year')


# ── Budget Allocation ─────────────────────────────────────────────────────────

class BudgetAllocation(db.Model):
    __tablename__ = 'budget_allocation'
    id                      = db.Column(db.Integer, primary_key=True)
    fiscal_year_id          = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    transaction_category_id = db.Column(db.Integer, db.ForeignKey('category_type.id'), nullable=False)
    budget_amount           = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    budget_mandatory_percent = db.Column(db.Numeric(5, 2), nullable=True)  # NULL if not mandatory


# ── Transaction ───────────────────────────────────────────────────────────────

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id                          = db.Column(db.Integer, primary_key=True)
    admin_id                    = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    transaction_type_id         = db.Column(db.Integer, db.ForeignKey('transaction_type.id'), nullable=False)
    transaction_docuType_id     = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=False)
    transaction_category_id     = db.Column(db.Integer, db.ForeignKey('category_type.id'), nullable=False)
    fiscal_year_id              = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    transaction_status_id       = db.Column(db.Integer, db.ForeignKey('transaction_status.id'), nullable=False)
    transaction_amount          = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    transaction_docuNumber      = db.Column(db.String(30), nullable=False, unique=True)  # auto-generated
    transaction_running_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    is_deposited                = db.Column(db.Integer, nullable=False, default=0)  # 0 = No, 1 = Yes
    deposited_date              = db.Column(db.Date, nullable=True)
    transaction_date            = db.Column(db.Date, nullable=False)
    transaction_description     = db.Column(db.String(255), nullable=False)
    created_at                  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at                  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                            onupdate=lambda: datetime.now(timezone.utc))