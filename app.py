from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Railway MySQL configuration
db_config = {
    'host': os.environ.get('MYSQLHOST'),
    'user': os.environ.get('MYSQLUSER'), 
    'password': os.environ.get('MYSQLPASSWORD'),
    'database': os.environ.get('MYSQLDATABASE'),
    'port': os.environ.get('MYSQLPORT', 19240)
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

@app.route('/')
def distributor_interface():
    return render_template('index.html')

# Keep all your API routes exactly as they were
@app.route('/api/inventory/add', methods=['POST'])
def add_inventory():
    try:
        data = request.json
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
            data['shop_name'], data.get('shop_owner'), data.get('shop_address'),
            data['product_name'], data.get('product_brand'), data.get('product_mrp'),
            data.get('product_size'), data['quantity'], data.get('selling_price'),
            data.get('manufacture_date'), data.get('expiry_date'),
            data.get('stock_status', 'IN_STOCK'), data.get('is_available', True)
        ))

        record_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Product inventory added successfully!', 'record_id': record_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Include all your other routes exactly as they were
@app.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    # ... your existing code
    pass

@app.route('/api/inventory/delete/<int:record_id>', methods=['DELETE'])
def delete_inventory(record_id):
    # ... your existing code  
    pass

@app.route('/api/inventory/search', methods=['GET'])
def search_inventory():
    # ... your existing code
    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
