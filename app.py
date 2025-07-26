from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import calendar
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('database/mess_menu.db')
    conn.row_factory = sqlite3.Row
    return conn

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get menu items with average ratings
    menu_items = conn.execute('''
        SELECT m.*, 
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.id) as rating_count
        FROM menu_items m
        LEFT JOIN ratings r ON m.id = r.menu_item_id
        WHERE m.is_available = 1
        GROUP BY m.id
        ORDER BY m.category, m.name
    ''').fetchall()
    
    conn.close()
    return render_template('index.html', menu_items=menu_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        
        if user_type == 'admin':
            user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        else:
            user = conn.execute('SELECT * FROM students WHERE username = ?', (username,)).fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user_type
            session['full_name'] = user['full_name']
            flash(f'Welcome, {user["full_name"]}!', 'success')
            
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        room_number = request.form['room_number']
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT * FROM students WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists!', 'error')
        else:
            password_hash = generate_password_hash(password)
            conn.execute('''
                INSERT INTO students (username, email, password_hash, full_name, phone, room_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, phone, room_number))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            conn.close()
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('register.html')

@app.route('/student_dashboard')
@require_login
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get recent orders
    recent_orders = conn.execute('''
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.student_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    # Get monthly bill
    current_month = datetime.now().strftime('%Y-%m')
    monthly_total = conn.execute('''
        SELECT COALESCE(SUM(total_amount), 0) as total
        FROM orders
        WHERE student_id = ? AND strftime('%Y-%m', order_date) = ?
    ''', (session['user_id'], current_month)).fetchone()['total']
    
    conn.close()
    return render_template('student_dashboard.html', 
                         recent_orders=recent_orders, 
                         monthly_total=monthly_total)

@app.route('/admin_dashboard')
@require_admin
def admin_dashboard():
    conn = get_db_connection()
    
    # Get statistics
    stats = {}
    stats['total_students'] = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    stats['total_orders'] = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    stats['pending_orders'] = conn.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'").fetchone()['count']
    stats['total_revenue'] = conn.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM orders').fetchone()['total']
    
    # Get recent orders
    recent_orders = conn.execute('''
        SELECT o.*, s.full_name, s.room_number, COUNT(oi.id) as item_count
        FROM orders o
        JOIN students s ON o.student_id = s.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id
        ORDER BY o.order_date DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    return render_template('admin_dashboard.html', stats=stats, recent_orders=recent_orders)

@app.route('/place_order', methods=['POST'])
@require_login
def place_order():
    if session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Student login required'})
    
    data = request.get_json()
    items = data.get('items', [])
    special_instructions = data.get('special_instructions', '')
    
    if not items:
        return jsonify({'success': False, 'message': 'No items selected'})
    
    conn = get_db_connection()
    
    try:
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in items:
            menu_item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
            if menu_item:
                item_total = menu_item['price'] * item['quantity']
                total_amount += item_total
                order_items.append({
                    'menu_item_id': item['id'],
                    'quantity': item['quantity'],
                    'price': menu_item['price']
                })
        
        # Create order
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (student_id, total_amount, special_instructions)
            VALUES (?, ?, ?)
        ''', (session['user_id'], total_amount, special_instructions))
        
        order_id = cursor.lastrowid
        
        # Add order items
        for item in order_items:
            cursor.execute('''
                INSERT INTO order_items (order_id, menu_item_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['menu_item_id'], item['quantity'], item['price']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Order placed successfully!', 'order_id': order_id})
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/my_orders')
@require_login
def my_orders():
    if session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    orders = conn.execute('''
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.student_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('my_orders.html', orders=orders)

@app.route('/order_details/<int:order_id>')
@require_login
def order_details(order_id):
    conn = get_db_connection()
    
    # Check if user can access this order
    if session.get('user_type') == 'student':
        order = conn.execute('''
            SELECT o.*, s.full_name, s.room_number, s.phone
            FROM orders o
            JOIN students s ON o.student_id = s.id
            WHERE o.id = ? AND o.student_id = ?
        ''', (order_id, session['user_id'])).fetchone()
    else:  # admin
        order = conn.execute('''
            SELECT o.*, s.full_name, s.room_number, s.phone
            FROM orders o
            JOIN students s ON o.student_id = s.id
            WHERE o.id = ?
        ''', (order_id,)).fetchone()
    
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('my_orders') if session.get('user_type') == 'student' else url_for('manage_orders'))
    
    # Get order items
    order_items = conn.execute('''
        SELECT oi.*, m.name, m.description
        FROM order_items oi
        JOIN menu_items m ON oi.menu_item_id = m.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    conn.close()
    return render_template('order_details.html', order=order, order_items=order_items)

@app.route('/manage_orders')
@require_admin
def manage_orders():
    conn = get_db_connection()
    
    status_filter = request.args.get('status', 'all')
    
    query = '''
        SELECT o.*, s.full_name, s.room_number, COUNT(oi.id) as item_count
        FROM orders o
        JOIN students s ON o.student_id = s.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
    '''
    
    if status_filter != 'all':
        query += f" WHERE o.status = '{status_filter}'"
    
    query += ' GROUP BY o.id ORDER BY o.order_date DESC'
    
    orders = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('manage_orders.html', orders=orders, status_filter=status_filter)

@app.route('/update_order_status', methods=['POST'])
@require_admin
def update_order_status():
    order_id = request.form['order_id']
    new_status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('manage_orders'))

@app.route('/monthly_bills')
@require_login
def monthly_bills():
    if session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get monthly bills for the past 6 months
    bills = conn.execute('''
        SELECT 
            strftime('%Y-%m', order_date) as month,
            strftime('%Y', order_date) as year,
            strftime('%m', order_date) as month_num,
            SUM(total_amount) as total_amount,
            COUNT(*) as order_count
        FROM orders
        WHERE student_id = ? AND order_date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month DESC
    ''', (session['user_id'],)).fetchall()
    
    # Add month names
    bills_with_names = []
    for bill in bills:
        month_name = calendar.month_name[int(bill['month_num'])]
        bills_with_names.append({
            'month': bill['month'],
            'year': bill['year'],
            'month_name': month_name,
            'total_amount': bill['total_amount'],
            'order_count': bill['order_count']
        })
    
    conn.close()
    return render_template('monthly_bills.html', bills=bills_with_names)

@app.route('/submit_rating', methods=['POST'])
@require_login
def submit_rating():
    if session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Student login required'})
    
    data = request.get_json()
    menu_item_id = data.get('menu_item_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    conn = get_db_connection()
    
    try:
        # Check if user already rated this item
        existing_rating = conn.execute(
            'SELECT * FROM ratings WHERE student_id = ? AND menu_item_id = ?',
            (session['user_id'], menu_item_id)
        ).fetchone()
        
        if existing_rating:
            # Update existing rating
            conn.execute('''
                UPDATE ratings 
                SET rating = ?, comment = ?, created_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND menu_item_id = ?
            ''', (rating, comment, session['user_id'], menu_item_id))
        else:
            # Insert new rating
            conn.execute('''
                INSERT INTO ratings (student_id, menu_item_id, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], menu_item_id, rating, comment))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Rating submitted successfully!'})
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/analytics')
@require_admin
def analytics():
    conn = get_db_connection()
    
    # Get rating analytics
    rating_stats = conn.execute('''
        SELECT 
            m.name,
            AVG(r.rating) as avg_rating,
            COUNT(r.id) as rating_count
        FROM menu_items m
        LEFT JOIN ratings r ON m.id = r.menu_item_id
        GROUP BY m.id
        ORDER BY avg_rating DESC
    ''').fetchall()
    
    # Get order analytics
    daily_orders = conn.execute('''
        SELECT 
            DATE(order_date) as order_day,
            COUNT(*) as order_count,
            SUM(total_amount) as daily_revenue
        FROM orders
        WHERE order_date >= date('now', '-30 days')
        GROUP BY DATE(order_date)
        ORDER BY order_day
    ''').fetchall()
    
    conn.close()
    return render_template('analytics.html', rating_stats=rating_stats, daily_orders=daily_orders)

@app.route('/manage_menu')
@require_admin
def manage_menu():
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM menu_items ORDER BY category, name').fetchall()
    conn.close()
    return render_template('manage_menu.html', menu_items=menu_items)

@app.route('/add_menu_item', methods=['POST'])
@require_admin
def add_menu_item():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    category = request.form['category']
    meal_type = request.form['meal_type']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO menu_items (name, description, price, category, meal_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, price, category, meal_type))
    conn.commit()
    conn.close()
    
    flash('Menu item added successfully!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/toggle_menu_item/<int:item_id>')
@require_admin
def toggle_menu_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
    
    if item:
        new_status = 0 if item['is_available'] else 1
        conn.execute('UPDATE menu_items SET is_available = ? WHERE id = ?', (new_status, item_id))
        conn.commit()
        flash('Menu item status updated!', 'success')
    
    conn.close()
    return redirect(url_for('manage_menu'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
