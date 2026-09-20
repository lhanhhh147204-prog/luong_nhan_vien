---
name: bo_nao_AI
description: |
  Bộ Não AI — Hệ thống điều phối skills toàn diện cho bài toán kế toán tiền lương
  Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH. Tổng hợp 15 skills từ nhiều nguồn uy tín
  (addyosmani/agent-skills, github/spec-kit, VoltAgent, heilcheng, OpenAccountants).
  Kích hoạt ngay khi bắt đầu bất kỳ phiên làm việc nào với hệ thống lương.
  ⚠️  MỌI CÂU HỎI BẮT BUỘC ĐI QUA: WORKFLOW.md trước khi trả lời.
---

> ## ⚠️ ĐIỂM VÀO BẮT BUỘC
> **Trước khi làm BẤT CỨ điều gì, đọc và thực thi [`WORKFLOW.md`](./WORKFLOW.md)**
> Workflow gồm 9 trạm kiểm tra — không được bỏ qua trạm nào.

# 🧠 BỘ NÃO AI — Hệ Thống Skills Kế Toán Hoàn Chỉnh

> Bộ tổng hợp và điều phối toàn bộ skills cho bài toán:
> **Quản lý & Tự động hóa Tiền Lương — Công Ty TNHH XD SX NHÔM KÍNH HOÀNG ANH**

---

## 📚 BẢNG KIỂM KÊ TOÀN BỘ SKILLS

### 🔴 NHÓM A: Skills Nền Tảng (Từ Kho Cũ — Đã Có Sẵn)

| Skill | Nguồn Gốc | Ứng Dụng Trong Bài Toán Kế Toán |
|---|---|---|
| `spec-kit` | [github/spec-kit](https://github.com/github/spec-kit) ⭐⭐⭐⭐⭐ | Lập kế hoạch trước khi sửa bảng lương lớn; ngăn vibe-coding |
| `grill-me-planning` | addyosmani/agent-skills | Hỏi rõ yêu cầu trước khi sửa công thức (tránh sửa sai) |
| `incremental-implementation` | addyosmani/agent-skills ⭐⭐⭐⭐ | Sửa từng phần nhỏ Excel, test từng bước |
| `debugging-and-error-recovery` | addyosmani/agent-skills ⭐⭐⭐⭐⭐ | Debug lỗi `#REF!` / `#VALUE!` / số lệch |
| `memory_manager` | Custom | Ghi nhớ quy tắc kế toán đặc thù của công ty |
| `agent-style-output` | Custom | Trả lời ngắn gọn, không thừa — style kế toán |
| `code-review-and-quality` | addyosmani/agent-skills | Review công thức Excel trước khi áp dụng |
| `session-startup` | Custom | Khởi động phiên làm việc |
| `performance-optimization` | addyosmani/agent-skills | Tối ưu file Excel nặng (34MB → <2MB) |
| `addyosmani-agent-skills` | addyosmani/agent-skills ⭐⭐⭐⭐⭐ | Index 24 engineering skills cấp production |

### 🔵 NHÓM B: Skills Mới — Chuyên Biệt Kế Toán (Vừa Tạo)

| Skill | Nguồn Gốc & Xếp Hạng | Ứng Dụng Cụ Thể |
|---|---|---|
| `excel-audit-and-repair` | addyosmani debugging + custom ⭐⭐⭐⭐⭐ | Phát hiện & sửa toàn bộ lỗi trong 2 file Excel |
| `payroll-automation` | VoltAgent awesome-agent-skills ⭐⭐⭐⭐⭐ | Tự động tính lương hàng tháng (BHXH, TNCN) |
| `financial-reporting` | anthropics/financial-services ⭐⭐⭐⭐ | Xuất báo cáo nội bộ + báo cáo thuế |
| `data-reconciliation` | heilcheng/awesome-agent-skills ⭐⭐⭐⭐⭐ | Đối chiếu UNC ngân hàng ↔ bảng lương |
| `tax-compliance-vn` | OpenAccountants + luật VN ⭐⭐⭐⭐⭐ | Tuân thủ BHXH, Thuế TNCN 2024 |

**Tổng cộng: 15 Skills sẵn sàng**

---

## 🗺️ SƠ ĐỒ QUYẾT ĐỊNH — DÙNG SKILL NÀO?

```
Yêu cầu đến
│
├── 📋 CHƯA RÕ / YÊU CẦU LỚN?
│   └──→ grill-me-planning → spec-kit → incremental-implementation
│
├── 🔧 VẤN ĐỀ EXCEL (File lỗi, nặng, công thức sai)?
│   └──→ excel-audit-and-repair
│       ├── Lỗi #REF!/#VALUE!     → phần "Phân loại lỗi"
│       ├── File >5MB              → phần "Dọn dẹp dung lượng"
│       └── Số liệu không khớp     → chuyển sang data-reconciliation
│
├── 💰 TÍNH LƯƠNG THÁNG MỚI?
│   └──→ payroll-automation
│       ├── Nhân viên HĐLĐ         → phần "Lao động chính thức"
│       ├── Nhân công khoán        → phần "Khoán < 1 tháng"
│       └── Đội khoán thi công     → phần "Đội khoán HĐ"
│
├── 🔄 ĐỐI CHIẾU UNC NGÂN HÀNG ↔ BẢNG LƯƠNG?
│   └──→ data-reconciliation
│       ├── Nhân viên báo thiếu    → phần "Phân tích chênh lệch"
│       └── Quyết toán cuối kỳ    → phần "Kiểm tra tam giác"
│
├── 📊 CẦN BÁO CÁO (BGĐ / Thuế / BHXH)?
│   └──→ financial-reporting
│       ├── Báo cáo nội bộ BGĐ    → Nhóm 1: Dashboard
│       ├── Tờ khai thuế TNCN     → Nhóm 2: Mẫu 05/KK-TNCN
│       └── Báo cáo BHXH          → Nhóm 3: D02-TS
│
├── ⚖️ KIỂM TRA TUÂN THỦ PHÁP LUẬT?
│   └──→ tax-compliance-vn
│       ├── Thuế TNCN đúng chưa?  → phần "Biểu thuế lũy tiến"
│       ├── BHXH có sai không?    → phần "Quy tắc BHXH"
│       └── Lập tờ khai thuế      → Checklist quý/năm
│
├── 🐛 GẶP LỖI / CRASH / BUG?
│   └──→ debugging-and-error-recovery
│
└── 📝 GHI LẠI QUY TẮC MỚI VỪA PHÁT HIỆN?
    └──→ memory_manager → lưu vào .agents/memory/
```

---

## 🔗 FLOW CÔNG VIỆC THÁNG (Monthly Workflow)

```
NGÀY 1-5 THÁNG:
  payroll-automation (Thu thập số liệu đầu vào)
       ↓
NGÀY 5-10:
  payroll-automation (Tính lương, BHXH, TNCN)
  + excel-audit-and-repair (Kiểm tra công thức)
       ↓
NGÀY 10-15:
  data-reconciliation (Đối chiếu với UNC đã chi)
       ↓
NGÀY 15-20:
  financial-reporting (Xuất báo cáo + tờ khai thuế)
  + tax-compliance-vn (Kiểm tra tuân thủ trước khi nộp)
       ↓
CUỐI THÁNG:
  memory_manager (Ghi lại bài học, cập nhật quy tắc)
```

---

## 📁 CẤU TRÚC FILE DỰ ÁN (Chuẩn Hóa)

```
c:\Users\lehoa\tien_luong\
├── 2026. Tiềnluong-OKAY.xlsx        ← File chính (cần tái cơ cấu)
├── Lương,MrPhu.xlsx                 ← File theo dõi thực tế + công nợ
├── CCCD_Images\                     ← Thư mục ảnh CCCD (tách khỏi Excel)
│   ├── CHINH_THUC\                  ← Nhân viên ký HĐ chính thức
│   └── KHOAN\                       ← Nhân công khoán / đội thầu
├── BaoCao_Thue\                     ← Tờ khai, bảng kê nộp thuế
│   ├── 2026_Q1_05-KK-TNCN.xlsx
│   └── ...
├── UNC_NganHang\                    ← Sao kê ngân hàng xuất CSV
│   ├── SaoKe_T01_2026.csv
│   └── ...
└── .agents\                         ← Hệ thống Skills AI
    └── skills\
        └── bo_nao_AI\               ← File này (hub điều phối)
```

---

## 📌 QUY TẮC BẤT BIẾN (Không Bao Giờ Vi Phạm)

```
1. KHÔNG sửa công thức trong bảng lương khi chưa backup file
2. KHÔNG xóa dòng nhân viên cũ — chuyển sang NGHI_VIEC
3. KHÔNG hard-code mức thuế/BH vào ô — phải dùng sheet THAM_SO
4. KHÔNG chuyển khoản mà không có bảng lương đối chiếu
5. KHÔNG bỏ qua lỗi #REF! dù "nhỏ" — mọi ô lỗi đều phải sửa
6. LUÔN backup trước khi thay đổi cấu trúc file
7. LUÔN kiểm tra tổng sau khi thêm/xóa nhân viên
```

---

## 🔍 TÀI LIỆU THAM KHẢO (Nguồn Skills)

| Nguồn | Stars | Lý Do Chọn |
|---|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | ⭐⭐⭐⭐⭐ | Production-grade, từ Google DevRel, framework debugging rõ ràng |
| [github/spec-kit](https://github.com/github/spec-kit) | ⭐⭐⭐⭐⭐ | Spec-first methodology, ngăn vibe-coding hiệu quả |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | ⭐⭐⭐⭐ | 1000+ skills, có payroll/business workflow chuyên biệt |
| [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | ⭐⭐⭐⭐ | Phân loại theo domain, có finance/reconciliation pattern |
| [OpenAccountants/openaccountants](https://github.com/openaccountants/openaccountants) | ⭐⭐⭐⭐ | MCP-ready, tax guides cho AI agent, 190+ jurisdictions |

---

*Bộ Não AI — Phiên bản 1.0 | Tạo: 2026-08-27 | Dự án: Kế Toán Nhôm Kính Hoàng Anh*
*Cập nhật định kỳ mỗi khi có thay đổi luật thuế hoặc quy trình nội bộ mới*
