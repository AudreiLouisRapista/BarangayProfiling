from datetime import datetime, timezone
from app import db
from .user import User


class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    position_type = db.Column(db.String(100), unique=True, nullable=False)


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), unique=True, nullable=False)


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_firstname = db.Column(db.String(100), nullable=False)
    employee_lastname = db.Column(db.String(100), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_phonenumber = db.Column(db.String(20))
    term_start_date = db.Column(db.String(100))
    term_end_date = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    position = db.relationship('Position', backref='employees')
    status = db.relationship('Status', backref='employees')
    user = db.relationship('User', backref='employee', uselist=False)

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        self.deleted_at = None
        db.session.commit()
