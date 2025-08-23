#!/usr/bin/env python3
"""
Reset database and create demo user for ClauseEase AI
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from models import User
from extensions import db

def reset_database():
    """Reset database and create demo user"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        print("🗑️  Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("🏗️  Creating all tables...")
        db.create_all()
        
        # Create demo user
        print("👤 Creating demo user...")
        demo_user = User(
            first_name="Demo",
            last_name="User",
            email="demo@example.com",
            phone="+1234567890",
            gender="Other",
            date_of_birth="1990-01-01",
            email_verified=True
        )
        demo_user.set_password("demo123")
        
        # Add to database
        db.session.add(demo_user)
        db.session.commit()
        
        print("✅ Demo user created successfully!")
        print("📧 Email: demo@example.com")
        print("📱 Phone: +1234567890")
        print("🔑 Password: demo123")
        print("✅ Email verified: Yes")
        print("\n🚀 You can now login with these credentials!")

if __name__ == "__main__":
    reset_database() 