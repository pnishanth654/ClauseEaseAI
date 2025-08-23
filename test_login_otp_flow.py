#!/usr/bin/env python3
"""
Test script to simulate login flow for unverified users
This tests that OTP emails are sent to the user's email from the database
"""

import sys
import os
sys.path.append('src')

from app import create_app
from models import User
from otp_utils import generate_otp, get_otp_expiry_time, send_email_otp
from extensions import db

def test_unverified_user_login_flow():
    """Test the flow when an unverified user tries to login"""
    app = create_app()
    
    with app.app_context():
        print("🔍 TESTING UNVERIFIED USER LOGIN FLOW")
        print("=" * 50)
        
        # Find an unverified user
        unverified_user = User.query.filter_by(email_verified=False).first()
        
        if not unverified_user:
            print("❌ No unverified users found in database!")
            print("   Create a new user or use the reset demo script")
            return
        
        print(f"👤 Found unverified user:")
        print(f"   ID: {unverified_user.id}")
        print(f"   Name: {unverified_user.first_name} {unverified_user.last_name}")
        print(f"   Email: {unverified_user.email}")
        print(f"   Email Verified: {unverified_user.email_verified}")
        print(f"   Current OTP: {unverified_user.email_otp}")
        
        # Simulate what happens when user is redirected to verification page
        print(f"\n📧 SIMULATING LOGIN → VERIFICATION REDIRECT")
        print("=" * 50)
        
        # Generate new OTP (as the app would do)
        print(f"🔐 Generating new OTP for user...")
        email_otp = generate_otp()
        unverified_user.email_otp = email_otp
        unverified_user.email_otp_expires = get_otp_expiry_time()
        
        # Save to database
        db.session.commit()
        print(f"✅ OTP saved to database: {email_otp}")
        
        # Send email (as the app would do)
        print(f"\n📧 SENDING OTP EMAIL TO USER'S EMAIL")
        print("=" * 50)
        
        try:
            print(f"📧 Attempting to send OTP to: {unverified_user.email}")
            email_sent = send_email_otp(unverified_user.email, email_otp)
            
            if email_sent:
                print(f"✅ EMAIL SENT SUCCESSFULLY!")
                print(f"   OTP Code: {email_otp}")
                print(f"   Sent to: {unverified_user.email}")
                print(f"   Expires in: 10 minutes")
                print(f"\n🎉 LOGIN FLOW TEST PASSED!")
                print(f"   User will receive OTP at their registered email address")
                return True
            else:
                print(f"❌ Email sending failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

def test_specific_email():
    """Test sending OTP to a specific email address"""
    app = create_app()
    
    with app.app_context():
        print("\n🎯 TESTING SPECIFIC EMAIL DELIVERY")
        print("=" * 50)
        
        # Test with the user's actual email
        test_email = "221301006@rajalakshmi.edu.in"  # Aruna's email
        test_otp = generate_otp()
        
        print(f"📧 Sending test OTP to: {test_email}")
        print(f"🔐 OTP Code: {test_otp}")
        
        try:
            email_sent = send_email_otp(test_email, test_otp)
            
            if email_sent:
                print(f"✅ EMAIL SENT SUCCESSFULLY!")
                print(f"   Check inbox: {test_email}")
                return True
            else:
                print(f"❌ Email sending failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    print("🚀 LOGIN OTP FLOW TEST")
    print("=" * 60)
    
    # Test 1: Unverified user login flow
    flow_test = test_unverified_user_login_flow()
    
    # Test 2: Specific email delivery
    email_test = test_specific_email()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Login Flow Test: {'PASS' if flow_test else 'FAIL'}")
    print(f"✅ Email Delivery: {'PASS' if email_test else 'FAIL'}")
    
    if flow_test and email_test:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Unverified users will receive OTP emails at their registered address")
    else:
        print(f"\n❌ Some tests failed - check error messages above")

if __name__ == "__main__":
    main() 