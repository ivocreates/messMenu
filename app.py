from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, date
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mess_menu_rater_secret_key_2025'

# Database configuration
DATABASE = 'database/mess_menu.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = get_db_connection()
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

@app.route('/')
def index():
    """Home page showing today's menu"""
    conn = get_db_connection()
    today = date.today().strftime('%Y-%m-%d')
    
    # Get today's menu items with average ratings
    menu_items = conn.execute('''
        SELECT m.*, 
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.rating) as rating_count
        FROM menu_items m
        LEFT JOIN ratings r ON m.id = r.menu_item_id
        WHERE m.date = ?
        GROUP BY m.id
        ORDER BY m.meal_type, m.id
    ''', (today,)).fetchall()
    
    conn.close()
    return render_template('index.html', menu_items=menu_items, today=today)

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission"""
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']
    
    conn = get_db_connection()
    
    if user_type == 'admin':
        user = conn.execute(
            'SELECT * FROM admins WHERE username = ?', (username,)
        ).fetchone()
    else:
        user = conn.execute(
            'SELECT * FROM students WHERE username = ?', (username,)
        ).fetchone()
    
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_type'] = user_type
        
        if user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('index'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('login'))

@app.route('/register')
def register():
    """Student registration page"""
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    """Handle student registration"""
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['full_name']
    student_id = request.form['student_id']
    
    conn = get_db_connection()
    
    # Check if username already exists
    existing_user = conn.execute(
        'SELECT id FROM students WHERE username = ? OR student_id = ?', 
        (username, student_id)
    ).fetchone()
    
    if existing_user:
        flash('Username or Student ID already exists!')
        conn.close()
        return redirect(url_for('register'))
    
    # Create new student
    hashed_password = generate_password_hash(password)
    conn.execute(
        'INSERT INTO students (username, password, full_name, student_id) VALUES (?, ?, ?, ?)',
        (username, hashed_password, full_name, student_id)
    )
    conn.commit()
    conn.close()
    
    flash('Registration successful! Please login.')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get menu items for today
    today = date.today().strftime('%Y-%m-%d')
    menu_items = conn.execute(
        'SELECT * FROM menu_items WHERE date = ? ORDER BY meal_type, id', 
        (today,)
    ).fetchall()
    
    # Get recent ratings
    recent_ratings = conn.execute('''
        SELECT r.*, m.item_name, m.meal_type, s.full_name
        FROM ratings r
        JOIN menu_items m ON r.menu_item_id = m.id
        JOIN students s ON r.student_id = s.id
        ORDER BY r.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    return render_template('admin_dashboard.html', menu_items=menu_items, 
                         recent_ratings=recent_ratings, today=today)

@app.route('/admin/add_menu', methods=['POST'])
def add_menu_item():
    """Add menu item"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    item_name = request.form['item_name']
    description = request.form['description']
    meal_type = request.form['meal_type']
    price = request.form['price']
    menu_date = request.form['date']
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO menu_items (item_name, description, meal_type, price, date) VALUES (?, ?, ?, ?, ?)',
        (item_name, description, meal_type, float(price), menu_date)
    )
    conn.commit()
    conn.close()
    
    flash('Menu item added successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/rate_item', methods=['POST'])
def rate_item():
    """Rate a menu item"""
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'success': False, 'message': 'Please login to rate items'})
    
    menu_item_id = request.json['menu_item_id']
    rating = request.json['rating']
    comment = request.json.get('comment', '')
    
    conn = get_db_connection()
    
    # Check if user already rated this item
    existing_rating = conn.execute(
        'SELECT id FROM ratings WHERE student_id = ? AND menu_item_id = ?',
        (session['user_id'], menu_item_id)
    ).fetchone()
    
    if existing_rating:
        # Update existing rating
        conn.execute(
            'UPDATE ratings SET rating = ?, comment = ?, created_at = ? WHERE id = ?',
            (rating, comment, datetime.now(), existing_rating['id'])
        )
    else:
        # Create new rating
        conn.execute(
            'INSERT INTO ratings (student_id, menu_item_id, rating, comment) VALUES (?, ?, ?, ?)',
            (session['user_id'], menu_item_id, rating, comment)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Rating submitted successfully!'})

@app.route('/menu/<date>')
def menu_by_date(date):
    """Show menu for specific date"""
    conn = get_db_connection()
    
    menu_items = conn.execute('''
        SELECT m.*, 
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.rating) as rating_count
        FROM menu_items m
        LEFT JOIN ratings r ON m.id = r.menu_item_id
        WHERE m.date = ?
        GROUP BY m.id
        ORDER BY m.meal_type, m.id
    ''', (date,)).fetchall()
    
    conn.close()
    return render_template('index.html', menu_items=menu_items, today=date)

@app.route('/analytics')
def analytics():
    """Analytics page for admin"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get top rated items
    top_items = conn.execute('''
        SELECT m.item_name, AVG(r.rating) as avg_rating, COUNT(r.rating) as rating_count
        FROM menu_items m
        JOIN ratings r ON m.id = r.menu_item_id
        GROUP BY m.id
        HAVING COUNT(r.rating) >= 3
        ORDER BY avg_rating DESC
        LIMIT 10
    ''').fetchall()
    
    # Get rating distribution
    rating_distribution = conn.execute('''
        SELECT rating, COUNT(*) as count
        FROM ratings
        GROUP BY rating
        ORDER BY rating
    ''').fetchall()
    
    conn.close()
    return render_template('analytics.html', top_items=top_items, 
                         rating_distribution=rating_distribution)

@app.route('/place_order', methods=['POST'])
def place_order():
    """Place a new order"""
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'success': False, 'message': 'Please login to place orders'})
    
    order_items = request.json.get('items', [])
    if not order_items:
        return jsonify({'success': False, 'message': 'No items in order'})
    
    conn = get_db_connection()
    
    # Calculate total amount
    total_amount = 0
    for item in order_items:
        menu_item = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
        if menu_item:
            total_amount += menu_item['price'] * item['quantity']
    
    # Create order
    cursor = conn.execute(
        'INSERT INTO orders (student_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)',
        (session['user_id'], date.today().strftime('%Y-%m-%d'), total_amount, 'pending')
    )
    order_id = cursor.lastrowid
    
    # Add order items
    for item in order_items:
        menu_item = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
        if menu_item:
            conn.execute(
                'INSERT INTO order_items (order_id, menu_item_id, quantity, price) VALUES (?, ?, ?, ?)',
                (order_id, item['id'], item['quantity'], menu_item['price'])
            )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Order #{order_id} placed successfully!', 'order_id': order_id})

@app.route('/orders')
def student_orders():
    """Student order history"""
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    orders = conn.execute('''
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.student_id = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('student_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
def order_details():
    """View order details"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get order details
    order = conn.execute('''
        SELECT o.*, s.full_name, s.student_id 
        FROM orders o
        JOIN students s ON o.student_id = s.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    
    if not order:
        flash('Order not found!')
        return redirect(url_for('index'))
    
    # Check if user can view this order
    if session['user_type'] == 'student' and order['student_id'] != session['user_id']:
        flash('Access denied!')
        return redirect(url_for('student_orders'))
    
    # Get order items
    order_items = conn.execute('''
        SELECT oi.*, m.item_name, m.description
        FROM order_items oi
        JOIN menu_items m ON oi.menu_item_id = m.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    return render_template('order_details.html', order=order, order_items=order_items)

@app.route('/admin/orders')
def admin_orders():
    """Admin view all orders"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    orders = conn.execute('''
        SELECT o.*, s.full_name, s.student_id, COUNT(oi.id) as item_count
        FROM orders o
        JOIN students s ON o.student_id = s.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/update_order_status', methods=['POST'])
def update_order_status():
    """Update order status"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    
    valid_statuses = ['pending', 'preparing', 'ready', 'served', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Order status updated successfully!'})

@app.route('/billing')
def student_billing():
    """Student billing and payment history"""
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get monthly bills
    monthly_bills = conn.execute('''
        SELECT 
            strftime('%Y-%m', o.order_date) as month,
            SUM(o.total_amount) as total_amount,
            COUNT(o.id) as order_count
        FROM orders o
        WHERE o.student_id = ? AND o.status != 'cancelled'
        GROUP BY strftime('%Y-%m', o.order_date)
        ORDER BY month DESC
    ''', (session['user_id'],)).fetchall()
    
    # Get recent orders for current month
    current_month = date.today().strftime('%Y-%m')
    recent_orders = conn.execute('''
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.student_id = ? AND strftime('%Y-%m', o.order_date) = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', (session['user_id'], current_month)).fetchall()
    
    conn.close()
    return render_template('student_billing.html', monthly_bills=monthly_bills, 
                         recent_orders=recent_orders, current_month=current_month)

@app.route('/admin/billing')
def admin_billing():
    """Admin billing overview"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get billing summary by student
    student_bills = conn.execute('''
        SELECT 
            s.full_name, 
            s.student_id,
            SUM(o.total_amount) as total_amount,
            COUNT(o.id) as order_count
        FROM students s
        LEFT JOIN orders o ON s.id = o.student_id AND o.status != 'cancelled'
        GROUP BY s.id
        HAVING SUM(o.total_amount) > 0
        ORDER BY total_amount DESC
    ''').fetchall()
    
    # Get monthly revenue
    monthly_revenue = conn.execute('''
        SELECT 
            strftime('%Y-%m', o.order_date) as month,
            SUM(o.total_amount) as revenue,
            COUNT(o.id) as order_count
        FROM orders o
        WHERE o.status != 'cancelled'
        GROUP BY strftime('%Y-%m', o.order_date)
        ORDER BY month DESC
        LIMIT 12
    ''').fetchall()
    
    conn.close()
    return render_template('admin_billing.html', student_bills=student_bills, 
                         monthly_revenue=monthly_revenue)
        JOIN ratings r ON m.id = r.menu_item_id
        GROUP BY m.id
        HAVING COUNT(r.rating) >= 3
        ORDER BY avg_rating DESC
        LIMIT 10
    ''').fetchall()
    
    # Get rating distribution
    rating_distribution = conn.execute('''
        SELECT rating, COUNT(*) as count
        FROM ratings
        GROUP BY rating
        ORDER BY rating
    ''').fetchall()
    
    conn.close()
    return render_template('analytics.html', top_items=top_items, 
                         rating_distribution=rating_distribution)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
