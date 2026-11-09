# TỔNG HỢP CÁC REPOSITORY GITHUB TIÊU BIỂU & TÀI NGUYÊN PHÙ HỢP VỚI DỰ ÁN
## Dự án: Hệ Thống Kế Toán Tiền Lương & Quản Trị Nhân Sự — Công Ty Nhôm Kính Hoàng Anh

Tài liệu này tổng hợp các kho lưu trữ mã nguồn mở (GitHub Repositories) xuất sắc nhất, được tuyển chọn kỹ lưỡng để làm chuẩn tham chiếu (benchmark) và tích hợp vào hệ thống kế toán nội bộ của công ty.

---

### 1. 🧮 Nhóm Logic Nghiệp Vụ: Tính Lương, Thuế TNCN & BHXH Việt Nam

| Repository | Công nghệ | Điểm nổi bật & Khả năng ứng dụng vào dự án |
| :--- | :--- | :--- |
| **[`googlesky/thue-2026`](https://github.com/googlesky/thue-2026)** | Python / Web | • Bộ công cụ tính thuế TNCN chuẩn Luật Việt Nam mới nhất.<br>• Thuật toán quy đổi **Gross ⇄ Net bằng tìm kiếm nhị phân (Binary Search)** cực nhanh và chính xác tuyệt đối.<br>• Hỗ trợ tính lương tăng ca (OT), thưởng năng suất, và quyết toán năm. |
| **[`thangtd-0050/pit`](https://github.com/thangtd-0050/pit)** | TypeScript / React / Tailwind | • Mô hình tính toán phân rã lương Gross - Net đầy đủ: BHXH (8%), BHYT (1.5%), BHTN (1%), Giảm trừ bản thân (11tr) & Người phụ thuộc (4.4tr).<br>• Cấu trúc kiểm thử (Unit Tests) hoàn chỉnh, dễ dàng chuyển đổi sang Python backend. |
| **[`frappe/hrms`](https://github.com/frappe/hrms)** | Python / Frappe (ERPNext) | • Tiêu chuẩn vàng của hệ thống quản trị nhân sự & tiền lương mã nguồn mở toàn cầu.<br>• Cung cấp kiến trúc chuẩn cho: Phiếu lương điện tử (Salary Slip), Cấu trúc lương (Salary Structure), Tạm ứng lương (Salary Advance) và Cấn trừ công nợ nhân viên tự động. |
| **[`Phat-pham99/Thue_thu_nhap_ca_nhan`](https://github.com/Phat-pham99/Thue_thu_nhap_ca_nhan)** | Python | • Script tính thuế TNCN tinh gọn, phù hợp để làm module microservice độc lập. |

---

### 2. 🎨 Nhóm Giao Diện: Fintech Dashboard, Dark Glassmorphism & Tương Tác

| Repository | Công nghệ | Điểm nổi bật & Khả năng ứng dụng vào dự án |
| :--- | :--- | :--- |
| **[`abderrahimghazali/shadcn-fintech`](https://github.com/abderrahimghazali/shadcn-fintech)** | Next.js / Tailwind / Framer Motion / Recharts | • **Chuẩn mực giao diện Fintech hiện đại:** Thiết kế Dark mode sang trọng, thẻ Card kính mờ phát sáng viền (Glow border), đồ thị sóng tài chính mượt mà.<br>• Rất tương đồng với phong cách **Ardena** mà dự án đang hướng tới. |
| **[`TailAdmin/tailadmin-free-tailwind-dashboard-template`](https://github.com/TailAdmin/tailadmin-free-tailwind-dashboard-template)** | Tailwind CSS / Alpine.js | • Bộ giao diện Dashboard quản trị tinh gọn, đầy đủ biểu đồ dòng tiền, bảng dữ liệu phân trang, trạng thái badge màu sắc chuyên nghiệp. |
| **[`21st.dev / Glassmorphism Elements`](https://21st.dev)** | CSS / Tailwind | • Kho linh kiện UI chuyên về hiệu ứng kính mờ (frosted glass), nút bấm gradient, thanh tiến trình ngân sách và widget "Cần xử lý ngay" (Action pill). |

---

### 3. 🛡️ Nhóm Cơ Sở Dữ Liệu & Audit Trail (Supabase / PostgreSQL)

| Tài nguyên | Khả năng ứng dụng |
| :--- | :--- |
| **Supabase Postgres Audit Triggers** | Tự động hóa việc ghi vết thay đổi (CDC - Change Data Capture) vào bảng `auditlog` trực tiếp ở tầng Database bằng PostgreSQL Trigger, đảm bảo tuân thủ 100% quy định kế toán QT-001. |
| **PgBouncer Pooling Optimization** | Cấu hình Transaction Pooling cổng 6543 giúp chịu tải cao trên tài khoản Supabase Free/Pro mà không bị tràn giới hạn kết nối (Connection Limit). |

---

### 4. Cách Tận Dụng Các Tài Nguyên Này Cho Các Bước Tiếp Theo
1. **Tham chiếu logic quy đổi Gross ⇄ Net:** Áp dụng thuật toán binary search của `googlesky/thue-2026` vào hàm chuyển đổi lương 2 chiều trên `api_server.py`.
2. **Hiện thực hóa UI Ardena:** Sử dụng các thành phần CSS/Tailwind của `shadcn-fintech` để xây dựng lại giao diện Dashboard kính mờ tối màu theo đúng lộ trình `docs/ROADMAP_UI_UX_ARDENA.md`.
