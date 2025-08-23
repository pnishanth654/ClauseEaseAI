#!/usr/bin/env python3
"""
Email Test Script for ClauseEase AI
This script tests the email configuration independently of the Flask app
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

def create_test_app():
    """Create a minimal Flask app for testing email"""
    app = Flask(__name__)
    
    # Mail configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your-app-password")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "your-email@gmail.com")
    app.config["MAIL_TIMEOUT"] = 10
    app.config["MAIL_USE_SSL"] = False
    
    return app

def test_email_configuration():
    """Test email configuration and display current settings"""
    print("🔍 EMAIL CONFIGURATION TEST")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please create a .env file with your email credentials")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Get email configuration
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = os.getenv("MAIL_PORT")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_use_tls = os.getenv("MAIL_USE_TLS")
    
    print(f"📧 MAIL_SERVER: {mail_server}")
    print(f"📧 MAIL_PORT: {mail_port}")
    print(f"📧 MAIL_USERNAME: {mail_username}")
    print(f"📧 MAIL_PASSWORD: {'***' if mail_password else 'NOT SET'}")
    print(f"📧 MAIL_USE_TLS: {mail_use_tls}")
    
    # Check for common issues
    issues = []
    
    if not mail_server:
        issues.append("MAIL_SERVER not set")
    elif mail_server == "smtp.google.com":
        issues.append("❌ MAIL_SERVER should be 'smtp.gmail.com' (not 'smtp.google.com')")
    
    if not mail_username:
        issues.append("MAIL_USERNAME not set")
    elif mail_username == "your-email@gmail.com":
        issues.append("MAIL_USERNAME still has default value")
    
    if not mail_password:
        issues.append("MAIL_PASSWORD not set")
    elif mail_password == "your-app-password":
        issues.append("MAIL_PASSWORD still has default value")
    
    if issues:
        print("\n⚠️  CONFIGURATION ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("\n✅ Email configuration looks good!")
    return True

def test_email_sending():
    """Test actual email sending"""
    print("\n📧 EMAIL SENDING TEST")
    print("=" * 50)
    
    try:
        # Create test app
        app = create_test_app()
        
        # Initialize mail
        mail = Mail(app)
        
        with app.app_context():
            # Test email message
            test_email = "pnishanth654@gmail.com"  # Send to specified email for testing
            test_otp = "123456"  # Test OTP
            
            msg = Message(
                subject="🔐 ClauseEase AI - Verification Code",
                recipients=[test_email],
                body=f"""
This is a test email from ClauseEase AI

Test OTP Code: {test_otp}
Expires in: 10 minutes

If you received this email, your email configuration is working!

Best regards,
ClauseEase AI Team
                """.strip()
            )
            
            print(f"📧 Attempting to send test email to: {test_email}")
            print(f"📧 Subject: {msg.subject}")
            print(f"📧 Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            print(f"📧 TLS: {app.config['MAIL_USE_TLS']}")
            
            # Send email
            mail.send(msg)
            
            print("\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Check your inbox: {test_email}")
            print(f"   Look for subject: {msg.subject}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ EMAIL SENDING FAILED!")
        print(f"   Error: {e}")
        print(f"   Error Type: {type(e).__name__}")
        
        # Provide specific troubleshooting tips
        if "Authentication" in str(e):
            print("\n🔧 TROUBLESHOOTING: Authentication Error")
            print("   - Check your Gmail App Password")
            print("   - Make sure 2-Factor Authentication is enabled")
            print("   - Verify MAIL_USERNAME and MAIL_PASSWORD in .env")
        
        elif "Connection" in str(e):
            print("\n🔧 TROUBLESHOOTING: Connection Error")
            print("   - Check MAIL_SERVER (should be 'smtp.gmail.com')")
            print("   - Verify MAIL_PORT (should be 587)")
            print("   - Check your internet connection")
        
        elif "Timeout" in str(e):
            print("\n🔧 TROUBLESHOOTING: Timeout Error")
            print("   - Check your firewall settings")
            print("   - Try increasing MAIL_TIMEOUT in app.py")
            print("   - Check if Gmail is blocking the connection")
        
        return False

def test_otp_generation():
    """Test OTP generation functionality"""
    print("\n🔐 OTP GENERATION TEST")
    print("=" * 50)
    
    try:
        # Import OTP utilities
        sys.path.append('src')
        from otp_utils import generate_otp, get_otp_expiry_time
        
        # Generate test OTP
        test_otp = generate_otp()
        expiry_time = get_otp_expiry_time()
        
        print(f"🔐 Generated OTP: {test_otp}")
        print(f"⏰ Expires at: {expiry_time}")
        print(f"⏰ Length: {len(test_otp)} digits")
        
        # Verify OTP format
        if test_otp.isdigit() and len(test_otp) == 6:
            print("✅ OTP format is correct (6 digits)")
        else:
            print("❌ OTP format is incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ OTP generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CLAUSEEASE AI - EMAIL & OTP TEST SUITE")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_email_configuration()
    
    # Test 2: OTP Generation
    otp_ok = test_otp_generation()
    
    # Test 3: Email Sending (only if config is ok)
    email_ok = False
    if config_ok:
        email_ok = test_email_sending()
    else:
        print("\n⏭️  Skipping email test due to configuration issues")
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Configuration: {'PASS' if config_ok else 'FAIL'}")
    print(f"✅ OTP Generation: {'PASS' if otp_ok else 'FAIL'}")
    print(f"✅ Email Sending: {'PASS' if email_ok else 'FAIL'}")
    
    if config_ok and otp_ok and email_ok:
        print("\n🎉 ALL TESTS PASSED! Your email system is working perfectly!")
    elif config_ok and otp_ok:
        print("\n⚠️  Configuration and OTP are working, but email sending failed")
        print("   Check the error messages above for troubleshooting steps")
    else:
        print("\n❌ Some tests failed. Please fix the issues above before proceeding")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 