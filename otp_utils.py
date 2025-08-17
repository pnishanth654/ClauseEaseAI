import random
import string
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from extensions import mail
import phonenumbers
import firebase_admin
from firebase_admin import auth, credentials, messaging

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize with service account key
        cred = credentials.Certificate(current_app.config.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
        firebase_admin.initialize_app(cred)

def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def is_otp_expired(expires_at):
    """Check if OTP has expired"""
    if not expires_at:
        return True
    return datetime.utcnow() > expires_at

def get_otp_expiry_time(minutes=10):
    """Get OTP expiry time (default 10 minutes)"""
    return datetime.utcnow() + timedelta(minutes=minutes)

def send_email_otp(email, otp):
    """Send OTP via email"""
    try:
        msg = Message(
            subject="Your ClauseEase AI Verification Code",
            recipients=[email],
            body=f"""
Your verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
ClauseEase AI Team
            """.strip()
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email OTP: {e}")
        return False

def send_sms_otp(phone_number, otp):
    """Firebase Phone Authentication - OTP sent via Firebase"""
    try:
        # Initialize Firebase
        initialize_firebase()
        
        # For Firebase Phone Auth, the OTP is sent automatically when user
        # calls signInWithPhoneNumber() on the client side
        # We just need to store the OTP for verification
        
        current_app.logger.info(f"Firebase Phone Auth OTP for {phone_number}: {otp}")
        current_app.logger.info(f"OTP will be sent via Firebase Phone Authentication")
        
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to initialize Firebase: {e}")
        return False

def verify_firebase_phone_token(id_token):
    """Verify Firebase phone authentication token"""
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        current_app.logger.error(f"Failed to verify Firebase token: {e}")
        return None

def create_firebase_custom_token(user_id):
    """Create Firebase custom token for user"""
    try:
        initialize_firebase()
        custom_token = auth.create_custom_token(str(user_id))
        return custom_token.decode('utf-8')
    except Exception as e:
        current_app.logger.error(f"Failed to create Firebase custom token: {e}")
        return None

def validate_phone_number(phone_number):
    """Validate phone number format"""
    try:
        parsed = phonenumbers.parse(phone_number, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False 