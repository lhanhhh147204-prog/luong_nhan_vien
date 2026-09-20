import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=QL_LUONG;Trusted_Connection=yes;'

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

statements = [
    # Bảng PhuCap - Các khoản phụ cấp miễn thuế riêng từng tháng
    """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PhuCap' AND xtype='U')
    CREATE TABLE PhuCap (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        nhan_vien_id INT NOT NULL FOREIGN KEY REFERENCES NhanVien(id),
        thang      VARCHAR(10) NOT NULL,
        nam        INT NOT NULL,
        pc_an      FLOAT DEFAULT 0,
        pc_xang_xe FLOAT DEFAULT 0,
        pc_dien_thoai FLOAT DEFAULT 0,
        pc_nha_o   FLOAT DEFAULT 0,
        pc_khac    FLOAT DEFAULT 0,
        ghi_chu    NVARCHAR(300)
    )
    """,
    # Bảng CongNo - Nợ lương tồn đọng
    """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CongNo' AND xtype='U')
    CREATE TABLE CongNo (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        nhan_vien_id INT NOT NULL FOREIGN KEY REFERENCES NhanVien(id),
        so_tien_no   FLOAT NOT NULL,
        thang_phat_sinh VARCHAR(10),
        nam_phat_sinh INT,
        trang_thai   NVARCHAR(50) DEFAULT N'Chưa giải quyết',
        ngay_du_kien_tra DATE,
        ghi_chu      NVARCHAR(300)
    )
    """,
    # Bảng ThanhToanUNC - Đối chiếu ủy nhiệm chi ngân hàng
    """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ThanhToanUNC' AND xtype='U')
    CREATE TABLE ThanhToanUNC (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        nhan_vien_id INT NOT NULL FOREIGN KEY REFERENCES NhanVien(id),
        thang        VARCHAR(10),
        nam          INT,
        ngay_chuyen  DATE,
        so_tien      FLOAT NOT NULL,
        so_unc       VARCHAR(50),
        ngan_hang    NVARCHAR(100),
        hinh_thuc    NVARCHAR(50) DEFAULT N'Chuyển khoản',
        ghi_chu      NVARCHAR(300)
    )
    """,
    # Bảng AuditLog - Ghi log mọi thay đổi dữ liệu theo QT-001
    """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AuditLog' AND xtype='U')
    CREATE TABLE AuditLog (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        bang_lien_quan NVARCHAR(100),
        hanh_dong  NVARCHAR(50),
        du_lieu_cu NVARCHAR(MAX),
        du_lieu_moi NVARCHAR(MAX),
        nguoi_thuc_hien NVARCHAR(100) DEFAULT N'Kế Toán',
        thoi_gian  DATETIME DEFAULT GETDATE(),
        ghi_chu    NVARCHAR(300)
    )
    """,
    # Bổ sung cột MST và so_npt vào NhanVien nếu chưa có
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='ma_so_thue')
        ALTER TABLE NhanVien ADD ma_so_thue VARCHAR(20)
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='so_npt')
        ALTER TABLE NhanVien ADD so_npt INT DEFAULT 0
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='trang_thai')
        ALTER TABLE NhanVien ADD trang_thai NVARCHAR(50) DEFAULT N'Đang làm'
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='luong_cb_dong_bh')
        ALTER TABLE NhanVien ADD luong_cb_dong_bh FLOAT DEFAULT 0
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='luong_thuc_te')
        ALTER TABLE NhanVien ADD luong_thuc_te FLOAT DEFAULT 0
    """,
    # Bổ sung cột cam_ket_08 vào NhanVien
    """
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('NhanVien') AND name='cam_ket_08')
        ALTER TABLE NhanVien ADD cam_ket_08 BIT DEFAULT 0
    """,
]

for i, stmt in enumerate(statements):
    cursor.execute(stmt)
    conn.commit()

# Seed dữ liệu nhân viên chính thức từ báo cáo đã có
nhan_vien_seed = [
    # (ho_ten, chuc_vu, loai_ns, ma_so_thue, so_npt, trang_thai, luong_cb_bh, luong_tt, cam_ket_08)
    ("Lê Duy Phú",           "Giám đốc",        1, "042079012339", 1, "Đang làm", 6000000, 25000000, 0),
    ("Lê Hoàng Anh",         "NV Thu mua",       1, "042204012755", 0, "Đang làm", 6000000, 14000000, 0),
    ("Nguyễn Thị Kim Trí",   "Kế toán",          1, "051189014994", 0, "Đang làm", 8000000, 18000000, 0),
    ("Nguyễn Văn Quyền",     "NV CT Phú Quốc",   1, "042089005787", 0, "Đang làm", 8000000, 22000000, 0),
    ("Lê Trọng Đức",         "Thợ khoán",        2, "",             0, "Ngừng TT", 0,       20000000, 0),
    ("Nguyễn Văn Chiến",     "Thợ khoán",        2, "",             0, "Ngừng TT", 0,       18000000, 0),
    ("Lê Văn Khê",           "Thợ khoán",        2, "",             0, "Ngừng TT", 0,       20000000, 0),
    ("Hồ Văn Phải",          "Thợ khoán",        2, "",             0, "Đang TT",  0,       20000000, 0),
    ("Hồ Thẩm",              "Trưởng đội CT Hồ Tràm", 3, "",        0, "Đang TT",  0,       0,        0),
    ("Lưu Trọng Hoàng",      "Trưởng đội Nam Khang",  3, "",        0, "Đang TT",  0,       0,        0),
    ("Nguyễn Chí Thanh",     "Trưởng đội Nam Khang",  3, "",        0, "Đang TT",  0,       0,        0),
    ("Võ Tấn Quang",         "Trưởng đội Nam Khang",  3, "",        0, "Đang TT",  0,       0,        0),
    ("Lò Văn Tiên",          "Trưởng đội Bayfront",   3, "",        0, "Đang TT",  0,       0,        0),
    ("Võ Thanh Hưng",        "Trưởng đội Bayfront",   3, "",        0, "Đang TT",  0,       0,        0),
    ("Nguyễn Ngọc Hưng",     "NV",               1, "",             0, "Đã nghỉ",  0,       0,        0),
    ("Tống Đắc Sơn",         "NV",               1, "",             0, "Đã nghỉ",  0,       0,        0),
]

for nv in nhan_vien_seed:
    cursor.execute("SELECT id FROM NhanVien WHERE ho_ten = ?", (nv[0],))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO NhanVien (ho_ten, chuc_vu, loai_nhan_su, ma_so_thue, so_npt, trang_thai, luong_cb_dong_bh, luong_thuc_te, cam_ket_08)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, nv)

conn.commit()

# Seed CongNo 2025
cong_no_data = [
    ("Lê Duy Phú",       13370000),
    ("Lê Hoàng Anh",     11370000),
    ("Nguyễn Văn Quyền", 17058461),
    ("Nguyễn Ngọc Hưng", 13278461),
]

for name, so_tien in cong_no_data:
    cursor.execute("SELECT id FROM NhanVien WHERE ho_ten = ?", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("SELECT id FROM CongNo WHERE nhan_vien_id = ?", (row.id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO CongNo (nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, trang_thai, ghi_chu)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row.id, so_tien, "12", 2025, "Chưa giải quyết", "Nợ tồn đọng từ năm 2025"))

conn.commit()
cursor.close()
conn.close()

print("Phase 0 complete: SQL Schema enhanced successfully!")
print("Tables added: PhuCap, CongNo, ThanhToanUNC, AuditLog")
print("Columns added to NhanVien: ma_so_thue, so_npt, trang_thai, luong_cb_dong_bh, luong_thuc_te, cam_ket_08")
print("Seeded 16 NhanVien + 4 CongNo records")
