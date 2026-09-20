---
name: excel-audit-and-repair
description: |
  Kiểm tra, phát hiện và sửa lỗi toàn diện trong file Excel kế toán.
  Sử dụng khi: file Excel chạy chậm, có lỗi #REF!/#VALUE!/#ERROR!, công thức bị gãy
  sau khi thêm/xóa dòng, hoặc file quá nặng do ảnh/dữ liệu dư thừa.
  Nguồn gốc: addyosmani/agent-skills + tùy chỉnh cho bài toán kế toán Nhôm Kính Hoàng Anh.
---

# 🔧 Excel Audit & Repair — Kế Toán Nhôm Kính Hoàng Anh

> Triết lý: **Chẩn đoán trước, sửa sau. Không sửa mù.**
> Nguồn gốc: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — debugging-and-error-recovery (thích nghi cho Excel)

---

## Khi Nào Kích Hoạt?

- ✅ File Excel > 5MB và mở chậm
- ✅ Xuất hiện lỗi `#REF!`, `#VALUE!`, `#NAME?`, `#ERROR!` trong bất kỳ sheet nào
- ✅ Công thức liên kết giữa sheet bị sai sau khi thêm/xóa nhân viên
- ✅ Sheet `total` / `DANHSACH` / monthly sheets không khớp số liệu với nhau
- ✅ Hình ảnh CCCD được nhúng trực tiếp làm phình file

---

## QUY TRÌNH 4 BƯỚC (DỪNG — ĐO — SỬA — XÁC NHẬN)

### 🔴 Bước 1: DỪNG — Không sửa ngay

Khi phát hiện lỗi, KHÔNG sửa ngay. Trước tiên:
1. Ghi lại ô bị lỗi, tên sheet, nội dung công thức bị lỗi
2. Xác định phạm vi ảnh hưởng: lỗi này lan ra bao nhiêu ô/sheet?
3. Kiểm tra: lỗi xuất hiện sau thao tác nào? (thêm dòng, đổi tên sheet, xóa nhân viên?)

### 🟡 Bước 2: ĐO — Phân loại lỗi

```
PHÂN LOẠI LỖI EXCEL:

🔴 #REF! — Tham chiếu ô bị gãy
   Nguyên nhân phổ biến: Công thức trỏ thẳng vào số dòng cố định (VD: 'T1'!S9)
                         khi sắp xếp lại nhân viên thì sai hoàn toàn
   Fix: Dùng XLOOKUP/SUMIFS tìm theo Mã NV thay vì theo số dòng

🟠 #VALUE! — Sai kiểu dữ liệu
   Nguyên nhân phổ biến: Ô chứa chữ nhưng công thức cộng số (SUM cộng ô text)
   Fix: Chuẩn hóa kiểu dữ liệu, dùng IFERROR hoặc VALUE()

🟡 File quá nặng (>5MB)
   Nguyên nhân phổ biến: Ảnh CCCD nhúng trực tiếp, hàng nghìn row trống có format
   Fix: Xóa ảnh, dọn dẹp row format dư thừa

🟢 Số liệu không khớp giữa sheets
   Nguyên nhân phổ biến: Cập nhật thủ công không đồng bộ
   Fix: Tạo single source of truth — DANH_SACH_MASTER, dùng XLOOKUP
```

### 🟠 Bước 3: SỬA — Theo Thứ Tự Ưu Tiên

**Ưu tiên 1: Sửa công thức động thay thế tham chiếu cứng**

Thay thế pattern nguy hiểm:
```
❌ CŨ (Dễ gãy):
='T1'!S9 + 'T2'!T10 + 'T3'!U11

✅ MỚI (Bền vững):
=SUMPRODUCT((DANHSACH!A:A=[@MaNV])*(T1!$A$8:$A$100=[@MaNV])*T1!$S$8:$S$100)
hoặc
=XLOOKUP([@MaNV], T1!$A:$A, T1!$S:$S, 0)
```

**Ưu tiên 2: Tách ảnh CCCD ra khỏi workbook**

- Xuất ảnh ra thư mục `CCCD_Images/`
- Trong file Excel: thay bằng đường link text hoặc hyperlink
- Kết quả: file từ 34MB → <2MB

**Ưu tiên 3: Xóa row format dư thừa**

```
Kiểm tra: Ctrl+End → xem last used cell có đúng không?
Nếu last row là 1000 mà chỉ có 20 nhân viên → 980 row format dư thừa
Fix: Select row 21 → Ctrl+Shift+End → Delete → Clear All
```

### 🟢 Bước 4: XÁC NHẬN — Kiểm Tra Sau Khi Sửa

- [ ] Tất cả ô lỗi `#REF!`, `#VALUE!` đã biến mất
- [ ] Tổng lương sheet `total` khớp với tổng từng tháng (T1+T2+...+Tn)
- [ ] Thêm 1 nhân viên mới → các sheet tự động cập nhật (không cần sửa tay)
- [ ] Xóa 1 nhân viên → không sinh thêm `#REF!` mới
- [ ] Dung lượng file đã giảm xuống < 3MB
- [ ] File mở trong < 5 giây

---

## Checklist Kiểm Toán File Excel Kế Toán

Chạy checklist này TRƯỚC KHI nộp báo cáo thuế hoặc chia sẻ file:

```
KIỂM TRA CẤU TRÚC:
- [ ] Có sheet DANH_SACH_MASTER chứa toàn bộ thông tin nhân viên không?
- [ ] Các sheet tháng (T1-T12) chỉ nhập số liệu, không nhập lại họ tên/CCCD/MST?
- [ ] Sheet total dùng XLOOKUP/SUMIFS thay vì trỏ cứng vào dòng?

KIỂM TRA SỐ LIỆU:
- [ ] Tổng lương 12 tháng = Tổng sheet total?
- [ ] Số BHXH phải nộp = Tổng lương đóng BH × 21.5% (doanh nghiệp) + 10.5% (NLĐ)?
- [ ] Thuế TNCN khớp với biểu lũy tiến hoặc 10% khoán?
- [ ] UNC ngân hàng đã đối chiếu khớp với số tiền thực lĩnh?

KIỂM TRA TUÂN THỦ PHÁP LUẬT:
- [ ] Bảng lương có đúng Mẫu 02-LĐTL (TT 200/2014/TT-BTC)?
- [ ] Lao động khoán đã khấu trừ 10% thuế TNCN?
- [ ] Lao động dưới 1 tháng không bị cộng nhầm vào BHXH?
```

---

## Lỗi Phổ Biến Đã Ghi Nhận (Error Log)

| Lỗi | Nguyên Nhân | Cách Sửa Đã Kiểm Chứng |
|---|---|---|
| `#REF!` ở sheet `total` cột Q | Công thức `=REF!-L8-M8...` trỏ cứng vào số dòng | Thay bằng XLOOKUP theo Mã NV |
| `#ERROR!` ở cột V sheet `total` | Công thức `='T1'!#REF!` — sheet T1 đã đổi cấu trúc | Tái tạo công thức SUMPRODUCT |
| File 34MB | 52 ảnh CCCD nhúng trực tiếp | Xuất ảnh ra thư mục riêng |
| Sheet T7/T8 sai ngày (hiện số 46204) | Ô date lưu dưới dạng số serial | Format ô thành Date dd/mm/yyyy |

---

*Skill được thiết kế cho: 2026. Tiềnluong-OKAY.xlsx & Lương,MrPhu.xlsx — Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH*
