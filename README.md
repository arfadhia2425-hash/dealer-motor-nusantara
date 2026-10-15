# Dealer Motor Nusantara — Praktikum Cloud Computing

Contoh aplikasi web pemesanan UMKM untuk tugas “Migrasi Sistem UMKM ke Resources Cloud”.

## Fitur
- Halaman publik menampilkan nama/deskripsi UMKM dan 6 produk beserta harga.
- Formulir pemesanan menyimpan data ke SQLite.
- `GET /health` mengembalikan `OK` jika aplikasi dan database dapat diakses; jika DB gagal, mengembalikan `DB ERROR` dengan HTTP 503.
- Endpoint contoh `/admin/orders` dilindungi token, namun untuk produksi sebaiknya gunakan autentikasi sungguhan atau jangan publikasikan endpoint ini.

## Menjalankan lokal (Python 3.10+)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_SECRET_KEY='ganti-dengan-random-secret'
export ADMIN_TOKEN='token-admin-yang-kuat'
python app.py
```
Buka `http://127.0.0.1:5000`. Cek `http://127.0.0.1:5000/health`.

## Deploy ke Ubuntu VM
Ikuti langkah di `DEPLOYMENT.md`. Gunakan IP publik VM untuk demo. Pastikan lokasi region/zone cloud dipilih di Indonesia dan dokumentasikan screenshot konsol sebagai bukti.

## Konfigurasi keamanan
- Jangan commit `.env`, token, atau password.
- Buka hanya port 22 (batasi ke IP admin), 80 dan 443. Jangan buka port 5000.
- Gunakan SSH key, bukan password SSH.
- Aktifkan HTTPS dengan sertifikat TLS.
- Backup database ke lokasi terpisah; uji restore secara berkala.

## Catatan
Nama UMKM, produk, harga, kelompok, dan anggota merupakan data contoh. Ganti placeholder sebelum pengumpulan. Bukti cloud harus berasal dari deployment yang benar-benar dilakukan kelompok.
