import sqlite3
import pandas as pd
import os

DB_PATH = 'database.db'
EXCEL_PATH = r"c:/Users/lehoa/OneDrive/Documents/BANG_LUONG'/He_Thong_Luong_HOANGANH.2026.xlsx"

def create_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT,
        tax_id TEXT,
        base_salary REAL,
        dependents INTEGER,
        is_contract_team BOOLEAN DEFAULT FALSE,
        has_commitment_08 BOOLEAN DEFAULT FALSE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month INTEGER,
        work_days REAL,
        allowance_meal REAL,
        allowance_phone REAL,
        allowance_housing REAL,
        bonus REAL,
        gross_salary REAL,
        insurance_deduction REAL,
        tax_deduction REAL,
        net_salary REAL,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )
    ''')

def migrate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    create_tables(cursor)

    print("Reading Excel file...")
    try:
        # Đọc danh sách nhân viên từ sheet Thang 1 (hoặc giả định 4 NV chính)
        # df_t1 = pd.read_excel(EXCEL_PATH, sheet_name='Thang 1', skiprows=3)
        # Chỉ lấy nhân viên HĐLĐ (vài dòng đầu)
        employees_data = [
            ("Lê Duy Phú", "Giám đốc", "042079012339", 6000000, 1, False, False),
            ("Lê Hoàng Anh", "NV Thu mua", "042204012755", 6000000, 1, False, False),
            ("Nguyễn Thị Kim Trí", "Kế toán", "051189014994", 8000000, 1, False, False),
            ("Nguyễn Văn Quyền", "NV CT Phú Quốc", "042089005787", 8000000, 2, False, False),
            # Đội khoán
            ("Hồ Thẩm", "Đội khoán CT", "", 0, 0, True, False),
            ("Lưu Trọng Hoàng", "Đội khoán CT", "", 0, 0, True, False),
            ("Nguyễn Chí Thanh", "Đội khoán CT", "", 0, 0, True, True),
            ("Lê Trọng Đức", "Nhân công khoán", "", 0, 0, True, False),
        ]
        
        # Xóa cũ
        cursor.execute("DELETE FROM payroll")
        cursor.execute("DELETE FROM employees")
        
        for emp in employees_data:
            cursor.execute('''
                INSERT INTO employees (name, position, tax_id, base_salary, dependents, is_contract_team, has_commitment_08)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', emp)
            
        conn.commit()
        print(f"Migrated {len(employees_data)} employees successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data()
