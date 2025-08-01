-- Fresh Database Schema for Mess Menu Rater
-- Created: August 2025
-- Theme Colors: #186F65, #B5CB99, #FCE09B, #B2533E

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;

-- Create Students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    student_id TEXT UNIQUE NOT NULL,
    room_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Create Admins table
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Create Menu Items table
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category TEXT NOT NULL, -- breakfast, lunch, dinner, snacks
    meal_type TEXT NOT NULL, -- veg, non-veg, vegan
    image_url TEXT,
    is_available BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, confirmed, preparing, ready, delivered, cancelled
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_time TEXT,
    special_instructions TEXT,
    payment_status TEXT DEFAULT 'pending', -- pending, paid, failed
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Create Order Items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- Create Ratings table
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    order_id INTEGER,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    UNIQUE(student_id, menu_item_id, order_id)
);

-- Insert default admin account
INSERT INTO admins (username, email, password_hash, full_name) VALUES 
('admin', 'admin@messmenu.com', 'scrypt:32768:8:1$ZjBmY2YwMTI5ODU4$e5b8b4c5d8a7f2e9c3b6a1d4e7f0c9b2a5d8e1f4c7b0a3d6e9f2c5b8a1d4e7f0', 'System Administrator');

-- Insert sample menu items
INSERT INTO menu_items (name, description, price, category, meal_type, is_available) VALUES 
-- Breakfast Items
('Poha', 'Flattened rice with vegetables and spices', 25.00, 'breakfast', 'veg', 1),
('Upma', 'Semolina cooked with vegetables', 30.00, 'breakfast', 'veg', 1),
('Idli Sambar', '4 pieces of steamed rice cakes with sambar', 35.00, 'breakfast', 'veg', 1),
('Masala Dosa', 'Crispy crepe with potato filling', 45.00, 'breakfast', 'veg', 1),
('Bread Omelette', 'Bread slices with spiced omelette', 40.00, 'breakfast', 'non-veg', 1),

-- Lunch Items
('Dal Rice', 'Yellow lentil curry with steamed rice', 50.00, 'lunch', 'veg', 1),
('Chicken Curry', 'Spicy chicken curry with rice', 85.00, 'lunch', 'non-veg', 1),
('Paneer Butter Masala', 'Cottage cheese in creamy tomato gravy', 75.00, 'lunch', 'veg', 1),
('Mixed Vegetable', 'Seasonal vegetables cooked with spices', 45.00, 'lunch', 'veg', 1),
('Fish Curry', 'Fresh fish in coconut curry with rice', 90.00, 'lunch', 'non-veg', 1),

-- Dinner Items
('Roti Sabzi', '4 wheat flatbreads with vegetable curry', 55.00, 'dinner', 'veg', 1),
('Biryani', 'Fragrant rice with marinated meat/vegetables', 95.00, 'dinner', 'non-veg', 1),
('Rajma Rice', 'Kidney bean curry with jeera rice', 60.00, 'dinner', 'veg', 1),
('Chole Bhature', 'Spiced chickpeas with fried bread', 70.00, 'dinner', 'veg', 1),

-- Snacks Items
('Samosa', 'Crispy fried pastry with potato filling', 15.00, 'snacks', 'veg', 1),
('Tea', 'Hot Indian spiced tea', 10.00, 'snacks', 'veg', 1),
('Coffee', 'Hot filter coffee', 15.00, 'snacks', 'veg', 1),
('Biscuits', 'Assorted tea biscuits', 12.00, 'snacks', 'veg', 1);

-- Insert sample student (password: student123)
INSERT INTO students (username, email, password_hash, full_name, phone, student_id, room_number) VALUES 
('student', 'student@college.edu', 'scrypt:32768:8:1$ZjBmY2YwMTI5ODU4$e5b8b4c5d8a7f2e9c3b6a1d4e7f0c9b2a5d8e1f4c7b0a3d6e9f2c5b8a1d4e7f0', 'John Doe', '9876543210', 'STU001', 'A-101');

-- Create indexes for better performance
CREATE INDEX idx_students_username ON students(username);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_admins_username ON admins(username);
CREATE INDEX idx_menu_items_category ON menu_items(category);
CREATE INDEX idx_orders_student_id ON orders(student_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_ratings_menu_item_id ON ratings(menu_item_id);
