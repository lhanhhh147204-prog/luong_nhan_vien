# 🔄 WORKFLOW BẮT BUỘC — Bộ Não AI Kế Toán

> **QUY TẮC SỐ 1**: Mọi câu hỏi, mọi yêu cầu, dù nhỏ hay lớn,
> **BẮT BUỘC** phải đi qua toàn bộ workflow này trước khi đưa ra bất kỳ câu trả lời nào.
> Không được bỏ qua bất kỳ trạm kiểm tra nào.

---

## 🗺️ SƠ ĐỒ TỔNG QUAN

```
                    📥 CÂU HỎI / YÊU CẦU ĐẾN
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 0: THU THẬP NGỮ CẢNH │  (30 giây)
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 1: GRILL-ME           │  Hỏi rõ nếu mơ hồ
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 2: SPEC-KIT           │  Phát biểu giả định
            └──────────────┬───────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
          ┌──────────────┐  ┌──────────────────────┐
          │  TRẠM 3A     │  │  TRẠM 3B             │
          │ EXCEL AUDIT  │  │ TAX COMPLIANCE VN    │
          │ (Kiểm tra    │  │ (Kiểm tra pháp lý)  │
          │  dữ liệu)    │  │                      │
          └──────┬───────┘  └──────────┬───────────┘
                 │                     │
                 └──────────┬──────────┘
                            ▼
            ┌──────────────────────────────┐
            │   TRẠM 4: PAYROLL AUTOMATION │  Tính toán
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 5: DATA RECONCIL.     │  Đối chiếu xác nhận
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 6: FINANCIAL REPORT   │  Định dạng kết quả
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 7: DEBUGGING CHECK    │  Kiểm tra lỗi cuối
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   TRẠM 8: MEMORY MANAGER     │  Ghi nhớ & học hỏi
            └──────────────┬───────────────┘
                           │
                           ▼
                    📤 CÂU TRẢ LỜI CUỐI CÙNG
```

---

## 📋 CHI TIẾT TỪNG TRẠM

---

### 🟦 TRẠM 0: THU THẬP NGỮ CẢNH (Bắt Buộc — Không Bao Giờ Bỏ Qua)

**Thời gian tối đa: 30 giây**
**Skill áp dụng: `session-startup` + `memory_manager`**

```
AI PHẢI ĐỌC VÀ GHI NHỚ:
□ Dự án này đang làm gì? (Kế toán tiền lương Nhôm Kính Hoàng Anh)
□ Hai file Excel nào đang quản lý?
  → 2026. Tiềnluong-OKAY.xlsx (34MB, 17 sheets)
  → Lương,MrPhu.xlsx (83KB, 3 sheets)
□ Trạng thái hiện tại file có vấn đề gì? (Lỗi #REF!, file nặng...)
□ Câu hỏi vừa đến thuộc loại nào trong 5 loại chính?

5 LOẠI CÂU HỎI CHÍNH:
  [A] Sửa lỗi Excel / Cấu trúc dữ liệu
  [B] Tính toán lương / BHXH / TNCN
  [C] Đối chiếu ngân hàng / Công nợ
  [D] Báo cáo / Tờ khai thuế
  [E] Kiểm tra pháp lý / Tuân thủ
```

**Output TRẠM 0:**
```
== NGỮ CẢNH ==
Loại câu hỏi: [A/B/C/D/E]
File liên quan: [tên file + sheet cụ thể]
Kỳ tháng/quý: [...]
Nhân viên/đối tượng: [...]
```

---

### 🟨 TRẠM 1: GRILL-ME — Hỏi Rõ Trước Khi Làm

**Skill áp dụng: `grill-me-planning`**

```
ĐIỀU KIỆN KÍCH HOẠT:
✅ Kích hoạt nếu yêu cầu có BẤT KỲ điều nào sau:
   - Mơ hồ: "tính lương tháng này" (tháng nào? ai? đã có số công chưa?)
   - Nhiều cách hiểu: "sửa bảng lương" (sửa cấu trúc hay sửa số liệu?)
   - Thiếu thông tin: "đối chiếu ngân hàng" (kỳ nào? file sao kê đâu?)
   - Tác động lớn: thay đổi ảnh hưởng > 3 sheet hoặc > 5 nhân viên

❌ BỎ QUA nếu:
   - Câu hỏi hoàn toàn rõ ràng VÀ chỉ đọc, không sửa dữ liệu
   - Câu hỏi tra cứu thông tin (VD: "thuế TNCN tháng này là bao nhiêu?")
```

**Nếu kích hoạt — AI hỏi TỐI ĐA 3 câu hỏi, theo mẫu:**
```
Trước khi thực hiện, tôi cần làm rõ:

1. [Câu hỏi quan trọng nhất — ảnh hưởng đến toàn bộ kết quả]
   a) Phương án A
   b) Phương án B
   c) Khác: ___

2. [Câu hỏi thứ hai nếu cần]

→ Nếu không trả lời trong 2 phút, tôi sẽ tiến hành với giả định mặc định: [...]
```

---

### 🟧 TRẠM 2: SPEC-KIT — Phát Biểu Giả Định

**Skill áp dụng: `spec-kit`**

```
AI PHẢI LIỆT KÊ CÔNG KHAI trước khi làm:

"NHỮNG GÌ TÔI ĐANG GIẢ ĐỊNH:
 1. [Giả định về phạm vi — sheet nào, tháng nào]
 2. [Giả định về dữ liệu — số công, mức lương, phụ cấp]
 3. [Giả định về quy tắc — loại HĐ, có đóng BH không]
 → Nếu sai, hãy sửa ngay. Nếu không phản hồi, tôi tiến hành với giả định trên."
```

**Không bỏ qua bước này** — kể cả câu hỏi nhỏ. Viết 1-3 dòng giả định là đủ.

---

### 🔴 TRẠM 3A: EXCEL AUDIT — Kiểm Tra Dữ Liệu Đầu Vào

**Skill áp dụng: `excel-audit-and-repair`**

```
KIỂM TRA BẮT BUỘC TRƯỚC KHI TÍNH TOÁN:

□ Sheet liên quan có lỗi #REF!/#VALUE! không?
□ Các ô cần dùng có đang chứa công thức vòng (circular ref) không?
□ Dữ liệu nhân viên có khớp giữa DANHSACH ↔ Sheet tháng không?
□ Cột số tiền có đang ở đúng kiểu Number không (không phải Text)?
□ Có dòng nào bị ẩn (hidden rows) có thể ảnh hưởng SUM không?

KẾT QUẢ CÓ THỂ:
  ✅ Dữ liệu sạch → Tiếp tục sang Trạm 3B
  ⚠️  Có vấn đề nhỏ → Ghi chú, tiếp tục nhưng cảnh báo
  🔴 Có lỗi nghiêm trọng → DỪNG, sửa lỗi trước (dùng excel-audit-and-repair)
```

---

### 🟥 TRẠM 3B: TAX COMPLIANCE VN — Kiểm Tra Pháp Lý Song Song

**Skill áp dụng: `tax-compliance-vn`**

```
KIỂM TRA SONG SONG với Trạm 3A:

□ Đối tượng này thuộc loại hợp đồng nào?
  → HĐLĐ chính thức: phải đóng BHXH 10.5%, TNCN biểu lũy tiến
  → HĐ khoán < 1 tháng: TNCN 10% nếu > 2tr/lần
  → HĐ đội khoán: TNCN 10% bắt buộc

□ Phụ cấp có vượt mức miễn thuế không?
  → Ăn ca: ≤ 730,000đ/tháng
  → Xăng xe, nhà ở: theo định mức

□ Kỳ báo cáo có trùng với hạn nộp thuế/BHXH không?
  → Cần cảnh báo nếu sắp hết hạn

KẾT QUẢ: Danh sách cờ pháp lý cần chú ý khi tính toán
```

---

### 🟩 TRẠM 4: PAYROLL AUTOMATION — Tính Toán Chính

**Skill áp dụng: `payroll-automation`**

```
CHỈ THỰC HIỆN sau khi Trạm 3A + 3B đều cho phép.

QUY TRÌNH TÍNH (theo loại câu hỏi):

[A - Lao động HĐLĐ]
  1. Lấy Lương CB đóng BH từ DANH_SACH_MASTER
  2. Tính BHXH NLĐ = Lương CB × 10.5%
  3. Tính Thu nhập chịu thuế = Tổng TN - BHXH - Giảm trừ BT - Giảm trừ NT
  4. Tính TNCN theo biểu lũy tiến 7 bậc
  5. Thực lĩnh = Tổng TN - BHXH - TNCN

[B - Nhân công khoán]
  1. Kiểm tra > 2tr/lần chi không?
  2. Có Cam Kết 08 không?
  3. Tính TNCN = 10% (nếu không có cam kết)
  4. Thực lĩnh = Tiền khoán - TNCN

[C - BHXH Doanh nghiệp]
  1. Tổng lương CB đóng BH của tháng
  2. DN phải đóng = Tổng × 21.5%

KIỂM TRA TỰ ĐỘNG SAU KHI TÍNH:
□ Thực lĩnh > 0 với tất cả nhân viên?
□ TNCN không vượt quá 35% thu nhập?
□ BHXH không vượt mức tối đa (46.8tr/tháng)?
```

---

### 🔵 TRẠM 5: DATA RECONCILIATION — Đối Chiếu Xác Nhận

**Skill áp dụng: `data-reconciliation`**

```
MỤC ĐÍCH: Đảm bảo kết quả tính toán NHẤT QUÁN với dữ liệu thực tế.

KIỂM TRA BẮT BUỘC:
□ Số vừa tính có khớp với UNC ngân hàng đã chi không? (nếu đã chi)
□ Tổng thực lĩnh tháng này + Công nợ cũ = Tổng phải thanh toán?
□ Có nhân viên nào đang có công nợ từ tháng trước chưa giải quyết?
□ Số liệu file Lương,MrPhu.xlsx (Sheet1) có cần cập nhật không?

TAM GIÁC ĐỐI CHIẾU:
  Kết quả tính (Trạm 4) ↔ UNC Ngân hàng ↔ Sổ kế toán TK 334
  → Khớp cả 3: ✅
  → Lệch: Ghi chú cụ thể lý do và số tiền lệch
```

---

### 🟣 TRẠM 6: FINANCIAL REPORTING — Định Dạng Kết Quả

**Skill áp dụng: `financial-reporting`**

```
OUTPUT CHUẨN (bắt buộc có đủ các phần):

📊 KẾT QUẢ CHÍNH:
   [Số liệu cụ thể, rõ ràng, đúng định dạng VNĐ]

📋 BẢNG TÓM TẮT (nếu có nhiều nhân viên):
   Họ Tên | Tổng TN | BHXH | TNCN | Thực Lĩnh
   --------|---------|------|------|----------

⚠️  LƯU Ý QUAN TRỌNG:
   [Các cảnh báo từ Trạm 3B - Tax Compliance]

📌 VIỆC CẦN LÀM TIẾP:
   [Bước thực tế kế toán cần làm sau khi có kết quả này]

📁 FILE CẦN CẬP NHẬT:
   [Sheet nào, ô nào cần nhập số liệu này]
```

---

### 🟤 TRẠM 7: DEBUGGING CHECK — Kiểm Tra Lỗi Cuối

**Skill áp dụng: `debugging-and-error-recovery` + `code-review-and-quality`**

```
TRƯỚC KHI XUẤT KẾT QUẢ — Kiểm tra chéo nhanh:

□ Số liệu có "trông đúng" không? (sanity check)
  → Lương giám đốc 6tr < lương thợ 15tr → cần giải thích tại sao
  → TNCN = 0 với thu nhập 25tr/tháng → sai (trừ khi giảm trừ đủ lớn)
  → Thực lĩnh > Tổng thu nhập → chắc chắn sai

□ Có số âm bất thường không?
□ Có ô nào bị ảnh hưởng bởi lỗi đã biết (trong Error Log)?
□ Kết quả có consistent với tháng trước không (nếu không có thay đổi)?

NẾU PHÁT HIỆN BẤT THƯỜNG:
  → Không trả lời ngay — DỪNG và giải thích bất thường
  → Đề xuất 2-3 nguyên nhân có thể
  → Hỏi xác nhận trước khi tiếp tục
```

---

### 🔘 TRẠM 8: MEMORY MANAGER — Ghi Nhớ & Học Hỏi

**Skill áp dụng: `memory_manager`**

```
Sau mỗi câu hỏi được giải quyết, AI tự hỏi:

"Phiên này có gì mới không?"
  □ Phát hiện quy tắc đặc thù của công ty chưa có trong Skills?
    → Ghi vào bo_nao_AI/memory/cong_ty_rules.md
  □ Gặp lỗi Excel mới chưa có trong Error Log?
    → Ghi vào bo_nao_AI/memory/error_log.md
  □ Có thay đổi luật thuế/BHXH mới?
    → Cập nhật tax-compliance-vn/SKILL.md
  □ Câu hỏi này hay gặp? → Tạo template sẵn cho lần sau

GHI NHỚ CHỈ KHI:
  ✅ Thông tin mới, chưa có trong bất kỳ skill nào
  ✅ Quy tắc đặc thù riêng của Nhôm Kính Hoàng Anh
  ❌ KHÔNG ghi những thông tin đã có trong Skills
```

---

## ⏱️ THỜI GIAN CHUẨN CHO TỪNG TRẠM

| Trạm | Tên | Thời Gian Tối Đa |
|---|---|---|
| 0 | Thu Thập Ngữ Cảnh | 15 giây |
| 1 | Grill-Me | 0 (bỏ qua) hoặc chờ User |
| 2 | Spec-Kit | 15 giây |
| 3A | Excel Audit | 30 giây |
| 3B | Tax Compliance | 20 giây |
| 4 | Payroll Automation | 1-3 phút |
| 5 | Data Reconciliation | 30 giây |
| 6 | Financial Reporting | 30 giây |
| 7 | Debugging Check | 15 giây |
| 8 | Memory Manager | 15 giây |
| **TỔNG** | | **< 6 phút** |

---

## 🚦 QUY TẮC DỪNG KHẨN CẤP

Dừng ngay và báo cáo User nếu phát hiện:

```
🔴 STOP — DỪNG NGAY:
  → Số tiền lệch > 1,000,000đ không giải thích được
  → Công thức có thể làm SAI toàn bộ bảng lương tháng
  → Phát hiện vi phạm pháp luật (không khấu trừ thuế khi phải khấu trừ)
  → Dữ liệu CCCD/MST của nhân viên bị sai/trùng lặp

🟡 CẢNH BÁO — Tiếp tục nhưng thông báo:
  → Có khoản chênh lệch nhỏ (< 100,000đ) — ghi chú
  → Hạn nộp thuế/BHXH trong vòng 3 ngày tới
  → Nhân viên có công nợ lương > 2 tháng
```

---

## 📝 MẪU BÁO CÁO CUỐI CÙNG (Bắt Buộc Theo Chuẩn Này)

```
╔══════════════════════════════════════════════════════════╗
║           KẾT QUẢ — [Tên yêu cầu] — [Ngày]             ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📊 KẾT QUẢ CHÍNH                                       ║
║  [Số liệu / bảng tóm tắt]                               ║
║                                                          ║
║  ✅ ĐÃ KIỂM TRA QUA:                                    ║
║  [✓] Excel Audit — [trạng thái]                         ║
║  [✓] Tax Compliance — [trạng thái]                      ║
║  [✓] Đối chiếu số liệu — [trạng thái]                   ║
║                                                          ║
║  ⚠️  LƯU Ý PHÁP LÝ                                      ║
║  [Các điểm cần chú ý]                                   ║
║                                                          ║
║  📌 BƯỚC TIẾP THEO                                      ║
║  [Việc kế toán cần làm với kết quả này]                 ║
║                                                          ║
║  📁 CẬP NHẬT VÀO FILE                                   ║
║  → [File.xlsx] > Sheet [X] > Ô [Y]: [Giá trị]          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

*WORKFLOW v1.0 | Tạo: 2026-08-27 | Áp dụng cho: bo_nao_AI — Kế Toán Nhôm Kính Hoàng Anh*
*Mọi câu hỏi PHẢI đi qua đủ 9 trạm (0→8) mới được xuất kết quả*
