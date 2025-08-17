#!/usr/bin/env python3
"""
Test script to verify OTP system is working
"""

from app import create_app
from otp_utils import generate_otp, send_email_otp, send_sms_otp

def test_otp_system():
    """Test the complete OTP system"""
    print("🧪 TESTING OTP SYSTEM...")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Generate test OTP
            otp = generate_otp()
            print(f"✅ Generated OTP: {otp}")
            print(f"   First 3 digits: {otp[:3]}")
            print(f"   Last 3 digits: {otp[3:]}")
            print()
            
            # Test Email OTP
            print("📧 Testing Email OTP...")
            email_result = send_email_otp("test@example.com", otp)
            print(f"Email OTP result: {email_result}")
            print()
            
            # Test SMS OTP
            print("📱 Testing SMS OTP...")
            sms_result = send_sms_otp("+1234567890", otp)
            print(f"SMS OTP result: {sms_result}")
            print()
            
            print("🎯 OTP TEST COMPLETE!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error testing OTP system: {e}")

if __name__ == "__main__":
    test_otp_system() 