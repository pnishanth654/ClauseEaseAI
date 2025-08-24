from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from extensions import mail

RESET_SALT = "password-reset"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=RESET_SALT)


def generate_reset_token(user_email: str) -> str:
    return _serializer().dumps({"email": user_email})


def verify_reset_token(token: str, max_age_seconds: int = 3600):
    data = _serializer().loads(token, max_age=max_age_seconds)
    return data.get("email")


def send_password_reset(email: str, token: str):
    reset_url = url_for("reset_password", token=token, _external=True)
    msg = Message(
        subject="Reset your password",
        recipients=[email],
        body=f"Use the link below to reset your password (valid for 1 hour):\n{reset_url}\nIf you didn't request this, ignore this email."
    )
    mail.send(msg) 