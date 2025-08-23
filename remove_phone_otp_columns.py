#!/usr/bin/env python3
"""
Script to remove phone OTP columns from the database
Run this script to clean up phone OTP related columns
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def remove_phone_otp_columns():
    print("🗑️ REMOVING PHONE OTP COLUMNS FROM DATABASE")
    print("=" * 50)
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env file!")
        return
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns exist before removing
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('phone_otp', 'phone_otp_expires', 'phone_verified')
            """))
            
            existing_columns = [row[0] for row in result]
            
            if not existing_columns:
                print("✅ No phone OTP columns found - already cleaned up!")
                return
            
            print(f"🔍 Found columns to remove: {existing_columns}")
            
            # Remove phone_otp column
            if 'phone_otp' in existing_columns:
                conn.execute(text("ALTER TABLE \"user\" DROP COLUMN phone_otp"))
                print("✅ Removed phone_otp column")
            
            # Remove phone_otp_expires column
            if 'phone_otp_expires' in existing_columns:
                conn.execute(text("ALTER TABLE \"user\" DROP COLUMN phone_otp_expires"))
                print("✅ Removed phone_otp_expires column")
            
            # Remove phone_verified column
            if 'phone_verified' in existing_columns:
                conn.execute(text("ALTER TABLE \"user\" DROP COLUMN phone_verified"))
                print("✅ Removed phone_verified column")
            
            conn.commit()
            print("\n🎉 Phone OTP columns successfully removed!")
            
    except Exception as e:
        print(f"❌ Error removing columns: {e}")
        print("🔧 Please check your database connection and permissions")

if __name__ == "__main__":
    remove_phone_otp_columns() 