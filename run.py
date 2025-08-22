#!/usr/bin/env python3
"""
Simple launcher for ClauseEase AI Flask application
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the app
from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting ClauseEase AI...")
    print("📁 Templates folder:", app.template_folder)
    print("📁 Static folder:", app.static_folder)
    app.run(debug=True, host='127.0.0.1', port=5000) 