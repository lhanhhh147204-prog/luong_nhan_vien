# BÁO CÁO PHIÊN LÀM VIỆC (SESSION STATE)
**Ngày giờ lưu:** 20/09/2026
**Dự án:** Hệ Thống Kế Toán Lương — Nhôm Kính Hoàng Anh 2026 (chien_than_AI)

## 1. Trạng Thái Hiện Tại (Current Status)
- **Mức độ hoàn thiện:** 100% Core Features. Đã hoàn thiện cả quy trình Thêm và Xóa Nhân Viên.
- **Môi trường Database:** PostgreSQL (Supabase). Lưu ý tài khoản Free Tier có thể bị "Unhealthy/Paused" nếu không sử dụng trong 1 tuần, cần Restart lại trên Dashboard Supabase khi webapp mất kết nối.
- **Môi trường Hosting:** Ứng dụng Flask API và Giao diện Dashboard tĩnh được kết hợp và triển khai thành công trên Vercel Serverless Functions.
- **Triển khai CI/CD:** Dự án đã được liên kết với kho GitHub cá nhân (`luong_nhan_vien`). Vercel sẽ tự động build và deploy phiên bản mới nhất mỗi khi có thay đổi trên nhánh `main`.
- **Trạng thái URL:** Dự án đang chạy Live tại `https://bangluong-seven.vercel.app`. Liên kết API (qua `const API = '';`) hoạt động ổn định nhờ cấu hình `vercel.json`.

## 2. Các Thay Đổi Chính Đã Thực Hiện (Phiên 20/09)
- **Tính năng Xóa Nhân Viên:** Viết thêm route `DELETE /api/nhan-vien/<id>` vào `api_server.py` với cơ chế kiểm tra an toàn (chỉ cho phép xóa khi chưa có dữ liệu Lương, Chi phí hoặc Công nợ). Thêm Form 5 trên giao diện (`update_dashboard.py`).
- **Xử lý lỗi kết nối API:** Hỗ trợ quá trình kiểm thử Local (với port 5055) và sau đó chuyển đổi `const API` về chuẩn Production (chuỗi rỗng `''`) để hoạt động đồng bộ trên Vercel.
- **Đóng gói dự án & Git:** Khởi tạo local Git repository cho thư mục `chien_than_AI`, bổ sung `.gitignore` (loại bỏ `__pycache__`, `.env`), và push toàn bộ mã nguồn lên GitHub.
- **Thiết lập Vercel:** Hướng dẫn kết nối thành công kho GitHub mới với Vercel project để triển khai dự án hoàn toàn tự động.

## 3. Công Việc Cho Phiên Tiếp Theo (Next Steps)
*(Nếu có)*
1. **Theo dõi Deployment:** Xác nhận Vercel đã build xong bản cập nhật mới nhất và trình duyệt không bị cache (dùng Ctrl + F5).
2. **Bổ sung tính năng Security:** Thêm Auth/Login đơn giản nếu cần bảo vệ URL khỏi người ngoài.
3. **Phát triển giao diện Di động (Mobile-friendly):** Tinh chỉnh CSS để giao diện dễ dùng hơn trên màn hình điện thoại của giám đốc hoặc nhân viên kế toán.
4. **Domain Custom:** Liên kết tên miền riêng (VD: `ketoan.nhomkinh.com`).

## 4. Ghi Chú Đặc Biệt (Notes)
- Mọi chỉnh sửa API sau này bắt buộc phải dùng `psycopg2` theo chuẩn PostgreSQL (không được dùng `pyodbc`).
- Code đang được quản lý cấu trúc Vercel qua file `vercel.json` (Route mọi thứ về `api_server.py`).
- Nếu muốn chỉnh sửa giao diện Frontend (`index.html`), bắt buộc phải sửa chuỗi HTML trong file `update_dashboard.py` vì file tĩnh `index.html` được sinh ra tự động từ đó.
