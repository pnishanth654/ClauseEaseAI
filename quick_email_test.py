#!/usr/bin/env python3
"""
Quick Email Test - Simple script to test email configuration
"""

import os
from dotenv import load_dotenv

def main():
    print("🔍 QUICK EMAIL CONFIGURATION CHECK")
    print("=" * 40)
    
    # Load .env file
    load_dotenv()
    
    # Check key email settings
    mail_server = os.getenv("MAIL_SERVER")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    
    print(f"📧 MAIL_SERVER: {mail_server}")
    print(f"📧 MAIL_USERNAME: {mail_username}")
    print(f"📧 MAIL_PASSWORD: {'***' if mail_password else 'NOT SET'}")
    
    # Quick validation
    if mail_server == "smtp.google.com":
        print("\n❌ ISSUE: MAIL_SERVER should be 'smtp.gmail.com'")
        print("   Fix: Change 'smtp.google.com' to 'smtp.gmail.com' in .env")
        return False
    
    if not mail_username or mail_username == "your-email@gmail.com":
        print("\n❌ ISSUE: MAIL_USERNAME not properly set")
        return False
    
    if not mail_password or mail_password == "your-app-password":
        print("\n❌ ISSUE: MAIL_PASSWORD not properly set")
        return False
    
    print("\n✅ Configuration looks good!")
    print("   Run 'python test_email.py' for full testing")
    return True

if __name__ == "__main__":
    main() 