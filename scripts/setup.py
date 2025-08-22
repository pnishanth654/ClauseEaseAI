#!/usr/bin/env python3
"""
Setup script for ClauseEase AI Authentication System
This script helps you configure the application for first-time use.
"""

import os
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create a .env file with default configuration."""
    if os.path.exists('.env'):
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    secret_key = generate_secret_key(64)
    
    env_content = f"""# Flask Configuration
FLASK_SECRET_KEY={secret_key}

# Database Configuration (PostgreSQL)
# Replace with your actual database URL
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DBNAME

# Email Configuration
# Option A: Gmail (Personal)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER="Your App <your@gmail.com>"

# Option B: Mailtrap (Development)
# MAIL_SERVER=sandbox.smtp.mailtrap.io
# MAIL_PORT=2525
# MAIL_USE_TLS=true
# MAIL_USERNAME=your_mailtrap_username
# MAIL_PASSWORD=your_mailtrap_password
# MAIL_DEFAULT_SENDER="Your App <noreply@yourapp.com>"

# Rate Limiting
RATELIMIT_STORAGE_URI=memory://

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default configuration")
    print("📝 Please update the .env file with your actual database and email settings")

def main():
    print("🚀 ClauseEase AI Authentication System Setup")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('.venv'):
        print("📦 Creating virtual environment...")
        os.system('python -m venv .venv')
        print("✅ Virtual environment created")
        print("💡 Activate it with: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (macOS/Linux)")
    else:
        print("✅ Virtual environment already exists")
    
    # Create .env file
    create_env_file()
    
    print("\n📋 Next Steps:")
    print("1. Activate your virtual environment")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Update .env file with your database and email settings")
    print("4. Run the application: python app.py")
    print("\n📚 For detailed setup instructions, see README.md")

if __name__ == "__main__":
    main() 