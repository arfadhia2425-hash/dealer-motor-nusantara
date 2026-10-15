#!/usr/bin/env bash
set -euo pipefail
DB_PATH="${DB_PATH:-/var/lib/dealermotor/orders.db}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/dealermotor}"
STAMP="$(date +%F-%H%M%S)"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
sqlite3 "$DB_PATH" ".backup '${BACKUP_DIR}/orders-${STAMP}.db'"
sqlite3 "${BACKUP_DIR}/orders-${STAMP}.db" "PRAGMA integrity_check;"
# Retensi contoh: hapus backup lokal lebih lama dari 14 hari.
find "$BACKUP_DIR" -type f -name 'orders-*.db' -mtime +14 -delete
