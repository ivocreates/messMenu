-- Mess Menu Rater Database Schema
-- SQLite Database Schema

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(100) NOT NULL,
    description TEXT,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
    price DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    is_available BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    UNIQUE(student_id, menu_item_id)
);

-- Orders table (KOT system)
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'preparing', 'ready', 'served', 'cancelled')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_menu_items_date ON menu_items(date);
CREATE INDEX IF NOT EXISTS idx_ratings_menu_item ON ratings(menu_item_id);
CREATE INDEX IF NOT EXISTS idx_ratings_student ON ratings(student_id);
CREATE INDEX IF NOT EXISTS idx_orders_student ON orders(student_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);

-- Insert default admin user (password: admin123)
-- The password will be properly hashed during setup
INSERT OR IGNORE INTO admins (username, password, full_name) 
VALUES ('admin', 'admin123', 'System Administrator');

-- Insert sample menu items for today
INSERT OR IGNORE INTO menu_items (item_name, description, meal_type, price, date) VALUES
('Idli Sambhar', 'Steamed rice cakes with lentil curry', 'breakfast', 25.00, date('now')),
('Masala Dosa', 'Crispy crepe with spiced potato filling', 'breakfast', 35.00, date('now')),
('Dal Rice', 'Lentil curry with steamed rice', 'lunch', 40.00, date('now')),
('Chicken Curry', 'Spiced chicken curry with rice', 'lunch', 80.00, date('now')),
('Vegetable Biryani', 'Aromatic rice with mixed vegetables', 'lunch', 60.00, date('now')),
('Chapati with Dal', 'Indian bread with lentil curry', 'dinner', 35.00, date('now')),
('Fried Rice', 'Wok-fried rice with vegetables', 'dinner', 45.00, date('now')),
('Tea', 'Indian spiced tea', 'snacks', 10.00, date('now')),
('Samosa', 'Deep-fried pastry with savory filling', 'snacks', 15.00, date('now'));
