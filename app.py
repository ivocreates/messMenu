"""
Mess Menu Rater - A modern Flask web application
Color Theme: #186F65, #B5CB99, #FCE09B, #B2533E
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime, date, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
from functools import wraps
import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.Config)

# Database helper functions
def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db_connection()
    with open('database/schema_new.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

# Utility functions
def hash_password(password):
    """Hash password using Werkzeug"""
    return generate_password_hash(password)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page"""
    user_stats = {}
    recent_orders = []
    popular_items = []
    
    if 'user_id' in session:
        conn = get_db_connection()
        
        # Get user statistics
        stats = conn.execute('''
            SELECT 
                COUNT(DISTINCT o.id) as total_orders,
                COUNT(DISTINCT r.id) as total_ratings,
                COALESCE(SUM(o.total_price), 0) as total_spent
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN ratings r ON u.id = r.user_id
            WHERE u.id = ?
        ''', (session['user_id'],)).fetchone()
        
        user_stats = dict(stats) if stats else {}
        
        # Get recent orders
        recent_orders = conn.execute('''
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (session['user_id'],)).fetchall()
        
        # Get popular items
        popular_items = conn.execute('''
            SELECT 
                mi.*, 
                AVG(r.rating) as avg_rating,
                COUNT(r.id) as rating_count
            FROM menu_items mi
            LEFT JOIN ratings r ON mi.id = r.menu_item_id
            WHERE mi.is_available = 1
            GROUP BY mi.id
            ORDER BY rating_count DESC, avg_rating DESC
            LIMIT 6
        ''').fetchall()
        
        conn.close()
    
    return render_template('index.html', 
                         user_stats=user_stats,
                         recent_orders=recent_orders,
                         popular_items=popular_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['is_admin'] = user['is_admin']
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([username, email, full_name, password, confirm_password]):
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        try:
            conn.execute(
                '''INSERT INTO users (username, email, full_name, password_hash, is_admin) 
                   VALUES (?, ?, ?, ?, ?)''',
                (username, email, full_name, hash_password(password), False)
            )
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred while creating your account.', 'danger')
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('index'))

@app.route('/menu')
@login_required
def menu():
    """Menu page"""
    conn = get_db_connection()
    
    # Get menu items with ratings
    menu_items = conn.execute('''
        SELECT 
            mi.*,
            AVG(r.rating) as avg_rating,
            COUNT(r.id) as rating_count
        FROM menu_items mi
        LEFT JOIN ratings r ON mi.id = r.menu_item_id
        WHERE mi.is_available = 1
        GROUP BY mi.id
        ORDER BY mi.meal_type, mi.name
    ''').fetchall()
    
    # Get user's ratings for these items
    user_ratings = {}
    if menu_items:
        item_ids = [str(item['id']) for item in menu_items]
        ratings = conn.execute(f'''
            SELECT menu_item_id, rating FROM ratings 
            WHERE user_id = ? AND menu_item_id IN ({','.join(['?'] * len(item_ids))})
        ''', [session['user_id']] + item_ids).fetchall()
        user_ratings = {r['menu_item_id']: r['rating'] for r in ratings}
    
    conn.close()
    
    return render_template('menu.html', 
                         menu_items=menu_items,
                         user_ratings=user_ratings)

@app.route('/my_orders')
@login_required
def my_orders():
    """User orders page"""
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT 
            o.*,
            m.name as item_name,
            m.description as item_description
        FROM orders o
        LEFT JOIN menu_items m ON o.menu_item_id = m.id
        WHERE o.user_id = ? 
        ORDER BY o.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('my_orders.html', orders=orders)

@app.route('/rate_item', methods=['POST'])
@login_required
def rate_item():
    """Rate a menu item"""
    data = request.get_json()
    menu_item_id = data.get('menu_item_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not menu_item_id or not rating:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid rating'}), 400
    
    conn = get_db_connection()
    
    # Check if user already rated this item
    existing_rating = conn.execute(
        'SELECT id FROM ratings WHERE user_id = ? AND menu_item_id = ?',
        (session['user_id'], menu_item_id)
    ).fetchone()
    
    try:
        if existing_rating:
            # Update existing rating
            conn.execute(
                '''UPDATE ratings 
                   SET rating = ?, comment = ?, created_at = CURRENT_TIMESTAMP 
                   WHERE user_id = ? AND menu_item_id = ?''',
                (rating, comment, session['user_id'], menu_item_id)
            )
        else:
            # Create new rating
            conn.execute(
                '''INSERT INTO ratings (user_id, menu_item_id, rating, comment) 
                   VALUES (?, ?, ?, ?)''',
                (session['user_id'], menu_item_id, rating, comment)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Rating saved successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': 'Error saving rating'}), 500

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    """Place an order"""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'success': False, 'message': 'No items selected'}), 400
    
    conn = get_db_connection()
    
    try:
        # Process each item individually (since our schema has one row per item)
        order_ids = []
        total_order_amount = 0
        
        for item in items:
            menu_item = conn.execute(
                'SELECT name, price FROM menu_items WHERE id = ? AND is_available = 1',
                (item['id'],)
            ).fetchone()
            
            if not menu_item:
                return jsonify({'success': False, 'message': f'Item {item["id"]} not available'}), 400
            
            quantity = int(item.get('quantity', 1))
            unit_price = menu_item['price']
            total_price = unit_price * quantity
            total_order_amount += total_price
            
            # Insert individual order item
            cursor = conn.execute(
                '''INSERT INTO orders (user_id, menu_item_id, quantity, unit_price, total_price, status, order_date, meal_type) 
                   VALUES (?, ?, ?, ?, ?, ?, date('now'), ?)''',
                (session['user_id'], item['id'], quantity, unit_price, total_price, 'pending', 'lunch')
            )
            
            order_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        flash(f'Order placed successfully! Items: {len(order_ids)}, Total: ₹{total_order_amount:.2f}', 'success')
        return jsonify({'success': True, 'order_ids': order_ids, 'total': total_order_amount})
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': 'Error placing order'}), 500

# Admin routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    
    # Get statistics
    stats = conn.execute('''
        SELECT 
            (SELECT COUNT(*) FROM users WHERE is_admin = 0) as total_users,
            (SELECT COUNT(*) FROM orders) as total_orders,
            (SELECT COUNT(*) FROM menu_items) as total_menu_items,
            (SELECT COALESCE(SUM(total_price), 0) FROM orders) as total_revenue,
            (SELECT COUNT(*) FROM ratings) as total_ratings
    ''').fetchone()
    
    # Get recent orders
    recent_orders = conn.execute('''
        SELECT o.*, u.username, u.full_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    # Get top rated items
    top_items = conn.execute('''
        SELECT 
            mi.name,
            AVG(r.rating) as avg_rating,
            COUNT(r.id) as rating_count
        FROM menu_items mi
        LEFT JOIN ratings r ON mi.id = r.menu_item_id
        GROUP BY mi.id
        HAVING rating_count > 0
        ORDER BY avg_rating DESC, rating_count DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_orders=recent_orders,
                         top_items=top_items)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin orders management"""
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT 
            o.*, 
            u.username, 
            u.full_name,
            m.name as item_name,
            m.description as item_description
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LEFT JOIN menu_items m ON o.menu_item_id = m.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    """Update order status"""
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    
    if not order_id or not status:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    if status not in ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    conn = get_db_connection()
    
    try:
        # Get current status
        old_status = conn.execute(
            'SELECT status FROM orders WHERE id = ?', (order_id,)
        ).fetchone()
        
        # Update status
        conn.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (status, order_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Order status updated',
            'old_status': old_status['status'] if old_status else 'unknown'
        })
    except Exception as e:
        conn.close()
        print(f"Error updating order status: {e}")
        return jsonify({'success': False, 'message': 'Error updating order status'}), 500

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_single_order_status(order_id):
    """Update individual order status (for JavaScript calls)"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        if status not in ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        conn = get_db_connection()
        
        # Get current status
        current = conn.execute(
            'SELECT status FROM orders WHERE id = ?', (order_id,)
        ).fetchone()
        
        if not current:
            conn.close()
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Update status
        conn.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (status, order_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Order #{order_id} status updated to {status}',
            'old_status': current['status']
        })
        
    except Exception as e:
        print(f"Error updating order {order_id} status: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/analytics')
@admin_required
def analytics():
    """Analytics page"""
    try:
        conn = get_db_connection()
        
        # Get key metrics
        total_items = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
        total_orders = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
        total_ratings = conn.execute('SELECT COUNT(*) as count FROM ratings').fetchone()['count']
        total_revenue = conn.execute('SELECT COALESCE(SUM(total_price), 0) as revenue FROM orders').fetchone()['revenue']
        
        # Get top rated items
        top_items = conn.execute('''
            SELECT 
                mi.id,
                mi.name,
                mi.meal_type,
                COUNT(r.id) as rating_count,
                AVG(r.rating) as avg_rating
            FROM menu_items mi
            LEFT JOIN ratings r ON mi.id = r.menu_item_id
            GROUP BY mi.id
            HAVING rating_count > 0
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT 6
        ''').fetchall()
        
        # Get order status summary
        order_summary = {}
        status_data = conn.execute('''
            SELECT status, COUNT(*) as count
            FROM orders
            GROUP BY status
        ''').fetchall()
        
        for row in status_data:
            order_summary[row['status']] = {'count': row['count']}
        
        # Get recent orders
        recent_orders = conn.execute('''
            SELECT 
                o.id,
                o.status,
                o.total_price,
                o.created_at,
                u.username,
                mi.name as item_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN menu_items mi ON o.menu_item_id = mi.id
            ORDER BY o.created_at DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        return render_template('analytics.html',
                             total_items=total_items,
                             total_orders=total_orders,
                             total_ratings=total_ratings,
                             total_revenue=total_revenue,
                             top_items=top_items,
                             order_summary=order_summary,
                             recent_orders=recent_orders)
        
    except Exception as e:
        print(f"Error in analytics route: {e}")
        flash('Error loading analytics data', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/billing')
@admin_required
def billing():
    """Billing page"""
    try:
        conn = get_db_connection()
        
        # Get this month's metrics
        current_month_orders = conn.execute('''
            SELECT COUNT(*) as count FROM orders 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        ''').fetchone()['count']
        
        current_month_revenue = conn.execute('''
            SELECT COALESCE(SUM(total_price), 0) as revenue FROM orders 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        ''').fetchone()['revenue']
        
        active_customers = conn.execute('''
            SELECT COUNT(DISTINCT user_id) as count FROM orders 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        ''').fetchone()['count']
        
        avg_order_value = conn.execute('''
            SELECT AVG(total_price) as avg_value FROM orders 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        ''').fetchone()['avg_value'] or 0
        
        # Get monthly billing data
        monthly_bills = conn.execute('''
            SELECT 
                u.id as user_id,
                u.username,
                u.email,
                strftime('%Y-%m', o.created_at) as month,
                COUNT(o.id) as order_count,
                COALESCE(SUM(o.total_price), 0) as total_amount,
                'pending' as status
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.is_admin = 0 AND o.id IS NOT NULL
            GROUP BY u.id, strftime('%Y-%m', o.created_at)
            ORDER BY month DESC, total_amount DESC
        ''').fetchall()
        
        conn.close()
        
        return render_template('billing.html', 
                             monthly_bills=monthly_bills,
                             current_month_orders=current_month_orders,
                             current_month_revenue=current_month_revenue,
                             active_customers=active_customers,
                             avg_order_value=avg_order_value,
                             daily_avg=current_month_revenue / 30 if current_month_revenue else 0,
                             weekly_avg=current_month_revenue / 4 if current_month_revenue else 0,
                             monthly_target=50000)
        
    except Exception as e:
        print(f"Error in billing route: {e}")
        flash('Error loading billing data', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/reviews')
def reviews():
    """Reviews page for menu items"""
    try:
        conn = get_db_connection()
        
        # Get all reviews with item details
        reviews = conn.execute('''
            SELECT 
                r.id,
                r.rating,
                r.review_text,
                r.created_at,
                u.username,
                mi.name as item_name,
                mi.meal_type
            FROM ratings r
            JOIN users u ON r.user_id = u.id
            JOIN menu_items mi ON r.menu_item_id = mi.id
            WHERE r.review_text IS NOT NULL AND r.review_text != ''
            ORDER BY r.created_at DESC
        ''').fetchall()
        
        # Get menu items for review form
        menu_items = conn.execute('SELECT id, name, meal_type FROM menu_items ORDER BY name').fetchall()
        
        # Get review statistics
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as average_rating,
                COUNT(DISTINCT menu_item_id) as reviewed_items,
                COUNT(DISTINCT user_id) as active_reviewers
            FROM ratings
            WHERE review_text IS NOT NULL AND review_text != ''
        ''').fetchone()
        
        conn.close()
        return render_template('reviews.html', 
                             reviews=reviews, 
                             menu_items=menu_items,
                             total_reviews=stats['total_reviews'],
                             average_rating=stats['average_rating'],
                             reviewed_items=stats['reviewed_items'],
                             active_reviewers=stats['active_reviewers'])
        
    except Exception as e:
        print(f"Error in reviews route: {e}")
        flash('Error loading reviews', 'error')
        return redirect(url_for('menu'))

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    """Submit a new review"""
    try:
        menu_item_id = request.form.get('menu_item_id')
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review_text')
        
        if not menu_item_id or rating < 1 or rating > 5 or not review_text:
            flash('Please provide all required fields', 'error')
            return redirect(url_for('reviews'))
        
        conn = get_db_connection()
        
        # Check if user already reviewed this item
        existing = conn.execute('''
            SELECT id FROM ratings 
            WHERE user_id = ? AND menu_item_id = ?
        ''', (session['user_id'], menu_item_id)).fetchone()
        
        if existing:
            # Update existing review
            conn.execute('''
                UPDATE ratings 
                SET rating = ?, review_text = ?, created_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND menu_item_id = ?
            ''', (rating, review_text, session['user_id'], menu_item_id))
            flash('Review updated successfully!', 'success')
        else:
            # Insert new review
            conn.execute('''
                INSERT INTO ratings (user_id, menu_item_id, rating, review_text, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session['user_id'], menu_item_id, rating, review_text))
            flash('Review submitted successfully!', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('reviews'))
        
    except Exception as e:
        print(f"Error submitting review: {e}")
        flash('Error submitting review', 'error')
        return redirect(url_for('reviews'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404,
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_code=500,
                         error_message="An internal server error occurred."), 500

# Initialize database on first run
def create_app():
    """Application factory"""
    if not os.path.exists(app.config['DATABASE_PATH']):
        init_db()
        print("Database initialized successfully!")
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Mess Menu Rater...")
    print("Color theme: #186F65, #B5CB99, #FCE09B, #B2533E")
    print("Demo accounts:")
    print("  Student: username=student, password=student123")
    print("  Admin: username=admin, password=admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)
