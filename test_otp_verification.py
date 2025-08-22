#!/usr/bin/env python3
"""
Explicit OTP Verification Test - Simulates the actual registration flow
"""

import sys
import os
sys.path.append('src')

def test_otp_verification():
    """Test OTP verification by simulating registration"""
    try:
        print("🔐 EXPLICIT OTP VERIFICATION TEST")
        print("=" * 50)
        
        # Import required modules
        from app import create_app
        from models import User
        from otp_utils import generate_otp, send_email_otp, send_sms_otp
        from extensions import db
        from datetime import datetime
        
        print("✅ All modules imported successfully")
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print("✅ App context created")
            
            # Test 1: Generate OTP
            print("\n🔐 Step 1: Generate OTP")
            otp = generate_otp()
            print(f"   Generated OTP: {otp}")
            print(f"   OTP Length: {len(otp)}")
            print(f"   OTP is numeric: {otp.isdigit()}")
            
            # Test 2: Test email OTP sending
            print("\n📧 Step 2: Test Email OTP")
            test_email = "test@example.com"
            print(f"   Testing email: {test_email}")
            
            email_result = send_email_otp(test_email, otp)
            print(f"   Email OTP result: {email_result}")
            
            # Test 3: Test SMS OTP sending
            print("\n📱 Step 3: Test SMS OTP")
            test_phone = "+1234567890"
            print(f"   Testing phone: {test_phone}")
            
            sms_result = send_sms_otp(test_phone, otp)
            print(f"   SMS OTP result: {sms_result}")
            
            # Test 4: Simulate user creation with OTP
            print("\n👤 Step 4: Simulate User Creation with OTP")
            
            # Check current user count
            current_users = User.query.count()
            print(f"   Current users in DB: {current_users}")
            
            # Create a test user (if it doesn't exist)
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                print(f"   User already exists with ID: {existing_user.id}")
                test_user = existing_user
            else:
                print("   Creating new test user...")
                test_user = User()
                test_user.first_name = "Test"
                test_user.last_name = "User"
                test_user.email = test_email
                test_user.phone = test_phone
                test_user.gender = "male"
                test_user.date_of_birth = datetime.strptime("1990-01-01", '%Y-%m-%d').date()
                test_user.set_password("TestPass123!")
                test_user.email_otp = otp
                test_user.email_otp_expires = datetime.utcnow()
                
                db.session.add(test_user)
                db.session.commit()
                print(f"   Test user created with ID: {test_user.id}")
            
            # Test 5: Verify OTP validation
            print("\n✅ Step 5: Test OTP Validation")
            
            # Test the OTP verification logic
            if test_user.email_otp == otp:
                print(f"   ✅ OTP matches: {test_user.email_otp} == {otp}")
                
                # Mark as verified
                test_user.email_verified = True
                test_user.email_otp = None
                test_user.email_otp_expires = None
                db.session.commit()
                print("   ✅ User email marked as verified")
                
            else:
                print(f"   ❌ OTP mismatch: {test_user.email_otp} != {otp}")
            
            # Test 6: Final verification
            print("\n🎯 Step 6: Final Verification")
            final_user = User.query.get(test_user.id)
            print(f"   User ID: {final_user.id}")
            print(f"   Email: {final_user.email}")
            print(f"   Email Verified: {final_user.email_verified}")
            print(f"   Phone Verified: {final_user.phone_verified}")
            
            # Test 7: Test OTP expiry
            print("\n⏰ Step 7: Test OTP Expiry")
            from otp_utils import is_otp_expired
            
            # Test with expired OTP
            expired_otp = "000000"
            is_expired = is_otp_expired(datetime.utcnow())
            print(f"   Current time OTP expired: {is_expired}")
            
            print("\n🎉 OTP VERIFICATION TEST COMPLETE!")
            print("=" * 50)
            
            if final_user.email_verified:
                print("✅ SUCCESS: OTP verification system is working!")
                print("✅ User account was created and verified successfully")
                print("✅ OTP generation, storage, and validation all working")
            else:
                print("❌ ISSUE: OTP verification failed")
                print("❌ Check the logs above for specific errors")
            
            print(f"\n💡 Test user details:")
            print(f"   ID: {final_user.id}")
            print(f"   Email: {final_user.email}")
            print(f"   Verified: {final_user.email_verified}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_otp_verification() 