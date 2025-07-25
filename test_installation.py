#!/usr/bin/env python3
"""
Test script for Mess Menu Rater Application
This script runs basic tests to verify the installation
"""

import sqlite3
import os
import sys
from datetime import date

def test_database():
    """Test database connectivity and tables"""
    print("Testing database...")
    
    if not os.path.exists('database/mess_menu.db'):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect('database/mess_menu.db')
        cursor = conn.cursor()
        
        # Test tables exist
        tables = ['students', 'admins', 'menu_items', 'ratings', 'orders', 'order_items']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"❌ Table {table} not found")
                return False
        
        # Test admin user exists
        cursor.execute("SELECT COUNT(*) FROM admins WHERE username='admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("❌ Default admin user not found")
            return False
        
        # Test sample data
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE date=?", (today,))
        menu_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✓ Database OK - {menu_count} menu items for today")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_files():
    """Test required files exist"""
    print("Testing required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'database/schema.sql',
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✓ All required files present")
    return True

def test_imports():
    """Test Python imports"""
    print("Testing Python imports...")
    
    try:
        import flask
        import sqlite3
        import werkzeug
        print(f"✓ Flask {flask.__version__} installed")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_application():
    """Test Flask application creation"""
    print("Testing Flask application...")
    
    try:
        # Temporarily add current directory to path
        sys.path.insert(0, '.')
        from app import app
        
        # Test app creation
        if app is None:
            print("❌ Flask app not created")
            return False
        
        # Test routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/login', '/register', '/admin']
        
        for route in required_routes:
            if route not in routes:
                print(f"❌ Route {route} not found")
                return False
        
        print("✓ Flask application OK")
        return True
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("Mess Menu Rater - Installation Test")
    print("=" * 50)
    
    tests = [
        test_files,
        test_imports,
        test_database,
        test_application
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to use.")
        print("\nTo start the application:")
        print("- Windows: run start_app.bat")
        print("- Manual: python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        if not os.path.exists('database/mess_menu.db'):
            print("\nTip: Run 'python setup.py' to initialize the database")
    
    print("=" * 50)

if __name__ == '__main__':
    run_tests()
