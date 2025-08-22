import random
import string
import os
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from extensions import mail
import phonenumbers

def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def is_otp_expired(expires_at):
    """Check if OTP has expired"""
    if not expires_at:
        return True
    return datetime.utcnow() > expires_at

def get_otp_expiry_time(minutes=None):
    """Get OTP expiry time (default from env or 10 minutes)"""
    if minutes is None:
        minutes = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
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
    """Send OTP via SMS - configurable service provider"""
    try:
        sms_provider = os.getenv('SMS_SERVICE_PROVIDER', 'console')
        
        if sms_provider == 'console':
            # Development mode - log to console
            current_app.logger.info(f"📱 SMS OTP for {phone_number}: {otp}")
            current_app.logger.info(f"💡 In production, this would be sent via {sms_provider}")
            return True
            
        elif sms_provider == 'twilio':
            # TODO: Implement Twilio SMS service
            current_app.logger.info(f"📱 SMS OTP for {phone_number}: {otp}")
            current_app.logger.info(f"🔄 Twilio integration not yet implemented")
            return True
            
        elif sms_provider == 'aws_sns':
            # TODO: Implement AWS SNS SMS service
            current_app.logger.info(f"📱 SMS OTP for {phone_number}: {otp}")
            current_app.logger.info(f"🔄 AWS SNS integration not yet implemented")
            return True
            
        else:
            current_app.logger.warning(f"Unknown SMS provider: {sms_provider}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS OTP: {e}")
        return False

def verify_otp(user_otp, stored_otp, expires_at):
    """Verify OTP code and check if expired"""
    if not stored_otp or not user_otp:
        return False
    if is_otp_expired(expires_at):
        return False
    return user_otp == stored_otp

def validate_phone_number(phone_number):
    """Validate phone number format"""
    try:
        parsed = phonenumbers.parse(phone_number, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False 