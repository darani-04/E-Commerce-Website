import sqlite3
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_ecom_key_123'  # Needed for session management
DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/deals')
def deals():
    return render_template('deals.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cart-page')
def cart_page():
    return render_template('cart.html')

@app.route('/my-orders')
def my_orders():
    return render_template('orders.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

# ================= API ENDPOINTS =================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()
        
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'username': user['username']}), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user_id' in session:
        return jsonify({'loggedIn': True, 'username': session['username']})
    return jsonify({'loggedIn': False})

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    is_deal = request.args.get('is_deal')
    search_query = request.args.get('search')
    conn = get_db_connection()
    query = 'SELECT * FROM products WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    if is_deal:
        query += ' AND is_deal = 1'
    if search_query:
        query += ' AND name LIKE ?'
        params.append(f'%{search_query}%')
        
    products = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(ix) for ix in products])

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    user_id = session['user_id']
    conn = get_db_connection()
    
    query = '''
        SELECT c.id as cart_id, p.id as product_id, p.name, p.price, p.image_url, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    '''
    cart_items = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(ix) for ix in cart_items])

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    user_id = session['user_id']
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if item already in cart
    item = cur.execute('SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id)).fetchone()
                      
    if item:
        cur.execute('UPDATE cart SET quantity = ? WHERE id = ?', (item['quantity'] + 1, item['id']))
    else:
        cur.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)', 
                   (user_id, product_id))
                   
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product added to cart'}), 200

@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart_item():
    user_id = session['user_id']
    data = request.json
    cart_id = data.get('cart_id')
    action = data.get('action') # 'increase' or 'decrease' or 'remove'
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    item = cur.execute('SELECT * FROM cart WHERE id = ? AND user_id = ?', (cart_id, user_id)).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'error': 'Item not found'}), 404
        
    if action == 'increase':
        cur.execute('UPDATE cart SET quantity = quantity + 1 WHERE id = ?', (cart_id,))
    elif action == 'decrease':
        if item['quantity'] > 1:
            cur.execute('UPDATE cart SET quantity = quantity - 1 WHERE id = ?', (cart_id,))
        else:
            cur.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
    elif action == 'remove':
        cur.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        
    conn.commit()
    conn.close()
    return jsonify({'message': 'Cart updated'}), 200

@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get cart items with prices
    query = '''
        SELECT c.id as cart_id, p.id as product_id, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    '''
    items = cur.execute(query, (user_id,)).fetchall()
    if not items:
        conn.close()
        return jsonify({'error': 'Cart is empty'}), 400
        
    total_amount = sum(item['price'] * item['quantity'] for item in items)
    
    # Create order
    cur.execute('INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)', (user_id, total_amount, 'Confirmed'))
    order_id = cur.lastrowid
    
    # Create order items
    for item in items:
        cur.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)', (order_id, item['product_id'], item['quantity'], item['price']))
    
    # Clear cart to simulate successful checkout
    cur.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Checkout successful. Thank you for your purchase!'}), 200

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    
    orders = cur.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user_id,)).fetchall()
    result = []
    
    for order in orders:
        order_dict = dict(order)
        items = cur.execute('''
            SELECT oi.quantity, oi.price, p.name 
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order['id'],)).fetchall()
        order_dict['items'] = [dict(ix) for ix in items]
        result.append(order_dict)
        
    conn.close()
    return jsonify(result), 200

@app.route('/api/wishlist', methods=['GET'])
@login_required
def get_wishlist():
    user_id = session['user_id']
    conn = get_db_connection()
    query = '''
        SELECT w.id as wishlist_id, p.id as product_id, p.name, p.price, p.image_url, p.category, p.description
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        WHERE w.user_id = ?
    '''
    items = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in items]), 200

@app.route('/api/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    user_id = session['user_id']
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
        conn.commit()
        return jsonify({'message': 'Added to wishlist'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Already in wishlist'}), 200
    finally:
        conn.close()

@app.route('/api/wishlist/remove', methods=['POST'])
@login_required
def remove_from_wishlist():
    user_id = session['user_id']
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM wishlist WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Removed from wishlist'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
