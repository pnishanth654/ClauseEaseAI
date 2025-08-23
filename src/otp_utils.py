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
        # Check if mail is properly configured
        if not current_app.config.get("MAIL_USERNAME") or current_app.config.get("MAIL_USERNAME") == "your-email@gmail.com":
            print(f"❌ EMAIL NOT CONFIGURED:")
            print(f"   Please set MAIL_USERNAME and MAIL_PASSWORD in your .env file")
            print(f"   OTP Code: {otp} (shown in terminal only)")
            return False
            
        if not current_app.config.get("MAIL_PASSWORD") or current_app.config.get("MAIL_PASSWORD") == "your-app-password":
            print(f"❌ EMAIL PASSWORD NOT CONFIGURED:")
            print(f"   Please set MAIL_PASSWORD in your .env file")
            print(f"   OTP Code: {otp} (shown in terminal only)")
            return False
        
        # Create and send email
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
        
        print(f"📧 Sending email to: {email}")
        print(f"📧 Email subject: {msg.subject}")
        mail.send(msg)
        print(f"✅ Email sent successfully to {email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email OTP: {e}")
        print(f"❌ EMAIL SENDING FAILED:")
        print(f"   Error: {e}")
        print(f"   Email: {email}")
        print(f"   OTP: {otp}")
        print(f"   Check your email configuration in .env file")
        print(f"   OTP Code: {otp} (shown in terminal only)")
        return False



def verify_otp(user_otp, stored_otp, expires_at):
    """Verify OTP code and check if expired"""
    if not stored_otp or not user_otp:
        return False
    if is_otp_expired(expires_at):
        return False
    return user_otp == stored_otp

 