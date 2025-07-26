#!/usr/bin/env python3
"""
Setup script for Mess Menu Rater Application
This script initializes the database and creates the admin user
"""

from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime, timedelta
import random
import os

def init_database():
    conn = sqlite3.connect('database/mess_menu.db')
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)
    
    # Create default admin with properly hashed password
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT OR REPLACE INTO admins (username, password, full_name) 
        VALUES (?, ?, ?)
    ''', ('admin', admin_password, 'System Administrator'))
    
    # Sample menu items for today
    today = datetime.now().strftime('%Y-%m-%d')
    
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
            cursor.execute(
                'INSERT INTO menu_items (item_name, description, meal_type, price, date) VALUES (?, ?, ?, ?, ?)',
                item
            )
        except sqlite3.IntegrityError:
            pass  # Item already exists
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with admin user: admin/admin123")

def create_database():
    """Create the database and tables from schema.sql"""
    try:
        # Create database directory if it doesn't exist
        os.makedirs('database', exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect('database/mess_menu.db')
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as schema_file:
            schema_sql = schema_file.read()
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
        
        # Update admin password with proper hash
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute("""
            UPDATE admins 
            SET password_hash = ? 
            WHERE username = 'admin'
        """, (admin_password_hash,))
        
        # Update student password with proper hash
        student_password_hash = generate_password_hash('password123')
        cursor.execute("""
            UPDATE students 
            SET password_hash = ? 
            WHERE username = 'student1'
        """, (student_password_hash,))
        
        conn.commit()
        conn.close()
        
        print("✅ Database created successfully!")
        print("✅ Admin credentials: admin / admin123")
        print("✅ Sample student: student1 / password123")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == '__main__':
    print("=== Mess Menu Rater Setup ===")
    init_database()
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Run: python app.py")
    print("3. Open your browser and go to: http://localhost:5000")
    print("\nDefault admin credentials:")
    print("Username: admin")
    print("Password: admin123")
