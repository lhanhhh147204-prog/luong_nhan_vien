import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pyodbc
import db_config

# Kết nối SQL Server cục bộ
conn_local = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=QL_LUONG;Trusted_Connection=yes;')
cursor_local = conn_local.cursor()

# Kết nối Supabase PostgreSQL
conn_remote = db_config.get_db_connection()
cursor_remote = conn_remote.cursor()

print("Bắt đầu chuyển dữ liệu từ Local SQL Server sang Supabase...")

# 1. Chuyển bảng NhanVien
cursor_local.execute("SELECT id, ho_ten, chuc_vu, loai_nhan_su FROM NhanVien")
nhanviens = cursor_local.fetchall()
for nv in nhanviens:
    cursor_remote.execute("""
        INSERT INTO NhanVien (id, ho_ten, chuc_vu, loai_nhan_su)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET 
            ho_ten = EXCLUDED.ho_ten,
            chuc_vu = EXCLUDED.chuc_vu,
            loai_nhan_su = EXCLUDED.loai_nhan_su;
    """, (nv.id, nv.ho_ten, nv.chuc_vu, nv.loai_nhan_su))
print(f"Đã chuyển {len(nhanviens)} nhân viên.")

# 2. Chuyển bảng LuongChinhThuc
cursor_local.execute("SELECT nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net, ghi_chu FROM LuongChinhThuc")
luongs = cursor_local.fetchall()
for l in luongs:
    cursor_remote.execute("""
        INSERT INTO LuongChinhThuc (nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net, ghi_chu)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (l.nhan_vien_id, l.thang, l.gross, l.bhxh_nld, l.thue_tncn, l.thuc_nhan_net, l.ghi_chu))
print(f"Đã chuyển {len(luongs)} bản ghi lương.")

# 3. Chuyển bảng ChiPhiKhoan
cursor_local.execute("SELECT nhan_vien_id, thang, so_tien FROM ChiPhiKhoan")
khoans = cursor_local.fetchall()
for k in khoans:
    cursor_remote.execute("""
        INSERT INTO ChiPhiKhoan (nhan_vien_id, thang, so_tien)
        VALUES (%s, %s, %s)
    """, (k.nhan_vien_id, k.thang, k.so_tien))
print(f"Đã chuyển {len(khoans)} bản ghi khoán.")

# 4. Chuyển bảng CongNo
cursor_local.execute("SELECT nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, ghi_chu, trang_thai FROM CongNo")
congnos = cursor_local.fetchall()
for c in congnos:
    cursor_remote.execute("""
        INSERT INTO CongNo (nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, ghi_chu, trang_thai)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (c.nhan_vien_id, c.so_tien_no, c.thang_phat_sinh, c.nam_phat_sinh, c.ghi_chu, c.trang_thai))
print(f"Đã chuyển {len(congnos)} bản ghi công nợ.")

# Reset sequence for NhanVien id in Postgres so new inserts work
cursor_remote.execute("SELECT MAX(id) FROM NhanVien")
max_id = cursor_remote.fetchone()[0] or 0
cursor_remote.execute(f"ALTER SEQUENCE nhanvien_id_seq RESTART WITH {max_id + 1}")

conn_remote.commit()
cursor_local.close()
conn_local.close()
cursor_remote.close()
conn_remote.close()
print("Chuyển dữ liệu hoàn tất! Hệ thống trên Cloud đã có đầy đủ dữ liệu.")
