---
name: data-reconciliation
description: |
  Đối chiếu dữ liệu giữa: Bảng lương Excel ↔ Sao kê/UNC ngân hàng ↔ Sổ kế toán.
  Sử dụng khi cần kiểm tra tiền đã chuyển khoản đúng chưa, phát hiện chênh lệch,
  hoặc xác nhận công nợ lương tồn đọng. Đặc biệt quan trọng trước khi quyết toán thuế.
  Nguồn gốc: addyosmani/agent-skills (debugging pattern) + heilcheng/awesome-agent-skills.
---

# 🔄 Data Reconciliation — Đối Chiếu Số Liệu 3 Chiều

> Triết lý: **Tiền trong bảng lương ≠ Tiền đã chuyển. Phải đối chiếu 3 nguồn.**
> Nguồn gốc: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — debugging + [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills)

---

## Khi Nào Kích Hoạt?

- ✅ Sau khi chi trả lương: Kiểm tra UNC đã khớp bảng lương chưa
- ✅ Nhân viên/thợ khoán phản ánh thiếu tiền
- ✅ Sheet `total` không khớp với thực tế chi trả UNC
- ✅ Chuẩn bị quyết toán thuế cuối năm
- ✅ Kiểm tra công nợ lương còn tồn đọng từ năm trước

---

## TAM GIÁC ĐỐI CHIẾU (3 Nguồn Bắt Buộc)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   [1] BẢNG LƯƠNG EXCEL          [2] UNC NGÂN HÀNG  │
│   (Tiền phải trả theo       ↔   (Tiền thực sự đã   │
│    hợp đồng & tính toán)         chuyển khoản)      │
│              ↕                          ↕           │
│         [3] SỔ KẾ TOÁN (TK 334 / TK 622 / TK 111)  │
│         (Ghi nhận phát sinh & thanh toán)           │
│                                                     │
│   ✅ Khớp cả 3 → OK                                │
│   ⚠️  Lệch giữa 1-2 → Chuyển thiếu/thừa            │
│   ⚠️  Lệch giữa 1-3 → Sai bút toán kế toán         │
│   ⚠️  Lệch giữa 2-3 → Sổ chưa cập nhật             │
└─────────────────────────────────────────────────────┘
```

---

## QUY TRÌNH ĐỐI CHIẾU 5 BƯỚC

### Bước 1: Chuẩn Bị Dữ Liệu

Thu thập 3 nguồn:
```
Nguồn 1 — Bảng Lương Excel:
  → Sheet T[X]: cột "Số tiền thực lĩnh" cho từng nhân viên
  → Sheet "ĐỘI KHOÁN": cột "Số tiền" cho từng đội khoán

Nguồn 2 — Sao Kê Ngân Hàng / UNC:
  → Xuất file CSV/Excel từ ngân hàng
  → Các cột cần: Ngày, Số tiền, Tên thụ hưởng, Số TK thụ hưởng, Nội dung

Nguồn 3 — Sổ Kế Toán:
  → Sổ cái TK 334 (kỳ tương ứng)
  → Bảng phát sinh TK 334 / TK 622
```

### Bước 2: Tạo Bảng Đối Chiếu

```excel
CỘT A: Họ Tên Nhân Viên/Đội Thợ
CỘT B: Mã NV / Số TK Thụ Hưởng
CỘT C: Số Tiền Bảng Lương (Nguồn 1)
CỘT D: Số Tiền UNC Thực Chi (Nguồn 2) — Dùng SUMIFS theo Tên/TK
CỘT E: Chênh Lệch = C - D
CỘT F: Trạng Thái =IF(ABS(E)=0,"✅ Khớp",IF(E>0,"⚠️ Còn nợ","🔴 Chuyển thừa"))
CỘT G: Ghi Chú (số UNC, ngày chuyển, kỳ nào)
```

Công thức SUMIFS đối chiếu UNC:
```excel
=SUMIFS(SaoKe!$E:$E,          ← Cột Số tiền ngân hàng
        SaoKe!$G:$G,          ← Cột Tên thụ hưởng
        "*"&[@HoTen]&"*",     ← Khớp một phần tên (NGUYEN CHI THANH ≈ Nguyễn Chí Thanh)
        SaoKe!$A:$A,          ← Cột Ngày giao dịch
        ">="&DATE(2026,M,1),   ← Từ đầu tháng
        SaoKe!$A:$A,
        "<="&DATE(2026,M,31))  ← Đến cuối tháng
```

### Bước 3: Phân Loại Chênh Lệch

```
PHÂN TÍCH KHI PHÁT HIỆN LỆCH:

🔴 Chênh Lệch Lớn (> 1,000,000đ):
   → Dừng lại, báo BGĐ/Kế toán trưởng
   → Kiểm tra: Có UNC nào nhầm tên thụ hưởng không?
   → Kiểm tra: Có thanh toán chia nhiều lần không?
   → Kiểm tra: Có thanh toán tiền mặt ngoài UNC không?

🟡 Chênh Lệch Nhỏ (< 100,000đ):
   → Thường do làm tròn số
   → Kiểm tra phí chuyển khoản

🟢 Chênh Lệch Do Kỳ Khác:
   → Tiền tháng này trả bù cho tháng trước
   → Ghi chú rõ ràng vào cột G
```

### Bước 4: Theo Dõi Công Nợ Tích Lũy

```
BẢNG CÔNG NỢ LƯƠNG TỒN ĐỌNG:

Nhân Viên | Nợ T[X-2] | Nợ T[X-1] | Nợ T[X] | Đã TT T[X] | Còn nợ
----------|-----------|-----------|---------|------------|--------
[Tên]     | [VNĐ]     | [VNĐ]     | [VNĐ]   | [VNĐ]      | [VNĐ]

Quy tắc:
- Cộng dồn nợ qua các tháng (từ Lương,MrPhu.xlsx Sheet1)
- Trừ đi từng UNC đã chuyển
- Kết quả = Số tiền còn thực nợ
```

### Bước 5: Xác Nhận Và Lưu Trữ

```
TRƯỚC KHI ĐỐI CHIẾU HOÀN THÀNH:
- [ ] Tất cả UNC đã được map với ≥ 1 bảng lương
- [ ] Không còn UNC "mồ côi" (chuyển tiền nhưng không có bảng lương tương ứng)
- [ ] Không còn dòng lương "trống" (có bảng lương nhưng không có UNC nào)
- [ ] Tổng UNC kỳ X = Tổng thực lĩnh kỳ X (sau khi trừ nợ cũ/cộng trả bù)
- [ ] Lưu file đối chiếu: DoiChieu_T[X]_YYYY.xlsx
```

---

## Xử Lý Trường Hợp Đặc Biệt (Đã Gặp Trong Dự Án)

| Trường Hợp | Ví Dụ Thực Tế | Cách Xử Lý |
|---|---|---|
| Thanh toán chia nhỏ < 5tr | Đinh Văn Tuấn, Đồng Trọng Sang | SUMIFS tổng nhiều UNC nhỏ theo kỳ |
| Tên trong UNC khác bảng lương | "NGUYEN CHI THANH" ≠ "Nguyễn Chí Thanh" | Dùng SEARCH hoặc map thủ công |
| Trả gộp nhiều tháng | Hồ Văn Phải — trả Q1 một lần | Ghi chú kỳ, phân bổ đều các tháng |
| Tiền khoán theo từng công trình | NamKhang, Hồ Tràm, Núi Hoa... | Tạo tab riêng theo công trình |
| Nhân viên nghỉ việc còn nợ lương | Nguyễn Ngọc Hưng — 13,278,461đ | Theo dõi riêng trong CONG_NO_NOI_BO |

---

*Skill tích hợp với: payroll-automation (Bước 3), financial-reporting (Báo cáo tổng hợp), excel-audit-and-repair (khi số lệch do công thức sai)*
