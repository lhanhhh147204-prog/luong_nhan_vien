import pandas as pd
import pyodbc
import math

EXCEL_PATH = r"c:\Users\lehoa\OneDrive\Documents\BANG_LUONG'\He_Thong_Luong_HOANGANH.2026.xlsx"
DB_NAME = "QL_LUONG"
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE={DB_NAME};Trusted_Connection=yes;'

print("Connecting to SQL Server...")
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

# Update DB schema if needed
cursor.execute("IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('LuongChinhThuc') AND name='ghi_chu') ALTER TABLE LuongChinhThuc ADD ghi_chu NVARCHAR(300)")
cursor.execute("IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id=OBJECT_ID('LuongChinhThuc') AND name='thue_tncn') ALTER TABLE LuongChinhThuc ADD thue_tncn FLOAT DEFAULT 0")

# Clear existing data before importing to prevent duplicates
print("Clearing old data...")
cursor.execute("DELETE FROM LuongChinhThuc")
cursor.execute("DELETE FROM ChiPhiKhoan")
conn.commit()

def get_or_create_nv(ho_ten, chuc_vu, loai_nhan_su):
    cursor.execute("SELECT id FROM NhanVien WHERE ho_ten = ?", (ho_ten,))
    row = cursor.fetchone()
    if row:
        return row.id
    else:
        cursor.execute("INSERT INTO NhanVien (ho_ten, chuc_vu, loai_nhan_su) VALUES (?, ?, ?)", 
                       (ho_ten, chuc_vu, loai_nhan_su))
        cursor.execute("SELECT @@IDENTITY AS id")
        return cursor.fetchone().id

try:
    print("Reading Excel file...")
    xls = pd.ExcelFile(EXCEL_PATH)
    
    print("Importing Luong Chinh Thuc from monthly sheets...")
    months = [f"Thang {i}" for i in range(1, 13)]
    
    for m in months:
        if m not in xls.sheet_names:
            continue
            
        df_raw = pd.read_excel(xls, sheet_name=m, header=None)
        header_row_idx = 3 # default
        for idx, row in df_raw.iterrows():
            row_str = " ".join([str(x).upper() for x in row.values])
            if "LƯƠNG" in row_str and "GROSS" in row_str:
                header_row_idx = idx
                break
                
        df_thang = pd.read_excel(xls, sheet_name=m, header=header_row_idx)
        # Dynamic columns based on position or name
        # We need Name, Gross, BH_NLD, Thue_TNCN, Net
        # We can find columns by keyword in header
        
        col_name = None
        col_gross = None
        col_bh = None
        col_tncn = None
        col_net = None
        
        for c in df_thang.columns:
            c_str = str(c).upper()
            if "HỌ VÀ TÊN" in c_str or "HỌ TÊN" in c_str: col_name = c
            elif "GROSS" in c_str: col_gross = c
            elif "BH NLĐ" in c_str or "10.5%" in c_str: col_bh = c
            elif "THUẾ TNCN" in c_str: col_tncn = c
            elif "NET" in c_str or "THỰC NHẬN" in c_str: col_net = c
            
        if not col_name or not col_gross:
            continue
            
        for idx, row in df_thang.iterrows():
            name = str(row[col_name]).strip()
            if pd.isna(name) or 'TỔNG' in name.upper() or 'NAN' in name.upper() or name == '' or 'LAO ĐỘNG' in name.upper() or str(row.iloc[0]).startswith("I.") or str(row.iloc[0]).startswith("II."):
                continue
                
            gross = float(row[col_gross]) if pd.notna(row[col_gross]) else 0.0
            bh_nld = float(row[col_bh]) if col_bh and pd.notna(row[col_bh]) else 0.0
            tncn = float(row[col_tncn]) if col_tncn and pd.notna(row[col_tncn]) else 0.0
            net_excel = float(row[col_net]) if col_net and pd.notna(row[col_net]) else 0.0
            
            if gross > 0:
                nv_id = get_or_create_nv(name, "Nhân Viên", 1)
                thang_str = m.replace("Thang", "Tháng")
                
                net_calculated = gross - bh_nld - tncn
                ghi_chu = ""
                if abs(net_calculated - net_excel) > 100:
                    ghi_chu = f"[!] CẢNH BÁO LỆCH: Excel = {net_excel:,.0f}, Tính toán = {net_calculated:,.0f}"
                    
                cursor.execute("""
                    INSERT INTO LuongChinhThuc (nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net, ghi_chu)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nv_id, thang_str, gross, bh_nld, tncn, net_excel, ghi_chu))

    print("Importing Chi Phi Khoan...")
    df_doikhoan_raw = pd.read_excel(xls, sheet_name="Thực chi-ĐộiKhoán", header=None)
    dk_header_idx = 1
    for idx, row in df_doikhoan_raw.iterrows():
        row_str = " ".join([str(x).upper() for x in row.values])
        if "HỌ VÀ TÊN" in row_str and "T1" in row_str:
            dk_header_idx = idx
            break
            
    df_doikhoan = pd.read_excel(xls, sheet_name="Thực chi-ĐộiKhoán", header=dk_header_idx)
    name_col = None
    for col in df_doikhoan.columns:
        if 'TÊN' in str(col).upper() or 'HỌ' in str(col).upper():
            name_col = col
            break
    if not name_col:
        name_col = df_doikhoan.columns[1]
    
    cursor.execute("SELECT ho_ten, loai_nhan_su FROM NhanVien")
    master_employees = {row.ho_ten.lower(): row.loai_nhan_su for row in cursor.fetchall()}
    
    for idx, row in df_doikhoan.iterrows():
        name = str(row[name_col]).strip()
        if pd.isna(name) or 'TỔNG' in name.upper() or 'NAN' in name.upper() or name == '': continue
        
        loai_ns = 2 
        for db_name, db_loai in master_employees.items():
            if db_name in name.lower() or name.lower() in db_name:
                loai_ns = db_loai
                break
                
        nv_id = get_or_create_nv(name, "Đội Khoán" if loai_ns == 3 else "Vãng Lai", loai_ns)
        
        month_cols = [c for c in df_doikhoan.columns if str(c).upper().startswith('T') and str(c)[1:].isdigit()]
        for col in month_cols:
            v = row[col]
            if pd.notna(v) and isinstance(v, (int, float)):
                v_float = float(v)
            elif pd.notna(v) and str(v).replace('.', '').replace(',', '').isdigit():
                v_float = float(str(v).replace('.', '').replace(',', ''))
            else:
                v_float = 0.0

            if v_float > 0:
                thang_str = f"Tháng {str(col)[1:]}"
                cursor.execute("""
                    INSERT INTO ChiPhiKhoan (nhan_vien_id, thang, so_tien)
                    VALUES (?, ?, ?)
                """, (nv_id, thang_str, v_float))

    conn.commit()
    print("Data imported successfully from He_Thong_Luong_HOANGANH.2026.xlsx!")

except Exception as e:
    conn.rollback()
    print(f"Error importing data: {e}")
finally:
    cursor.close()
    conn.close()
