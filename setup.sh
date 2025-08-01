#!/bin/bash

# Mess Menu Rater - Setup Script
# This script sets up the complete environment for the Mess Menu Rater application

echo "🍽️ Setting up Mess Menu Rater..."
echo "=================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Install required packages
echo "📦 Installing required packages..."
pip install flask requests sqlite3

# Initialize database
echo "🗄️ Setting up database..."
python -c "
import sqlite3
import os

# Create database directory
if not os.path.exists('database'):
    os.makedirs('database')

# Initialize database with schema
conn = sqlite3.connect('database/mess_menu.db')
cursor = conn.cursor()

# Read and execute schema
try:
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)
    print('✅ Database schema loaded successfully')
except FileNotFoundError:
    print('⚠️ Schema file not found, creating basic schema...')
    # Create basic schema if file doesn't exist
    schema = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        meal_type TEXT NOT NULL,
        available BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        special_instructions TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    );
    
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        comment TEXT,
        review_text TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    );
    '''
    cursor.executescript(schema)

# Create demo accounts
cursor.execute('''
    INSERT OR IGNORE INTO users (username, email, password, full_name, role) 
    VALUES (?, ?, ?, ?, ?)
''', ('admin', 'admin@mess.com', 'admin123', 'Administrator', 'admin'))

cursor.execute('''
    INSERT OR IGNORE INTO users (username, email, password, full_name, role) 
    VALUES (?, ?, ?, ?, ?)
''', ('student', 'student@mess.com', 'student123', 'Demo Student', 'student'))

# Add sample menu items
menu_items = [
    ('Dal Rice', 'Traditional dal with steamed rice', 45.0, 'Main Course', 'lunch'),
    ('Chicken Curry', 'Spicy chicken curry with rice', 85.0, 'Main Course', 'lunch'),
    ('Paneer Butter Masala', 'Rich paneer in tomato gravy', 75.0, 'Main Course', 'dinner'),
    ('Vegetable Biryani', 'Aromatic rice with mixed vegetables', 65.0, 'Main Course', 'lunch'),
    ('Masala Dosa', 'Crispy dosa with potato filling', 55.0, 'South Indian', 'breakfast'),
    ('Idli Sambar', 'Steamed idli with sambar', 35.0, 'South Indian', 'breakfast'),
    ('Chapati with Dal', 'Fresh chapati with lentil curry', 40.0, 'Main Course', 'dinner'),
    ('Fried Rice', 'Chinese style fried rice', 60.0, 'Chinese', 'lunch'),
    ('Tea', 'Hot masala tea', 10.0, 'Beverages', 'breakfast'),
    ('Coffee', 'Filter coffee', 15.0, 'Beverages', 'breakfast')
]

for item in menu_items:
    cursor.execute('''
        INSERT OR IGNORE INTO menu_items (name, description, price, category, meal_type)
        VALUES (?, ?, ?, ?, ?)
    ''', item)

conn.commit()
conn.close()
print('✅ Database initialized with demo data')
"

# Create static directories
echo "📁 Creating required directories..."
mkdir -p static/css static/js static/images
mkdir -p templates

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Demo Accounts Created:"
echo "   👨‍🎓 Student: username=student, password=student123"
echo "   👨‍💼 Admin: username=admin, password=admin123"
echo ""
echo "🚀 To start the application, run:"
echo "   ./start_app.sh (Linux/Mac) or start_app.bat (Windows)"
echo ""
echo "🌐 The app will be available at: http://localhost:5000"
echo "=================================="
