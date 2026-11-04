import json
import os

JSON_PATH = r"c:/Users/lehoa/OneDrive/Documents/BANG_LUONG'/chien_than_AI/migration_data.json"
ARTIFACT_PATH = r"C:/Users/lehoa/.gemini/antigravity-ide/brain/5b2737a9-1870-4940-905a-88da40104fcc/bang_tong_hop.md"

def generate():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    employees = data['employees']
    months_data = data['data']
    
    # Calculate totals
    totals = {}
    for month, records in months_data.items():
        for name, amount in records.items():
            # Skip invalid names like "Người lập biểu"
            if name in ["Người lập biểu", "(Ký, họ tên)", "Nguyễn Thanh Hoan"]:
                continue
            if amount == 0:
                continue
                
            if name not in totals:
                totals[name] = {'total': 0, 'months': {}}
            totals[name]['total'] += amount
            totals[name]['months'][month] = amount
            
    # Generate Markdown
    md = "# 📊 Bảng Tổng Hợp Tiền Lương (T1 - T8)\n\n"
    md += "Dưới đây là bảng tổng hợp thu nhập của toàn bộ nhân sự từ Tháng 1 đến Tháng 8 năm 2026 dựa trên dữ liệu lịch sử. Kế toán có thể dùng bảng này để cân đối dòng tiền và công nợ.\n\n"
    
    md += "| STT | Họ Tên | Chức Vụ | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | **TỔNG CỘNG** |\n"
    md += "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    
    # Sort by total descending
    sorted_emps = sorted(totals.items(), key=lambda x: x[1]['total'], reverse=True)
    
    grand_total = 0
    for idx, (name, info) in enumerate(sorted_emps, 1):
        job = employees.get(name, {}).get('job', '')
        row = f"| {idx} | **{name}** | {job} "
        for m in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']:
            val = info['months'].get(m, 0)
            if val > 0:
                row += f"| {val:,.0f} "
            else:
                row += "| - "
        row += f"| **{info['total']:,.0f}** |\n"
        md += row
        grand_total += info['total']
        
    md += f"| | **TỔNG QUỸ LƯƠNG** | | | | | | | | | | **{grand_total:,.0f}** |\n"
    
    with open(ARTIFACT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
        
if __name__ == "__main__":
    generate()
