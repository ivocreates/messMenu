#!/usr/bin/env python3
"""
Setup script for Mess Menu Rater Application
This script initializes the database and creates the admin user
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def setup_database():
    """Setup the database with initial data"""
    print("Setting up database...")
    
    # Create database directory if it doesn't exist
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Connect to database
    conn = sqlite3.connect('database/mess_menu.db')
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # Create admin user with hashed password
    admin_password = generate_password_hash('admin123')
    
    try:
        # First, delete existing admin if any (for reset)
        conn.execute('DELETE FROM admins WHERE username = ?', ('admin',))
        
        # Insert new admin with properly hashed password
        conn.execute(
            'INSERT INTO admins (username, password, full_name) VALUES (?, ?, ?)',
            ('admin', admin_password, 'System Administrator')
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    except sqlite3.IntegrityError:
        print("✓ Admin user already exists")
    
    conn.commit()
    conn.close()
    print("✓ Database setup completed!")

def create_sample_data():
    """Create sample menu items for testing"""
    print("Creating sample data...")
    
    conn = sqlite3.connect('database/mess_menu.db')
    
    # Sample menu items for today
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    
    sample_items = [
        ('Idli Sambhar', 'Steamed rice cakes with lentil curry', 'breakfast', 25.00, today),
        ('Masala Dosa', 'Crispy crepe with spiced potato filling', 'breakfast', 35.00, today),
        ('Poha', 'Flattened rice with vegetables and spices', 'breakfast', 20.00, today),
        ('Dal Rice', 'Lentil curry with steamed rice', 'lunch', 40.00, today),
        ('Chicken Curry', 'Spiced chicken curry with rice', 'lunch', 80.00, today),
        ('Vegetable Biryani', 'Aromatic rice with mixed vegetables', 'lunch', 60.00, today),
        ('Rajma Rice', 'Kidney bean curry with rice', 'lunch', 45.00, today),
        ('Chapati with Dal', 'Indian bread with lentil curry', 'dinner', 35.00, today),
        ('Fried Rice', 'Wok-fried rice with vegetables', 'dinner', 45.00, today),
        ('Paneer Butter Masala', 'Cottage cheese in rich tomato gravy', 'dinner', 70.00, today),
        ('Tea', 'Indian spiced tea', 'snacks', 10.00, today),
        ('Coffee', 'Filter coffee', 'snacks', 15.00, today),
        ('Samosa', 'Deep-fried pastry with savory filling', 'snacks', 15.00, today),
        ('Sandwich', 'Vegetable sandwich', 'snacks', 25.00, today),
    ]
    
    for item in sample_items:
        try:
            conn.execute(
                'INSERT INTO menu_items (item_name, description, meal_type, price, date) VALUES (?, ?, ?, ?, ?)',
                item
            )
        except sqlite3.IntegrityError:
            pass  # Item already exists
    
    conn.commit()
    conn.close()
    print("✓ Sample data created!")

if __name__ == '__main__':
    print("=== Mess Menu Rater Setup ===")
    setup_database()
    create_sample_data()
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Run: python app.py")
    print("3. Open your browser and go to: http://localhost:5000")
    print("\nDefault admin credentials:")
    print("Username: admin")
    print("Password: admin123")
