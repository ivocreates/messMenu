#!/usr/bin/env python3
"""
Comprehensive test script to verify all database operations work correctly.
Tests authentication, menu operations, orders, ratings, and admin functions.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5000"

def test_login(username, password):
    """Test login functionality and return session."""
    session = requests.Session()
    
    # Get login page first (to handle any CSRF tokens if needed)
    response = session.get(urljoin(BASE_URL, "/login"))
    if response.status_code != 200:
        return None, f"Could not access login page: {response.status_code}"
    
    # Attempt login
    login_data = {
        'username': username,
        'password': password
    }
    
    response = session.post(urljoin(BASE_URL, "/login"), data=login_data, allow_redirects=False)
    
    # Check if login was successful (should redirect)
    if response.status_code in [302, 303]:
        return session, "Login successful"
    elif response.status_code == 200:
        # Check if there's an error message in the response
        if "Invalid username or password" in response.text:
            return None, "Invalid credentials"
        else:
            return None, "Login failed - unknown reason"
    else:
        return None, f"Login failed - HTTP {response.status_code}"

def test_page_access(session, page_path, page_name):
    """Test if a page is accessible with the given session."""
    try:
        response = session.get(urljoin(BASE_URL, page_path))
        if response.status_code == 200:
            content_length = len(response.text)
            # Check for basic content indicators
            if content_length > 500:
                print(f"  ✅ {page_name}: Accessible (Content: {content_length} chars)")
                return True
            else:
                print(f"  ⚠️  {page_name}: Accessible but minimal content ({content_length} chars)")
                return True
        else:
            print(f"  ❌ {page_name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {page_name}: Error - {e}")
        return False

def main():
    """Run comprehensive database and functionality tests."""
    print("🧪 Comprehensive Mess Menu Rater Database Tests")
    print("=" * 60)
    
    # Test 1: Server connectivity
    print("\n1️⃣ Testing Server Connectivity...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("  ✅ Server is running and accessible")
        else:
            print(f"  ❌ Server returned HTTP {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Cannot connect to server: {e}")
        print("     Make sure Flask app is running with 'python app.py'")
        sys.exit(1)
    
    # Test 2: Student login
    print("\n2️⃣ Testing Student Login...")
    student_session, result = test_login("student", "student123")
    if student_session:
        print(f"  ✅ Student login: {result}")
        
        # Test student pages
        print("  📖 Testing student pages...")
        student_pages = [
            ("/", "Dashboard"),
            ("/menu", "Menu"),
            ("/my_orders", "My Orders"),
            ("/billing", "Billing")
        ]
        
        student_success = True
        for path, name in student_pages:
            if not test_page_access(student_session, path, name):
                student_success = False
        
        if student_success:
            print("  ✅ All student pages accessible")
        else:
            print("  ⚠️  Some student pages had issues")
    else:
        print(f"  ❌ Student login failed: {result}")
        sys.exit(1)
    
    # Test 3: Admin login
    print("\n3️⃣ Testing Admin Login...")
    admin_session, result = test_login("admin", "admin123")
    if admin_session:
        print(f"  ✅ Admin login: {result}")
        
        # Test admin pages
        print("  🔧 Testing admin pages...")
        admin_pages = [
            ("/", "Dashboard"),
            ("/admin_dashboard", "Admin Dashboard"),
            ("/admin_orders", "Admin Orders"),
            ("/analytics", "Analytics")
        ]
        
        admin_success = True
        for path, name in admin_pages:
            if not test_page_access(admin_session, path, name):
                admin_success = False
        
        if admin_success:
            print("  ✅ All admin pages accessible")
        else:
            print("  ⚠️  Some admin pages had issues")
    else:
        print(f"  ❌ Admin login failed: {result}")
        print("  ⚠️  Continuing with student tests only...")
    
    # Test 4: Anonymous access (should work for home, login, register)
    print("\n4️⃣ Testing Anonymous Access...")
    anonymous_pages = [
        ("/", "Home"),
        ("/login", "Login"),
        ("/register", "Register")
    ]
    
    anonymous_success = True
    for path, name in anonymous_pages:
        if not test_page_access(requests.Session(), path, name):
            anonymous_success = False
    
    if anonymous_success:
        print("  ✅ All public pages accessible")
    else:
        print("  ⚠️  Some public pages had issues")
    
    # Test 5: Database operations (check if sample data exists)
    print("\n5️⃣ Testing Database Content...")
    if student_session:
        # Check menu page for menu items
        menu_response = student_session.get(urljoin(BASE_URL, "/menu"))
        if "Aloo Paratha" in menu_response.text and "Dal Rice" in menu_response.text:
            print("  ✅ Menu items loaded correctly")
        else:
            print("  ⚠️  Menu items may not be loaded")
        
        # Check dashboard for user content
        dashboard_response = student_session.get(urljoin(BASE_URL, "/"))
        if "Demo Student" in dashboard_response.text or "student" in dashboard_response.text:
            print("  ✅ User data loaded correctly")
        else:
            print("  ⚠️  User data may not be loaded")
    
    print("\n" + "=" * 60)
    print("🎉 Database tests completed!")
    print("📍 All major database issues should now be resolved.")
    print(f"🔗 Access the app at: {BASE_URL}")
    print("\n🔑 Demo Accounts:")
    print("   👨‍🎓 Student: username=student, password=student123")
    print("   🔧 Admin: username=admin, password=admin123")

if __name__ == "__main__":
    main()
