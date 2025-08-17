from datetime import datetime
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=True)
    phone = db.Column(db.String(32), unique=True, index=True, nullable=True)
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    email_otp = db.Column(db.String(6), nullable=True)
    phone_otp = db.Column(db.String(6), nullable=True)
    email_otp_expires = db.Column(db.DateTime, nullable=True)
    phone_otp_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Ensure at least one of email or phone is provided at the app level
        # (DB can't enforce XOR easily; we validate in forms/routes)
        UniqueConstraint('email', name='uq_users_email'),
        UniqueConstraint('phone', name='uq_users_phone'),
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password) 