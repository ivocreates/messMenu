#!/usr/bin/env python3
"""
Database initialization script for Mess Menu Rater
Creates tables and inserts demo data with proper password hashing
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_database():
    """Create the database and tables with proper data."""
    
    # Ensure database directory exists
    db_dir = "database"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, "mess_menu.db")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating new database: {db_path}")
    
    try:
        # Create tables
        print("Creating tables...")
        
        # Users table (unified students and admins)
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                full_name VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                student_id VARCHAR(20) UNIQUE,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Menu items table
        cursor.execute('''
            CREATE TABLE menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
                price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                date DATE NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ratings table
        cursor.execute('''
            CREATE TABLE ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
                UNIQUE(user_id, menu_item_id)
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled')),
                order_date DATE NOT NULL,
                meal_type VARCHAR(20) NOT NULL,
                special_instructions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
            )
        ''')
        
        # Bills table
        cursor.execute('''
            CREATE TABLE bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                status VARCHAR(20) NOT NULL DEFAULT 'unpaid' CHECK (status IN ('unpaid', 'partial', 'paid')),
                due_date DATE,
                paid_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, month, year)
            )
        ''')
        
        # Bill items table
        cursor.execute('''
            CREATE TABLE bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL,
                order_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
        ''')
        
        print("Tables created successfully!")
        
        # Insert demo users with proper password hashing
        print("Creating demo users...")
        student_password = generate_password_hash('student123')
        admin_password = generate_password_hash('admin123')
        
        cursor.execute('''
            INSERT INTO users (username, email, full_name, password_hash, student_id, is_admin) VALUES
            (?, ?, ?, ?, ?, ?)
        ''', ('student', 'student@mess.edu', 'Demo Student', student_password, 'STU001', 0))
        
        cursor.execute('''
            INSERT INTO users (username, email, full_name, password_hash, student_id, is_admin) VALUES
            (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@mess.edu', 'Demo Administrator', admin_password, None, 1))
        
        print("Demo users created!")
        print("  Student: username=student, password=student123")
        print("  Admin: username=admin, password=admin123")
        
        # Insert sample menu items
        print("Creating sample menu items...")
        menu_items = [
            ('Aloo Paratha', 'Fresh potato stuffed paratha served with curd and pickle', 'breakfast', 25.00),
            ('Poha', 'Traditional flattened rice with onions, mustard seeds and curry leaves', 'breakfast', 20.00),
            ('Masala Chai', 'Hot spiced tea with milk and sugar', 'breakfast', 10.00),
            ('Dal Rice', 'Yellow lentil curry with steamed basmati rice', 'lunch', 35.00),
            ('Chicken Curry', 'Spicy chicken curry cooked in traditional spices', 'lunch', 65.00),
            ('Mixed Vegetable', 'Seasonal vegetables cooked with aromatic spices', 'lunch', 30.00),
            ('Chapati', 'Fresh whole wheat flatbread', 'lunch', 8.00),
            ('Rajma Rice', 'Kidney bean curry served with basmati rice', 'dinner', 40.00),
            ('Paneer Butter Masala', 'Cottage cheese in rich tomato and cream gravy', 'dinner', 55.00),
            ('Samosa', 'Crispy fried pastry filled with spiced potatoes', 'snacks', 15.00)
        ]
        
        for item in menu_items:
            cursor.execute('''
                INSERT INTO menu_items (name, description, meal_type, price, date, is_available) 
                VALUES (?, ?, ?, ?, date('now'), 1)
            ''', item)
        
        print(f"Created {len(menu_items)} menu items!")
        
        # Insert sample ratings
        print("Creating sample ratings...")
        ratings = [
            (1, 1, 5, 'Amazing aloo paratha! Best I have had.'),
            (1, 4, 4, 'Good dal rice, could use more spices.'),
            (1, 8, 5, 'Perfect rajma! Reminded me of home cooking.')
        ]
        
        for rating in ratings:
            cursor.execute('''
                INSERT INTO ratings (user_id, menu_item_id, rating, comment) 
                VALUES (?, ?, ?, ?)
            ''', rating)
        
        print(f"Created {len(ratings)} sample ratings!")
        
        # Insert sample orders
        print("Creating sample orders...")
        orders = [
            (1, 1, 2, 25.00, 50.00, 'served', 'breakfast', 'Extra curd please'),
            (1, 3, 1, 10.00, 10.00, 'served', 'breakfast', None),
            (1, 4, 1, 35.00, 35.00, 'ready', 'lunch', None),
            (1, 7, 2, 8.00, 16.00, 'ready', 'lunch', 'Fresh and hot')
        ]
        
        for order in orders:
            cursor.execute('''
                INSERT INTO orders (user_id, menu_item_id, quantity, unit_price, total_price, status, order_date, meal_type, special_instructions) 
                VALUES (?, ?, ?, ?, ?, ?, date('now'), ?, ?)
            ''', order)
        
        print(f"Created {len(orders)} sample orders!")
        
        # Create sample bills
        print("Creating sample bills...")
        cursor.execute('''
            INSERT INTO bills (user_id, month, year, total_amount, paid_amount, status, due_date) 
            VALUES (1, 1, 2025, 250.00, 100.00, 'partial', date('now', '+30 days'))
        ''')
        
        # Link orders to bills
        cursor.execute('''
            INSERT INTO bill_items (bill_id, order_id, amount) VALUES
            (1, 1, 50.00),
            (1, 2, 10.00),
            (1, 3, 35.00),
            (1, 4, 16.00)
        ''')
        
        print("Sample bills created!")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Database initialized successfully!")
        print(f"📍 Database location: {db_path}")
        print("🎯 Ready to run the Flask app!")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
