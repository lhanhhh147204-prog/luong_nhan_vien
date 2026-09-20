---
name: payroll-automation
description: |
  Tự động hóa tính toán bảng lương: Lương cơ bản, phụ cấp, BHXH, Thuế TNCN cho cả
  lao động chính thức và nhân công khoán. Sử dụng khi cần tính lương tháng mới,
  cập nhật nhân sự, hoặc tái cơ cấu bảng lương. Tuân thủ luật BHXH 2024 và TT 80/2021.
  Nguồn gốc: addyosmani/agent-skills + VoltAgent/awesome-agent-skills (tùy chỉnh payroll VN).
---

# 💰 Payroll Automation — Kế Toán Nhôm Kính Hoàng Anh

> Triết lý: **Tham số hóa tất cả. Không hard-code con số luật vào ô Excel.**
> Nguồn gốc: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) + [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)

---

## Khi Nào Kích Hoạt?

- ✅ Đầu tháng: Tính bảng lương tháng mới
- ✅ Có nhân viên mới ký HĐ / nghỉ việc / thay đổi mức lương
- ✅ Có thay đổi quy định BHXH, mức lương tối thiểu vùng
- ✅ Cần kiểm tra lại Thuế TNCN đã tính đúng chưa
- ✅ Xuất bảng lương Mẫu 02-LĐTL để ký trình Giám đốc

---

## Cấu Trúc Dữ Liệu Chuẩn

### Sheet DANH_SACH_MASTER (Nguồn Sự Thật Duy Nhất)

| Cột | Trường | Ví Dụ |
|---|---|---|
| A | Mã NV | DP, HA, KT, VQ... |
| B | Họ và Tên | Lê Duy Phú |
| C | CCCD/CMND | 042079012339 |
| D | MST Cá Nhân | (nếu có) |
| E | Chức Vụ | Giám đốc |
| F | Loại HĐ | `CHINH_THUC` / `KHOAN_VIEC` / `VANG_LAI` |
| G | Lương CB đóng BH | 6,000,000 |
| H | Lương thỏa thuận thực tế | 25,000,000 |
| I | Ngày bắt đầu HĐ | 01/10/2025 |
| J | Số người phụ thuộc | 2 |
| K | Mức giảm trừ NT | =J*4,400,000 |
| L | Trạng thái | `DANG_LAM` / `NGHI_VIEC` / `THU_VIEC` |

### Sheet THAM_SO (Bảng Tham Số Luật)

```
BHXH_NLD    = 8%     (Người lao động)
BHYT_NLD    = 1.5%   (Người lao động)  
BHTN_NLD    = 1%     (Người lao động)
TONG_NLD    = 10.5%  (Tổng NLĐ đóng)

BHXH_DN     = 17.5%  (Doanh nghiệp)
BHYT_DN     = 3%     (Doanh nghiệp)
BHTN_DN     = 1%     (Doanh nghiệp)
TONG_DN     = 21.5%  (Tổng DN đóng)

GIAM_TRU_BT = 11,000,000  (Giảm trừ bản thân 2024)
GIAM_TRU_NT = 4,400,000   (Giảm trừ người phụ thuộc)
THUE_KHOAN  = 10%    (TNCN khoán < 1 tháng)
```

---

## QUY TRÌNH TÍNH LƯƠNG HÀNG THÁNG

### Phase 1: Thu Thập Dữ Liệu Đầu Vào

Khai báo cho tháng X:
```
- Số ngày công chuẩn: [số ngày]
- Danh sách nhân viên đi làm đủ / nghỉ có phép / nghỉ không phép
- Phụ cấp phát sinh: xăng xe, điện thoại, nhà ở, ăn ca, chuyên cần
- Thưởng: Tết, hiệu suất
- Danh sách nhân công khoán mới: họ tên, CCCD, số tiền khoán
- UNC đã thanh toán kỳ trước
```

### Phase 2: Tính Lương Từng Loại Nhân Sự

**A. Lao Động Ký HĐLĐ (Đóng BHXH):**
```
1. Lương cơ sở đóng BH = [Từ DANH_SACH_MASTER cột G]
2. BHXH NLĐ phải đóng = Lương CB đóng BH × 10.5%
3. Thu nhập chịu thuế = Tổng thu nhập - BHXH NLĐ - Giảm trừ bản thân - Giảm trừ NT
4. Thuế TNCN = Tính theo biểu lũy tiến 7 bậc
5. Thực lĩnh = Tổng thu nhập - BHXH NLĐ - Thuế TNCN
```

**B. Nhân Công Khoán < 1 Tháng (HĐLĐ ngắn hạn):**
```
1. Thu nhập khoán = [Thỏa thuận]
2. Nếu tổng thu nhập từ đơn vị này trong năm > 2,000,000 VNĐ/lần:
   → Khấu trừ Thuế TNCN 10% (không phụ thuộc giảm trừ gia cảnh)
3. Có Cam Kết 08/CK-TNCN: → Không khấu trừ (nếu thu nhập ≤ 11tr/tháng)
4. Thực lĩnh = Thu nhập - Thuế TNCN (nếu có)
5. Chứng từ: Lập Bảng kê 05-1/BK-TNCN
```

**C. Đội Khoán Nhân Công (Hợp Đồng Đội Khoán):**
```
1. Tổng giá trị hợp đồng khoán = [Theo HĐ từng công trình]
2. Khấu trừ Thuế TNCN 10% (bắt buộc - có HĐ đội khoán)
3. Thực thanh toán = Tổng HĐ - 10% Thuế TNCN
4. Chứng từ: Biên bản nghiệm thu + Bảng kê thanh toán đội khoán
```

### Phase 3: Kiểm Tra Tự Động

```
KIỂM TRA BẮT BUỘC TRƯỚC KHI IN:
- [ ] Tổng lương phát sinh = Tổng lương chính + Phụ cấp + Thưởng
- [ ] BHXH doanh nghiệp phải nộp = Tổng lương CB đóng BH × 21.5%
- [ ] BHXH + TNCN NLĐ đã trừ đúng?
- [ ] Nhân công khoán có đúng hết bị khấu trừ 10%?
- [ ] Tổng UNC cần chi = Tổng thực lĩnh (kiểm tra số tiền trong file ngân hàng)
- [ ] Số tiền trên bảng lương khớp với Sổ cái TK 334?
```

### Phase 4: Xuất Bảng Lương

Tự động tạo:
1. **Mẫu 02-LĐTL** (TT200/2014) — In để ký
2. **Bảng đề nghị thanh toán UNC** — Gửi ngân hàng
3. **Bảng kê 05-1/BK-TNCN** — Nộp cơ quan thuế
4. **Phiếu lương cá nhân** — Gửi từng nhân viên

---

## Biểu Thuế TNCN Lũy Tiến 7 Bậc (2024)

| Bậc | Thu Nhập Tính Thuế/Tháng | Thuế Suất | Công Thức Nhanh |
|---|---|---|---|
| 1 | ≤ 5,000,000 | 5% | TN × 5% |
| 2 | 5-10 triệu | 10% | TN × 10% - 250,000 |
| 3 | 10-18 triệu | 15% | TN × 15% - 750,000 |
| 4 | 18-32 triệu | 20% | TN × 20% - 1,650,000 |
| 5 | 32-52 triệu | 25% | TN × 25% - 3,250,000 |
| 6 | 52-80 triệu | 30% | TN × 30% - 5,850,000 |
| 7 | > 80 triệu | 35% | TN × 35% - 9,850,000 |

---

## Công Thức Excel Tính Thuế TNCN Tự Động

```excel
=IFERROR(
  IF([@TNTT]<=0, 0,
  IF([@TNTT]<=5000000, [@TNTT]*5%,
  IF([@TNTT]<=10000000, [@TNTT]*10%-250000,
  IF([@TNTT]<=18000000, [@TNTT]*15%-750000,
  IF([@TNTT]<=32000000, [@TNTT]*20%-1650000,
  IF([@TNTT]<=52000000, [@TNTT]*25%-3250000,
  IF([@TNTT]<=80000000, [@TNTT]*30%-5850000,
  [@TNTT]*35%-9850000))))))),
0)

[Ghi chú: TNTT = Thu nhập tính thuế = Tổng TN - BHXH NLĐ - Giảm trừ BT - Giảm trừ NT]
```

---

## Quy Tắc An Toàn

1. **Không xóa dòng nhân viên cũ** — Chuyển sang trạng thái `NGHI_VIEC` để giữ lịch sử
2. **Không sửa tham số luật** mà không có văn bản pháp lý mới
3. **Backup trước khi xử lý lương** — Lưu file tháng cũ với tên `TienLuong_YYYY_MM.xlsx`
4. **Không để trống cột CCCD** với lao động khoán — Bắt buộc khi quyết toán thuế

---

*Skill được thiết kế cho: Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH — Tuân thủ TT 200/2014, Luật BHXH 2024, TT 80/2021/TT-BTC*
