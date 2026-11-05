# -*- coding: utf-8 -*-
# database/migrate_add_nhanvien_fields.py
# Migration: Them cot cam_ket_08, so_npt, ma_so_thue vao bang NhanVien.
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db_config

MIGRATIONS = [
    "ALTER TABLE NhanVien ADD COLUMN IF NOT EXISTS cam_ket_08 BOOLEAN DEFAULT FALSE",
    "ALTER TABLE NhanVien ADD COLUMN IF NOT EXISTS so_npt INT DEFAULT 0",
    "ALTER TABLE NhanVien ADD COLUMN IF NOT EXISTS ma_so_thue VARCHAR(20)",
    "ALTER TABLE NhanVien ADD COLUMN IF NOT EXISTS ngay_vao_lam DATE",
    "ALTER TABLE ChiPhiKhoan ADD COLUMN IF NOT EXISTS ghi_chu TEXT",
]

def run():
    conn = db_config.get_db_connection()
    cursor = conn.cursor()
    for sql in MIGRATIONS:
        try:
            cursor.execute(sql)
            print("  OK: " + sql[:80])
        except Exception as e:
            print("  ERR: " + str(e))
    conn.commit()
    cursor.close()
    conn.close()
    print("Migration done.")

if __name__ == "__main__":
    print("=== MIGRATION: Add columns to NhanVien ===")
    run()
