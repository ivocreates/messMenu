import sqlite3
import hashlib
from datetime import datetime

def init_database():
    conn = sqlite3.connect('messmenu.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create admins table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create menu_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        available BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create daily_menu table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id),
        UNIQUE(menu_item_id, date)
    )
    ''')
    
    # Create reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'preparing', 'ready', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    )
    ''')
    
    # Insert default admin
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO admins (username, password, email, full_name) 
    VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password, 'admin@messmenu.com', 'Administrator'))
    
    # Insert sample menu items
    sample_items = [
        ('Chicken Biryani', 'Fragrant basmati rice with tender chicken pieces', 150.0, 'Main Course'),
        ('Vegetable Pulao', 'Mixed vegetable rice with aromatic spices', 100.0, 'Main Course'),
        ('Dal Tadka', 'Yellow lentils tempered with cumin and spices', 80.0, 'Curry'),
        ('Paneer Butter Masala', 'Cottage cheese in rich tomato gravy', 120.0, 'Curry'),
        ('Roti', 'Fresh wheat flatbread', 15.0, 'Bread'),
        ('Naan', 'Leavened bread baked in tandoor', 25.0, 'Bread'),
        ('Mixed Vegetable Curry', 'Seasonal vegetables in curry sauce', 90.0, 'Curry'),
        ('Chicken Curry', 'Spicy chicken curry with traditional spices', 140.0, 'Curry'),
        ('Rice', 'Steamed basmati rice', 40.0, 'Rice'),
        ('Raita', 'Yogurt with cucumber and spices', 30.0, 'Side Dish'),
        ('Samosa', 'Crispy pastry with spiced potato filling', 20.0, 'Snacks'),
        ('Tea', 'Hot masala tea', 10.0, 'Beverages'),
        ('Lassi', 'Sweet yogurt drink', 25.0, 'Beverages'),
        ('Gulab Jamun', 'Sweet milk dumplings in syrup', 35.0, 'Dessert'),
        ('Ice Cream', 'Vanilla ice cream', 40.0, 'Dessert')
    ]
    
    for item in sample_items:
        cursor.execute('''
        INSERT OR IGNORE INTO menu_items (name, description, price, category) 
        VALUES (?, ?, ?, ?)
        ''', item)
    
    # Insert sample student
    student_password = hashlib.sha256('student123'.encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO students (username, password, email, full_name) 
    VALUES (?, ?, ?, ?)
    ''', ('student', student_password, 'student@messmenu.com', 'Test Student'))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")
    print("Default admin login: username='admin', password='admin123'")
    print("Default student login: username='student', password='student123'")

if __name__ == '__main__':
    init_database()
