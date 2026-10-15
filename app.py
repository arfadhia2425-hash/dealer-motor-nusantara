import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ganti-secret-key-ini")
DB_PATH = os.environ.get("DB_PATH", "orders.db")

PRODUCTS = [
    {"name": "Honda Beat CBS", "price": 18500000, "description": "Motor matic praktis untuk mobilitas harian."},
    {"name": "Honda Scoopy", "price": 22000000, "description": "Motor matic bergaya retro modern."},
    {"name": "Honda Vario 160", "price": 28000000, "description": "Motor matic dengan desain sporty."},
    {"name": "Yamaha NMAX", "price": 32500000, "description": "Motor matic touring yang nyaman."},
    {"name": "Yamaha Aerox", "price": 29000000, "description": "Motor matic sporty untuk penggunaan harian."},
    {"name": "Suzuki Satria F150", "price": 29000000, "description": "Motor underbone dengan karakter sporty."},
]

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)

@app.route("/order", methods=["POST"])
def order():
    customer_name = request.form.get("customer_name", "").strip()
    product_name = request.form.get("product_name", "").strip()
    try:
        quantity = int(request.form.get("quantity", "1"))
    except ValueError:
        quantity = 0
    allowed = {p["name"] for p in PRODUCTS}
    if not customer_name or product_name not in allowed or not (1 <= quantity <= 99):
        flash("Data pesanan tidak valid. Periksa nama, produk, dan jumlah.", "error")
        return redirect(url_for("index"))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO orders (customer_name, product_name, quantity, created_at) VALUES (?, ?, ?, ?)",
            (customer_name, product_name, quantity, datetime.now().isoformat(timespec="seconds"))
        )
    flash("Permintaan informasi motor berhasil disimpan untuk demo praktikum.", "success")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    # Endpoint wajib: mengembalikan teks OK. Koneksi DB juga diuji untuk nilai tambah.
    try:
        with sqlite3.connect(DB_PATH, timeout=2) as conn:
            conn.execute("SELECT 1")
        return "OK", 200, {"Content-Type": "text/plain; charset=utf-8"}
    except sqlite3.Error:
        return "DB ERROR", 503, {"Content-Type": "text/plain; charset=utf-8"}

@app.route("/admin/orders")
def admin_orders():
    # Demo lokal saja. Jangan buka endpoint ini ke publik tanpa autentikasi.
    token = os.environ.get("ADMIN_TOKEN")
    if not token or request.args.get("token") != token:
        return "Forbidden", 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        orders = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([dict(row) for row in orders])

init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
