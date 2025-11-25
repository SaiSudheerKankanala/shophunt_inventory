from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os
import logging

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Railway MySQL configuration - with fallbacks
db_config = {
    'host': os.environ.get('MYSQLHOST', 'ballast.proxy.rlwy.net'),
    'user': os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', 'SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi'),
    'database': os.environ.get('MYSQLDATABASE', 'railway'),
    'port': int(os.environ.get('MYSQLPORT', 19240))
}

print("🔧 Database Configuration:")
print(f"Host: {db_config['host']}")
print(f"Database: {db_config['database']}")
print(f"User: {db_config['user']}")

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        print("✅ Database connected successfully!")
        return connection
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

@app.route('/')
def distributor_interface():
    try:
        print("🔄 Loading main page...")
        return render_template('index.html')
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return f"Error loading page: {e}", 500

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({"status": "healthy", "database": "connected"})
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Your existing API routes with added error handling
@app.route('/api/inventory/add', methods=['POST'])
def add_inventory():
    try:
        print("🔄 Add inventory endpoint called")
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO product_inventory (
                shop_name, shop_owner, shop_address,
                product_name, product_brand, product_mrp, product_size,
                quantity, selling_price, manufacture_date, expiry_date,
                stock_status, is_available
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('shop_name'), data.get('shop_owner'), data.get('shop_address'),
            data.get('product_name'), data.get('product_brand'), data.get('product_mrp'),
            data.get('product_size'), data.get('quantity'), data.get('selling_price'),
            data.get('manufacture_date'), data.get('expiry_date'),
            data.get('stock_status', 'IN_STOCK'), data.get('is_available', True)
        ))

        record_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Product inventory added successfully!', 'record_id': record_id}), 201

    except Exception as e:
        print(f"❌ Error in add_inventory: {e}")
        return jsonify({'error': str(e)}), 400

# Keep your other routes but add similar error handling...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

