import json
import os

JSON_PATH = r"c:/Users/lehoa/OneDrive/Documents/BANG_LUONG'/chien_than_AI/migration_data.json"
ARTIFACT_PATH = r"C:/Users/lehoa/.gemini/antigravity-ide/brain/d3eaa032-5dea-48bc-a801-6f2b91a796c8/bao_cao_thong_ke_luong.md"

def generate():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    employees = data['employees']
    months_data = data['data']
    
    # Calculate totals
    totals = {}
    for month, records in months_data.items():
        for name, amount in records.items():
            if name in ["Người lập biểu", "(Ký, họ tên)", "Nguyễn Thanh Hoan"]:
                continue
            if amount == 0:
                continue
                
            if name not in totals:
                totals[name] = {'total': 0, 'months': {}, 'job': employees.get(name, {}).get('job', '')}
            totals[name]['total'] += amount
            totals[name]['months'][month] = amount
            
    # Generate Markdown
    md = "# 📊 Báo Cáo Tổng Hợp Lương & Tư Vấn Cân Đối Thuế (T1 - T8/2026)\n\n"
    md += "Báo cáo này cung cấp cái nhìn tổng quan về quỹ lương đã chi trả, giúp **Kế toán** cân đối dòng tiền và **Giám đốc** có phương án tối ưu thuế Thu nhập cá nhân (TNCN) & Thuế Thu nhập doanh nghiệp (TNDN).\n\n"
    
    md += "## 1. Bảng Tổng Hợp Chi Trả Lương (VNĐ)\n\n"
    md += "| STT | Họ Tên | Chức Vụ | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | **TỔNG CỘNG** |\n"
    md += "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    
    sorted_emps = sorted(totals.items(), key=lambda x: x[1]['total'], reverse=True)
    
    grand_total = 0
    high_income_emps = []
    
    for idx, (name, info) in enumerate(sorted_emps, 1):
        job = info['job']
        row = f"| {idx} | **{name}** | {job} "
        
        # Check if average income is high (> 11 triệu/tháng)
        months_worked = len(info['months'])
        avg_income = info['total'] / months_worked if months_worked > 0 else 0
        if avg_income > 11000000:
            high_income_emps.append((name, job, avg_income, info['total']))
            
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']:
            val = info['months'].get(m, 0)
            if val > 0:
                row += f"| {val:,.0f} "
            else:
                row += "| - "
        row += f"| **{info['total']:,.0f}** |\n"
        md += row
        grand_total += info['total']
        
    md += f"| | **TỔNG QUỸ LƯƠNG** | | | | | | | | | | **{grand_total:,.0f}** |\n\n"
    
    md += "## 2. Phân Tích & Tư Vấn Dành Cho Giám Đốc (Tối Ưu Thuế)\n\n"
    
    md += "> [!IMPORTANT]\n"
    md += "> Tổng quỹ lương 8 tháng là **{:,.0f} VNĐ**. Đây là khoản chi phí hợp lý được trừ khi tính thuế TNDN. Giám đốc cần đảm bảo toàn bộ chi phí này có đầy đủ hồ sơ (Hợp đồng lao động, Bảng chấm công, Bảng lương có chữ ký, Chứng từ thanh toán) để cơ quan thuế chấp nhận.\n\n".format(grand_total)
    
    md += "### 2.1. Cảnh Báo Thuế Thu Nhập Cá Nhân (TNCN)\n\n"
    md += "Dưới đây là các nhân sự có thu nhập bình quân/tháng > **11.000.000 VNĐ** (mức giảm trừ gia cảnh bản thân). Nếu không có người phụ thuộc hoặc không thiết kế cơ cấu lương hợp lý, các nhân sự này sẽ phát sinh thuế TNCN phải nộp:\n\n"
    
    for name, job, avg, total in high_income_emps:
        md += f"- **{name}** ({job}): Thu nhập TB **{avg:,.0f} VNĐ/tháng** (Tổng: {total:,.0f} VNĐ)\n"
        
    md += "\n> [!TIP]\n"
    md += "> **Giải pháp tối ưu hóa thuế TNCN:**\n"
    md += "> 1. **Đăng ký người phụ thuộc:** Yêu cầu các nhân sự trên cung cấp hồ sơ người phụ thuộc (con cái, cha mẹ già) để được giảm trừ thêm 4.400.000 VNĐ/người/tháng.\n"
    md += "> 2. **Cơ cấu lại khoản thu nhập (Miễn thuế TNCN):** Thay vì cộng dồn hết vào lương cơ bản/lương khoán, kế toán nên tách thành các khoản phụ cấp không chịu thuế như:\n"
    md += ">    - Phụ cấp ăn ca (Tối đa 730.000 VNĐ/tháng).\n"
    md += ">    - Phụ cấp điện thoại, xăng xe, công tác phí (Theo quy chế công ty).\n"
    md += ">    - Phụ cấp trang phục (Tối đa 5.000.000 VNĐ/năm).\n"
    
    md += "\n### 2.2. Tư Vấn Về Lao Động Thời Vụ / Giao Khoán (Thợ Nhôm Kính)\n\n"
    md += "Nhóm thợ (Lò Văn Tiên, Hồ Văn Phải, Lê Văn Độ, v.v.) thường là lao động tự do hoặc làm theo công trình.\n"
    md += "- **Lưu ý:** Nếu ký hợp đồng dưới 3 tháng và chi trả từ 2 triệu VNĐ/lần trở lên, doanh nghiệp phải khấu trừ **10% thuế TNCN** trước khi trả thu nhập.\n"
    md += "- **Giải pháp:** Yêu cầu nhóm thợ làm **Bản cam kết mẫu 08/CK-TNCN** (cam kết tổng thu nhập trong năm chưa đến mức phải nộp thuế) để doanh nghiệp tạm thời không khấu trừ 10% thuế của họ, giúp thợ nhận đủ tiền mặt mà doanh nghiệp vẫn hợp lệ chi phí.\n"
    
    md += "\n## 3. Khuyến Nghị Cho Kế Toán (Cân Đối Sổ Sách)\n\n"
    md += "1. **Kiểm tra khớp số liệu:** Cân đối số liệu tổng ở cột cuối cùng ({:,.0f} VNĐ) khớp với dòng tiền chi ra trên Sổ Quỹ Tiền Mặt hoặc Sổ Tiền Gửi Ngân Hàng.\n".format(grand_total)
    md += "2. **Lưu trữ hồ sơ Khoán:** Các cá nhân có tháng làm tháng nghỉ (VD: Lò Văn Tiên làm T1, T2 nghỉ) cần có hợp đồng giao khoán công việc cụ thể hoặc biên bản nghiệm thu khối lượng công việc từng đợt để giải trình lý do trả lương không đều đặn.\n"
    
    with open(ARTIFACT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
        print(f"Báo cáo đã được tạo tại: {ARTIFACT_PATH}")

if __name__ == "__main__":
    generate()
