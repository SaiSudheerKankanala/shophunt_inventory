# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

app = Flask(__name__)

# -------------------------
# MySQL configuration
# -------------------------
db_config = {
    'host': 'ballast.proxy.rlwy.net',
    'user': 'root',
    'password': 'SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi',
    'database': 'shop_hunt'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

# -------------------------
# HTML frontend
# -------------------------
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shop Hunt - Distributor Portal</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);}
        h1 { text-align:center; color:#333; margin-bottom:30px; }
        .form-section { margin-bottom:30px; padding:20px; border:1px solid #ddd; border-radius:8px; background:#f9f9f9; }
        .form-group { margin-bottom:15px; }
        label { font-weight:bold; display:block; margin-bottom:5px; color:#555; }
        input, select, textarea { margin:5px; padding:10px; width:300px; border:1px solid #ddd; border-radius:4px; font-size:14px; }
        button { padding:12px 25px; background:#007bff; color:white; border:none; border-radius:4px; cursor:pointer; font-size:16px; margin:5px; }
        button:hover { background:#0056b3; }
        .btn-danger { background:#dc3545; } .btn-danger:hover { background:#c82333; }
        .btn-success { background:#28a745; } .btn-success:hover { background:#218838; }
        .response { margin-top:15px; padding:15px; border-radius:4px; font-weight:bold; }
        .success { background:#d4edda; color:#155724; border:1px solid #c3e6cb; }
        .error { background:#f8d7da; color:#721c24; border:1px solid #f5c6cb; }
        table { width:100%; border-collapse:collapse; margin-top:15px; }
        th, td { border:1px solid #ddd; padding:12px; text-align:left; }
        th { background:#007bff; color:white; }
        tr:nth-child(even) { background:#f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ Shop Hunt - Distributor Portal</h1>

        <!-- Add Inventory Form -->
        <div class="form-section">
            <h2>➕ Add Product Inventory</h2>
            <div class="form-group">
                <label>Shop Information:</label>
                <input type="text" id="shopName" placeholder="Shop Name" value="Super Mart">
                <input type="text" id="shopOwner" placeholder="Shop Owner" value="Raj Kumar">
            </div>
            <div class="form-group">
                <textarea id="shopAddress" placeholder="Shop Address" style="width:615px;height:60px;">123 MG Road, Chennai</textarea>
            </div>
            <div class="form-group">
                <label>Product Information:</label>
                <input type="text" id="productName" placeholder="Product Name" value="Dove Shampoo">
                <input type="text" id="productBrand" placeholder="Product Brand" value="Dove">
            </div>
            <div class="form-group">
                <input type="number" id="productMrp" placeholder="Product MRP" value="180.00" step="0.01">
                <input type="text" id="productSize" placeholder="Product Size" value="200ml">
            </div>
            <div class="form-group">
                <label>Inventory Details:</label>
                <input type="number" id="quantity" placeholder="Quantity" value="50">
                <input type="number" id="sellingPrice" placeholder="Selling Price" value="175.00" step="0.01">
            </div>
            <div class="form-group">
                <input type="date" id="manufactureDate" placeholder="Manufacture Date">
                <input type="date" id="expiryDate" placeholder="Expiry Date">
            </div>
            <div class="form-group">
                <label>Stock Status:</label>
                <select id="stockStatus">
                    <option value="IN_STOCK">In Stock</option>
                    <option value="LOW_STOCK">Low Stock</option>
                    <option value="OUT_OF_STOCK">Out of Stock</option>
                </select>
                <select id="isAvailable">
                    <option value="true">Available</option>
                    <option value="false">Not Available</option>
                </select>
            </div>
            <button class="btn-success" onclick="addInventory()">📥 Add to Inventory</button>
            <div id="addResponse" class="response"></div>
        </div>

        <!-- Search Section -->
        <div class="form-section">
            <h2>🔍 Search Inventory</h2>
            <input type="text" id="searchProduct" placeholder="Product Name">
            <input type="text" id="searchShop" placeholder="Shop Name">
            <input type="text" id="searchBrand" placeholder="Brand">
            <button onclick="searchInventory()">Search</button>
            <button onclick="getAllInventory()">Show All</button>
        </div>

        <!-- Data Display Section -->
        <div class="form-section">
            <h2>📊 Current Inventory</h2>
            <div id="inventoryData"></div>
        </div>
    </div>

<script>
const API_BASE = window.location.origin;

// Add inventory
async function addInventory() {
    const data = {
        shop_name: document.getElementById('shopName').value,
        shop_owner: document.getElementById('shopOwner').value,
        shop_address: document.getElementById('shopAddress').value,
        product_name: document.getElementById('productName').value,
        product_brand: document.getElementById('productBrand').value,
        product_mrp: parseFloat(document.getElementById('productMrp').value),
        product_size: document.getElementById('productSize').value,
        quantity: parseInt(document.getElementById('quantity').value),
        selling_price: parseFloat(document.getElementById('sellingPrice').value),
        manufacture_date: document.getElementById('manufactureDate').value,
        expiry_date: document.getElementById('expiryDate').value,
        stock_status: document.getElementById('stockStatus').value,
        is_available: document.getElementById('isAvailable').value === 'true'
    };
    await postData('/api/inventory/add', data, 'addResponse');
    getAllInventory();
}

// Get all inventory
async function getAllInventory() {
    try {
        const response = await fetch(API_BASE + '/api/inventory/all');
        const result = await response.json();
        if(result.data && result.data.length>0){ displayInventory(result.data); }
        else { document.getElementById('inventoryData').innerHTML='<p>No inventory found.</p>'; }
    } catch(e) {
        document.getElementById('inventoryData').innerHTML='<div class="error">Error loading data: '+e+'</div>';
    }
}

// Search inventory
async function searchInventory() {
    const params = new URLSearchParams();
    const product = document.getElementById('searchProduct').value;
    const shop = document.getElementById('searchShop').value;
    const brand = document.getElementById('searchBrand').value;
    if(product) params.append('product', product);
    if(shop) params.append('shop', shop);
    if(brand) params.append('brand', brand);
    try {
        const response = await fetch(API_BASE+'/api/inventory/search?'+params);
        const result = await response.json();
        if(result.results && result.results.length>0){ displayInventory(result.results); }
        else { document.getElementById('inventoryData').innerHTML='<p>No results found.</p>'; }
    } catch(e){
        document.getElementById('inventoryData').innerHTML='<div class="error">Search error: '+e+'</div>';
    }
}

// Display inventory
function displayInventory(data){
    let html='<table><thead><tr><th>ID</th><th>Shop</th><th>Product</th><th>Brand</th><th>Size</th><th>Qty</th><th>Price</th><th>MRP</th><th>Status</th><th>Expiry</th><th>Action</th></tr></thead><tbody>';
    data.forEach(item=>{
        html+=`<tr>
            <td>${item.record_id}</td>
            <td>${item.shop_name}</td>
            <td>${item.product_name}</td>
            <td>${item.product_brand||'N/A'}</td>
            <td>${item.product_size||'N/A'}</td>
            <td>${item.quantity}</td>
            <td>₹${item.selling_price||0}</td>
            <td>₹${item.product_mrp||0}</td>
            <td>${item.stock_status}</td>
            <td>${item.expiry_date||'N/A'}</td>
            <td><button class="btn-danger" onclick="deleteInventory(${item.record_id})">Delete</button></td>
        </tr>`;
    });
    html+='</tbody></table>';
    document.getElementById('inventoryData').innerHTML=html;
}

// Delete inventory
async function deleteInventory(id){
    if(!confirm('Are you sure to delete?')) return;
    try {
        const response = await fetch(API_BASE+'/api/inventory/delete/'+id,{method:'DELETE'});
        const result = await response.json();
        if(response.ok){ alert('Deleted successfully'); getAllInventory(); }
        else { alert('Error: '+result.error); }
    } catch(e){ alert('Error deleting record: '+e); }
}

// POST utility
async function postData(endpoint, data, responseId){
    try {
        const response = await fetch(API_BASE+endpoint,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify(data)
        });
        const result = await response.json();
        const el = document.getElementById(responseId);
        el.innerHTML = response.ok?'✅ '+result.message:'❌ Error: '+result.error;
        el.className = response.ok?'response success':'response error';
    } catch(e){
        const el = document.getElementById(responseId);
        el.innerHTML = '❌ Network Error: '+e; el.className='response error';
    }
}

// Set default dates
window.onload=function(){
    getAllInventory();
    const today=new Date().toISOString().split('T')[0];
    const nextYear=new Date(); nextYear.setFullYear(nextYear.getFullYear()+1);
    const nextYearStr=nextYear.toISOString().split('T')[0];
    document.getElementById('manufactureDate').value=today;
    document.getElementById('expiryDate').value=nextYearStr;
}
</script>
</body>
</html>
"""

# -------------------------
# Flask Routes
# -------------------------
@app.route('/')
def distributor_interface():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/inventory/add', methods=['POST'])
def add_inventory():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error':'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO product_inventory(
                shop_name, shop_owner, shop_address,
                product_name, product_brand, product_mrp, product_size,
                quantity, selling_price, manufacture_date, expiry_date,
                stock_status, is_available
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data['shop_name'], data.get('shop_owner'), data.get('shop_address'),
            data['product_name'], data.get('product_brand'), data.get('product_mrp'),
            data.get('product_size'), data['quantity'], data.get('selling_price'),
            data.get('manufacture_date'), data.get('expiry_date'),
            data.get('stock_status','IN_STOCK'), data.get('is_available',True)
        ))
        record_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message':'Product inventory added successfully!','record_id':record_id}),201
    except Exception as e:
        return jsonify({'error':str(e)}),400

@app.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error':'DB connection failed'}),500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_inventory ORDER BY last_updated DESC")
        data = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify({'count':len(data),'data':data}),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@app.route('/api/inventory/delete/<int:record_id>', methods=['DELETE'])
def delete_inventory(record_id):
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error':'DB connection failed'}),500
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product_inventory WHERE record_id=%s",(record_id,))
        record = cursor.fetchone()
        if not record: cursor.close(); conn.close(); return jsonify({'error':'Record not found'}),404
        cursor.execute("DELETE FROM product_inventory WHERE record_id=%s",(record_id,))
        conn.commit(); cursor.close(); conn.close()
        return jsonify({'message':'Inventory record deleted'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@app.route('/api/inventory/search', methods=['GET'])
def search_inventory():
    try:
        product_name = request.args.get('product','')
        shop_name = request.args.get('shop','')
        brand = request.args.get('brand','')
        conn = get_db_connection()
        if conn is None: return jsonify({'error':'DB connection failed'}),500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM product_inventory WHERE 1=1"
        params=[]
        if product_name: query+=" AND product_name LIKE %s"; params.append(f"%{product_name}%")
        if shop_name: query+=" AND shop_name LIKE %s"; params.append(f"%{shop_name}%")
        if brand: query+=" AND product_brand LIKE %s"; params.append(f"%{brand}%")
        query+=" ORDER BY product_name, shop_name"
        cursor.execute(query,params)
        results = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify({'count':len(results),'results':results}),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

# -------------------------
# Run app (Railway)
# -------------------------
if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
