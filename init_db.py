import sqlite3
import os

def init_db():
    db_path = 'database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create Users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create Products table
    c.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            category TEXT,
            is_deal BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create Cart table
    c.execute('''
        CREATE TABLE cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    # Create Wishlist table
    c.execute('''
        CREATE TABLE wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id),
            UNIQUE(user_id, product_id)
        )
    ''')

    # Create Orders table
    c.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create Order Items table
    c.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    # Insert dummy products
    products = [
        ('Wireless Noise Cancelling Headphones', 24999.00, 'High quality over-ear headphones with active noise cancellation.', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=400&auto=format&fit=crop', 'Electronics', 1),
        ('Smart Watch Pro', 15999.00, 'Fitness tracking, heart rate monitor, and notifications on your wrist.', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=400&auto=format&fit=crop', 'Electronics', 0),
        ('4K Ultra HD Action Camera', 11999.00, 'Waterproof action camera with 4K video capabilities and accessories.', 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=400&auto=format&fit=crop', 'Cameras', 1),
        ('Eco-Friendly Water Bottle', 1999.00, 'Insulated stainless steel water bottle keeps drinks cold for 24 hours.', 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?q=80&w=400&auto=format&fit=crop', 'Home', 0),
        ('Professional DSLR Camera', 74999.00, 'Capture stunning photos and videos with this professional-grade DSLR.', 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=400&auto=format&fit=crop', 'Cameras', 0),
        ('Mechanical Gaming Keyboard', 9999.00, 'RGB backlit mechanical keyboard with tactile switches for gaming.', 'https://images.unsplash.com/photo-1595225476474-87563907a212?q=80&w=400&auto=format&fit=crop', 'Accessories', 1),
        ('Minimalist Desk Lamp', 3499.00, 'Sleek metal desk lamp with adjustable brightness and color temperature.', 'https://loremflickr.com/400/400/lamp', 'Home', 0),
        ('Premium Leather Wallet', 4999.00, 'Genuine leather bifold wallet with RFID blocking technology.', 'https://images.unsplash.com/photo-1627123424574-724758594e93?q=80&w=400&auto=format&fit=crop', 'Accessories', 0),
        ('Smartphone Stand', 899.00, 'Adjustable aluminum smartphone stand for desk.', 'https://loremflickr.com/400/400/smartphone', 'Accessories', 1),
        ('Bluetooth Speaker', 3999.00, 'Portable waterproof Bluetooth speaker with 12-hour battery life.', 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?q=80&w=400&auto=format&fit=crop', 'Electronics', 1),
        ('Ceramic Coffee Mug', 1299.00, 'Handcrafted ceramic coffee mug, perfect for your morning brew.', 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?q=80&w=400&auto=format&fit=crop', 'Home', 0),
        ('Vintage Film Camera', 18999.00, 'Classic 35mm film camera for authentic photography.', 'https://loremflickr.com/400/400/camera', 'Cameras', 0),
        ('Fitness Resistance Bands', 1499.00, 'Set of 5 premium latex resistance bands for home workouts.', 'https://loremflickr.com/400/400/fitness', 'Accessories', 1),
        ('Smart Home Hub', 9999.00, 'Central control system for all your smart home devices.', 'https://images.unsplash.com/photo-1558089687-f282ffcbc126?q=80&w=400&auto=format&fit=crop', 'Electronics', 0),
        ('Ergonomic Office Chair', 12999.00, 'Comfortable mesh office chair with lumbar support.', 'https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?q=80&w=400&auto=format&fit=crop', 'Home', 1),
        ('Mirrorless Camera Lens', 45000.00, 'High-quality 50mm prime lens for mirrorless cameras.', 'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?q=80&w=400&auto=format&fit=crop', 'Cameras', 0),
        ('Gaming Mouse', 4999.00, 'High precision gaming mouse with customizable RGB lighting.', 'https://loremflickr.com/400/400/mouse', 'Accessories', 1),
        ('Laptop Backpack', 3599.00, 'Water-resistant laptop backpack with USB charging port.', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=400&auto=format&fit=crop', 'Accessories', 0),
        ('Yoga Mat', 1999.00, 'Non-slip yoga mat with alignment lines for proper posture.', 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?q=80&w=400&auto=format&fit=crop', 'Sports', 1),
        ('Dumbbell Set', 8999.00, 'Adjustable dumbbell set for home strength training.', 'https://loremflickr.com/400/400/dumbbell', 'Sports', 0),
        ('Running Shoes', 6500.00, 'Lightweight and breathable running shoes for all-day comfort.', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400&auto=format&fit=crop', 'Fashion', 1),
        ('Denim Jacket', 3999.00, 'Classic fit denim jacket for a stylish casual look.', 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?q=80&w=400&auto=format&fit=crop', 'Fashion', 0),
        ('Sunglasses', 1299.00, 'Polarized sunglasses to protect your eyes with style.', 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=400&auto=format&fit=crop', 'Fashion', 1),
        ('Cookware Set', 15999.00, 'Non-stick 10-piece cookware set for versatile cooking.', 'https://images.unsplash.com/photo-1584286595398-a59f21d313f5?q=80&w=400&auto=format&fit=crop', 'Home', 1),
        ('Summer Floral Dress', 1999.00, 'Light and breezy floral print dress perfect for summer.', 'https://loremflickr.com/400/400/dress', 'Fashion', 1),
        ('Elegant Evening Gown', 5999.00, 'Stunning evening gown for formal occasions.', 'https://loremflickr.com/400/400/gown', 'Fashion', 0),
        ('Casual Cotton Dress', 1499.00, 'Comfortable everyday cotton dress in solid colors.', 'https://loremflickr.com/400/400/clothing', 'Fashion', 1),
        ('Embroidered Maxi Dress', 3499.00, 'Beautiful floor-length maxi dress with fine embroidery.', 'https://loremflickr.com/400/400/fashion', 'Fashion', 0),
        ('Party Wear Mini Dress', 2499.00, 'Stylish mini dress with sequin details for parties.', 'https://loremflickr.com/400/400/party', 'Fashion', 1),
        ('Robot Vacuum Cleaner', 21999.00, 'Smart robot vacuum cleaner with mopping functionality.', 'https://loremflickr.com/400/400/vacuum', 'Smart Home', 0),
        ('Air Purifier', 12500.00, 'HEPA air purifier for clean and fresh indoor air.', 'https://loremflickr.com/400/400/purifier', 'Home', 1)
    ]
    
    c.executemany('INSERT INTO products (name, price, description, image_url, category, is_deal) VALUES (?, ?, ?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with sample products.")

if __name__ == '__main__':
    init_db()
