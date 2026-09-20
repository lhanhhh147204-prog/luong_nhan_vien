# BÁO CÁO PHIÊN LÀM VIỆC (SESSION STATE)
**Ngày giờ lưu:** 18/09/2026
**Dự án:** Hệ Thống Kế Toán Lương — Nhôm Kính Hoàng Anh 2026 (chien_than_AI)

## 1. Trạng Thái Hiện Tại (Current Status)
- **Mức độ hoàn thiện:** 100% Core Features. Đã fix triệt để các lỗi phát sinh sau khi migrate DB.
- **Môi trường Database:** PostgreSQL (Supabase). Lưu ý tài khoản Free Tier có thể bị "Unhealthy/Paused" nếu không sử dụng trong 1 tuần, cần Restart lại trên Dashboard Supabase khi webapp mất kết nối.
- **Môi trường Hosting:** Ứng dụng Flask API và Giao diện Dashboard tĩnh được kết hợp và triển khai thành công trên Vercel Serverless Functions.
- **Trạng thái URL:** Dự án đang chạy Live tại `https://bangluong-seven.vercel.app`. Liên kết API (qua `const API = '';`) hoạt động ổn định nhờ cấu hình `vercel.json`.

## 2. Các Thay Đổi Chính Đã Thực Hiện (Phiên 18/09)
- Đã đọc và kích hoạt lại Não bộ AI (Workflow 9 trạm).
- Sửa lỗi nghiêm trọng trong `tax_engine.py`: Chuyển đổi cú pháp truy cập thuộc tính (như `row.nhan_vien_id`) của `pyodbc` sang cú pháp truy cập chỉ số (như `row[1]`) để tương thích hoàn toàn với `psycopg2`. (Bug gây ra lỗi "name 'pyodbc' is not defined" trên giao diện Radar AI).
- Chạy lại script `update_dashboard.py` để update file `index.html` và xóa bỏ thông báo lỗi hardcode.
- Hướng dẫn xử lý lỗi Supabase bị Pause (Unhealthy status) trên Cloud.

## 3. Công Việc Cho Phiên Tiếp Theo (Next Steps)
*(Nếu có)*
1. **Kiểm thử quy trình Nhập liệu (End-to-End):** Thử nhập lương tháng mới hoặc công nợ mới trực tiếp trên Dashboard (Cloud) và verify dữ liệu trên Supabase.
2. **Bổ sung tính năng Security:** Thêm Auth/Login đơn giản nếu cần bảo vệ URL khỏi người ngoài.
3. **Phát triển giao diện Di động (Mobile-friendly):** Tinh chỉnh CSS để giao diện dễ dùng hơn trên màn hình điện thoại của giám đốc hoặc nhân viên.
4. **Domain Custom:** Liên kết tên miền riêng (VD: `ketoan.nhomkinh.com`).

## 4. Ghi Chú Đặc Biệt (Notes)
- Mọi chỉnh sửa API sau này bắt buộc phải dùng `psycopg2` theo chuẩn PostgreSQL (không được dùng `pyodbc`).
- Code đang được quản lý cấu trúc Vercel qua file `vercel.json` (Route mọi thứ về `api_server.py`).
- Cần thận trọng nếu thay đổi schema Database trên Supabase; phải cập nhật code Python tương ứng (đặc biệt là các câu query SQL thuần).
