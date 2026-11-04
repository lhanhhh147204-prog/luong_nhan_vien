import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_config

def init_db():
    conn = db_config.get_db_connection()
    cursor = conn.cursor()

    # Tạo bảng NhanVien
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NhanVien (
            id SERIAL PRIMARY KEY,
            ho_ten VARCHAR(255) NOT NULL,
            chuc_vu VARCHAR(100),
            loai_nhan_su INT DEFAULT 1,
            ngay_vao_lam DATE
        )
    """)

    # Tạo bảng LuongChinhThuc
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LuongChinhThuc (
            id SERIAL PRIMARY KEY,
            nhan_vien_id INT REFERENCES NhanVien(id),
            thang VARCHAR(50) NOT NULL,
            gross FLOAT,
            bhxh_nld FLOAT,
            thue_tncn FLOAT,
            thuc_nhan_net FLOAT,
            ghi_chu TEXT
        )
    """)

    # Tạo bảng ChiPhiKhoan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChiPhiKhoan (
            id SERIAL PRIMARY KEY,
            nhan_vien_id INT REFERENCES NhanVien(id),
            thang VARCHAR(50) NOT NULL,
            so_tien FLOAT,
            ghi_chu TEXT
        )
    """)

    # Tạo bảng CongNo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CongNo (
            id SERIAL PRIMARY KEY,
            nhan_vien_id INT REFERENCES NhanVien(id),
            so_tien_no FLOAT NOT NULL,
            thang_phat_sinh INT,
            nam_phat_sinh INT,
            ghi_chu TEXT,
            trang_thai VARCHAR(50) DEFAULT 'Chưa giải quyết'
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Khởi tạo cấu trúc Database trên Supabase PostgreSQL thành công!")

if __name__ == '__main__':
    init_db()
