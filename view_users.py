#!/usr/bin/env python3
"""
Simple script to view all users in the ClauseEase AI database
"""

from app import create_app
from models import User
from extensions import db

def view_users():
    """Display all users in the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            if not users:
                print("❌ No users found in database!")
                return
            
            print(f"✅ Found {len(users)} user(s) in database:\n")
            print("-" * 80)
            
            for user in users:
                print(f"👤 User ID: {user.id}")
                print(f"   Name: {user.first_name} {user.last_name}")
                print(f"   Email: {user.email or 'Not provided'}")
                print(f"   Phone: {user.phone or 'Not provided'}")
                print(f"   Gender: {user.gender}")
                print(f"   Date of Birth: {user.date_of_birth}")
                print(f"   Email Verified: {'✅ Yes' if user.email_verified else '❌ No'}")
                print(f"   Phone Verified: {'✅ Yes' if user.phone_verified else '❌ No'}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Updated: {user.updated_at}")
                print("-" * 80)
                
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
            print("Make sure your database is running and .env file is configured!")

if __name__ == "__main__":
    view_users() 