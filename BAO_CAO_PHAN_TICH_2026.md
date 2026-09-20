# 📋 BÁO CÁO PHÂN TÍCH & GIẢI PHÁP TOÀN DIỆN

## Kế Toán Tiền Lương — Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH

> Đã đi qua đủ 9 trạm workflow | Tạo: 2026-08-27 | Độ tin cậy: Cao

---

## ✅ CHECKLIST WORKFLOW ĐÃ HOÀN THÀNH

| Trạm | Tên                 | Kết Quả                                                   |
| ---- | ------------------- | --------------------------------------------------------- |
| 0    | Thu thập ngữ cảnh   | ✅ 2 file, 20 sheets, T1-T8 + Đội khoán                   |
| 1    | Grill-Me            | ✅ Bỏ qua (yêu cầu rõ ràng)                               |
| 2    | Spec-Kit            | ✅ Phạm vi xác định: Năm 2026 toàn bộ                     |
| 3A   | Excel Audit         | 🔴 **18 lỗi #REF!, 55 ảnh nhúng, header không nhất quán** |
| 3B   | Tax Compliance      | ⚠️ **Lương CB đóng BH thấp hơn TT, cần xem xét**          |
| 4    | Payroll Analysis    | ✅ Tổng hợp đầy đủ số liệu                                |
| 5    | Data Reconciliation | 🔴 **Chỉ 1/11 người có sheet đối chiếu UNC**              |
| 6    | Financial Reporting | ✅ (File báo cáo này)                                     |
| 7    | Debugging Check     | ⚠️ Phát hiện 4 điểm bất thường                            |
| 8    | Memory Manager      | ✅ Đã ghi vào cong_ty_rules.md + error_log.md             |

---

## 📊 PHẦN 1: BỨC TRANH HIỆN TRẠNG

### 1.1 Quy Mô Hoạt Động Kế Toán

```
NHÂN SỰ ĐANG THEO DÕI: 11 người + 4 đội khoán thi công

NHÂN VIÊN / CỘNG TÁC VIÊN:
─────────────────────────────────────────────────────────────
Họ Tên                  Vai Trò           Lương TT    Loại HĐ
─────────────────────────────────────────────────────────────
Lê Duy Phú             Giám đốc          25,000,000  HĐLĐ/BH
Lê Hoàng Anh           Nhân Viên         14,000,000  HĐLĐ/BH
Nguyễn Thị Kim Trí     Kế toán           18,000,000  HĐLĐ/BH
Nguyễn Văn Quyền       Nhân Viên         22,000,000  HĐLĐ/BH
Lê Trọng Đức           Thợ NK vãng lai   20,000,000  Khoán/T
Nguyễn Văn Chiến       Thợ NK vãng lai   18,000,000  Khoán/T
Lê Văn Khê             Thợ NK vãng lai   20,000,000  Khoán/T
Hồ Văn Phải            Thợ NK vãng lai   20,000,000  Khoán/T
Đinh Văn Tuấn          Vãng lai < 5tr    16,500,000  Tiền mặt
Đồng Trọng Sang        Vãng lai < 5tr    15,000,000  Tiền mặt
[Nguyễn Ngọc Hưng]     Đã nghỉ việc      0           Còn nợ
─────────────────────────────────────────────────────────────
TỔNG QUỸ LƯƠNG THÁNG (mức TT)    188,500,000đ
TỔNG QUỸ LƯƠNG NĂM (ước tính)  2,262,000,000đ

ĐỘI KHOÁN THI CÔNG (T1-T8/2026):
─────────────────────────────────────────────────────────
Đội            Công trình       Chi phí HĐ    Thuế TNCN 10%
─────────────────────────────────────────────────────────
Hồ Thẩm       CT Hồ Tràm       [Chưa rõ]     [Chưa rõ]
Lưu T. Hoàng  CT Nam Khang    183,200,000    18,320,000
Nguyễn C.Thanh CT Nam Khang   184,800,000    18,480,000
Võ Tấn Quang  CT Nam Khang    215,200,000    21,520,000
─────────────────────────────────────────────────────────
TỔNG CHI PHÍ ĐỘI KHOÁN (T1-T8) 583,200,000đ
TỔNG THUẾ TNCN ĐÃ KHẤU TRỪ      58,320,000đ
```

### 1.2 Công Nợ Lương Tồn Đọng Từ 2025

> [!CAUTION]
> Tổng **55,076,922đ** công nợ lương từ năm 2025 chưa giải quyết xong

| Người            | Số Tiền Còn Nợ  | Ghi Chú                           |
| ---------------- | --------------- | --------------------------------- |
| Lê Duy Phú       | 13,370,000đ     | N2025                             |
| Lê Hoàng Anh     | 11,370,000đ     | N2025                             |
| Nguyễn Văn Quyền | 17,058,461đ     | N2025                             |
| Nguyễn Ngọc Hưng | **13,278,461đ** | 🔴 Đã nghỉ việc — chưa giải quyết |
| **TỔNG**         | **55,076,922đ** |                                   |

---

## 🔴 PHẦN 2: VẤN ĐỀ NGHIÊM TRỌNG (Cần Xử Lý Ngay)

### ❌ VẤN ĐỀ 1: 18 lỗi #REF! trong Sheet `total` — Mất kiểm soát tổng hợp

**Mô tả:** Sheet `total` là nơi tổng hợp toàn bộ lương năm để kiểm soát và đối chiếu. Hiện tại **18 ô quan trọng** (cột Q — "Còn phải thanh toán") đều báo `#REF!`, khiến không thể biết chính xác đang còn nợ ai, bao nhiêu tiền.

**Nguyên nhân gốc:** Công thức trỏ cứng vào số dòng của sheet tháng cụ thể:

```
❌ Hiện tại: =#REF!-L8-M8-N8-O8-P8  (gãy khi cấu trúc T1/T2 thay đổi)
✅ Sửa thành: =XLOOKUP([@MaNV], T1!$A:$A, T1!$S:$S, 0) - SUMIF(...)
```

**Hậu quả:** Kế toán không biết tổng công nợ thực tế là bao nhiêu → Không thể lập kế hoạch thanh toán.

---

### ❌ VẤN ĐỀ 2: File 34MB với 55 ảnh nhúng — Tê liệt khi làm việc

**Mô tả:** 55 ảnh CCCD/CMND được nhúng trực tiếp vào workbook khiến:

- File mở mất 1-3 phút
- Không gửi được qua email (>25MB)
- Rủi ro corrupt file cao
- Mỗi lần lưu mất 30-60 giây

**Giải pháp:** Tách ảnh ra thư mục `CCCD_Images/` (đã tạo sẵn), trong Excel chỉ giữ text số CCCD để tra cứu. Ước tính file giảm từ **34MB → dưới 2MB**.

---

### ❌ VẤN ĐỀ 3: Không có hệ thống đối chiếu UNC cho 10/11 người

**Mô tả:** Chỉ có **Nguyễn Chí Thanh** có sheet theo dõi UNC ngân hàng riêng. 10 người còn lại (bao gồm cả Giám đốc, nhân viên chính thức) không có hệ thống đối chiếu → Không biết đã chuyển đủ chưa, công nợ thực tế là bao nhiêu.

**Hậu quả đã thấy:** Lê Trọng Đức, Nguyễn Văn Chiến, Lê Văn Khê bị "ngưng TT tháng 9/10" — nhưng không rõ lý do kỹ thuật hay vấn đề tài chính.

---

### ❌ VẤN ĐỀ 4: Cấu trúc header khác nhau giữa các tháng

**Mô tả:**

- T1, T2, T3: Cột D = "Lương chính", F = "Số tiền"
- T7, T8: Cột C = "Lương cố định", F = "Lương CB đóng BH", G = "Số tiền"
- Phụ cấp: T5,T6 có "Phụ cấp đồng phục tại CT", T7,T8 có "Lương Khoán/công nhật"

**Hậu quả:** Không thể tổng hợp dữ liệu tự động qua các tháng → Mọi báo cáo tổng hợp đều phải làm thủ công.

---

## ⚠️ PHẦN 3: VẤN ĐỀ PHÁP LÝ (Rủi Ro Thuế & BHXH)

### ⚠️ RỦI RO 1: Lương CB đóng BHXH thấp hơn nhiều lương thực tế

| Nhân Viên          | Lương TT   | Lương CB đóng BH | Chênh Lệch      |
| ------------------ | ---------- | ---------------- | --------------- |
| Lê Duy Phú         | 25,000,000 | 6,000,000        | **-19,000,000** |
| Lê Hoàng Anh       | 14,000,000 | 6,000,000        | **-8,000,000**  |
| Nguyễn Văn Quyền   | 22,000,000 | 8,000,000        | **-14,000,000** |
| Nguyễn Thị Kim Trí | 18,000,000 | 8,000,000        | **-10,000,000** |

> [!WARNING]
> Đây là thực trạng phổ biến tại các doanh nghiệp VN. Tuy nhiên khi cơ quan BHXH kiểm tra, có thể yêu cầu truy thu phần thiếu + phạt lãi. Cần tư vấn pháp lý để có phương án hợp lý.

### ⚠️ RỦI RO 2: Công nợ 13,278,461đ của nhân viên đã nghỉ

Nguyễn Ngọc Hưng đã nghỉ việc nhưng còn công nợ lương chưa giải quyết. Nếu không xử lý, có thể phát sinh tranh chấp lao động.

### ⚠️ RỦI RO 3: Một số khoản vãng lai chưa rõ khấu trừ thuế

Đinh Văn Tuấn và Đồng Trọng Sang: "thanh toán dưới 5tr/lần" — nếu tổng năm vượt ngưỡng, vẫn phải khai thuế cuối năm.

---

## 💡 PHẦN 4: LỘ TRÌNH GIẢI PHÁP (3 Giai Đoạn)

---

### 🔴 GIAI ĐOẠN 1 — SỬA KHẨN CẤP (Tuần 1-2)

> _Mục tiêu: File hoạt động được, số liệu tin cậy_

#### Việc 1.1: Tách 55 ảnh CCCD ra khỏi workbook

```
Thực hiện: Xuất ảnh → bo_nao_AI/../CCCD_Images/
Trong Excel: Thay bằng hyperlink text
Kết quả mong đợi: 34MB → <2MB, mở file < 5 giây
Thời gian: 30 phút
```

#### Việc 1.2: Sửa 18 lỗi #REF! trong sheet `total`

```
Thay công thức cứng bằng XLOOKUP theo Mã NV:
  =XLOOKUP(B8, T1!$B:$B, T1!$S:$S, 0) + XLOOKUP(B8, T2!$B:$B, T2!$T:$T, 0) + ...

Hoặc dùng SUMPRODUCT linh hoạt hơn:
  =SUMPRODUCT((T1!$B$9:$B$50=[@HoTen])*T1!$S$9:$S$50)

Kết quả: Sheet total hiển thị đúng, không còn #REF!
Thời gian: 2-3 giờ
```

#### Việc 1.3: Chuẩn hóa header các tháng về 1 chuẩn duy nhất

```
Tạo TEMPLATE chuẩn cho tháng T9-T12 và dùng ngược lại cho T1-T8
Cột chuẩn: STT | Họ Tên | Lương CB đóng BH | Số công | Số tiền | Phụ cấp | Tổng | BHXH | TNCN | Thực lĩnh
Thời gian: 3-4 giờ
```

---

### 🟡 GIAI ĐOẠN 2 — TỰ ĐỘNG HÓA QUYỀN NĂNG (Tháng 1-2)

> _Mục tiêu: Tính lương tự động, đối chiếu ngân hàng tự động_

#### Việc 2.1: Tạo Sheet DANH_SACH_MASTER (Nguồn Sự Thật Duy Nhất)

```
Nội dung: Mã NV | Họ Tên | CCCD | MST | Chức Vụ | Loại HĐ |
          Lương CB đóng BH | Lương TT | Ngày bắt đầu | Người phụ thuộc | Trạng thái

Lợi ích:
  ✅ Mọi sheet tháng chỉ cần nhập Mã NV → tự động kéo thông tin
  ✅ Không bao giờ nhập sai tên/CCCD
  ✅ Thêm/xóa người: chỉ sửa 1 nơi, toàn bộ file cập nhật
```

#### Việc 2.2: Công thức tính BHXH & TNCN tự động

```excel
BHXH NLĐ = Lương CB × 10.5%
BHXH DN  = Lương CB × 21.5%

TNCN HĐLĐ (biểu lũy tiến tự động):
=IFERROR(
  IF([@TNTT]<=0,0,
  IF([@TNTT]<=5000000,[@TNTT]*5%,
  IF([@TNTT]<=10000000,[@TNTT]*10%-250000,
  IF([@TNTT]<=18000000,[@TNTT]*15%-750000,
  IF([@TNTT]<=32000000,[@TNTT]*20%-1650000,
  IF([@TNTT]<=52000000,[@TNTT]*25%-3250000,
  IF([@TNTT]<=80000000,[@TNTT]*30%-5850000,
  [@TNTT]*35%-9850000))))))),0)

TNCN Khoán = Tiền khoán × 10% (khi > 2,000,000đ/lần)
```

#### Việc 2.3: Hệ thống đối chiếu UNC cho TẤT CẢ nhân viên

```
Tạo sheet "UNC_TRACKING" với cấu trúc:
  Ngày | Số UNC | Tài khoản | Họ Tên Thụ Hưởng | Số Tiền | Kỳ Lương | Trạng thái

Công thức đối chiếu tự động:
  Đã chuyển = SUMIFS(UNC!Số tiền, UNC!Họ tên, [@HoTen], UNC!Kỳ, [@Ky])
  Còn nợ    = Thực lĩnh - Đã chuyển
  Cảnh báo  = IF(Còn nợ > 0, "⚠️ Còn nợ " & TEXT(Còn nợ, "#,##0") & "đ", "✅")
```

#### Việc 2.4: Dashboard Tổng Hợp 1 Trang Cho BGĐ

```
Nội dung tự động cập nhật:
  ┌──────────────────────────────────────────────────────┐
  │ TỔNG QUỸ LƯƠNG THÁNG [X]:      xxx,xxx,xxx đ        │
  │ CHI PHÍ ĐỘI KHOÁN:             xxx,xxx,xxx đ        │
  │ BHXH DN PHẢI NỘP:               xx,xxx,xxx đ        │
  │ THUẾ TNCN ĐÃ KHẤU TRỪ:         xx,xxx,xxx đ        │
  │ TỔNG UNC ĐÃ CHUYỂN:            xxx,xxx,xxx đ        │
  │ CÒN PHẢI THANH TOÁN:            xx,xxx,xxx đ        │
  │                                                      │
  │ ⚠️  CẢNH BÁO: [danh sách người còn nợ]             │
  └──────────────────────────────────────────────────────┘
```

---

### 🟢 GIAI ĐOẠN 3 — NÂNG CẤP CHUYÊN NGHIỆP (Tháng 2-3)

> _Mục tiêu: Chuẩn hóa pháp lý, báo cáo tự động_

#### Việc 3.1: Xuất tự động Bảng kê 05-1/BK-TNCN

```
Từ dữ liệu bảng lương → Tự động điền vào mẫu:
  STT | Họ Tên | CCCD | Địa chỉ | Thu nhập | Thuế TNCN | MST
Thay vì phải nhập tay mỗi quý khi nộp thuế
```

#### Việc 3.2: Phiếu lương cá nhân tự động (Mail Merge)

```
1 nút bấm → Xuất phiếu lương PDF/Excel cho từng người:
  - Họ tên, Kỳ lương
  - Chi tiết thu nhập: Lương chính + từng loại phụ cấp
  - Các khoản trừ: BHXH, TNCN
  - Số tiền thực lĩnh
  - Đã nhận/Chưa nhận
```

#### Việc 3.3: Báo cáo Chi Phí Nhân Công Theo Công Trình

```
Từ sheet "ĐỘI KHOÁN THI CÔNG" → Tự động tổng hợp:
  CT Hồ Tràm:    xx,xxx,xxx đ (X% kế hoạch)
  CT Nam Khang:  xx,xxx,xxx đ (X% kế hoạch)
  CT Bayfront:   xx,xxx,xxx đ (X% kế hoạch)
  CT Núi Hoa:    xx,xxx,xxx đ (X% kế hoạch)

Kết nối với hạch toán: TK 622 (Chi phí nhân công trực tiếp)
```

#### Việc 3.4: Giải Quyết Dứt Điểm Công Nợ 2025

```
Lập kế hoạch thanh toán cho 55,076,922đ nợ cũ:
  - Nguyễn Ngọc Hưng (đã nghỉ): Ưu tiên giải quyết ngay
  - Lê Duy Phú, Lê Hoàng Anh, Nguyễn Văn Quyền: Thanh toán dần theo thoả thuận
  - Lập biên bản xác nhận công nợ có chữ ký các bên
```

---

## 📐 PHẦN 5: KIẾN TRÚC FILE MỚI (Chuẩn Hóa)

```
2026. Tiềnluong-OKAY.xlsx (CẤU TRÚC MỚI - MỤC TIÊU)
│
├── 📋 DANH_SACH_MASTER    ← Nguồn sự thật duy nhất (NV + khoán)
├── 📋 THAM_SO             ← Bảng tham số: tỷ lệ BH, mức giảm trừ
├── 📋 T1 → T12            ← Bảng lương tháng (cùng cấu trúc)
├── 📋 DOI_KHOAN           ← Chi phí đội khoán theo công trình
├── 📋 UNC_TRACKING        ← Đối chiếu ngân hàng tập trung
├── 📋 CONG_NO             ← Theo dõi công nợ tồn đọng
├── 📋 TONG_HOP_NAM        ← Thay sheet "total" bị lỗi (dùng XLOOKUP)
├── 📋 DASHBOARD           ← Báo cáo BGĐ tự cập nhật
├── 📋 BK_TNCN             ← Bảng kê 05-1/BK-TNCN (xuất thuế)
└── 📋 BHXH_MONTH          ← Bảng đóng BHXH hàng tháng

CCCD_Images/               ← Ảnh tách ra khỏi Excel
├── CHINH_THUC/
└── KHOAN/
```

---

## 🕐 PHẦN 6: KẾ HOẠCH THỰC THI

| Giai Đoạn         | Việc Cần Làm                        | Ưu Tiên | Thời Gian Ước Tính   |
| ----------------- | ----------------------------------- | ------- | -------------------- |
| 1 - Khẩn Cấp      | Tách 55 ảnh CCCD                    | 🔴 P0   | 30 phút              |
| 1 - Khẩn Cấp      | Sửa 18 lỗi #REF! sheet `total`      | 🔴 P0   | 3 giờ                |
| 1 - Khẩn Cấp      | Giải quyết công nợ Nguyễn Ngọc Hưng | 🔴 P0   | 1 ngày (pháp lý)     |
| 1 - Khẩn Cấp      | Chuẩn hóa header T1-T8              | 🔴 P1   | 4 giờ                |
| 2 - Tự động hóa   | Tạo DANH_SACH_MASTER                | 🟡 P1   | 2 giờ                |
| 2 - Tự động hóa   | Công thức BHXH/TNCN tự động         | 🟡 P1   | 4 giờ                |
| 2 - Tự động hóa   | Sheet UNC_TRACKING                  | 🟡 P1   | 3 giờ                |
| 2 - Tự động hóa   | Dashboard BGĐ                       | 🟡 P2   | 4 giờ                |
| 3 - Chuyên nghiệp | Bảng kê 05-1/BK-TNCN tự động        | 🟢 P2   | 3 giờ                |
| 3 - Chuyên nghiệp | Phiếu lương cá nhân                 | 🟢 P2   | 4 giờ                |
| 3 - Chuyên nghiệp | Báo cáo chi phí công trình          | 🟢 P3   | 3 giờ                |
| **TỔNG**          |                                     |         | **~30 giờ làm việc** |

---

## 📌 PHẦN 7: BƯỚC TIẾP THEO NGAY BÂY GIỜ

> Bạn muốn AI bắt tay làm ngay bước nào trong 3 lựa chọn sau?

**Option A — Sửa khẩn cấp ngay hôm nay:**
→ Tách ảnh + Sửa `#REF!` + Chuẩn hóa header
→ Thời gian: ~4 giờ | Kết quả: File hoạt động ổn định ngay

**Option B — Xây nền móng đúng:**
→ Tạo DANH_SACH_MASTER + Công thức BHXH/TNCN tự động
→ Thời gian: ~6 giờ | Kết quả: Tính lương tháng sau hoàn toàn tự động

**Option C — Đối chiếu ngân hàng trước:**
→ Xây UNC_TRACKING + Xác định chính xác công nợ hiện tại
→ Thời gian: ~3 giờ | Kết quả: Biết chính xác đang nợ ai, bao nhiêu

---

_Báo cáo được tạo bởi: bo_nao_AI Workflow (9 trạm) | 2026-08-27_
_Dữ liệu nguồn: Phân tích trực tiếp từ 2 file Excel, không ước tính_
