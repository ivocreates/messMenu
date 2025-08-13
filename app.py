from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
from functools import wraps
from config import config
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config.from_object(config)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions for file upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the relative path"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(file_path)
            # Return relative path for storing in database
            return f"uploads/images/{unique_filename}"
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    return None

def delete_uploaded_file(file_path):
    """Delete uploaded file from filesystem"""
    if file_path and file_path.startswith('uploads/images/'):
        full_path = os.path.join('static', file_path)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

# Database configuration
DATABASE = app.config['DATABASE']

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_type'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    # Get today's menu for home page
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    daily_menu = conn.execute('''
        SELECT mi.*, dm.date 
        FROM daily_menu dm 
        JOIN menu_items mi ON dm.menu_item_id = mi.id 
        WHERE dm.date = ? AND mi.available = 1
        ORDER BY mi.category, mi.name
    ''', (today,)).fetchall()
    conn.close()
    
    return render_template('home.html', daily_menu=daily_menu)

# Public route: today's menu (no login required)
@app.route('/menu/today')
def public_today_menu():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    daily_items = conn.execute('''
        SELECT dm.*, mi.name, mi.description, mi.price, mi.id as menu_item_id,
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.id) as review_count
        FROM daily_menu dm 
        JOIN menu_items mi ON dm.menu_item_id = mi.id 
        LEFT JOIN reviews r ON mi.id = r.menu_item_id
        WHERE dm.date = ?
        GROUP BY dm.id
    ''', (today,)).fetchall()
    conn.close()
    return render_template('public_today_menu.html', daily_items=daily_items, today=today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        if user_type == 'admin':
            user = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?',
                              (username, password_hash)).fetchone()
        else:
            user = conn.execute('SELECT * FROM students WHERE username = ? AND password = ?',
                              (username, password_hash)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user_type
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard' if user_type == 'admin' else 'student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        full_name = request.form['full_name']
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (username, password, email, full_name) VALUES (?, ?, ?, ?)',
                        (username, password_hash, email, full_name))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get dashboard statistics
    total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    total_menu_items = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
    pending_orders = conn.execute('SELECT COUNT(*) as count FROM orders WHERE status = "pending"').fetchone()['count']
    total_revenue = conn.execute('SELECT SUM(total_amount) as total FROM orders WHERE status = "completed"').fetchone()['total'] or 0
    
    # Recent orders
    recent_orders = conn.execute('''
        SELECT o.*, s.full_name 
        FROM orders o 
        JOIN students s ON o.student_id = s.id 
        ORDER BY o.created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         total_students=total_students,
                         total_menu_items=total_menu_items,
                         pending_orders=pending_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

@app.route('/admin/menu')
@admin_required
def admin_menu():
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM menu_items ORDER BY name').fetchall()
    conn.close()
    return render_template('admin/menu.html', menu_items=menu_items)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        
        # Handle image upload or URL
        image_path = None
        
        # Check for file upload first
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename:  # File was selected
                image_path = save_uploaded_file(file)
                if not image_path:
                    flash('Error uploading image. Please try again.', 'error')
                    return render_template('admin/add_menu_item.html')
        
        # If no file uploaded, check for URL
        if not image_path:
            image_url = request.form.get('image_url', '').strip()
            if image_url:
                image_path = image_url
        
        conn = get_db_connection()
        conn.execute('INSERT INTO menu_items (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)',
                    (name, description, price, category, image_path))
        conn.commit()
        conn.close()
        
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('admin_menu'))
    
    return render_template('admin/add_menu_item.html')

@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu_item(item_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        available = 'available' in request.form
        
        # Get current item to handle image replacement
        current_item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
        current_image = current_item['image_url'] if current_item else None
        
        # Handle image upload or URL
        image_path = current_image  # Keep current image by default
        
        # Check for file upload first
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename:  # New file was selected
                new_image_path = save_uploaded_file(file)
                if new_image_path:
                    # Delete old uploaded file if it exists
                    if current_image and current_image.startswith('uploads/images/'):
                        delete_uploaded_file(current_image)
                    image_path = new_image_path
                else:
                    flash('Error uploading image. Please try again.', 'error')
                    conn.close()
                    return render_template('admin/edit_menu_item.html', item=current_item)
        
        # If no file uploaded, check for URL change
        elif 'image_url' in request.form:
            new_image_url = request.form.get('image_url', '').strip()
            if new_image_url != current_image:
                # Delete old uploaded file if switching to URL
                if current_image and current_image.startswith('uploads/images/'):
                    delete_uploaded_file(current_image)
                image_path = new_image_url
        
        conn.execute('''UPDATE menu_items 
                        SET name = ?, description = ?, price = ?, category = ?, image_url = ?, available = ?
                        WHERE id = ?''',
                    (name, description, price, category, image_path, available, item_id))
        conn.commit()
        conn.close()
        
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('admin_menu'))
    
    item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    return render_template('admin/edit_menu_item.html', item=item)

@app.route('/admin/menu/delete/<int:item_id>')
@admin_required
def delete_menu_item(item_id):
    conn = get_db_connection()
    
    # Get the item to delete its image file if needed
    item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
    
    # Delete the menu item
    conn.execute('DELETE FROM menu_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    # Delete uploaded image file if it exists
    if item and item['image_url'] and item['image_url'].startswith('uploads/images/'):
        delete_uploaded_file(item['image_url'])
    
    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('admin_menu'))

@app.route('/admin/daily-menu')
@admin_required
def daily_menu():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's menu
    daily_items = conn.execute('''
        SELECT dm.*, mi.name, mi.description, mi.price 
        FROM daily_menu dm 
        JOIN menu_items mi ON dm.menu_item_id = mi.id 
        WHERE dm.date = ?
    ''', (today,)).fetchall()
    
    # Get all menu items for adding
    all_items = conn.execute('SELECT * FROM menu_items WHERE available = 1').fetchall()
    
    conn.close()
    
    return render_template('admin/daily_menu.html', daily_items=daily_items, all_items=all_items, today=today)

# Remove item from today's menu
@app.route('/admin/daily-menu/delete/<int:daily_id>')
@admin_required
def delete_daily_menu_item(daily_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM daily_menu WHERE id = ?', (daily_id,))
    conn.commit()
    conn.close()
    flash('Item removed from today\'s menu!', 'success')
    return redirect(url_for('daily_menu'))

@app.route('/admin/daily-menu/add', methods=['POST'])
@admin_required
def add_daily_menu_item():
    menu_item_id = request.form['menu_item_id']
    date = request.form['date']
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO daily_menu (menu_item_id, date) VALUES (?, ?)',
                    (menu_item_id, date))
        conn.commit()
        flash('Item added to daily menu!', 'success')
    except sqlite3.IntegrityError:
        flash('Item already in daily menu for this date', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('daily_menu'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.*, s.full_name 
        FROM orders o 
        JOIN students s ON o.student_id = s.id 
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin/orders.html', orders=orders)

# Admin view: student bills
@app.route('/admin/bills')
@admin_required
def admin_bills():
    conn = get_db_connection()
    bills = conn.execute('''
        SELECT s.id as student_id, s.full_name, s.username, COALESCE(SUM(o.total_amount),0) as total
        FROM students s
        LEFT JOIN orders o ON s.id = o.student_id AND o.status = "completed" AND o.cleared = 0
        GROUP BY s.id
        ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/bills.html', bills=bills)

# Admin: clear student bill (mark all completed orders as cleared)
@app.route('/admin/bills/clear/<int:student_id>', methods=['POST'])
@admin_required
def clear_student_bill(student_id):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET cleared = 1 WHERE student_id = ? AND status = "completed"', (student_id,))
    conn.commit()
    conn.close()
    flash('Student bill cleared!', 'success')
    return redirect(url_for('admin_bills'))

# Admin: view detailed bill for a student
@app.route('/admin/bills/view/<int:student_id>')
@admin_required
def view_student_bill(student_id):
    conn = get_db_connection()
    
    # Get student info
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    # Get all orders for this student
    orders = conn.execute('''
        SELECT o.*, 
               GROUP_CONCAT(mi.name || ' x' || oi.quantity) as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE o.student_id = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', (student_id,)).fetchall()
    
    # Calculate totals
    total_pending = conn.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE student_id = ? AND status = "completed" AND cleared = 0', (student_id,)).fetchone()['total']
    total_cleared = conn.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE student_id = ? AND cleared = 1', (student_id,)).fetchone()['total']
    
    conn.close()
    
    return render_template('admin/view_bill.html', 
                         student=student, 
                         orders=orders,
                         total_pending=total_pending,
                         total_cleared=total_cleared)

# Admin: edit order details
@app.route('/admin/bills/edit/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def edit_order_bill(order_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        total_amount = float(request.form['total_amount'])
        status = request.form['status']
        
        conn.execute('UPDATE orders SET total_amount = ?, status = ? WHERE id = ?',
                    (total_amount, status, order_id))
        conn.commit()
        conn.close()
        
        flash('Order updated successfully!', 'success')
        return redirect(url_for('admin_bills'))
    
    # Get order details
    order = conn.execute('''
        SELECT o.*, s.full_name, s.username,
               GROUP_CONCAT(mi.name || ' (x' || oi.quantity || ' @ ₹' || oi.price || ')' SEPARATOR ', ') as items
        FROM orders o
        JOIN students s ON o.student_id = s.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE o.id = ?
        GROUP BY o.id
    ''', (order_id,)).fetchone()
    
    conn.close()
    
    return render_template('admin/edit_bill.html', order=order)

# Admin: delete order
@app.route('/admin/bills/delete/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    conn = get_db_connection()
    
    # Delete order items first
    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    
    # Delete order
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    
    conn.commit()
    conn.close()
    
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('admin_bills'))

# Admin view: registered students
@app.route('/admin/students')
@admin_required
def admin_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/students.html', students=students)

@app.route('/admin/orders/update/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
    flash('Order status updated!', 'success')
    return redirect(url_for('admin_orders'))

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    conn = get_db_connection()
    
    # Get today's menu
    today = datetime.now().strftime('%Y-%m-%d')
    daily_items = conn.execute('''
        SELECT dm.*, mi.name, mi.description, mi.price, mi.id as menu_item_id,
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.id) as review_count
        FROM daily_menu dm 
        JOIN menu_items mi ON dm.menu_item_id = mi.id 
        LEFT JOIN reviews r ON mi.id = r.menu_item_id
        WHERE dm.date = ?
        GROUP BY dm.id
    ''', (today,)).fetchall()
    
    # Get recent orders
    recent_orders = conn.execute('''
        SELECT * FROM orders 
        WHERE student_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('student/dashboard.html', daily_items=daily_items, recent_orders=recent_orders)

# Student profile update
@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            conn.execute('UPDATE students SET full_name=?, email=?, password=? WHERE id=?', (full_name, email, password_hash, session['user_id']))
        else:
            conn.execute('UPDATE students SET full_name=?, email=? WHERE id=?', (full_name, email, session['user_id']))
        conn.commit()
        flash('Profile updated!', 'success')
        student = conn.execute('SELECT * FROM students WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('student/profile.html', student=student)

@app.route('/student/menu')
@login_required
def student_menu():
    conn = get_db_connection()
    menu_items = conn.execute('''
        SELECT mi.*, 
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.id) as review_count
        FROM menu_items mi 
        LEFT JOIN reviews r ON mi.id = r.menu_item_id
        WHERE mi.available = 1
        GROUP BY mi.id
        ORDER BY mi.category, mi.name
    ''').fetchall()
    conn.close()
    
    return render_template('student/menu.html', menu_items=menu_items)

@app.route('/student/cart')
@login_required
def shopping_cart():
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM menu_items WHERE available = 1 ORDER BY category, name').fetchall()
    conn.close()
    return render_template('student/cart.html', menu_items=menu_items)

@app.route('/student/reviews')
@login_required
def student_reviews():
    conn = get_db_connection()
    reviews = conn.execute('''
        SELECT r.*, mi.name as menu_item_name
        FROM reviews r
        JOIN menu_items mi ON r.menu_item_id = mi.id
        WHERE r.student_id = ?
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('student/reviews.html', reviews=reviews)

@app.route('/student/review/<int:item_id>', methods=['GET', 'POST'])
@login_required
def add_review(item_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        
        # Check if user already reviewed this item
        existing = conn.execute('SELECT id FROM reviews WHERE student_id = ? AND menu_item_id = ?',
                               (session['user_id'], item_id)).fetchone()
        
        if existing:
            conn.execute('''UPDATE reviews 
                           SET rating = ?, comment = ?, created_at = CURRENT_TIMESTAMP
                           WHERE id = ?''',
                        (rating, comment, existing['id']))
            flash('Review updated successfully!', 'success')
        else:
            conn.execute('INSERT INTO reviews (student_id, menu_item_id, rating, comment) VALUES (?, ?, ?, ?)',
                        (session['user_id'], item_id, rating, comment))
            flash('Review added successfully!', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('student_menu'))
    
    item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
    existing_review = conn.execute('SELECT * FROM reviews WHERE student_id = ? AND menu_item_id = ?',
                                  (session['user_id'], item_id)).fetchone()
    conn.close()
    
    return render_template('student/review.html', item=item, existing_review=existing_review)

@app.route('/student/orders')
@login_required
def student_orders():
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT * FROM orders 
        WHERE student_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('student/orders.html', orders=orders)

@app.route('/student/order', methods=['POST'])
@login_required
def place_order():
    items = request.json.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items selected'}), 400
    
    conn = get_db_connection()
    
    # Calculate total
    total = 0
    for item in items:
        price = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()['price']
        total += price * item['quantity']
    
    # Create order
    order_id = conn.execute('''
        INSERT INTO orders (student_id, total_amount, status) 
        VALUES (?, ?, 'pending')
    ''', (session['user_id'], total)).lastrowid
    
    # Add order items
    for item in items:
        price = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()['price']
        conn.execute('''
            INSERT INTO order_items (order_id, menu_item_id, quantity, price) 
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['id'], item['quantity'], price))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'order_id': order_id})

@app.route('/student/bills')
@login_required
def student_bills():
    conn = get_db_connection()
    
    # Weekly bills
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    weekly_orders = conn.execute('''
        SELECT * FROM orders 
        WHERE student_id = ? AND created_at >= ? AND status = 'completed' AND cleared = 0
        ORDER BY created_at DESC
    ''', (session['user_id'], week_ago)).fetchall()
    
    # Monthly bills
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    monthly_orders = conn.execute('''
        SELECT * FROM orders 
        WHERE student_id = ? AND created_at >= ? AND status = 'completed' AND cleared = 0
        ORDER BY created_at DESC
    ''', (session['user_id'], month_ago)).fetchall()
    
    conn.close()
    
    weekly_total = sum(order['total_amount'] for order in weekly_orders)
    monthly_total = sum(order['total_amount'] for order in monthly_orders)
    
    return render_template('student/bills.html', 
                         weekly_orders=weekly_orders,
                         monthly_orders=monthly_orders,
                         weekly_total=weekly_total,
                         monthly_total=monthly_total)

# Admin profile update
@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admins WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            conn.execute('UPDATE admins SET full_name=?, email=?, password=? WHERE id=?', (full_name, email, password_hash, session['user_id']))
        else:
            conn.execute('UPDATE admins SET full_name=?, email=? WHERE id=?', (full_name, email, session['user_id']))
        conn.commit()
        flash('Profile updated!', 'success')
        admin = conn.execute('SELECT * FROM admins WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('admin/profile.html', admin=admin)

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
