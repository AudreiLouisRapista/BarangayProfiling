from datetime import datetime, timezone
from extensions import db


# ── Lookup: Transaction Type ──────────────────────────────────────────────────

class TransactionType(db.Model):
    __tablename__ = 'transaction_type'

    id                  = db.Column(db.Integer, primary_key=True)
    transaction_types   = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    transactions = db.relationship('Transaction', backref='transaction_type', lazy=True)

    def __repr__(self):
        return f'<TransactionType {self.transaction_types}>'


# ── Lookup: Document Type ─────────────────────────────────────────────────────

class DocumentType(db.Model):
    __tablename__ = 'document_type'

    id              = db.Column(db.Integer, primary_key=True)
    document_types  = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    transactions = db.relationship('Transaction', backref='document_type', lazy=True)

    def __repr__(self):
        return f'<DocumentType {self.document_types}>'


# ── Lookup: Category Type ─────────────────────────────────────────────────────

class CategoryType(db.Model):
    __tablename__ = 'category_type'

    id              = db.Column(db.Integer, primary_key=True)
    category_type   = db.Column(db.String(50), nullable=False, unique=True)
    #type_nature     = db.Column(db.String(10), nullable=False)   # 'income' or 'expense'

    # Relationships
    transactions       = db.relationship('Transaction', backref='category_type', lazy=True)
    budget_allocations = db.relationship('BudgetAllocation', backref='category_type', lazy=True)

    def __repr__(self):
        return f'<CategoryType {self.category_type}>'


# ── Lookup: Transaction Status ────────────────────────────────────────────────

class TransactionStatus(db.Model):
    __tablename__ = 'transaction_status'

    id          = db.Column(db.Integer, primary_key=True)
    status_type = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    transactions = db.relationship('Transaction', backref='transaction_status', lazy=True)

    def __repr__(self):
        return f'<TransactionStatus {self.status_type}>'


# ── Fiscal Year ───────────────────────────────────────────────────────────────

class FiscalYear(db.Model):
    __tablename__ = 'fiscal_year'

    id                      = db.Column(db.Integer, primary_key=True)
    fiscal_year             = db.Column(db.String(4), nullable=False, unique=True)  # e.g. '2026'
    total_approved_budget   = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    ordinance_number        = db.Column(db.String(100), nullable=False)             # e.g. 'Ordinance No. 2026-01'
    ordinance_date          = db.Column(db.Date, nullable=False)

    fiscal_status_id = db.Column(db.Integer, db.ForeignKey('fiscal_status.id'), nullable=False, default=2)
    # Relationships
    transactions       = db.relationship('Transaction', backref='fiscal_year', lazy=True)
    budget_allocations = db.relationship('BudgetAllocation', backref='fiscal_year', lazy=True)

    def __repr__(self):
        return f'<FiscalYear {self.fiscal_year} — {self.status}>'

# ── Fiscal Status ───────────────────────────────────────────────────────────
class FiscalStatus(db.Model):
    __tablename__ = 'fiscal_status'

    id              = db.Column(db.Integer, primary_key=True)
    fiscal_type     = db.Column(db.String(50), nullable=False, unique=True)  # e.g. 'Open', 'Closed', 'Pending'

    # Relationship
    fiscal_years = db.relationship('FiscalYear', backref='status', lazy=True)

    def __repr__(self):
        return f'<FiscalStatus {self.status_name}>'

# ── Budget Allocation ─────────────────────────────────────────────────────────

class BudgetAllocation(db.Model):
    __tablename__ = 'budget_allocation'

    id                          = db.Column(db.Integer, primary_key=True)
    fiscal_year_id              = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    transaction_category_id     = db.Column(db.Integer, db.ForeignKey('category_type.id'), nullable=False)
    budget_amount               = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    budget_mandatory_percent    = db.Column(db.Numeric(5, 2), nullable=True)

    def __repr__(self):
        return f'<BudgetAllocation FY:{self.fiscal_year_id} Category:{self.transaction_category_id}>'
    
    def to_dict(self):
        """Convert SQLAlchemy model to JSON-serializable dictionary"""
        return {
            'id': self.id,
            'budget_amount': float(self.budget_amount),
            'budget_mandatory_percent': float(self.budget_mandatory_percent) if self.budget_mandatory_percent else None,
            'category_type': {
                'category_type': self.category_type.category_type,
                'type_nature': getattr(self.category_type, 'type_nature', None)
            } if self.category_type else None,
            'fiscal_year': {
                'fiscal_year': self.fiscal_year.fiscal_year
            } if self.fiscal_year else None,
        }


# ── Transaction ───────────────────────────────────────────────────────────────

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id                          = db.Column(db.Integer, primary_key=True)
    user_id                    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type_id         = db.Column(db.Integer, db.ForeignKey('transaction_type.id'), nullable=False)
    transaction_docuType_id     = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=False)
    transaction_category_id     = db.Column(db.Integer, db.ForeignKey('category_type.id'), nullable=False)
    fiscal_year_id              = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    transaction_status_id       = db.Column(db.Integer, db.ForeignKey('transaction_status.id'), nullable=False)
    transaction_amount          = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    transaction_docuNumber      = db.Column(db.String(30), nullable=False, unique=True)
    transaction_running_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    is_deposited                = db.Column(db.Integer, nullable=False, default=0)
    deposited_date              = db.Column(db.Date, nullable=True)
    transaction_date            = db.Column(db.Date, nullable=False)
    transaction_description     = db.Column(db.String(255), nullable=False)
    created_at                  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at                  = db.Column(db.DateTime,
                                            default=lambda: datetime.now(timezone.utc),
                                            onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Transaction {self.transaction_docuNumber} — ₱{self.transaction_amount}>'
    
    def to_dict(self):
        """Convert SQLAlchemy model to JSON-serializable dictionary"""
        return {
            'id': self.id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_description': self.transaction_description,
            'transaction_docuNumber': self.transaction_docuNumber,
            'transaction_amount': float(self.transaction_amount),
            'transaction_running_balance': float(self.transaction_running_balance),
            'is_deposited': self.is_deposited,
            'deposited_date': self.deposited_date.isoformat() if self.deposited_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Nested relationships
            'category_type': {
                'category_type': self.category_type.category_type,
                'type_nature': getattr(self.category_type, 'type_nature', None)
            } if self.category_type else None,
            'transaction_type': {
                'transaction_types': self.transaction_type.transaction_types
            } if self.transaction_type else None,
            'transaction_status': {
                'status_type': self.transaction_status.status_type
            } if self.transaction_status else None,
        }