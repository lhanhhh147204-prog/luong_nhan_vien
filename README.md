# 💼 HỆ THỐNG KẾ TOÁN TIỀN LƯƠNG & DASHBOARD ĐIỀU HÀNH 2026
> **Công Ty TNHH XD SX TM Nhôm Kính Hoàng Anh**
> Dự án tự động hóa kế toán tiền lương, tính thuế TNCN, BHXH và theo dõi công nợ lương theo chuẩn pháp luật Việt Nam.

---

## 📁 CẤU TRÚC PHÂN TẦNG THƯ MỤC (PROJECT STRUCTURE)

```
BANG_LUONG/
│
├── 📊 He_Thong_Luong_HOANGANH.2026.xlsx     # Bảng tính Excel gốc 2026 (Mẫu 02-LĐTL)
│
└── 📂 chien_than_AI/                        # Toàn bộ mã nguồn hệ thống
    │
    ├── 🚀 [Core Web App & API - Production]
    │   ├── api_server.py                    # Backend Flask API chính (Cổng 5055 & Vercel)
    │   ├── update_dashboard.py              # Engine sinh giao diện Dashboard HTML
    │   ├── tax_engine.py                    # Engine tính Thuế TNCN lũy tiến & BHXH VN
    │   ├── db_config.py                     # Cấu hình kết nối Supabase PostgreSQL
    │   ├── requirements.txt                 # Khai báo dependencies
    │   ├── vercel.json                      # Cấu hình Deploy Serverless Vercel
    │   ├── START_APP.bat                    # Phím tắt 1-click khởi chạy hệ thống
    │   └── SESSION_STATE.md                 # Nhật ký phiên làm việc & Roadmap
    │
    ├── 📂 database/                         # Quản lý CSDL & Lịch sử Migration
    │   ├── init_postgres_db.py              # Khởi tạo schema PostgreSQL trên Supabase
    │   ├── phase0_enhance_schema.py         # Nâng cấp bảng schema
    │   ├── phase1_rebuild_schema.py         # Tái tạo cấu trúc bảng chuẩn hóa
    │   ├── create_mssql_db.py               # Schema SQL Server (Local)
    │   ├── import_excel_to_sql.py           # Bóc tách & nạp Excel vào SQL Server
    │   ├── migrate_data_to_supabase.py      # Chuyển đổi dữ liệu lên Cloud Supabase
    │   ├── migration_data.json              # Dữ liệu snapshot trung gian
    │   ├── verify_sql.py                    # Kiểm tra tính toàn vẹn dữ liệu
    │   └── run_truncate.py                  # Dọn dẹp bảng dữ liệu
    │
    ├── 📂 docs/                             # Báo cáo, Tài liệu kỹ thuật & Quy tắc
    │   ├── BAO_CAO_PHAN_TICH_2026.md        # Báo cáo phân tích chuyên sâu lương 2026
    │   ├── WORKFLOW.md                      # Quy trình vận hành & nghiệp vụ kế toán
    │   ├── ROADMAP_UI_UX_ARDENA.md          # Lộ trình thiết kế UI/UX Fintech Dark Glassmorphism
    │   ├── GITHUB_RESOURCES_BENCHMARK.md    # Tuyển tập GitHub Repos tiêu chuẩn cho dự án
    │   └── memory/                          # Bộ nhớ quy tắc công ty & nhật ký lỗi
    │       ├── cong_ty_rules.md             # Quy tắc nghiệp vụ đặc thù công ty
    │       ├── error_log.md                 # Nhật ký lỗi & cách khắc phục
    │       └── SESSION_STATE.md             # Bản lưu trạng thái bộ nhớ
    │
    ├── 📂 skills/                           # Bộ 5 Kỹ năng AI Kế toán (Agent Skills)
    │   ├── excel-audit-and-repair/          # Kiểm tra & sửa lỗi file Excel
    │   ├── payroll-automation/              # Tự động hóa tính lương
    │   ├── financial-reporting/             # Lập báo cáo tài chính & thuế
    │   ├── data-reconciliation/             # Đối soát UNC ngân hàng ↔ Bảng lương
    │   └── tax-compliance-vn/               # Kiểm tra tuân thủ chính sách thuế TNCN/BHXH
    │
    └── 📂 archive/                          # Lưu trữ lịch sử & Scratchpad
        ├── webapp_legacy/                   # Phiên bản thử nghiệm FastAPI + SQLite cũ
        └── scratch/                         # 27 script nháp, test công thức lúc phát triển
```

---

## ⚡ HƯỚNG DẪN KHỞI CHẠY (QUICK START)

### Cách 1: Khởi động 1-Click (Khuyến nghị cho Windows)
* Nhấp đúp vào file **`START_APP.bat`**.
* Hệ thống sẽ tự động bật API Server và mở trình duyệt tại: **`http://localhost:5055`**.

### Cách 2: Khởi động thủ công bằng Terminal
```bash
# Di chuyển vào thư mục dự án
cd "c:\Users\lehoa\OneDrive\Documents\BANG_LUONG'\chien_than_AI"

# Chạy API Server
python api_server.py
```

### 🌐 Môi trường Live Production
* **URL:** `https://bangluong-seven.vercel.app`
* **CI/CD:** Tự động build qua GitHub repo `luong_nhan_vien` mỗi khi push lên nhánh `main`.

---

## 🛡️ CÁC TÍNH NĂNG CHÍNH
1. **Form 1 - Bảng Lương Tháng:** Tính tự động Gross, BHXH (10.5%), Thuế TNCN bậc lũy tiến, Miễn trừ gia cảnh và ăn ca.
2. **Form 2 - Chi Phí Khoán:** Ghi nhận tiền khoán thi công công trình ngoài thực địa.
3. **Form 3 - Ghi Nhận Công Nợ:** Quản lý tiền lương còn nợ nhân viên theo tháng/năm.
4. **Form 4 - Thêm Nhân Sự:** Phân loại 3 nhóm nhân viên: HĐLĐ chính thức, Vãng lai (Cam kết 08), Đội khoán.
5. **Form 5 - Xóa Nhân Sự:** Khóa an toàn, chỉ cho phép xóa khi chưa phát sinh giao dịch lương/công nợ.
