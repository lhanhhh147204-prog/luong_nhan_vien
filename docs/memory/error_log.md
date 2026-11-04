# Error Log — Lỗi Đã Gặp & Cách Sửa

> Ghi nhận bởi TRẠM 8 (Memory Manager) sau mỗi phiên làm việc.
> Đọc file này ở TRẠM 7 (Debugging Check) để tránh lặp lại lỗi cũ.

---

## Cấu Trúc Mỗi Mục

```
### [LỖI-XXX] Tên lỗi ngắn gọn
- **Ngày phát hiện**: DD/MM/YYYY
- **File/Sheet**: [tên file] > [tên sheet] > [ô]
- **Mô tả**: Lỗi gì, biểu hiện thế nào
- **Nguyên nhân gốc**: Tại sao xảy ra
- **Cách sửa đã kiểm chứng**: Các bước cụ thể
- **Phòng ngừa**: Làm gì để không tái diễn
```

---

## Lỗi Đã Biết

(Chưa có lỗi nào được ghi nhận cho dự án này. Các lỗi phát sinh sẽ được Memory Manager cập nhật tự động vào đây)

### [LỖI-001] "name 'pyodbc' is not defined" hoặc "tuple object has no attribute"
- **Ngày phát hiện**: 18/09/2026
- **File/Sheet**: `tax_engine.py` (Hàm `run_anomaly_detection`)
- **Mô tả**: Khi chạy phát hiện bất thường, Radar AI báo lỗi hệ thống liên quan đến DB.
- **Nguyên nhân gốc**: Do migrate từ SQL Server (pyodbc) sang PostgreSQL (psycopg2). `psycopg2` mặc định trả về Tuple cho mỗi `row`, nhưng code cũ vẫn dùng cú pháp gọi thuộc tính của `pyodbc` (`row.nhan_vien_id`). Lỗi này bị bắt bởi `except` và lưu cứng vào file HTML.
- **Cách sửa đã kiểm chứng**: 
  1. Thay thế các cú pháp gọi thuộc tính bằng chỉ số Tuple (ví dụ: đổi `row.nhan_vien_id` thành `row[1]`).
  2. Chạy lại lệnh `python update_dashboard.py` để sinh lại `index.html`.
- **Phòng ngừa**: Luôn nhớ `psycopg2` cursor thông thường trả về Tuple (trừ khi dùng `DictCursor`). Không dùng cú pháp `row.thuoc_tinh` khi thao tác với DB từ nay về sau.

### [LỖI-002] Mất kết nối API - Webapp báo lỗi "Không thể kết nối"
- **Ngày phát hiện**: 18/09/2026
- **File/Sheet**: `webapp/index.html` (Môi trường Cloud)
- **Mô tả**: Gọi API bị thất bại hoặc trạng thái Supabase báo "Unhealthy".
- **Nguyên nhân gốc**: Tài khoản Supabase Free Tier sẽ tự động tạm ngưng (Pause) Database nếu không có truy cập trong 7 ngày để tiết kiệm tài nguyên.
- **Cách sửa đã kiểm chứng**: Đăng nhập trang quản trị Supabase, bấm "Restore Project" / "Restart Project" để đánh thức Database.
- **Phòng ngừa**: Truy cập vào Webapp ít nhất 1 lần/tuần hoặc nâng cấp lên gói Pro (nếu cần uptime 100%). Nếu test ở local, phải chạy `python api_server.py` thay vì bấm đúp mở file `index.html`.

---

*Cập nhật tự động bởi TRẠM 8 sau mỗi phiên làm việc*
