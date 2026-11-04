import pyodbc

# Test connection to master and create database if not exists
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=master;Trusted_Connection=yes;'

try:
    print("Connecting to SQL Server (master)...")
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    db_name = "QL_LUONG"
    
    # Check if db exists
    cursor.execute("SELECT name FROM master.dbo.sysdatabases WHERE name = ?", (db_name,))
    if not cursor.fetchone():
        print(f"Creating database {db_name}...")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print("Database created.")
    else:
        print(f"Database {db_name} already exists.")
        
    cursor.close()
    conn.close()
    
    # Reconnect to QL_LUONG
    conn_str_db = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE={db_name};Trusted_Connection=yes;'
    print(f"Connecting to {db_name}...")
    conn = pyodbc.connect(conn_str_db)
    cursor = conn.cursor()
    
    # Create tables
    tables = [
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='NhanVien' and xtype='U')
        CREATE TABLE NhanVien (
            id INT IDENTITY(1,1) PRIMARY KEY,
            ho_ten NVARCHAR(100) NOT NULL,
            chuc_vu NVARCHAR(100),
            ma_so_thue VARCHAR(50),
            loai_nhan_su INT NOT NULL -- 1: Chinh thuc, 2: Vang lai, 3: Doi khoan
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='LuongChinhThuc' and xtype='U')
        CREATE TABLE LuongChinhThuc (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nhan_vien_id INT FOREIGN KEY REFERENCES NhanVien(id),
            thang VARCHAR(20),
            gross FLOAT,
            bhxh_nld FLOAT,
            thuc_nhan_net FLOAT
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ChiPhiKhoan' and xtype='U')
        CREATE TABLE ChiPhiKhoan (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nhan_vien_id INT FOREIGN KEY REFERENCES NhanVien(id),
            thang VARCHAR(20),
            so_tien FLOAT
        )
        """
    ]
    
    for stmt in tables:
        cursor.execute(stmt)
        
    conn.commit()
    print("Tables created successfully.")
    
except Exception as e:
    print(f"Error: {e}")
