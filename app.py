
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "kunci-demo-lokal-ganti-saat-deploy"
)

PRODUCTS = [
    {"name": "Honda Beat CBS", "price": 18500000, "description": "Motor matic praktis untuk mobilitas harian."},
    {"name": "Honda Scoopy", "price": 22000000, "description": "Motor matic bergaya retro modern."},
    {"name": "Honda Vario 160", "price": 28000000, "description": "Motor matic dengan desain sporty."},
    {"name": "Yamaha NMAX", "price": 32500000, "description": "Motor matic touring yang nyaman."},
    {"name": "Yamaha Aerox", "price": 29000000, "description": "Motor matic sporty untuk penggunaan harian."},
    {"name": "Suzuki Satria F150", "price": 29000000, "description": "Motor underbone dengan karakter sporty."},
]


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

    allowed = {product["name"] for product in PRODUCTS}

    if (
        not customer_name
        or product_name not in allowed
        or not (1 <= quantity <= 99)
    ):
        flash(
            "Data pesanan tidak valid. Periksa nama, produk, dan jumlah.",
            "error"
        )
        return redirect(url_for("index"))

    flash(
        "Permintaan berhasil diterima untuk demo. "
        "Data ini tidak disimpan; silakan hubungi dealer untuk konfirmasi.",
        "success"
    )
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return "OK", 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
