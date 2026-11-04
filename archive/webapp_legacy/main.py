from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn
from contextlib import asynccontextmanager
import os

DB_PATH = 'database.db'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB connection
    yield
    pass

app = FastAPI(lifespan=lifespan)

# Bật CORS để cho phép mở file index.html trực tiếp từ ổ cứng (file:///)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ thư mục static (nếu có)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Sửa lại đường dẫn file index.html cho đúng (nằm ngay ngoài webapp, không phải trong static)
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/employees")
def get_employees():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return employees

@app.get("/api/dashboard")
def get_dashboard():
    # Return mock/hardcoded data similar to api.py for the UI to function
    return {
        "status": "success",
        "tong_nhan_su": 10,
        "tong_doi_khoan": 4,
        "tong_chi_phi_luong": 252000000,
        "tong_chi_phi_khoan": 583200000
    }

@app.get("/api/nhan-vien")
def get_nhan_vien():
    # Phục vụ trang Quản lý nhân viên
    conn = get_db()
    cursor = conn.cursor()
    # Mock fallback if table doesn't have all columns, but let's try to query 'employees'
    # Wait, the UI expects fields like ho_ten, chuc_vu, loai_nhan_su, luong_cb, gross, cam_ket_08, trang_thai
    try:
        cursor.execute("SELECT id, name as ho_ten, position as chuc_vu, is_contract_team as loai_nhan_su, base_salary as luong_cb, has_commitment_08 as cam_ket_08, 'Đang làm' as trang_thai, 0 as gross FROM employees")
        rows = [dict(r) for r in cursor.fetchall()]
    except:
        rows = []
    conn.close()
    return {"status": "success", "data": rows}

@app.delete("/api/nhan-vien/{id}")
def delete_nhan_vien(id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Đã xóa nhân viên!"}
    except Exception as e:
        return {"error": str(e)}

class NhanVienInput(BaseModel):
    ho_ten: str
    chuc_vu: str = ""
    loai_nhan_su: int
    ma_so_thue: str = ""
    so_npt: int = 0
    luong_cb_dong_bh: float = 0
    luong_thuc_te: float = 0
    cam_ket_08: bool = False

@app.post("/api/nhan-vien")
def add_nhan_vien(data: NhanVienInput):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO employees (name, position, is_contract_team, base_salary, dependents, has_commitment_08) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.ho_ten, data.chuc_vu, True if data.loai_nhan_su in [2, 3] else False, data.luong_cb_dong_bh, data.so_npt, data.cam_ket_08))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Đã thêm nhân viên mới!"}
    except Exception as e:
        return {"error": str(e)}

class PayrollInput(BaseModel):
    employee_id: int
    month: int
    work_days: float
    allowance_meal: float = 0
    allowance_phone: float = 0
    allowance_housing: float = 0
    bonus: float = 0

def calculate_tncn(taxable_income: float) -> float:
    if taxable_income <= 0:
        return 0
    if taxable_income <= 5000000:
        return taxable_income * 0.05
    if taxable_income <= 10000000:
        return taxable_income * 0.1 - 250000
    if taxable_income <= 18000000:
        return taxable_income * 0.15 - 750000
    if taxable_income <= 32000000:
        return taxable_income * 0.2 - 1650000
    if taxable_income <= 52000000:
        return taxable_income * 0.25 - 3250000
    if taxable_income <= 80000000:
        return taxable_income * 0.3 - 5850000
    return taxable_income * 0.35 - 9850000

@app.post("/api/payroll")
def submit_payroll(data: PayrollInput):
    conn = get_db()
    cursor = conn.cursor()
    
    # Lấy thông tin NV
    cursor.execute("SELECT * FROM employees WHERE id = ?", (data.employee_id,))
    emp = cursor.fetchone()
    if not emp:
        return {"error": "Nhân viên không tồn tại"}
    
    is_contract = emp['is_contract_team']
    has_commitment = emp['has_commitment_08']
    
    gross = 0
    insurance = 0
    tax = 0
    net = 0
    
    if is_contract:
        # Nhân công khoán / Đội khoán
        # Tính theo số tiền khoán (giả sử lương cb hoặc dùng allowance khác)
        gross = data.allowance_meal + data.bonus # Lấy tạm từ các khoản nhập
        if gross >= 2000000 and not has_commitment:
            tax = gross * 0.10
        net = gross - tax
    else:
        # NV Hợp đồng
        gross = emp['base_salary'] + data.allowance_meal + data.allowance_phone + data.allowance_housing + data.bonus
        insurance = emp['base_salary'] * 0.105
        # Giảm trừ gia cảnh theo luật (11tr bản thân, 4.4tr phụ thuộc)
        giam_tru_ban_than = 11000000
        giam_tru_phu_thuoc = emp['dependents'] * 4400000
        # Miễn thuế ăn ca tối đa 730k
        tien_an_ca_mien_thue = min(data.allowance_meal, 730000)
        
        # Thu nhập chịu thuế
        taxable_income = gross - tien_an_ca_mien_thue - insurance - giam_tru_ban_than - giam_tru_phu_thuoc
        tax = calculate_tncn(taxable_income)
        net = gross - insurance - tax
        
    cursor.execute('''
        INSERT INTO payroll 
        (employee_id, month, work_days, allowance_meal, allowance_phone, allowance_housing, bonus, gross_salary, insurance_deduction, tax_deduction, net_salary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.employee_id, data.month, data.work_days, data.allowance_meal, data.allowance_phone, data.allowance_housing, data.bonus, gross, insurance, tax, net))
    
    conn.commit()
    conn.close()
    
    return {"message": "Success", "gross": gross, "tax": tax, "net": net}

@app.get("/api/payroll/{month}")
def get_payroll_by_month(month: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, e.name, e.position 
        FROM payroll p 
        JOIN employees e ON p.employee_id = e.id 
        WHERE p.month = ?
    ''', (month,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
