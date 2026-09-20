"""
api_server.py - Flask API Backend cho Dashboard Kế Toán
Cổng: http://localhost:5055
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import db_config
from update_dashboard import generate_html

app = Flask(__name__)
CORS(app)  # Cho phép Dashboard HTML gọi API

def get_conn():
    return db_config.get_db_connection()

# ─────────────────────────────────────────────
# GET /api/nhan-vien — Lấy danh sách nhân viên
# ─────────────────────────────────────────────
@app.route('/api/nhan-vien', methods=['GET'])
def get_nhan_vien():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ho_ten, chuc_vu, loai_nhan_su FROM NhanVien ORDER BY loai_nhan_su, ho_ten")
    result = []
    for r in cursor.fetchall():
        result.append({
            "id": r[0],
            "ho_ten": r[1],
            "chuc_vu": r[2] if r[2] else "",
            "loai_nhan_su": r[3]
        })
    cursor.close(); conn.close()
    return jsonify(result)

# ─────────────────────────────────────────────────────────────────
# POST /api/nhan-vien — Thêm mới nhân viên
# Body: { ho_ten, chuc_vu, loai_nhan_su }
# ─────────────────────────────────────────────────────────────────
@app.route('/api/nhan-vien', methods=['POST'])
def them_nhan_vien():
    data = request.json
    ho_ten = data.get('ho_ten', '').strip()
    chuc_vu = data.get('chuc_vu', '').strip()
    loai = int(data.get('loai_nhan_su', 1))
    if not ho_ten:
        return jsonify({"error": "Họ tên không được trống"}), 400
    conn = get_conn()
    cursor = conn.cursor()
    # Kiểm tra trùng
    cursor.execute("SELECT id FROM NhanVien WHERE ho_ten = %s", (ho_ten,))
    if cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({"error": f"Nhân viên '{ho_ten}' đã tồn tại"}), 409
    cursor.execute("INSERT INTO NhanVien (ho_ten, chuc_vu, loai_nhan_su) VALUES (%s,%s,%s) RETURNING id", (ho_ten, chuc_vu, loai))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True, "id": new_id, "ho_ten": ho_ten})

# ─────────────────────────────────────────────────────────────────────────
# POST /api/luong — Nhập bảng lương 1 nhân viên 1 tháng
# Body: { nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net }
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/luong', methods=['POST'])
def nhap_luong():
    data = request.json
    nv_id    = int(data.get('nhan_vien_id'))
    thang    = data.get('thang', '').strip()        # e.g. "Tháng 9"
    gross    = float(data.get('gross', 0))
    bh_nld   = float(data.get('bhxh_nld', 0))
    tncn     = float(data.get('thue_tncn', 0))
    net      = float(data.get('thuc_nhan_net', 0))

    if not thang or gross <= 0:
        return jsonify({"error": "Thiếu thông tin bắt buộc (tháng, gross > 0)"}), 400

    # Sanity check
    net_calc = gross - bh_nld - tncn
    ghi_chu = ""
    if abs(net_calc - net) > 100:
        ghi_chu = f"[!] LỆCH: Excel={net:,.0f}, Tính={net_calc:,.0f}"

    conn = get_conn()
    cursor = conn.cursor()
    # Kiểm tra đã có chưa → nếu có thì UPDATE
    cursor.execute("SELECT id FROM LuongChinhThuc WHERE nhan_vien_id=%s AND thang=%s", (nv_id, thang))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE LuongChinhThuc 
            SET gross=%s, bhxh_nld=%s, thue_tncn=%s, thuc_nhan_net=%s, ghi_chu=%s
            WHERE nhan_vien_id=%s AND thang=%s
        """, (gross, bh_nld, tncn, net, ghi_chu, nv_id, thang))
        action = "updated"
    else:
        cursor.execute("""
            INSERT INTO LuongChinhThuc (nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net, ghi_chu)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (nv_id, thang, gross, bh_nld, tncn, net, ghi_chu))
        action = "inserted"
    conn.commit()
    cursor.close(); conn.close()

    return jsonify({
        "success": True,
        "action": action,
        "ghi_chu": ghi_chu,
        "net_tinh_toan": net_calc
    })

# ─────────────────────────────────────────────────────────────────────────
# POST /api/khoan — Nhập chi phí khoán / vãng lai
# Body: { nhan_vien_id, thang, so_tien }
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/khoan', methods=['POST'])
def nhap_khoan():
    data = request.json
    nv_id    = int(data.get('nhan_vien_id'))
    thang    = data.get('thang', '').strip()
    so_tien  = float(data.get('so_tien', 0))
    if not thang or so_tien <= 0:
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ChiPhiKhoan WHERE nhan_vien_id=%s AND thang=%s", (nv_id, thang))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE ChiPhiKhoan SET so_tien=%s WHERE nhan_vien_id=%s AND thang=%s", (so_tien, nv_id, thang))
        action = "updated"
    else:
        cursor.execute("INSERT INTO ChiPhiKhoan (nhan_vien_id, thang, so_tien) VALUES (%s,%s,%s)", (nv_id, thang, so_tien))
        action = "inserted"
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True, "action": action})

# ─────────────────────────────────────────────────────────────────────────
# POST /api/cong-no — Nhập công nợ mới
# Body: { nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, ghi_chu }
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/cong-no', methods=['POST'])
def nhap_cong_no():
    data = request.json
    nv_id  = int(data.get('nhan_vien_id'))
    so_no  = float(data.get('so_tien_no', 0))
    thang  = int(data.get('thang_phat_sinh', 1))
    nam    = int(data.get('nam_phat_sinh', 2026))
    gc     = data.get('ghi_chu', '')
    if so_no <= 0:
        return jsonify({"error": "Số tiền nợ phải > 0"}), 400
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CongNo (nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, ghi_chu, trang_thai)
        VALUES (%s,%s,%s,%s,%s,'Chưa giải quyết')
    """, (nv_id, so_no, thang, nam, gc))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True})

# ─────────────────────────────────────────────────────────────────────────
# GET / — Trả về Dashboard HTML động
# ─────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# DELETE /api/nhan-vien/<int:id> — Xóa nhân viên
# ─────────────────────────────────────────────────────────────────
@app.route('/api/nhan-vien/<int:id>', methods=['DELETE'])
def xoa_nhan_vien(id):
    conn = get_conn()
    cursor = conn.cursor()
    # Kiểm tra xem có dính dữ liệu không
    cursor.execute("SELECT COUNT(*) FROM LuongChinhThuc WHERE nhan_vien_id=%s", (id,))
    if cursor.fetchone()[0] > 0:
        cursor.close(); conn.close()
        return jsonify({"error": "Không thể xóa: Nhân viên đã có dữ liệu Lương chính thức."}), 400
    
    cursor.execute("SELECT COUNT(*) FROM ChiPhiKhoan WHERE nhan_vien_id=%s", (id,))
    if cursor.fetchone()[0] > 0:
        cursor.close(); conn.close()
        return jsonify({"error": "Không thể xóa: Nhân viên đã có dữ liệu Chi phí khoán."}), 400
        
    cursor.execute("SELECT COUNT(*) FROM CongNo WHERE nhan_vien_id=%s", (id,))
    if cursor.fetchone()[0] > 0:
        cursor.close(); conn.close()
        return jsonify({"error": "Không thể xóa: Nhân viên đang có dữ liệu Công nợ."}), 400

    # Nếu an toàn, tiến hành xóa
    cursor.execute("DELETE FROM NhanVien WHERE id=%s", (id,))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"success": True, "message": "Đã xóa nhân viên khỏi hệ thống."})

@app.route('/', methods=['GET'])
def render_dashboard():
    html = generate_html()
    return html

if __name__ == '__main__':
    print("=" * 60)
    print("  [API] Server running at http://localhost:5055")
    print("  [API] Press CTRL+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5055, debug=False)
