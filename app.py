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
        print("❌ Error connecting:", e)
        return None


# -------------------------
# HTML UI
# -------------------------
HTML_INTERFACE = """  
( SAME HTML YOU PROVIDED — unchanged )  
"""

# -------------------------
# Flask Routes
# -------------------------
@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)


@app.route("/api/inventory/add", methods=["POST"])
def add_inventory():
    try:
        data = request.json

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO product_inventory(
                shop_name, shop_owner, shop_address,
                product_name, product_brand, product_mrp, product_size,
                quantity, selling_price, manufacture_date, expiry_date,
                stock_status, is_available
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data["shop_name"], data.get("shop_owner"), data.get("shop_address"),
            data["product_name"], data.get("product_brand"), data.get("product_mrp"),
            data.get("product_size"), data["quantity"], data.get("selling_price"),
            data.get("manufacture_date"), data.get("expiry_date"),
            data.get("stock_status", "IN_STOCK"), data.get("is_available", True)
        ))

        conn.commit()
        rid = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({"message": "Product added!", "record_id": rid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/inventory/all", methods=["GET"])
def get_all():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "DB connection failed"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_inventory ORDER BY last_updated DESC")
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/inventory/delete/<int:rid>", methods=["DELETE"])
def delete_inventory(rid):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "DB connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute("DELETE FROM product_inventory WHERE record_id=%s", (rid,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Record deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/inventory/search", methods=["GET"])
def search_inventory():
    try:
        product = request.args.get("product", "")
        shop = request.args.get("shop", "")
        brand = request.args.get("brand", "")

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "DB connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM product_inventory WHERE 1=1"
        params = []

        if product:
            query += " AND product_name LIKE %s"
            params.append(f"%{product}%")

        if shop:
            query += " AND shop_name LIKE %s"
            params.append(f"%{shop}%")

        if brand:
            query += " AND product_brand LIKE %s"
            params.append(f"%{brand}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"count": len(results), "results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
