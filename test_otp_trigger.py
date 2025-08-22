#!/usr/bin/env python3
"""
Test script to trigger OTP functionality
"""

import sys
import os
sys.path.append('src')

from app import create_app
from models import User
from otp_utils import generate_otp, send_email_otp, send_sms_otp
from extensions import db

def test_otp_trigger():
    """Test OTP generation and sending"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Testing OTP System...")
            
            # Test 1: Generate OTP
            otp = generate_otp()
            print(f"✅ Generated OTP: {otp}")
            
            # Test 2: Test email OTP
            test_email = "test@example.com"
            print(f"📧 Testing email OTP to: {test_email}")
            
            email_success = send_email_otp(test_email, otp)
            if email_success:
                print("✅ Email OTP sent successfully!")
            else:
                print("❌ Email OTP failed!")
            
            # Test 3: Test SMS OTP
            test_phone = "+1234567890"
            print(f"📱 Testing SMS OTP to: {test_phone}")
            
            sms_success = send_sms_otp(test_phone, otp)
            if sms_success:
                print("✅ SMS OTP sent successfully!")
            else:
                print("❌ SMS OTP failed!")
            
            # Test 4: Check database connection
            try:
                user_count = User.query.count()
                print(f"✅ Database connection working! Users in DB: {user_count}")
            except Exception as e:
                print(f"❌ Database error: {e}")
            
            print("\n🎯 OTP System Test Complete!")
            print("💡 Now try registering a user through the web interface:")
            print("   http://localhost:5000/register")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_otp_trigger() 