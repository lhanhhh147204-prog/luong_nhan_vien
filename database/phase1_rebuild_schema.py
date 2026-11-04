import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=QL_LUONG;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

# Các cột cần thêm vào LuongChinhThuc
columns_to_add = [
    "nam INT",
    "so_cong FLOAT",
    "luong_chinh FLOAT",
    "pc_an_trua FLOAT",
    "pc_dien_thoai FLOAT",
    "pc_nha_o FLOAT",
    "thuong_trach_nhiem FLOAT",
    "thuong_chuyen_can FLOAT",
    "chi_phi_khac FLOAT",
    "luong_khoan FLOAT",
    "tam_ung FLOAT",
    "thue_tncn FLOAT"
]

print("Cập nhật bảng LuongChinhThuc...")
for col_def in columns_to_add:
    col_name = col_def.split(" ")[0]
    # Check if column exists
    cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('LuongChinhThuc') AND name = '{col_name}')
            ALTER TABLE LuongChinhThuc ADD {col_def}
    """)

# Xóa bảng PhuCap cũ vì đã gộp vào LuongChinhThuc
cursor.execute("IF EXISTS (SELECT * FROM sysobjects WHERE name='PhuCap' AND xtype='U') DROP TABLE PhuCap")

conn.commit()
cursor.close()
conn.close()

print("Cập nhật Database Schema thành công!")
