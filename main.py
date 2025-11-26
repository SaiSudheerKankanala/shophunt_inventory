from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import Error
import os
import time

app = Flask(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQLHOST', 'ballast.proxy.rlwy.net'),
            user=os.environ.get('MYSQLUSER', 'root'),
            password=os.environ.get('MYSQLPASSWORD', 'SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi'),
            database=os.environ.get('MYSQLDATABASE', 'shop_hunt'),
            port=int(os.environ.get('MYSQLPORT', 3306)),
            connect_timeout=30
        )
        
        # Test connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        
        print("✅ Database connection successful")
        return connection
        
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

def initialize_database():
    """Initialize database table if it doesn't exist"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_inventory (
                    record_id INT AUTO_INCREMENT PRIMARY KEY,
                    shop_name VARCHAR(255),
                    shop_owner VARCHAR(255),
                    shop_address TEXT,
                    product_name VARCHAR(255),
                    product_brand VARCHAR(255),
                    product_mrp DECIMAL(10,2),
                    product_size VARCHAR(50),
                    quantity INT,
                    selling_price DECIMAL(10,2),
                    manufacture_date DATE,
                    expiry_date DATE,
                    stock_status VARCHAR(50),
                    is_available BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            print("✅ Database table initialized")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

# Initialize database when app starts
initialize_database()

# ... (keep all your existing HTML_INTERFACE and API routes exactly as they are) ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

