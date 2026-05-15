from datetime import datetime, timezone
from app import db
from .user import User
from .employee import Status


class HealthStatus(db.Model):
    __tablename__ = 'healthstatus'
    id = db.Column(db.Integer, primary_key=True)
    blood_type = db.Column(db.String(100), nullable=True)
    is_pwd = db.Column(db.Integer, nullable=True)
    disability_type = db.Column(db.String(100), nullable=True)
    is_senior_citizen = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class Demographic(db.Model):
    __tablename__ = 'demographic'
    id = db.Column(db.Integer, primary_key=True)
    educational_attaiment = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    monthly_income = db.Column(db.Float(precision=2), nullable=True)
    is_voter = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    purok_number = db.Column(db.Integer, nullable=True)
    street_name = db.Column(db.String(100), nullable=True)
    house_number = db.Column(db.Integer, nullable=True)
    is_head_of_family = db.Column(db.String(100), nullable=True)
    creatd_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class Residence(db.Model):
    __tablename__ = 'residence'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    heathStatus_id = db.Column(db.Integer, db.ForeignKey('healthstatus.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    demographic_id = db.Column(db.Integer, db.ForeignKey('demographic.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    residence_firstname = db.Column(db.String(100), nullable=True)
    residence_lastname = db.Column(db.String(100), nullable=True)
    residence_middlename = db.Column(db.String(100), nullable=True)
    residence_suffix = db.Column(db.String(100), nullable=True)
    residence_birthday = db.Column(db.String(100), nullable=True)
    residence_civilStatus = db.Column(db.String(100), nullable=True)
    residence_citizenship = db.Column(db.String(100), nullable=True)
    residence_phoneNumber = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='residence')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_residences')
    status = db.relationship('Status', backref='residence')
    health = db.relationship('HealthStatus', backref='residence')
    address = db.relationship('Address', backref='residence')
    demographic = db.relationship('Demographic', backref='residence')

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        self.deleted_at = None
        db.session.commit()
