from datetime import datetime, timezone
from app import db


class FiscalYear(db.Model):
    __tablename__ = 'fiscal_year'
    id = db.Column(db.Integer, primary_key=True)
    year_label = db.Column(db.String(20), unique=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class TransactionType(db.Model):
    __tablename__ = 'transaction_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class DocumentType(db.Model):
    __tablename__ = 'document_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class CategoryType(db.Model):
    __tablename__ = 'category_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class TransactionStatus(db.Model):
    __tablename__ = 'transaction_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class BudgetAllocation(db.Model):
    __tablename__ = 'budget_allocation'
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year_id = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)

    fiscal_year = db.relationship('FiscalYear', backref='budget_allocations')


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year_id = db.Column(db.Integer, db.ForeignKey('fiscal_year.id'), nullable=False)
    transaction_type_id = db.Column(db.Integer, db.ForeignKey('transaction_type.id'), nullable=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=False)
    category_type_id = db.Column(db.Integer, db.ForeignKey('category_type.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('transaction_status.id'), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    reference_number = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    transaction_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    fiscal_year = db.relationship('FiscalYear', backref='transactions')
    transaction_type = db.relationship('TransactionType', backref='transactions')
    document_type = db.relationship('DocumentType', backref='transactions')
    category_type = db.relationship('CategoryType', backref='transactions')
    status = db.relationship('TransactionStatus', backref='transactions')
