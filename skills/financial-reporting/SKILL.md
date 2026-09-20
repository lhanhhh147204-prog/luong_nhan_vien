---
name: financial-reporting
description: |
  Tổng hợp và xuất báo cáo tài chính nhân sự: Quỹ lương theo tháng/quý/năm,
  Chi phí nhân công theo từng công trình (TK 622), báo cáo BHXH, quyết toán TNCN.
  Sử dụng khi cần báo cáo cho Ban Giám Đốc, nộp thuế, hoặc kiểm tra giá thành.
  Nguồn gốc: addyosmani/agent-skills + anthropics/financial-services (thích nghi VN).
---

# 📊 Financial Reporting — Báo Cáo Tài Chính Nhân Sự

> Triết lý: **Một lần nhập, nhiều lần báo cáo. Không copy-paste giữa các file.**
> Nguồn gốc: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) + anthropics/financial-services

---

## Khi Nào Kích Hoạt?

- ✅ Cuối tháng/quý: Lập báo cáo quỹ lương tổng hợp
- ✅ Cần báo cáo chi phí nhân công theo từng dự án/công trình
- ✅ Lập tờ khai thuế TNCN (tháng/quý/năm)
- ✅ Lập Báo cáo tình hình sử dụng lao động & đóng BHXH
- ✅ BGĐ hỏi: "Tháng này chi lương bao nhiêu? So với tháng trước?"

---

## Danh Sách Báo Cáo Cần Tạo

### 📋 NHÓM 1: Báo Cáo Nội Bộ (Dành Cho BGĐ)

**1.1 Dashboard Quỹ Lương**
```
- Tổng quỹ lương tháng hiện tại: [VNĐ]
- So với tháng trước: [+X% / -X%]
- Phân rã: Lương chính | Phụ cấp | Thưởng | BHXH DN
- Top 5 nhân sự lương cao nhất
- Nhân sự mới/nghỉ việc trong tháng
```

**1.2 Báo Cáo Chi Phí Theo Công Trình**
```
Công trình: [Tên]        Đội thi công: [Tên đội]
Chi phí nhân công: [VNĐ] Ngân sách: [VNĐ] Chênh lệch: [%]
Tháng thực hiện: [...]   Trạng thái: [Đang thi công / Hoàn thành]
```

**1.3 Công Nợ Lương Tồn Đọng**
```
Nhân viên: [Tên]  Nợ từ: [Kỳ]  Số tiền còn nợ: [VNĐ]
Đã thanh toán UNC: [VNĐ]  Còn phải TT: [VNĐ]
```

### 📋 NHÓM 2: Báo Cáo Thuế (Nộp Cơ Quan Thuế)

**2.1 Tờ Khai Thuế TNCN Hàng Quý (Mẫu 05/KK-TNCN)**
```
- Tổng thu nhập phát sinh: [VNĐ]
- Tổng thuế đã khấu trừ: [VNĐ]
- Phân theo từng loại: HĐ chính thức / Khoán / Đội thầu
```

**2.2 Bảng Kê Chi Tiết (Mẫu 05-1/BK-TNCN)**
```
STT | Họ Tên | CCCD | Địa chỉ | Thu nhập | Thuế TNCN khấu trừ | MST
```

**2.3 Quyết Toán Thuế TNCN Năm (Mẫu 05/QT-TNCN)**
```
- Tổng thu nhập cả năm theo từng nhân viên
- Tổng thuế đã khấu trừ
- Thuế còn phải nộp / Được hoàn
```

### 📋 NHÓM 3: Báo Cáo BHXH (Nộp BHXH)

**3.1 Bảng Đăng Ký Lao Động Tháng (D02-TS)**
```
- Danh sách tham gia mới
- Danh sách tạm dừng/chấm dứt
- Thay đổi mức đóng
```

**3.2 Phiếu Đóng BHXH Hàng Tháng**
```
Tổng lương đóng BH: [VNĐ]
BHXH DN phải đóng (21.5%): [VNĐ]
BHXH NLĐ đã khấu trừ (10.5%): [VNĐ]
Tổng cộng chuyển khoản: [VNĐ]
```

---

## QUY TRÌNH TẠO BÁO CÁO

### Bước 1: Xác định Loại Báo Cáo và Kỳ Báo Cáo

```
Trả lời 3 câu hỏi:
1. Đây là báo cáo gì? (nội bộ / thuế / BHXH)
2. Kỳ báo cáo: tháng / quý / năm?
3. Người nhận là ai? (BGĐ / Cơ quan thuế / Cơ quan BHXH)
```

### Bước 2: Thu Thập Dữ Liệu Nguồn

Lấy dữ liệu từ:
- `DANH_SACH_MASTER` → Danh sách nhân viên
- Sheet `T[X]` → Lương tháng tương ứng
- Sheet `ĐỘI KHOÁN THI CÔNG` → Chi phí đội khoán theo công trình
- Sheet `Mr Thanh` (và tương tự) → Dữ liệu UNC ngân hàng
- Sheet `total` → Tổng hợp năm

### Bước 3: Kiểm Tra Chéo (Cross-Validation)

```
RULE: Số liệu phải khớp ở 3 điểm:
1. Bảng lương chi tiết (sheet T[X])
2. Sổ kế toán TK 334 (Phải trả người lao động)
3. UNC ngân hàng đã thực chi
```

### Bước 4: Định Dạng Và Xuất Báo Cáo

```
Báo cáo nội bộ:
→ Dashboard tổng hợp 1 trang A4 (in màu)
→ Biểu đồ cột so sánh các tháng

Báo cáo thuế/BHXH:
→ Đúng mẫu biểu theo quy định
→ Có số hiệu, ngày lập, chữ ký Giám đốc + Kế toán trưởng
→ Đóng dấu (nếu nộp bản giấy)
```

---

## Template Dashboard BGĐ (1 Trang A4)

```
=== BÁO CÁO LƯƠNG THÁNG [X] NĂM 2026 ===
Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH

TỔNG QUAN:
┌─────────────────────────────────────────────┐
│ Tổng Quỹ Lương:        [xxx,xxx,xxx đ]      │
│ So với T[X-1]:         [+/-X.X%]            │
│ Số nhân sự:            [X người]            │
│ Đóng BHXH (DN):        [xxx,xxx,xxx đ]      │
│ Thuế TNCN khấu trừ:    [xxx,xxx,xxx đ]      │
│ Đã chuyển khoản UNC:   [xxx,xxx,xxx đ]      │
│ Còn phải thanh toán:   [xxx,xxx,xxx đ]      │
└─────────────────────────────────────────────┘

CHI PHÍ NHÂN CÔNG THEO CÔNG TRÌNH:
- CT [Tên]: [VNĐ] / [% KH]
- CT [Tên]: [VNĐ] / [% KH]

CẢNH BÁO:
⚠️  [Tên NV] - Còn công nợ lương [X] triệu từ T[Y]
⚠️  BHXH tháng [X] chưa nộp (hạn: ngày [Z])
```

---

*Skill được thiết kế để tích hợp với: excel-audit-and-repair, payroll-automation, data-reconciliation*
