-- Mess Menu Rater Database Schema
-- SQLite Database Schema (Updated for app.py compatibility)

-- Users table (unified students and admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    student_id VARCHAR(20) UNIQUE,
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    date DATE NOT NULL,
    is_available BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    UNIQUE(user_id, menu_item_id)
);

-- Orders table (KOT system)
CREATE TABLE IF NOT EXISTS orders (
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
);

-- Bills table (monthly billing)
CREATE TABLE IF NOT EXISTS bills (
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
);

-- Bill items table (detailed breakdown)
CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Insert demo accounts
INSERT OR REPLACE INTO users (username, email, full_name, password_hash, student_id, is_admin) VALUES
    ('student', 'student@mess.edu', 'Demo Student', 'pbkdf2:sha256:260000$nT8WkY6QP8$e6b2c5b8c5d7e8f9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8', 'STU001', 0),
    ('admin', 'admin@mess.edu', 'Demo Administrator', 'pbkdf2:sha256:260000$nT8WkY6QP8$e6b2c5b8c5d7e8f9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8', NULL, 1);

-- Insert sample menu items for today
INSERT OR REPLACE INTO menu_items (id, name, description, meal_type, price, date, is_available) VALUES
    (1, 'Aloo Paratha', 'Fresh potato stuffed paratha served with curd and pickle', 'breakfast', 25.00, date('now'), 1),
    (2, 'Poha', 'Traditional flattened rice with onions, mustard seeds and curry leaves', 'breakfast', 20.00, date('now'), 1),
    (3, 'Masala Chai', 'Hot spiced tea with milk and sugar', 'breakfast', 10.00, date('now'), 1),
    (4, 'Dal Rice', 'Yellow lentil curry with steamed basmati rice', 'lunch', 35.00, date('now'), 1),
    (5, 'Chicken Curry', 'Spicy chicken curry cooked in traditional spices', 'lunch', 65.00, date('now'), 1),
    (6, 'Mixed Vegetable', 'Seasonal vegetables cooked with aromatic spices', 'lunch', 30.00, date('now'), 1),
    (7, 'Chapati', 'Fresh whole wheat flatbread', 'lunch', 8.00, date('now'), 1),
    (8, 'Rajma Rice', 'Kidney bean curry served with basmati rice', 'dinner', 40.00, date('now'), 1),
    (9, 'Paneer Butter Masala', 'Cottage cheese in rich tomato and cream gravy', 'dinner', 55.00, date('now'), 1),
    (10, 'Samosa', 'Crispy fried pastry filled with spiced potatoes', 'snacks', 15.00, date('now'), 1);

-- Insert sample ratings
INSERT OR REPLACE INTO ratings (user_id, menu_item_id, rating, comment) VALUES
    (1, 1, 5, 'Amazing aloo paratha! Best I have had.'),
    (1, 4, 4, 'Good dal rice, could use more spices.'),
    (1, 8, 5, 'Perfect rajma! Reminded me of home cooking.');

-- Insert sample orders
INSERT OR REPLACE INTO orders (user_id, menu_item_id, quantity, unit_price, total_price, status, order_date, meal_type, special_instructions) VALUES
    (1, 1, 2, 25.00, 50.00, 'served', date('now'), 'breakfast', 'Extra curd please'),
    (1, 3, 1, 10.00, 10.00, 'served', date('now'), 'breakfast', NULL),
    (1, 4, 1, 35.00, 35.00, 'ready', date('now'), 'lunch', NULL),
    (1, 7, 2, 8.00, 16.00, 'ready', date('now'), 'lunch', 'Fresh and hot');

-- Create bills for the demo student
INSERT OR REPLACE INTO bills (user_id, month, year, total_amount, paid_amount, status, due_date) VALUES
    (1, 1, 2025, 250.00, 100.00, 'partial', date('now', '+30 days'));

-- Link orders to bills
INSERT OR REPLACE INTO bill_items (bill_id, order_id, amount) VALUES
    (1, 1, 50.00),
    (1, 2, 10.00),
    (1, 3, 35.00),
    (1, 4, 16.00);
