import pyodbc

DB_NAME = "QL_LUONG"
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE={DB_NAME};Trusted_Connection=yes;'

print("Connecting to SQL Server to verify data...")
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

print("\n--- Nhập bảng NhanVien ---")
cursor.execute("SELECT * FROM NhanVien")
for row in cursor.fetchall():
    print(f"ID: {row.id} | Name: {row.ho_ten} | Type: {row.loai_nhan_su}")

print("\n--- Tổng chi phí Khoán & Vãng Lai theo người ---")
cursor.execute("""
    SELECT n.ho_ten, SUM(c.so_tien) as TongTien
    FROM ChiPhiKhoan c
    JOIN NhanVien n ON c.nhan_vien_id = n.id
    GROUP BY n.ho_ten
""")
for row in cursor.fetchall():
    print(f"{row.ho_ten}: {row.TongTien:,.0f} đ")

cursor.close()
conn.close()
