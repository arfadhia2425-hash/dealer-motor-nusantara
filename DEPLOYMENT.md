# Panduan Deploy (Ubuntu 22.04/24.04)

> Jalankan di VM cloud yang region/zone-nya benar-benar berada di Indonesia. Screenshot dan catat konfigurasi aktual.

## 1. Siapkan VM
1. Buat akun cloud dan aktifkan MFA.
2. Pilih region Indonesia (periksa nama region/zone yang tersedia di provider).
3. Buat VM Ubuntu LTS dengan minimum 1 vCPU, RAM 1–2 GB, disk 20–25 GB.
4. Pasang SSH public key. Beri VM IP publik statis jika tersedia.
5. Firewall/security group: SSH TCP 22 hanya dari IP admin; HTTP TCP 80 dan HTTPS TCP 443 dari internet. Jangan buka 5000.

## 2. Instal aplikasi
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
sudo adduser --system --group --home /opt/dealermotor dealer
sudo mkdir -p /opt/dealermotor
sudo chown -R "$USER":"$USER" /opt/dealermotor
# Salin app.py, requirements.txt, templates/, static/ ke /opt/dealermotor
cd /opt/dealermotor
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
Simpan rahasia di file `/etc/dealermotor.env` yang hanya dapat dibaca root dan service:
```bash
sudo install -m 600 /dev/null /etc/dealermotor.env
sudo nano /etc/dealermotor.env
```
Isi:
```
FLASK_SECRET_KEY=GANTI_DENGAN_RANDOM_PANJANG
ADMIN_TOKEN=GANTI_DENGAN_TOKEN_KUAT
DB_PATH=/var/lib/dealermotor/orders.db
```
Buat folder data dan beri hak akses kepada akun service:
```bash
sudo mkdir -p /var/lib/dealermotor
sudo chown -R dealer:dealer /var/lib/dealermotor
sudo chown -R dealer:dealer /opt/dealermotor
```

## 3. systemd service
Buat `/etc/systemd/system/dealermotor.service`:
```
[Unit]
Description=Dealer Motor Nusantara Flask App
After=network.target

[Service]
User=dealer
Group=dealer
WorkingDirectory=/opt/dealermotor
EnvironmentFile=/etc/dealermotor.env
ExecStart=/opt/dealermotor/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 app:app
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
Aktifkan:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dealermotor
sudo systemctl status dealermotor
```

## 4. Nginx reverse proxy
Buat `/etc/nginx/sites-available/dealermotor`:
```
server {
    listen 80;
    server_name _;
    client_max_body_size 1m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Lalu:
```bash
sudo ln -s /etc/nginx/sites-available/dealermotor /etc/nginx/sites-enabled/dealermotor
sudo nginx -t
sudo systemctl reload nginx
```
Cek `http://IP-PUBLIK/` dan `http://IP-PUBLIK/health`. Untuk HTTPS, hubungkan domain yang dikuasai kelompok lalu pasang sertifikat TLS (misalnya Certbot/Let's Encrypt) dan paksa redirect HTTP ke HTTPS.

## 5. Firewall host (sesuaikan SSH admin)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from IP_PUBLIK_ADMIN to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```
Pastikan aturan firewall cloud juga sesuai. Ganti `IP_PUBLIK_ADMIN`.

## 6. Backup dan uji restore
Contoh backup SQLite (jalankan sebagai akun dengan akses DB):
```bash
sudo install -d -o dealer -g dealer -m 700 /var/backups/dealermotor
sudo -u dealer sqlite3 /var/lib/dealermotor/orders.db ".backup '/var/backups/dealermotor/orders-$(date +%F-%H%M).db'"
```
Jika `sqlite3` CLI belum ada: `sudo apt install sqlite3`.
Backup lokal di VM tidak cukup untuk bencana kehilangan VM. Salin backup terenkripsi ke object storage atau server terpisah yang juga berada di Indonesia, batasi aksesnya, dan dokumentasikan retensi.
Uji restore pada file terpisah:
```bash
sudo -u dealer sqlite3 /var/backups/dealermotor/orders-YYYY-MM-DD-HHMM.db "PRAGMA integrity_check;"
sudo -u dealer sqlite3 /tmp/restore-test.db ".restore /var/backups/dealermotor/orders-YYYY-MM-DD-HHMM.db"
sudo -u dealer sqlite3 /tmp/restore-test.db "SELECT COUNT(*) FROM orders;"
```
Catat waktu, nama backup, hasil `integrity_check`, jumlah data sebelum/sesudah, dan screenshot. Jangan menimpa DB produksi saat uji.

## 7. Monitoring dan notifikasi
- Pantau CPU, RAM, disk, status VM, dan uptime dari dashboard provider.
- Buat alert ketika instance tidak sehat, CPU tinggi berkelanjutan, disk hampir penuh, atau biaya melewati anggaran.
- Untuk monitoring aplikasi sederhana: jalankan `curl -fsS http://127.0.0.1/health` dan catat hasilnya.
- Konfigurasikan kanal notifikasi email/console sesuai fitur provider; uji dengan kondisi simulasi yang aman dan screenshot bukti.

## 8. Uji penerimaan
- [ ] Halaman publik terbuka dari jaringan di luar kampus.
- [ ] Ada nama/deskripsi UMKM dan minimal 5 produk serta harga.
- [ ] Footer berisi nomor kelompok dan 4 nama anggota.
- [ ] `/health` menghasilkan teks `OK` saat sehat.
- [ ] Kode dan README tersedia di repository Git.
- [ ] Port 5000 tidak terbuka ke publik.
- [ ] Backup berhasil dan restore diuji.
- [ ] Monitoring/notifikasi telah diuji.
- [ ] Biaya aktual dicatat.
- [ ] Bukti decommission dibuat setelah demo jika VM harus dihapus.
