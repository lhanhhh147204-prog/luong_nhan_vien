# KẾ HOẠCH NÂNG CẤP GIAO DIỆN (UI/UX BACKLOG)
## Đề xuất: Tái thiết kế Hệ thống Bảng Lương theo phong cách Ardena (Fintech Dark Glassmorphism)

**Ngày ghi nhận:** 05/11/2026  
**Nguồn cảm hứng:** Video demo `ardena.mp4` (Fintech & Asset Portfolio Dashboard)  
**Mục tiêu:** Nâng cấp toàn diện giao diện webapp Bảng Lương Hoàng Anh từ dạng dashboard cơ bản lên chuẩn giao diện phần mềm tài chính chuyên nghiệp quốc tế (SaaS).

---

### 1. Bản sắc Thị giác (Visual Identity & Theme)
- **Phong cách:** Dark Glassmorphism (Kính mờ cao cấp).
- **Màu nền:** Tông đen than chì sâu (`#111215` / `#16171b`).
- **Thẻ nội dung (Cards):** Kính mờ với `backdrop-filter: blur(16px)`, hiệu ứng đổ bóng đa tầng và viền phát sáng mỏng tinh tế (`border: 1px solid rgba(255, 255, 255, 0.08)`).
- **Màu điểm nhấn (Accent Colors):**
  - **Đỏ cam san hô (`#FF4D2E`):** Dành cho các nút hành động chính (Primary Action), nút xác nhận và cảnh báo rủi ro cao.
  - **Xanh ngọc Mint (`#10B981`):** Dành cho trạng thái đã thanh toán, tăng trưởng dương và các khoản an toàn.
  - **Vàng hổ phách (`#F59E0B`):** Cảnh báo cần lưu ý (Cam kết 08, công nợ).

---

### 2. Các Thành Phần Giao Diện Sẽ Triển Khai (Components)

#### 🔹 2.1. Thanh điều hướng thu gọn linh hoạt (Collapsible Sidebar)
- Cho phép thu gọn thành dải icon (Icon Rail) để tối ưu không gian hiển thị số liệu hoặc mở rộng thành menu đầy đủ.
- Tích hợp avatar người dùng, chuyển đổi chế độ xem nhanh.

#### 🔹 2.2. Biểu đồ Dòng tiền & Quỹ lương trung tâm (Hero Chart)
- Biểu đồ sóng mượt mà (Smooth Area Chart với Chart.js) hiển thị biến động:
  - Tổng Gross theo tháng.
  - Thực lĩnh Net theo tháng.
  - Tỷ lệ trích đóng BHXH và thuế TNCN.
- Bộ lọc thời gian nhanh dạng pill: `6 Tháng`, `1 Năm`, `Cả năm 2025/2026`.

#### 🔹 2.3. Bảng điều khiển "Cần xử lý ngay" (Widget: "Needs you today")
- Đặt ở cột bên phải tương tự Ardena, trực tiếp liên kết với API `tax_engine`:
  - **Cảnh báo công nợ:** Hiển thị 4 khoản nợ quá hạn > 3 tháng (Lê Duy Phú, Lê Hoàng Anh, Nguyễn Văn Quyền, Nguyễn Ngọc Hưng) kèm nút hành động 1-chạm: `[Đã thu hồi]` / `[Gửi nhắc nợ]`.
  - **Cảnh báo rủi ro thuế:** Danh sách các khoản chi khoán $\ge$ 2 triệu chưa có Cam kết 08 kèm nút `[Bổ sung CK08]` hoặc `[Khấu trừ 10%]`.

#### 🔹 2.4. Ngăn trượt chi tiết nhân sự (Slide-over Drawer)
- Khi click vào bất kỳ nhân viên nào trong danh sách, một bảng trượt mượt mà xuất hiện từ mép phải màn hình:
  - Hồ sơ nhân viên, mã số thuế, số người phụ thuộc.
  - Chi tiết bóc tách phiếu lương: Lương cơ bản, phụ cấp ăn trưa, điện thoại, trách nhiệm.
  - Diễn giải từng bậc lũy tiến thuế TNCN (từ Bậc 1 đến Bậc 7).
  - Lịch sử tạm ứng và biến động công nợ qua các tháng.

#### 🔹 2.5. Toast thông báo có nút Hoàn tác (Undo Toast)
- Khi người dùng cập nhật trạng thái công nợ hoặc nhập bảng lương, toast xuất hiện ở góc dưới màn hình kèm nút `[Hoàn tác]` trong 5 giây.

---

### 3. Tệp Cần Tác Động Khi Kích Hoạt
1. `update_dashboard.py` (hàm `generate_html` sinh ra mã HTML/CSS/JS mới).
2. Tích hợp sẵn với API Server phiên bản 2.1 vừa hoàn thiện (`/api/thong-ke`, `/api/kiem-tra`, `/api/cong-no`, `/api/nhat-ky`).

---

### 4. Trạng Thái Hiện Tại
- **Trạng thái:** `PENDING / BACKLOG` (Đã lưu ý tưởng và kế hoạch chi tiết, sẵn sàng thực thi khi người dùng yêu cầu).
