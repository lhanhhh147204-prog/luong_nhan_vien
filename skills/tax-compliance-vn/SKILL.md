---
name: tax-compliance-vn
description: |
  Đảm bảo tuân thủ luật thuế Việt Nam cho doanh nghiệp sản xuất-thi công nhôm kính:
  Thuế TNCN (biểu lũy tiến & khoán 10%), BHXH/BHYT/BHTN, quyết toán cuối năm.
  Sử dụng khi cần kiểm tra tính đúng đắn của các khoản trích lập, lập tờ khai thuế,
  hoặc chuẩn bị hồ sơ quyết toán. Cập nhật theo luật hiện hành 2024-2026.
  Nguồn gốc: OpenAccountants/openaccountants + Micode-ai/accounting-ai-agent (thích nghi VN).
---

# ⚖️ Tax Compliance VN — Tuân Thủ Thuế Việt Nam

> Triết lý: **Đúng luật từ đầu — Không để thanh tra phát hiện sai.**
> Nguồn gốc: OpenAccountants pattern + Thuế TNCN / Luật BHXH 2024 Việt Nam

---

## Khi Nào Kích Hoạt?

- ✅ Kiểm tra xem tháng này có khoản nào bị tính sai không?
- ✅ Lập tờ khai Thuế TNCN hàng quý (hạn: 30/4, 31/7, 31/10, 31/1)
- ✅ Quyết toán TNCN năm (hạn: 31/3 năm sau)
- ✅ Đăng ký người phụ thuộc cho nhân viên
- ✅ Có nhân viên mới/nghỉ việc: xác định nghĩa vụ thuế và BH cuối cùng
- ✅ Cơ quan thuế/BHXH có thông báo kiểm tra

---

## BỘ QUY TẮC THUẾ TNCN (2024-2026)

### 1. Các Khoản Thu Nhập Chịu Thuế TNCN

```
CHỊU THUẾ (phải khai báo):
✅ Lương, thưởng theo HĐLĐ
✅ Phụ cấp: Xăng xe, điện thoại, nhà ở, ăn ca VƯỢt định mức
✅ Tiền khoán việc > 2,000,000đ/lần chi trả

MIỄN THUẾ (không khai báo):
❌ Phụ cấp xăng xe đến mức khoán của Nhà nước (không vượt)
❌ Phụ cấp ăn ca ≤ 730,000đ/tháng (theo NĐ 12/2022)
❌ Tiền thuê nhà ≤ 15% tổng thu nhập từ tiền lương
❌ Bảo hiểm sức khỏe, tai nạn mà DN mua cho NLĐ
❌ Quà tặng lễ tết ≤ 5,000,000đ/lần (không phải tiền mặt)
❌ Hỗ trợ khó khăn 1 lần/năm (có hội đồng xét)
```

### 2. Quy Tắc BHXH — Đối Tượng Đóng

```
PHẢI ĐÓNG BHXH (bắt buộc):
✅ HĐLĐ từ đủ 1 tháng trở lên (kể cả HĐLĐ có thời hạn xác định)
✅ Lương đóng BH: Tối thiểu = Lương tối thiểu vùng (Vùng 1: 4,960,000đ/tháng - 2024)
                  Tối đa = 20 × Lương cơ sở (= 20 × 2,340,000 = 46,800,000đ/tháng)

KHÔNG ĐÓNG BHXH:
❌ HĐLĐ dưới 1 tháng (Hợp đồng khoán việc theo mùa vụ)
❌ Lao động nước ngoài chưa có HĐ > 1 năm (xem xét riêng)
❌ Người đang hưởng lương hưu đồng thời làm việc (không đóng BHXH, chỉ đóng BHYT)
```

### 3. Quy Tắc Riêng Cho Nhân Công Khoán/Thi Công

```
TRƯỜNG HỢP CÓ HỢP ĐỒNG ĐỘI KHOÁN:
→ Bắt buộc khấu trừ 10% Thuế TNCN trên tổng tiền thanh toán
→ Lập Bảng kê 05-1/BK-TNCN
→ Cấp Chứng từ khấu trừ thuế cho từng người
→ Không đóng BHXH (vì HĐ khoán, không phải HĐLĐ)

TRƯỜNG HỢP CÓ CAM KẾT 08/CK-TNCN:
→ NLĐ cam kết thu nhập năm ≤ mức phải nộp thuế
→ DN không khấu trừ 10%
→ NLĐ tự khai thuế (nếu có thu nhập từ nơi khác)
→ Chỉ áp dụng với thu nhập ≤ khoảng 2,000,000đ/lần chi trả từ 1 nguồn

NHÂN CÔNG VÃNG LAI/TỰ DO (Không có HĐ):
→ Nếu thanh toán > 2,000,000đ/lần: khấu trừ 10% (Mẫu 08)
→ Nếu ≤ 2,000,000đ/lần: không cần khấu trừ
→ PHẢI có bảng kê chi tiết tên, CCCD, số tiền để chứng minh với thuế
```

---

## CHECKLIST TUÂN THỦ HÀNG THÁNG

### Checklist Tháng (Thực Hiện Trước Ngày 20 Tháng Sau)

```
THUẾ TNCN:
- [ ] Đã tính đúng TNCN cho toàn bộ HĐLĐ chính thức?
- [ ] Đã khấu trừ 10% cho nhân công khoán > 2tr/lần?
- [ ] Đã lập Bảng kê 05-1/BK-TNCN đầy đủ?
- [ ] Đã nộp tờ khai (nếu nộp hàng tháng)?

BHXH:
- [ ] Đã báo tăng cho NLĐ mới trong tháng?
- [ ] Đã báo giảm cho NLĐ nghỉ việc?
- [ ] Đã chuyển tiền BHXH đúng hạn?
- [ ] Đã kiểm tra mức đóng tối đa/tối thiểu?

HỒ SƠ:
- [ ] Hợp đồng đội khoán đã ký đầy đủ?
- [ ] CCCD photocopy có chữ ký của NLĐ?
- [ ] Bảng lương có chữ ký Giám đốc và Kế toán?
- [ ] UNC ngân hàng đã lưu đủ?
```

### Checklist Quý (Thực Hiện Trước Cuối Tháng Tiếp Theo Sau Quý)

```
- [ ] Lập và nộp tờ khai 05/KK-TNCN (qua ThueDienTu.gdt.gov.vn)
- [ ] Kiểm tra: Tổng thuế đã khấu trừ theo bảng kê = Tổng trên tờ khai?
- [ ] Nộp thuế TNCN đúng số trên tờ khai
- [ ] Lưu biên lai nộp thuế điện tử
```

### Checklist Năm (Thực Hiện Trước 31/3 Năm Sau)

```
- [ ] Lập tờ khai quyết toán 05/QT-TNCN
- [ ] Xét: Nhân viên nào được DN quyết toán thay? (làm duy nhất 1 nơi, ủy quyền)
- [ ] Cấp Chứng từ khấu trừ thuế TNCN (mẫu CTT50) cho NLĐ tự quyết toán
- [ ] Đăng ký lại người phụ thuộc (gia hạn hàng năm trước 31/12)
- [ ] Kiểm tra: Có khoản nào đã trích sai thuế không? → Khai bổ sung
```

---

## BẢNG TRA CỨU NHANH — CÁC MỨC TIÊU CHUẨN 2024

| Khoản Mục | Quy Định | Mức Hiện Tại |
|---|---|---|
| Lương cơ sở (Nhà nước) | NĐ 24/2023 | 2,340,000đ/tháng |
| LTT vùng 1 (TP.HCM, Hà Nội) | NĐ 74/2024 | 4,960,000đ/tháng |
| LTT vùng 2 | NĐ 74/2024 | 4,410,000đ/tháng |
| Phụ cấp ăn ca miễn thuế | Thông tư BTC | ≤ 730,000đ/tháng |
| Giảm trừ bản thân | Luật TNCN | 11,000,000đ/tháng |
| Giảm trừ người phụ thuộc | Luật TNCN | 4,400,000đ/NT/tháng |
| BHXH DN đóng | Luật BHXH 2024 | 21.5% |
| BHXH NLĐ đóng | Luật BHXH 2024 | 10.5% |
| Thuế TNCN khoán | TT 80/2021 | 10% (> 2tr/lần) |
| Mức BHXH tối đa | 20 × LCS | 46,800,000đ/tháng |

---

## CÁC LỖI PHỔ BIẾN CẦN TRÁNH

```
🔴 LỖI NẶNG (Có thể bị phạt):
   ✗ Không khấu trừ 10% cho nhân công khoán > 2tr
   ✗ Không lập bảng kê BK-TNCN
   ✗ Đóng BHXH thấp hơn mức lương thực tế ghi trên HĐLĐ
   ✗ Không khai báo nhân viên mới vào tháng đầu tiên

🟡 LỖI TRUNG BÌNH (Cần điều chỉnh):
   ✗ Để phụ cấp ăn ca > 730,000đ vào thu nhập không khấu trừ
   ✗ Không cập nhật giảm trừ người phụ thuộc khi có thay đổi
   ✗ Tính thuế theo lương thỏa thuận thay vì thu nhập tính thuế

🟢 LỖI NHỎ (Nên khắc phục):
   ✗ Sai định dạng ngày sinh trên bảng kê (phải ghi dd/mm/yyyy)
   ✗ Mã số thuế NLĐ trống
   ✗ Địa chỉ thường trú ghi tắt quá (thiếu tỉnh/huyện/xã)
```

---

*Skill tuân thủ: Luật BHXH 2024, Luật Thuế TNCN sửa đổi 2012 & các thông tư hướng dẫn, TT 80/2021/TT-BTC, NĐ 74/2024/NĐ-CP*
*Cập nhật: Tháng 8/2026 — Kiểm tra lại khi có thay đổi chính sách mới*
