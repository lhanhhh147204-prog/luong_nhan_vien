import db_config
import json
import os
from tax_engine import run_anomaly_detection

DB_NAME = "QL_LUONG"
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE={DB_NAME};Trusted_Connection=yes;'
HTML_PATH = r"c:\Users\lehoa\OneDrive\Documents\BANG_LUONG'\chien_than_AI\webapp\index.html"

def fmt_vnd(n):
    """Format số tiền VND chính xác, không làm tròn"""
    if n is None: return "0"
    return f"{int(round(n)):,}".replace(",", ".")

def get_month_num(m_str):
    try:
        return int(''.join(filter(str.isdigit, m_str)))
    except:
        return 99

def generate_html():
    print("Connecting to SQL Server for Dashboard...")
    conn = db_config.get_db_connection()
    cursor = conn.cursor()

    # --- KPIs ---
    cursor.execute("SELECT SUM(gross), SUM(bhxh_nld), SUM(thue_tncn), SUM(thuc_nhan_net) FROM LuongChinhThuc")
    r = cursor.fetchone()
    total_gross = r[0] or 0
    total_bh = r[1] or 0
    total_tncn = r[2] or 0
    total_net = r[3] or 0

    cursor.execute("SELECT SUM(c.so_tien) FROM ChiPhiKhoan c JOIN NhanVien n ON c.nhan_vien_id=n.id WHERE n.loai_nhan_su=2")
    total_vanglai = (cursor.fetchone()[0] or 0)

    cursor.execute("SELECT SUM(c.so_tien) FROM ChiPhiKhoan c JOIN NhanVien n ON c.nhan_vien_id=n.id WHERE n.loai_nhan_su=3")
    total_doikhoan = (cursor.fetchone()[0] or 0)

    cursor.execute("SELECT SUM(so_tien_no) FROM CongNo")
    total_congno = (cursor.fetchone()[0] or 0)

    # --- Monthly chart data ---
    cursor.execute("SELECT thang, SUM(gross), SUM(thuc_nhan_net) FROM LuongChinhThuc GROUP BY thang")
    monthly_data = cursor.fetchall()
    monthly_data.sort(key=lambda x: get_month_num(x[0]))
    chart_labels = [m[0] for m in monthly_data]
    chart_gross_values = [round(m[1]) for m in monthly_data]
    chart_net_values = [round(m[2]) for m in monthly_data]

    # --- Anomaly Alerts ---
    anomalies = run_anomaly_detection()
    cursor.execute("SELECT thang, ho_ten, ghi_chu FROM LuongChinhThuc lct JOIN NhanVien nv ON lct.nhan_vien_id=nv.id WHERE ghi_chu IS NOT NULL AND ghi_chu != ''")
    for row in cursor.fetchall():
        anomalies.append({"loai": "SAI SO EXCEL", "msg": f"{row[0]} - {row[1]}: {row[2]}"})

    alerts_html = ""
    if anomalies:
        for a in anomalies:
            is_err = "LOI" in a['loai'].upper().replace(" ","") or "SAI" in a['loai'].upper()
            cls = "alert-red" if is_err else "alert-orange"
            alerts_html += f'<div class="alert-row {cls}"><span class="alert-badge">{a["loai"]}</span><span class="alert-text">{a["msg"]}</span></div>'
    else:
        alerts_html = '<div class="alert-row alert-green"><span class="alert-badge">OK</span><span class="alert-text">✅ Không phát hiện bất thường pháp lý hay sai số nào trong kỳ này.</span></div>'

    # --- Monthly salary table ---
    cursor.execute("SELECT thang, SUM(gross), SUM(bhxh_nld), SUM(thue_tncn), SUM(thuc_nhan_net) FROM LuongChinhThuc GROUP BY thang")
    luong_rows_data = cursor.fetchall()
    luong_rows_data.sort(key=lambda x: get_month_num(x[0]))
    luong_rows = ""
    for r in luong_rows_data:
        luong_rows += f"<tr><td class='bold'>{r[0]}</td><td class='num'>{fmt_vnd(r[1])}</td><td class='num red-text'>- {fmt_vnd(r[2])}</td><td class='num red-text'>- {fmt_vnd(r[3])}</td><td class='num green-text bold'>{fmt_vnd(r[4])}</td></tr>"

    # --- New Metrics ---
    total_chiphi = total_gross + total_vanglai + total_doikhoan
    if total_chiphi == 0: total_chiphi = 1
    total_thue_nha_nuoc = total_bh + total_tncn
    # BHXH NSDLĐ: Nguời sử dụng lao động đóng 21.5% (BHXH 17.5% + BHYT 3% + BHTN 1%)
    # Nếu biết phần NLĐ = 10.5%, thì NSD = NLĐ * (21.5/10.5)
    total_bhxh_nsdld = round(total_bh * (21.5 / 10.5))
    total_bhxh_toan_phan = total_bh + total_bhxh_nsdld  # Tổng BHXH hai phía

    cursor.execute("SELECT COUNT(DISTINCT nhan_vien_id) FROM CongNo WHERE trang_thai LIKE '%Chưa%'")
    count_congno_people = cursor.fetchone()[0] or 0

    # --- Khoán table ---
    cursor.execute("SELECT n.ho_ten, n.loai_nhan_su, SUM(c.so_tien) FROM ChiPhiKhoan c JOIN NhanVien n ON c.nhan_vien_id=n.id GROUP BY n.ho_ten, n.loai_nhan_su ORDER BY SUM(c.so_tien) DESC")
    khoan_rows = ""
    for r in cursor.fetchall():
        loai = "Vãng lai" if r[1] == 2 else "Đội khoán"
        ti_trong = (r[2] / total_chiphi) * 100
        khoan_rows += f"<tr><td>{r[0]}</td><td><span class='tag'>{loai}</span></td><td class='num bold'>{fmt_vnd(r[2])}</td><td class='num'>{ti_trong:.1f}%</td></tr>"

    # --- Cong no table ---
    cursor.execute("SELECT n.ho_ten, c.so_tien_no, c.thang_phat_sinh, c.nam_phat_sinh, c.ghi_chu, c.trang_thai FROM CongNo c JOIN NhanVien n ON c.nhan_vien_id=n.id ORDER BY c.nam_phat_sinh, c.thang_phat_sinh")
    congno_rows = ""
    for r in cursor.fetchall():
        row_class = "no-row" if "chua" in str(r[5]).lower() else ""
        congno_rows += f"<tr class='{row_class}'><td class='bold'>{r[0]}</td><td>T{r[2]}/{r[3]}</td><td class='num red-text bold'>- {fmt_vnd(r[1])}</td><td>{r[4] or ''}</td><td><span class='status-badge status-no'>Chưa giải quyết</span></td></tr>"

    # --- HDLD table ---
    cursor.execute("SELECT n.ho_ten, n.chuc_vu, SUM(l.gross), SUM(l.thuc_nhan_net) FROM NhanVien n LEFT JOIN LuongChinhThuc l ON n.id = l.nhan_vien_id WHERE n.loai_nhan_su = 1 GROUP BY n.ho_ten, n.chuc_vu ORDER BY n.ho_ten")
    hdld_rows = ""
    for r in cursor.fetchall():
        cv = r[1] or 'Chưa cập nhật'
        gross = r[2] or 0
        net = r[3] or 0
        hdld_rows += f"<tr><td class='bold'>{r[0]}</td><td>{cv}</td><td class='num bold'>{fmt_vnd(gross)}</td><td class='num green-text bold'>{fmt_vnd(net)}</td></tr>"

    # --- Monthly JSON for client-side filtering ---
    monthly_json_data = []
    for m in monthly_data:
        monthly_json_data.append({
            "thang": m[0],
            "gross": round(m[1]),
            "net": round(m[2])
        })
    monthly_json = json.dumps(monthly_json_data, ensure_ascii=False)

    chart_labels_json = json.dumps(chart_labels, ensure_ascii=False)
    chart_gross_json = json.dumps(chart_gross_values)
    chart_net_json = json.dumps(chart_net_values)
    
    chart_cost_labels_json = json.dumps(["Lương Chính Thức (HĐLĐ)", "Đội Khoán", "Vãng Lai"], ensure_ascii=False)
    chart_cost_values_json = json.dumps([round(total_gross), round(total_doikhoan), round(total_vanglai)])
    
    chart_tax_labels_json = json.dumps(["Thực Nhận (NET)", "BHXH (10.5%)", "Thuế TNCN"], ensure_ascii=False)
    chart_tax_values_json = json.dumps([round(total_net), round(total_bh), round(total_tncn)])
    # --- Month options for filter dropdown ---
    month_options = ""
    for m in monthly_data:
        month_options += f"<option value='{m[0]}'>{m[0]}</option>"

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Hệ Thống Kế Toán Lương — Nhôm Kính Hoàng Anh 2026</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --bg: #f4f7fb;
      --surface: #ffffff;
      --surface2: #f8fafc;
      --border: #e2e8f0;
      --border-focus: #cbd5e1;
      --text: #0f172a;
      --muted: #64748b;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-glow: rgba(37,99,235,0.15);
      --green: #10b981;
      --green-light: #d1fae5;
      --red: #ef4444;
      --red-light: #fee2e2;
      --orange: #f97316;
      --orange-light: #ffedd5;
      --radius: 12px;
      --radius-sm: 8px;
      --shadow-sm: 0 2px 4px rgba(0,0,0,0.02);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.04);
      --shadow-lg: 0 12px 24px rgba(0,0,0,0.06);
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }}
    body {{ background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; -webkit-font-smoothing: antialiased; }}
    
    /* NAVBAR */
    .navbar {{
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 0 40px; height: 72px; display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 200;
      box-shadow: var(--shadow-sm);
    }}
    .brand {{ display: flex; align-items: center; gap: 14px; }}
    .brand-logo {{
      width: 44px; height: 44px; border-radius: 10px;
      background: linear-gradient(135deg, var(--accent), #4f46e5);
      color: white; display: flex; align-items: center; justify-content: center; font-size: 20px;
      box-shadow: 0 4px 12px var(--accent-glow);
    }}
    .brand h1 {{ font-size: 18px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px; }}
    .brand p {{ font-size: 13px; color: var(--muted); font-weight: 600; }}
    .nav-right {{ display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--accent); background: #eff6ff; padding: 6px 12px; border-radius: 20px; }}
    .dot-live {{ width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: blink 2s infinite; box-shadow: 0 0 8px var(--accent); }}
    @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}

    /* TABS */
    .tab-bar {{
      background: var(--surface); border-bottom: 1px solid var(--border);
      padding: 0 40px; display: flex; gap: 8px; position: sticky; top: 72px; z-index: 100;
      box-shadow: var(--shadow-sm);
    }}
    .tab-btn {{
      padding: 16px 20px; font-size: 14px; font-weight: 700; color: var(--muted);
      background: none; border: none; cursor: pointer; border-bottom: 3px solid transparent; margin-bottom: -1px;
      transition: all 0.2s ease;
    }}
    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
    .tab-pane {{ display: none; opacity: 0; animation: fadeIn 0.4s forwards; }}
    .tab-pane.active {{ display: block; }}
    @keyframes fadeIn {{ to {{ opacity: 1; }} }}

    /* LAYOUT */
    .container {{ max-width: 1440px; margin: 0 auto; padding: 32px 40px; }}

    /* KPI */
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; margin-bottom: 32px; }}
    .kpi-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
      padding: 24px; box-shadow: var(--shadow-md); transition: transform 0.2s;
      position: relative; overflow: hidden;
    }}
    .kpi-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-lg); }}
    .kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; }}
    .kpi-blue::before {{ background: var(--accent); }}
    .kpi-green::before {{ background: var(--green); }}
    .kpi-orange::before {{ background: var(--orange); }}
    .kpi-red::before {{ background: var(--red); }}
    
    .kpi-label {{ font-size: 13px; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
    .kpi-value {{ font-size: 28px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -1px; color: var(--text); }}
    .kpi-sub {{ font-size: 13px; color: var(--muted); font-weight: 600; margin-top: 8px; display: inline-block; padding: 4px 8px; background: var(--surface2); border-radius: 6px; }}

    /* PANELS */
    .panel {{
      background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
      padding: 24px; box-shadow: var(--shadow-md);
    }}
    .panel-title {{
      font-size: 16px; font-weight: 800; color: var(--text); padding-bottom: 16px;
      border-bottom: 1px solid var(--border); margin-bottom: 20px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .row-2col {{ display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 24px; }}
    
    /* ALERTS */
    .alert-row {{
      display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px;
      border-radius: 8px; margin-bottom: 10px; font-size: 14px; border: 1px solid transparent;
      transition: transform 0.2s;
    }}
    .alert-row:hover {{ transform: translateX(4px); }}
    .alert-green {{ background: #f0fdf4; border-color: #bbf7d0; }}
    .alert-orange {{ background: #fff7ed; border-color: #fed7aa; }}
    .alert-red {{ background: #fef2f2; border-color: #fecaca; }}
    .alert-badge {{
      font-size: 11px; font-weight: 800; padding: 4px 8px; border-radius: 6px; white-space: nowrap;
      flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .alert-green .alert-badge {{ background: var(--green); color: white; }}
    .alert-orange .alert-badge {{ background: var(--orange); color: white; }}
    .alert-red .alert-badge {{ background: var(--red); color: white; }}
    .alert-text {{ color: var(--text); line-height: 1.5; font-weight: 600; }}

    /* TABLES */
    .tbl-wrapper {{ overflow-x: auto; max-height: 400px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    thead th {{
      position: sticky; top: 0; background: #f8fafc; padding: 14px 16px;
      text-align: left; font-weight: 800; font-size: 12px; color: var(--muted);
      border-bottom: 2px solid var(--border); text-transform: uppercase; letter-spacing: 0.5px; z-index: 10;
    }}
    tbody td {{ padding: 14px 16px; border-bottom: 1px solid var(--border); font-weight: 600; color: #334155; }}
    tbody tr:hover td {{ background: #f1f5f9; }}
    tbody tr:last-child td {{ border-bottom: none; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; font-size: 15px; letter-spacing: -0.5px; }}
    .bold {{ font-weight: 800 !important; color: var(--text) !important; }}
    .green-text {{ color: var(--green) !important; }}
    .red-text {{ color: var(--red) !important; }}
    .tag {{
      display: inline-block; font-size: 12px; padding: 4px 10px; border-radius: 6px; font-weight: 700;
      background: #eff6ff; color: var(--accent); border: 1px solid #bfdbfe;
    }}
    .no-row td {{ background: #fff1f2; }}
    .status-badge {{
      font-size: 12px; padding: 4px 10px; border-radius: 6px; font-weight: 800; display: inline-block;
    }}
    .status-no {{ background: #fee2e2; color: var(--red); border: 1px solid #fecaca; }}

    /* FORM */
    .form-section {{
      background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
      padding: 32px; margin-bottom: 24px; box-shadow: var(--shadow-md);
    }}
    .form-section-title {{
      font-size: 18px; font-weight: 800; color: var(--text); margin-bottom: 24px;
      padding-bottom: 16px; border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 10px;
    }}
    .form-row {{ display: grid; gap: 20px; margin-bottom: 20px; }}
    .form-row-3 {{ grid-template-columns: repeat(3,1fr); }}
    .form-row-2 {{ grid-template-columns: repeat(2,1fr); }}
    .form-row-4 {{ grid-template-columns: repeat(4,1fr); }}
    .form-group {{ display: flex; flex-direction: column; gap: 8px; }}
    .form-group label {{ font-size: 12px; font-weight: 800; color: var(--text); text-transform: uppercase; letter-spacing: 0.5px; }}
    .form-group input, .form-group select {{
      border: 2px solid var(--border); border-radius: var(--radius-sm); padding: 12px 16px;
      font-size: 15px; color: var(--text); background: #fff; font-family: 'Plus Jakarta Sans', sans-serif;
      transition: all 0.2s; outline: none; font-weight: 600;
    }}
    .form-group input:focus, .form-group select:focus {{ border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-glow); }}
    .form-group input[type="number"] {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .form-hint {{ font-size: 12px; color: var(--muted); margin-top: 2px; font-weight: 600; }}

    .preview-box {{
      background: #eff6ff; border: 1px solid #bfdbfe; border-radius: var(--radius-sm);
      padding: 20px 24px; margin: 20px 0; display: flex; flex-wrap: wrap; gap: 32px;
    }}
    .preview-item {{ display: flex; flex-direction: column; gap: 4px; }}
    .preview-label {{ font-size: 12px; color: #3b82f6; font-weight: 800; text-transform: uppercase; }}
    .preview-value {{ font-size: 20px; font-weight: 800; font-variant-numeric: tabular-nums; }}

    .calc-helper {{
      display: flex; align-items: center; gap: 12px; margin-top: 16px;
      padding: 16px; background: var(--surface2); border-radius: var(--radius-sm); border: 1px dashed var(--border-focus);
    }}
    .calc-helper label {{ color: var(--text); font-weight: 700; font-size: 14px; white-space: nowrap; }}
    .calc-helper input {{
      border: 2px solid var(--border); border-radius: 6px; padding: 8px 12px;
      font-size: 14px; width: 180px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 700;
    }}
    .calc-helper button {{
      padding: 8px 16px; background: var(--accent); color: #fff; border: none;
      border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 800; transition: 0.2s;
    }}
    .calc-helper button:hover {{ background: var(--accent-hover); transform: translateY(-2px); box-shadow: 0 4px 12px var(--accent-glow); }}

    /* BUTTONS */
    .btn {{ display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 24px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 800; border: none; cursor: pointer; transition: all 0.2s; font-family: 'Plus Jakarta Sans', sans-serif; box-shadow: var(--shadow-sm); }}
    .btn-primary {{ background: var(--accent); color: #fff; }}
    .btn-primary:hover {{ background: var(--accent-hover); transform: translateY(-2px); box-shadow: 0 4px 12px var(--accent-glow); }}
    .btn-success {{ background: var(--green); color: #fff; }}
    .btn-success:hover {{ background: #059669; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16,185,129,0.2); }}
    .btn-orange {{ background: var(--orange); color: #fff; }}
    .btn-orange:hover {{ background: #ea580c; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(249,115,22,0.2); }}
    .btn-outline {{ background: #fff; color: var(--text); border: 2px solid var(--border); padding: 10px 22px; }}
    .btn-outline:hover {{ background: var(--surface2); border-color: var(--muted); }}
    .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none !important; }}
    .btn-group {{ display: flex; gap: 12px; margin-top: 24px; }}

    /* TOAST */
    #toast {{ position: fixed; bottom: 32px; right: 32px; z-index: 9999; display: flex; flex-direction: column; gap: 12px; }}
    .toast {{
      background: white; color: var(--text); border-radius: 10px;
      padding: 16px 20px; min-width: 300px; max-width: 400px; font-size: 14px; font-weight: 700;
      display: flex; align-items: center; gap: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
      border: 1px solid var(--border);
      animation: toastIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .toast.ok {{ border-left: 5px solid var(--green); }}
    .toast.err {{ border-left: 5px solid var(--red); }}
    .toast.warn {{ border-left: 5px solid var(--orange); }}
    @keyframes toastIn {{ from{{transform:translateX(100px);opacity:0}} to{{transform:translateX(0);opacity:1}} }}

    /* DIVIDER */
    hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}

    .section-note {{ font-size: 13px; color: var(--muted); font-weight: 600; background: var(--surface2); padding: 4px 10px; border-radius: 6px; }}

    /* Tổng kết row */
    .summary-row {{ background: #eff6ff !important; font-weight: 800; }}
    .summary-row td {{ color: var(--accent) !important; border-top: 2px solid #bfdbfe; font-size: 15px; }}
  </style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar">
  <div class="brand">
    <div class="brand-logo">⚡</div>
    <div>
      <h1>HỆ THỐNG KẾ TOÁN LƯƠNG 2026</h1>
      <p>Công Ty TNHH XD SX Nhôm Kính Hoàng Anh</p>
    </div>
  </div>
  <div class="nav-right"><div class="dot-live"></div> Đang kết nối CSDL QL_LUONG</div>
</nav>

<!-- TABS -->
<div class="tab-bar">
  <button class="tab-btn active" id="tab-tongquan" onclick="switchTab('tongquan')">📊 Tổng Quan</button>
  <button class="tab-btn" id="tab-nhaplieu" onclick="switchTab('nhaplieu')">✏️ Nhập Liệu</button>
</div>

<!-- ==================== TAB: TỔNG QUAN ==================== -->
<div class="tab-pane active" id="pane-tongquan">
<div class="container">

  <!-- BỘ LỌC THÁNG -->
  <div style="display:flex; align-items:center; gap:16px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px 24px; margin-bottom:24px; box-shadow:var(--shadow-sm);">
    <span style="font-size:14px; font-weight:800; color:var(--text);">📅 Xem theo kỳ:</span>
    <select id="month-filter" onchange="filterByMonth(this.value)" style="border:1px solid var(--border); border-radius:8px; padding:8px 16px; font-size:14px; font-weight:700; font-family:inherit; background:var(--surface2); color:var(--text); cursor:pointer; outline:none;">
      <option value="all">— Tổng cả năm —</option>
      {month_options}
    </select>
    <div id="filter-summary" style="display:none; margin-left:auto; display:flex; gap:16px; align-items:center;">
      <span style="font-size:13px; color:var(--muted); font-weight:600;">Gross:</span>
      <span id="fs-gross" style="font-size:16px; font-weight:800; color:var(--text);">—</span>
      <span style="font-size:13px; color:var(--muted); font-weight:600; margin-left:12px;">Thực nhận (NET):</span>
      <span id="fs-net" style="font-size:16px; font-weight:800; color:#15803d;">—</span>
    </div>
  </div>

  <!-- KPI -->
  <div class="kpi-grid">
    <div class="kpi-card kpi-blue">
      <div class="kpi-label">Quỹ Lương HĐLĐ (Gross)</div>
      <div class="kpi-value">{fmt_vnd(total_gross)} đ</div>
      <div class="kpi-sub">Thực nhận: {fmt_vnd(total_net)} đ</div>
    </div>
    <div class="kpi-card kpi-green">
      <div class="kpi-label">Tổng Chi Đội Khoán Thi Công</div>
      <div class="kpi-value">{fmt_vnd(total_doikhoan)} đ</div>
      <div class="kpi-sub">Tính từ dữ liệu thực chi</div>
    </div>
    <div class="kpi-card kpi-orange">
      <div class="kpi-label">Tổng Chi Vãng Lai / Khoán Nhỏ</div>
      <div class="kpi-value">{fmt_vnd(total_vanglai)} đ</div>
      <div class="kpi-sub">Thợ nhôm kính vãng lai</div>
    </div>
    <div class="kpi-card kpi-red">
      <div class="kpi-label">Công Nợ Lương Tồn Đọng</div>
      <div class="kpi-value">{fmt_vnd(total_congno)} đ</div>
      <div class="kpi-sub">Cần xử lý dứt điểm</div>
    </div>
  </div>

  <!-- RADAR AI -->
  <div class="panel" style="margin-bottom:32px; border-color:var(--orange); box-shadow: 0 4px 16px rgba(249,115,22,0.1);">
    <div class="panel-title" style="color:var(--orange); border-bottom:none; margin-bottom:0; padding-bottom:12px;">🚨 Radar AI — Giám Sát Bất Thường</div>
    <div>
      {alerts_html}
    </div>
  </div>

  <!-- BIỂU ĐỒ TỔNG QUAN -->
  <div class="panel" style="margin-bottom:24px;">
    <div class="panel-title">Biểu Đồ So Sánh Quỹ Lương Tổng Hợp (Gross vs Net) Theo Tháng</div>
    <canvas id="salaryChart" height="70"></canvas>
  </div>

  <div class="row-2col" style="grid-template-columns: 1fr 1fr; margin-bottom:32px;">
    <div class="panel">
      <div class="panel-title">Cơ Cấu Chi Phí Nhân Sự</div>
      <div style="position: relative; height: 300px; width: 100%; display: flex; justify-content: center;">
        <canvas id="costChart"></canvas>
      </div>
    </div>
    <div class="panel">
      <div class="panel-title">Tỷ Trọng Khấu Trừ Nghĩa Vụ</div>
      <div style="position: relative; height: 300px; width: 100%; display: flex; justify-content: center;">
        <canvas id="taxChart"></canvas>
      </div>
    </div>
  </div>

  <!-- 1. BÁO CÁO NGHĨA VỤ NỘP NGÂN SÁCH -->
  <div class="panel" style="margin-bottom:32px; border-left: 5px solid var(--accent);">
    <div class="panel-title">
      🏛 Báo Cáo Nghĩa Vụ Nộp Ngân Sách (Nhà Nước)
      <span class="section-note">Cả phần Người Lao Động và Người Sử Dụng Lao Động</span>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:20px;">
      <div style="background:#fff7ed; border:1px solid #fed7aa; padding:20px; border-radius:10px;">
        <div style="font-size:12px; color:#c2410c; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Phần NLĐ Đóng (10.5% Gross)</div>
        <div style="font-size:14px; color:#7c3aed; font-weight:600; margin-bottom:6px;">BHXH 8% + BHYT 1.5% + BHTN 1%</div>
        <div style="font-size:26px; color:#ea580c; font-weight:900;">{fmt_vnd(total_bh)} <span style="font-size:16px;">đ</span></div>
      </div>
      <div style="background:#f0f9ff; border:1px solid #bae6fd; padding:20px; border-radius:10px;">
        <div style="font-size:12px; color:#0369a1; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Phần NSDĐ Đóng (21.5% Gross)</div>
        <div style="font-size:14px; color:#7c3aed; font-weight:600; margin-bottom:6px;">BHXH 17.5% + BHYT 3% + BHTN 1%</div>
        <div style="font-size:26px; color:#0284c7; font-weight:900;">{fmt_vnd(total_bhxh_nsdld)} <span style="font-size:16px;">đ</span></div>
      </div>
    </div>
    <div style="display:flex; justify-content:space-around; align-items:center; background:var(--surface2); padding:24px; border-radius:10px; border:1px dashed var(--border-focus);">
      <div style="text-align:center;">
        <div style="font-size:14px; color:var(--muted); font-weight:800; text-transform:uppercase; margin-bottom:8px;">Tổng BHXH Hai Phía</div>
        <div style="font-size:22px; color:var(--text); font-weight:800;">{fmt_vnd(total_bhxh_toan_phan)} <span style="font-size:14px; color:var(--muted);">đ</span></div>
      </div>
      <div style="font-size:28px; color:var(--muted); font-weight:800;">+</div>
      <div style="text-align:center;">
        <div style="font-size:14px; color:var(--muted); font-weight:800; text-transform:uppercase; margin-bottom:8px;">Thuế TNCN Khấu Trừ</div>
        <div style="font-size:22px; color:var(--text); font-weight:800;">{fmt_vnd(total_tncn)} <span style="font-size:14px; color:var(--muted);">đ</span></div>
      </div>
      <div style="font-size:28px; color:var(--muted); font-weight:800;">=</div>
      <div style="text-align:center;">
        <div style="font-size:16px; color:var(--accent); font-weight:900; text-transform:uppercase; margin-bottom:8px;">TỔNG TIỀN PHẢI CHUẨN BỊ</div>
        <div style="font-size:32px; color:var(--accent); font-weight:900; padding:8px 20px; background:#eff6ff; border-radius:8px; box-shadow: 0 4px 12px var(--accent-glow);">{fmt_vnd(total_bhxh_toan_phan + total_tncn)} <span style="font-size:18px;">đ</span></div>
      </div>
    </div>
  </div>

  <!-- 2. QUỸ LƯƠNG CHÍNH THỨC (HĐLĐ) -->
  <div class="panel" style="margin-bottom:32px;">
    <div class="panel-title">
      💰 Phân Tích Lương Chính Thức (HĐLĐ)
      <span class="section-note">Bao gồm lương chi tiết từng tháng và nhân sự</span>
    </div>
    
    <div style="display:flex; gap:24px; margin-bottom:24px;">
      <div style="flex:1; background:#f0fdf4; border:1px solid #bbf7d0; padding:20px; border-radius:10px;">
        <div style="font-size:14px; color:#166534; font-weight:800; text-transform:uppercase; margin-bottom:8px;">Tổng Lương Thực Nhận (NET)</div>
        <div style="font-size:28px; color:#15803d; font-weight:900;">{fmt_vnd(total_net)} <span style="font-size:18px;">đ</span></div>
      </div>
      <div style="flex:1; background:#fef2f2; border:1px solid #fecaca; padding:20px; border-radius:10px;">
        <div style="font-size:14px; color:#991b1b; font-weight:800; text-transform:uppercase; margin-bottom:8px;">Tổng Khấu Trừ (BHXH + TNCN)</div>
        <div style="font-size:28px; color:#b91c1c; font-weight:900;">{fmt_vnd(total_thue_nha_nuoc)} <span style="font-size:18px;">đ</span></div>
      </div>
    </div>

    <div class="row-2col" style="grid-template-columns: 1fr 1fr;">
      <div class="tbl-wrapper">
        <table id="luong-table">
          <thead>
            <tr>
              <th>Tháng</th>
              <th class="num">Tổng Gross</th>
              <th class="num">BHXH (10.5%)</th>
              <th class="num">Thuế TNCN</th>
              <th class="num">Thực Nhận (NET)</th>
            </tr>
          </thead>
          <tbody>
            {luong_rows}
            <tr class="summary-row">
              <td class="bold">TỔNG CỘNG</td>
              <td class="num">{fmt_vnd(total_gross)}</td>
              <td class="num red-text">- {fmt_vnd(total_bh)}</td>
              <td class="num red-text">- {fmt_vnd(total_tncn)}</td>
              <td class="num green-text bold">{fmt_vnd(total_net)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="tbl-wrapper">
        <table>
          <thead><tr><th>Họ và Tên (HĐLĐ)</th><th>Chức Vụ</th><th class="num">Tổng Lương Gross</th><th class="num">Tổng NET</th></tr></thead>
          <tbody>{hdld_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 3. THỐNG KÊ CHI PHÍ THUÊ NGOÀI (KHOÁN / VÃNG LAI) -->
  <div class="panel" style="margin-bottom:24px;">
    <div class="panel-title">
      👷 Thống Kê Chi Phí Thuê Ngoài (Khoán / Vãng Lai)
      <span class="section-note">Tỷ trọng so với tổng chi phí nhân sự: {fmt_vnd(total_chiphi)} đ</span>
    </div>
    
    <div style="display:flex; gap:20px; margin-bottom:16px;">
      <div style="flex:1; background:#fff7ed; border:1px solid #fed7aa; padding:16px; border-radius:8px;">
        <div style="font-size:13px; color:#c2410c; font-weight:700; text-transform:uppercase; margin-bottom:4px;">Tổng Chi Đội Khoán</div>
        <div style="font-size:24px; color:#ea580c; font-weight:800;">{fmt_vnd(total_doikhoan)} <span style="font-size:16px;">đ</span></div>
      </div>
      <div style="flex:1; background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:8px;">
        <div style="font-size:13px; color:#475569; font-weight:700; text-transform:uppercase; margin-bottom:4px;">Tổng Chi Vãng Lai</div>
        <div style="font-size:24px; color:#334155; font-weight:800;">{fmt_vnd(total_vanglai)} <span style="font-size:16px;">đ</span></div>
      </div>
    </div>

    <div class="tbl-wrapper">
      <table>
        <thead><tr><th>Họ và Tên / Đội</th><th>Phân Loại</th><th class="num">Tổng Tiền Đã Chi</th><th class="num">Tỷ Trọng (%)</th></tr></thead>
        <tbody>
          {khoan_rows}
          <tr class="summary-row">
            <td class="bold">TỔNG CỘNG</td>
            <td></td>
            <td class="num">{fmt_vnd(total_doikhoan + total_vanglai)}</td>
            <td class="num">{((total_doikhoan + total_vanglai) / total_chiphi * 100):.1f}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- 4. QUẢN TRỊ CÔNG NỢ LƯƠNG -->
  <div class="panel">
    <div class="panel-title">
      ⚠️ Quản Trị Công Nợ Lương
      <span class="section-note">Các khoản nợ nhân viên cần thanh toán</span>
    </div>
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
      <div style="background:#fee2e2; color:#b91c1c; font-weight:800; padding:12px 20px; border-radius:8px; border:1px solid #fecaca;">
        🔥 Đang nợ {count_congno_people} nhân viên
      </div>
      <div style="background:#fef2f2; padding:12px 20px; border-radius:8px; border:1px solid #fecaca; display:flex; align-items:center; gap:8px;">
        <span style="font-size:13px; color:#991b1b; font-weight:800; text-transform:uppercase;">Tổng Tiền Nợ:</span>
        <span style="font-size:20px; color:#b91c1c; font-weight:800;">{fmt_vnd(total_congno)} đ</span>
      </div>
    </div>
    <div class="tbl-wrapper">
      <table>
        <thead><tr><th>Họ và Tên</th><th>Kỳ Phát Sinh</th><th class="num">Số Tiền Nợ</th><th>Ghi Chú</th><th>Trạng Thái</th></tr></thead>
        <tbody>{congno_rows}</tbody>
      </table>
    </div>
  </div>

</div>
</div>

<!-- ==================== TAB: NHẬP LIỆU ==================== -->
<div class="tab-pane" id="pane-nhaplieu">
<div class="container">

  <!-- FORM 1: LƯƠNG CHÍNH THỨC -->
  <div class="form-section">
    <div class="form-section-title">
      👔 Nhập Lương Chính Thức (Hợp Đồng Lao Động)
    </div>
    <div class="form-row form-row-3">
      <div class="form-group">
        <label>Nhân Viên *</label>
        <select id="f-luong-nv"><option value="">— Chọn nhân viên —</option></select>
      </div>
      <div class="form-group">
        <label>Kỳ Lương (Tháng) *</label>
        <select id="f-luong-thang">
          <option value="Tháng 1">Tháng 1/2026</option><option value="Tháng 2">Tháng 2/2026</option>
          <option value="Tháng 3">Tháng 3/2026</option><option value="Tháng 4">Tháng 4/2026</option>
          <option value="Tháng 5">Tháng 5/2026</option><option value="Tháng 6">Tháng 6/2026</option>
          <option value="Tháng 7">Tháng 7/2026</option><option value="Tháng 8">Tháng 8/2026</option>
          <option value="Tháng 9" selected>Tháng 9/2026</option><option value="Tháng 10">Tháng 10/2026</option>
          <option value="Tháng 11">Tháng 11/2026</option><option value="Tháng 12">Tháng 12/2026</option>
        </select>
      </div>
      <div class="form-group">
        <label>Tổng Thu Nhập - GROSS (đồng) *</label>
        <input type="number" id="f-luong-gross" placeholder="Ví dụ: 25000000" oninput="calcNet()"/>
        <span class="form-hint">Nhập đúng số tiền, không làm tròn</span>
      </div>
    </div>
    <div class="form-row form-row-3">
      <div class="form-group">
        <label>BHXH NLĐ Trừ Lương (đồng)</label>
        <input type="number" id="f-luong-bh" placeholder="= Lương CB × 10.5%" oninput="calcNet()"/>
        <span class="form-hint">Tự nhập hoặc dùng công cụ tính bên dưới</span>
      </div>
      <div class="form-group">
        <label>Thuế TNCN Phải Nộp (đồng)</label>
        <input type="number" id="f-luong-tncn" placeholder="0 nếu không phát sinh" oninput="calcNet()"/>
      </div>
      <div class="form-group">
        <label>Lương Thực Nhận NET (đồng)</label>
        <input type="number" id="f-luong-net" placeholder="Nhập từ Excel hoặc để AI tính" oninput="calcNet()"/>
        <span class="form-hint">Nếu để trống, hệ thống tự tính = Gross - BHXH - TNCN</span>
      </div>
    </div>

    <div class="calc-helper">
      <label>Tự tính BHXH: Lương CB đóng BH =</label>
      <input type="number" id="f-luong-cb" placeholder="Ví dụ: 6000000"/>
      <button onclick="autoCalcBH()">⚡ Tính BHXH 10.5%</button>
      <span style="color:var(--muted); font-size:12px;">Kết quả sẽ điền tự động vào ô BHXH bên trên</span>
    </div>

    <div class="preview-box" id="preview-box" style="display:none;">
      <div class="preview-item">
        <span class="preview-label">Gross</span>
        <span class="preview-value" style="color:var(--accent);" id="pr-gross">—</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">BHXH Trừ</span>
        <span class="preview-value" style="color:var(--red);" id="pr-bh">—</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">Thuế TNCN</span>
        <span class="preview-value" style="color:var(--orange);" id="pr-tncn">—</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">NET Tính Toán</span>
        <span class="preview-value" style="color:var(--green);" id="pr-net">—</span>
      </div>
      <div class="preview-item" id="pr-warn-wrap" style="display:none;">
        <span class="preview-label">⚠ Cảnh Báo Lệch</span>
        <span class="preview-value" style="color:var(--red); font-size:13px;" id="pr-warn">—</span>
      </div>
    </div>

    <div class="btn-group">
      <button class="btn btn-primary" id="btn-save-luong" onclick="saveLuong()">💾 Lưu Bản Ghi Lương</button>
      <button class="btn btn-outline" onclick="clearLuong()">🔄 Xóa Form</button>
    </div>
  </div>

  <!-- FORM 2: KHOÁN / VÃNG LAI -->
  <div class="form-section">
    <div class="form-section-title">🔧 Nhập Chi Phí Khoán / Vãng Lai</div>
    <div class="form-row form-row-3">
      <div class="form-group">
        <label>Nhân Viên / Đội Khoán *</label>
        <select id="f-khoan-nv"><option value="">— Chọn nhân viên —</option></select>
      </div>
      <div class="form-group">
        <label>Kỳ Thanh Toán (Tháng) *</label>
        <select id="f-khoan-thang">
          <option value="Tháng 1">Tháng 1/2026</option><option value="Tháng 2">Tháng 2/2026</option>
          <option value="Tháng 3">Tháng 3/2026</option><option value="Tháng 4">Tháng 4/2026</option>
          <option value="Tháng 5">Tháng 5/2026</option><option value="Tháng 6">Tháng 6/2026</option>
          <option value="Tháng 7">Tháng 7/2026</option><option value="Tháng 8">Tháng 8/2026</option>
          <option value="Tháng 9" selected>Tháng 9/2026</option><option value="Tháng 10">Tháng 10/2026</option>
          <option value="Tháng 11">Tháng 11/2026</option><option value="Tháng 12">Tháng 12/2026</option>
        </select>
      </div>
      <div class="form-group">
        <label>Số Tiền Chi Trả (đồng) *</label>
        <input type="number" id="f-khoan-sotien" placeholder="Ví dụ: 21000000"/>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-orange" onclick="saveKhoan()">💾 Lưu Chi Phí Khoán</button>
      <button class="btn btn-outline" onclick="clearKhoan()">🔄 Xóa Form</button>
    </div>
  </div>

  <!-- FORM 3: CÔNG NỢ -->
  <div class="form-section">
    <div class="form-section-title">⚠️ Ghi Nhận Công Nợ Lương Tồn Đọng</div>
    <div class="form-row form-row-4">
      <div class="form-group">
        <label>Nhân Viên *</label>
        <select id="f-no-nv"><option value="">— Chọn nhân viên —</option></select>
      </div>
      <div class="form-group">
        <label>Tháng Phát Sinh</label>
        <input type="number" id="f-no-thang" min="1" max="12" value="9"/>
      </div>
      <div class="form-group">
        <label>Năm</label>
        <input type="number" id="f-no-nam" value="2026"/>
      </div>
      <div class="form-group">
        <label>Số Tiền Nợ (đồng) *</label>
        <input type="number" id="f-no-sotien" placeholder="Ví dụ: 5000000"/>
      </div>
    </div>
    <div class="form-row form-row-2">
      <div class="form-group">
        <label>Ghi Chú</label>
        <input type="text" id="f-no-ghichu" placeholder="Ví dụ: Chưa thanh toán do thiếu ngân quỹ tháng 9"/>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn" style="background:#fee2e2;color:var(--red);border:1px solid #fecaca;" onclick="saveCongNo()">⚠️ Ghi Nhận Công Nợ</button>
    </div>
  </div>

  <!-- FORM 4: THÊM NHÂN VIÊN -->
  <div class="form-section">
    <div class="form-section-title">➕ Thêm Nhân Viên Mới Vào Hệ Thống</div>
    <div class="form-row form-row-3">
      <div class="form-group">
        <label>Họ và Tên *</label>
        <input type="text" id="f-nv-hoten" placeholder="Ví dụ: Nguyễn Văn A"/>
      </div>
      <div class="form-group">
        <label>Chức Vụ</label>
        <input type="text" id="f-nv-chucvu" placeholder="Ví dụ: Thợ Nhôm Kính"/>
      </div>
      <div class="form-group">
        <label>Phân Loại Nhân Sự *</label>
        <select id="f-nv-loai">
          <option value="1">Loại 1 — HĐLĐ Chính Thức (Có đóng BHXH)</option>
          <option value="2">Loại 2 — Vãng Lai / Khoán Nhỏ</option>
          <option value="3">Loại 3 — Đội Khoán Thi Công</option>
        </select>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-success" onclick="saveNhanVien()">✅ Thêm Vào Hệ Thống</button>
    </div>
  </div>

  
  <!-- FORM 5: XÓA NHÂN VIÊN -->
  <div class="form-section" style="border-color:#fecaca;">
    <div class="form-section-title" style="color:#b91c1c;">❌ Xóa Nhân Viên Khỏi Hệ Thống</div>
    <div class="form-row form-row-2">
      <div class="form-group">
        <label>Chọn Nhân Viên Cần Xóa *</label>
        <select id="f-del-nv"><option value="">— Chọn nhân viên —</option></select>
      </div>
      <div class="form-group" style="justify-content: flex-end;">
        <button class="btn btn-outline" style="background:#fee2e2;color:#b91c1c;border-color:#fecaca;" onclick="deleteNhanVien()">🗑 Xác Nhận Xóa</button>
      </div>
    </div>
    <span class="form-hint" style="color:#b91c1c;">Lưu ý: Chỉ có thể xóa khi nhân viên chưa có bất kỳ dữ liệu lương/khoán/công nợ nào.</span>
  </div>

  <!-- CẬP NHẬT DASHBOARD -->
  <div class="form-section" style="background:#eff6ff; border-color:#bfdbfe;">
    <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
      <div>
        <div style="font-size:14px; font-weight:700; color:var(--accent); margin-bottom:4px;">🔄 Cập Nhật Dashboard</div>
        <div style="font-size:13px; color:var(--muted);">Sau khi nhập đủ dữ liệu cho tháng mới, bấm nút này để cập nhật toàn bộ biểu đồ và số liệu tổng quan.</div>
      </div>
      <button class="btn btn-primary" id="btn-rebuild" onclick="rebuildDashboard()">🔄 Cập Nhật Ngay</button>
    </div>
  </div>

</div>
</div>

<!-- TOAST -->
<div id="toast"></div>

<!-- SCRIPTS -->
<script>
const API = '';

function switchTab(tab) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('pane-' + tab).classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  if (tab === 'nhaplieu' && !window._nvLoaded) loadNhanVien();
}}

function showToast(msg, type='ok') {{
  const icons = {{ok:'✅', err:'❌', warn:'⚠️'}};
  const el = document.createElement('div');
  el.className = `toast ${{type}}`;
  el.innerHTML = `<span>${{icons[type]}}</span><span>${{msg}}</span>`;
  document.getElementById('toast').appendChild(el);
  setTimeout(() => {{ el.style.opacity='0'; el.style.transition='0.3s'; setTimeout(()=>el.remove(),300); }}, 4500);
}}

async function loadNhanVien() {{
  try {{
    const r = await fetch('/api/nhan-vien');
    if (!r.ok) throw new Error();
    const list = await r.json();
    const selectors = ['#f-luong-nv','#f-khoan-nv','#f-no-nv','#f-del-nv'];
    const labels = {{1:'HĐ chính thức', 2:'Vãng lai', 3:'Đội khoán'}};
    selectors.forEach(sel => {{
      const el = document.querySelector(sel);
      el.innerHTML = '<option value="">— Chọn nhân viên —</option>';
      list.forEach(nv => {{
        el.innerHTML += `<option value="${{nv.id}}">${{nv.ho_ten}} (${{labels[nv.loai_nhan_su]||''}})</option>`;
      }});
    }});
    window._nvLoaded = true;
  }} catch(e) {{
    showToast('Không thể kết nối API Server. Hãy chạy api_server.py!', 'err');
  }}
}}

function fmtVND(n) {{
  return Math.round(n).toLocaleString('de-DE').replace(/\./g, '.') + ' đ';
}}

function calcNet() {{
  const gross = parseFloat(document.getElementById('f-luong-gross').value)||0;
  const bh    = parseFloat(document.getElementById('f-luong-bh').value)||0;
  const tncn  = parseFloat(document.getElementById('f-luong-tncn').value)||0;
  const netExcel = parseFloat(document.getElementById('f-luong-net').value)||0;
  if (gross <= 0) {{ document.getElementById('preview-box').style.display='none'; return; }}
  const netCalc = gross - bh - tncn;
  document.getElementById('pr-gross').textContent = fmtVND(gross);
  document.getElementById('pr-bh').textContent = fmtVND(bh);
  document.getElementById('pr-tncn').textContent = fmtVND(tncn);
  document.getElementById('pr-net').textContent = fmtVND(netCalc);
  const warnWrap = document.getElementById('pr-warn-wrap');
  if (netExcel > 0 && Math.abs(netCalc - netExcel) > 100) {{
    warnWrap.style.display='flex';
    document.getElementById('pr-warn').textContent = `Excel: ${{fmtVND(netExcel)}} | Tính toán: ${{fmtVND(netCalc)}}`;
  }} else {{ warnWrap.style.display='none'; }}
  document.getElementById('preview-box').style.display='flex';
}}

function autoCalcBH() {{
  const lcb = parseFloat(document.getElementById('f-luong-cb').value)||0;
  if (lcb>0) {{ document.getElementById('f-luong-bh').value=Math.round(lcb*0.105); calcNet(); }}
}}

async function saveLuong() {{
  const nv_id = document.getElementById('f-luong-nv').value;
  const thang = document.getElementById('f-luong-thang').value;
  const gross = parseFloat(document.getElementById('f-luong-gross').value)||0;
  const bh    = parseFloat(document.getElementById('f-luong-bh').value)||0;
  const tncn  = parseFloat(document.getElementById('f-luong-tncn').value)||0;
  const net   = parseFloat(document.getElementById('f-luong-net').value)||(gross-bh-tncn);
  if (!nv_id||!thang||gross<=0) {{ showToast('Vui lòng điền đủ: Nhân viên, Tháng, Gross!','warn'); return; }}
  const btn = document.getElementById('btn-save-luong');
  btn.disabled=true; btn.textContent='⏳ Đang lưu...';
  try {{
    const r = await fetch('/api/luong', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{nhan_vien_id:nv_id,thang,gross,bhxh_nld:bh,thue_tncn:tncn,thuc_nhan_net:net}})}});
    const res = await r.json();
    if (res.success) {{
      showToast(`Đã ${{res.action==='updated'?'cập nhật':'lưu mới'}} lương ${{thang}} — Gross: ${{fmtVND(gross)}}`,'ok');
      if (res.ghi_chu) showToast(res.ghi_chu,'warn');
      clearLuong();
    }} else showToast(res.error||'Lỗi không xác định','err');
  }} catch(e) {{ showToast('Lỗi kết nối API Server!','err'); }}
  btn.disabled=false; btn.textContent='💾 Lưu Bản Ghi Lương';
}}

async function saveKhoan() {{
  const nv_id=document.getElementById('f-khoan-nv').value;
  const thang=document.getElementById('f-khoan-thang').value;
  const so_tien=parseFloat(document.getElementById('f-khoan-sotien').value)||0;
  if (!nv_id||so_tien<=0) {{ showToast('Vui lòng điền đủ thông tin!','warn'); return; }}
  try {{
    const r=await fetch('/api/khoan',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{nhan_vien_id:nv_id,thang,so_tien}})}});
    const res=await r.json();
    if (res.success) {{ showToast(`Đã lưu chi phí khoán ${{thang}}: ${{fmtVND(so_tien)}}`,'ok'); clearKhoan(); }}
    else showToast(res.error||'Lỗi!','err');
  }} catch(e) {{ showToast('Lỗi kết nối API Server!','err'); }}
}}

async function saveCongNo() {{
  const nv_id=document.getElementById('f-no-nv').value;
  const thang=parseInt(document.getElementById('f-no-thang').value)||9;
  const nam=parseInt(document.getElementById('f-no-nam').value)||2026;
  const so_no=parseFloat(document.getElementById('f-no-sotien').value)||0;
  const gc=document.getElementById('f-no-ghichu').value;
  if (!nv_id||so_no<=0) {{ showToast('Vui lòng điền Nhân viên và Số tiền nợ!','warn'); return; }}
  try {{
    const r=await fetch('/api/cong-no',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{nhan_vien_id:nv_id,so_tien_no:so_no,thang_phat_sinh:thang,nam_phat_sinh:nam,ghi_chu:gc}})}});
    const res=await r.json();
    if (res.success) showToast(`Đã ghi nhận công nợ: ${{fmtVND(so_no)}}`,'ok');
    else showToast(res.error||'Lỗi!','err');
  }} catch(e) {{ showToast('Lỗi kết nối API Server!','err'); }}
}}

async function saveNhanVien() {{
  const ho_ten=document.getElementById('f-nv-hoten').value.trim();
  const chuc_vu=document.getElementById('f-nv-chucvu').value.trim();
  const loai=document.getElementById('f-nv-loai').value;
  if (!ho_ten) {{ showToast('Họ tên không được trống!','warn'); return; }}
  try {{
    const r=await fetch('/api/nhan-vien',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{ho_ten,chuc_vu,loai_nhan_su:loai}})}});
    const res=await r.json();
    if (res.success) {{
      showToast(`Đã thêm nhân viên: ${{res.ho_ten}}`,'ok');
      document.getElementById('f-nv-hoten').value='';
      document.getElementById('f-nv-chucvu').value='';
      window._nvLoaded=false; loadNhanVien();
    }} else showToast(res.error||'Lỗi!','err');
  }} catch(e) {{ showToast('Lỗi kết nối API Server!','err'); }}
}}

async function rebuildDashboard() {{
  const btn=document.getElementById('btn-rebuild');
  btn.disabled=true; btn.textContent='⏳ Đang cập nhật...';
  try {{
    const r=await fetch(`${{API}}/api/rebuild-dashboard`,{{method:'POST'}});
    const res=await r.json();
    if (res.success) showToast('Dashboard đã cập nhật! Bấm F5 để xem số liệu mới.','ok');
    else showToast('Lỗi: '+res.msg,'err');
  }} catch(e) {{ showToast('Lỗi kết nối API Server!','err'); }}
  btn.disabled=false; btn.textContent='🔄 Cập Nhật Ngay';
}}

function clearLuong() {{
  ['f-luong-gross','f-luong-bh','f-luong-tncn','f-luong-net','f-luong-cb'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('f-luong-nv').selectedIndex=0;
  document.getElementById('preview-box').style.display='none';
}}
function clearKhoan() {{
  document.getElementById('f-khoan-sotien').value='';
  document.getElementById('f-khoan-nv').selectedIndex=0;
}}

// === BỘ LỌC THÁNG ===
const _monthlyData = {monthly_json};

function fmtVNDn(n) {{
  return Math.round(n).toLocaleString('de-DE') + ' đ';
}}

function filterByMonth(val) {{
  // Lọc các hàng bảng lương
  const rows = document.querySelectorAll('#luong-table tbody tr:not(.summary-row)');
  rows.forEach(row => {{
    const monthCell = row.querySelector('td:first-child');
    if (!monthCell) return;
    row.style.display = (val === 'all' || monthCell.textContent.trim() === val) ? '' : 'none';
  }});

  // Cập nhật mini KPI filter bar
  const summary = document.getElementById('filter-summary');
  if (val === 'all') {{
    summary.style.display = 'none';
  }} else {{
    const d = _monthlyData.find(m => m.thang === val);
    if (d) {{
      document.getElementById('fs-gross').textContent = fmtVNDn(d.gross);
      document.getElementById('fs-net').textContent = fmtVNDn(d.net);
    }}
    summary.style.display = 'flex';
  }}
}}

// --- Chart 1: Salary (Gross vs Net) ---
const commonTooltip = {{
  backgroundColor: '#1e293b', padding: 12,
  titleFont: {{family:'Plus Jakarta Sans',size:13}}, bodyFont: {{family:'Plus Jakarta Sans',size:13}},
  callbacks: {{ label: ctx => '  ' + Math.round(ctx.raw).toLocaleString('de-DE') + ' đ' }}
}};

new Chart(document.getElementById('salaryChart').getContext('2d'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels_json},
    datasets: [
      {{
        label: 'Gross (Tổng Thu Nhập)',
        data: {chart_gross_json},
        backgroundColor: 'rgba(37,99,235,0.2)',
        borderColor: 'rgba(37,99,235,0.8)',
        borderWidth: 1.5, borderRadius: 4, barPercentage: 0.8
      }},
      {{
        label: 'Net (Thực Nhận)',
        data: {chart_net_json},
        backgroundColor: 'rgba(16,185,129,0.2)',
        borderColor: 'rgba(16,185,129,0.8)',
        borderWidth: 1.5, borderRadius: 4, barPercentage: 0.8
      }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'top', labels: {{ font: {{family:'Plus Jakarta Sans',size:13}} }} }},
      tooltip: commonTooltip
    }},
    scales: {{
      y: {{
        beginAtZero: true, grid: {{ color: '#f1f5f9' }},
        ticks: {{ color: '#64748b', font: {{family:'Plus Jakarta Sans',size:12}}, callback: v => (v/1000000).toFixed(0) + ' tr' }}
      }},
      x: {{ grid: {{display:false}}, ticks: {{color:'#64748b',font:{{family:'Plus Jakarta Sans',size:12}}}} }}
    }}
  }}
}});

// --- Chart 2: Cost Structure ---
new Chart(document.getElementById('costChart').getContext('2d'), {{
  type: 'doughnut',
  data: {{
    labels: {chart_cost_labels_json},
    datasets: [{{
      data: {chart_cost_values_json},
      backgroundColor: ['rgba(37,99,235,0.8)', 'rgba(249,115,22,0.8)', 'rgba(71,85,105,0.8)'],
      borderWidth: 0
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{family:'Plus Jakarta Sans',size:12}} }} }},
      tooltip: commonTooltip
    }},
    cutout: '65%'
  }}
}});

// --- Chart 3: Tax Structure ---
new Chart(document.getElementById('taxChart').getContext('2d'), {{
  type: 'doughnut',
  data: {{
    labels: {chart_tax_labels_json},
    datasets: [{{
      data: {chart_tax_values_json},
      backgroundColor: ['rgba(16,185,129,0.8)', 'rgba(234,179,8,0.8)', 'rgba(239,68,68,0.8)'],
      borderWidth: 0
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{family:'Plus Jakarta Sans',size:12}} }} }},
      tooltip: commonTooltip
    }},
    cutout: '65%'
  }}
}});
</script>

</body>
</html>"""

    cursor.close()
    conn.close()
    return html_content

if __name__ == "__main__":
    html = generate_html()
    print("Dashboard generated successfully (length: {})".format(len(html)))
