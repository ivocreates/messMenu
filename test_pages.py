#!/usr/bin/env python3
"""
Quick test script to verify all pages are accessible and working properly.
This script tests that all main routes return successful responses.
"""

import requests
import sys
from urllib.parse import urljoin

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5000"

# List of pages to test
PAGES_TO_TEST = [
    "/",           # Home page
    "/login",      # Login page  
    "/register",   # Register page
]

def test_page(url, page_name):
    """Test a single page and return results."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text
            # Check for basic HTML structure and no empty pages
            if len(content) > 100 and "<html" in content and "<body" in content:
                print(f"✅ {page_name}: OK (Status: {response.status_code}, Content Length: {len(content)})")
                return True
            else:
                print(f"❌ {page_name}: Empty or invalid content (Length: {len(content)})")
                return False
        else:
            print(f"❌ {page_name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {page_name}: Connection error - {e}")
        return False

def main():
    """Run all page tests."""
    print("🧪 Testing Mess Menu Rater Pages...")
    print("="*50)
    
    # Test server connectivity
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"🌐 Server Status: Connected (Flask app running)")
    except requests.exceptions.RequestException:
        print(f"❌ Server Status: Cannot connect to {BASE_URL}")
        print("   Make sure the Flask app is running with 'python app.py'")
        sys.exit(1)
    
    print()
    
    # Test each page
    all_tests_passed = True
    for page_path in PAGES_TO_TEST:
        url = urljoin(BASE_URL, page_path)
        page_name = page_path if page_path != "/" else "Home"
        success = test_page(url, page_name)
        if not success:
            all_tests_passed = False
    
    print()
    print("="*50)
    
    if all_tests_passed:
        print("🎉 All tests passed! The web app is working correctly.")
        print(f"🔗 Visit the app at: {BASE_URL}")
        print()
        print("Demo Accounts:")
        print("  👨‍🎓 Student: username=student, password=student123")
        print("  🔧 Admin: username=admin, password=admin123")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
