#!/usr/bin/env python3
"""
Script to clean up expired OTPs from the database.
Run this script to remove expired OTPs and prevent verification issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from models import User
from otp_utils import is_otp_expired
from extensions import db

def cleanup_expired_otps():
    """Clean up expired OTPs from the database"""
    app = create_app()
    
    with app.app_context():
        print("🧹 Starting OTP cleanup...")
        
        # Find users with expired OTPs
        users_with_expired_otps = []
        all_users = User.query.filter(User.email_otp.isnot(None)).all()
        
        for user in all_users:
            if is_otp_expired(user.email_otp_expires):
                users_with_expired_otps.append(user)
                print(f"📧 User {user.id} ({user.email}) has expired OTP: {user.email_otp}")
        
        if not users_with_expired_otps:
            print("✅ No expired OTPs found!")
            return
        
        print(f"\n🔍 Found {len(users_with_expired_otps)} users with expired OTPs")
        
        # Clean up expired OTPs
        for user in users_with_expired_otps:
            user.email_otp = None
            user.email_otp_expires = None
            print(f"🧹 Cleaned up expired OTP for user {user.id}")
        
        # Commit changes
        db.session.commit()
        print(f"✅ Successfully cleaned up {len(users_with_expired_otps)} expired OTPs!")

if __name__ == "__main__":
    cleanup_expired_otps() 