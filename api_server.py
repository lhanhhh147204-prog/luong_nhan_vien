"""
api_server.py - Flask API Backend cho Dashboard Kế Toán Tiền Lương
Cổng: http://localhost:5055
Vercel: https://bangluong-seven.vercel.app

Phiên bản: 2.1 — Tối ưu hoá toàn diện & Tuân thủ Chuẩn Kế toán
  - Quản lý vòng đời kết nối DB qua Flask `g` và `teardown_appcontext` (chống rò rỉ connection pool)
  - Error handling tập trung trên tất cả routes
  - Đầy đủ CRUD endpoints (GET/POST/PATCH/DELETE)
  - Audit Trail tự động ghi lại mọi thao tác thêm/sửa/xóa vào bảng auditlog (QT-001)
  - Endpoint nhật ký kiểm toán: GET /api/nhat-ky
  - Endpoint báo cáo tháng, thống kê tổng hợp & kiểm tra bất thường
  - Logging chuẩn mực
"""
import os
import json
import logging
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import db_config
from update_dashboard import generate_html

# ─────────────────────────────────────────────
# CẤU HÌNH LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Cho phép Dashboard HTML gọi API

# ─────────────────────────────────────────────
# QUẢN LÝ KẾT NỐI DB (Flask `g` lifecycle)
# ─────────────────────────────────────────────
def get_conn():
    """
    Lấy kết nối DB từ context `g` của request.
    Nếu chưa có hoặc bị đóng, tạo kết nối mới.
    """
    if 'db_conn' not in g or g.db_conn.closed:
        g.db_conn = db_config.get_db_connection()
    return g.db_conn

@app.teardown_appcontext
def teardown_db(exception=None):
    """Tự động đóng kết nối sau khi mỗi request kết thúc (tránh rò rỉ connection pool)."""
    conn = g.pop('db_conn', None)
    if conn is not None and not conn.closed:
        try:
            conn.close()
        except Exception:
            pass

# ─────────────────────────────────────────────
# AUDIT LOGGING HELPER (Quy định QT-001)
# ─────────────────────────────────────────────
def record_audit(cursor, bang, hanh_dong, du_lieu_cu=None, du_lieu_moi=None, nguoi="Kế toán", ghi_chu=""):
    """
    Ghi nhật ký thay đổi vào bảng auditlog.
    """
    try:
        cursor.execute("""
            INSERT INTO auditlog (bang_lien_quan, hanh_dong, du_lieu_cu, du_lieu_moi, nguoi_thuc_hien, thoi_gian, ghi_chu)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            bang,
            hanh_dong,
            json.dumps(du_lieu_cu, ensure_ascii=False) if du_lieu_cu else None,
            json.dumps(du_lieu_moi, ensure_ascii=False) if du_lieu_moi else None,
            nguoi,
            ghi_chu
        ))
    except Exception as e:
        logger.warning("Không thể ghi auditlog: %s", e)

# ─────────────────────────────────────────────
# DECORATOR: Xử lý lỗi tập trung
# ─────────────────────────────────────────────
def handle_errors(f):
    """Bọc mọi route — trả về JSON lỗi chuẩn mực thay vì crash 500 không kiểm soát."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (ValueError, TypeError) as e:
            logger.warning("Dữ liệu đầu vào không hợp lệ tại %s: %s", request.path, e)
            return jsonify({"error": f"Dữ liệu không hợp lệ: {e}"}), 400
        except Exception as e:
            logger.error("Lỗi server tại %s: %s", request.path, e, exc_info=True)
            return jsonify({"error": "Lỗi server nội bộ. Vui lòng thử lại."}), 500
    return wrapper

# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.route('/api/health', methods=['GET'])
@handle_errors
def health_check():
    """
    GET /api/health — Kiểm tra kết nối DB và trạng thái server.
    """
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
    return jsonify({
        "status": "ok",
        "database": "connected",
        "db_version": version
    })

# =============================================================================
# NHÂN VIÊN
# =============================================================================

@app.route('/api/nhan-vien', methods=['GET'])
@handle_errors
def get_nhan_vien():
    """
    GET /api/nhan-vien — Lấy danh sách nhân viên.
    Query params: ?loai_nhan_su=1
    """
    loai_filter = request.args.get('loai_nhan_su')
    conn = get_conn()
    with conn.cursor() as cursor:
        if loai_filter:
            cursor.execute("""
                SELECT id, ho_ten, chuc_vu, loai_nhan_su, ngay_vao_lam,
                       ma_so_thue, so_npt, cam_ket_08
                FROM NhanVien
                WHERE loai_nhan_su = %s
                ORDER BY ho_ten
            """, (int(loai_filter),))
        else:
            cursor.execute("""
                SELECT id, ho_ten, chuc_vu, loai_nhan_su, ngay_vao_lam,
                       ma_so_thue, so_npt, cam_ket_08
                FROM NhanVien
                ORDER BY loai_nhan_su, ho_ten
            """)
        result = []
        for r in cursor.fetchall():
            result.append({
                "id":           r[0],
                "ho_ten":       r[1],
                "chuc_vu":      r[2] or "",
                "loai_nhan_su": r[3],
                "ngay_vao_lam": r[4].isoformat() if r[4] else None,
                "ma_so_thue":   r[5] or "",
                "so_npt":       r[6] if r[6] is not None else 0,
                "cam_ket_08":   bool(r[7]) if r[7] is not None else False,
            })
    return jsonify(result)


@app.route('/api/nhan-vien', methods=['POST'])
@handle_errors
def them_nhan_vien():
    """
    POST /api/nhan-vien — Thêm mới nhân viên kèm ghi Audit Trail.
    """
    data = request.json or {}
    ho_ten   = str(data.get('ho_ten', '')).strip()
    chuc_vu  = str(data.get('chuc_vu', '')).strip()
    loai     = int(data.get('loai_nhan_su', 1))
    nvl      = data.get('ngay_vao_lam') or None
    mst      = str(data.get('ma_so_thue', '')).strip() or None
    so_npt   = int(data.get('so_npt', 0))
    cam_ket  = bool(data.get('cam_ket_08', False))

    if not ho_ten:
        return jsonify({"error": "Họ tên không được trống"}), 400
    if loai not in (1, 2):
        return jsonify({"error": "loai_nhan_su phải là 1 (HĐLĐ) hoặc 2 (Khoán)"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM NhanVien WHERE ho_ten = %s", (ho_ten,))
        if cursor.fetchone():
            return jsonify({"error": f"Nhân viên '{ho_ten}' đã tồn tại"}), 409

        cursor.execute("""
            INSERT INTO NhanVien (ho_ten, chuc_vu, loai_nhan_su, ngay_vao_lam, ma_so_thue, so_npt, cam_ket_08)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (ho_ten, chuc_vu, loai, nvl, mst, so_npt, cam_ket))
        new_id = cursor.fetchone()[0]

        record_audit(
            cursor=cursor,
            bang="NhanVien",
            hanh_dong="INSERT",
            du_lieu_moi={"id": new_id, "ho_ten": ho_ten, "chuc_vu": chuc_vu, "loai_nhan_su": loai},
            ghi_chu=f"Thêm nhân viên mới '{ho_ten}'"
        )
    conn.commit()
    logger.info("Thêm nhân viên mới: %s (id=%d)", ho_ten, new_id)
    return jsonify({"success": True, "id": new_id, "ho_ten": ho_ten}), 201


@app.route('/api/nhan-vien/<int:nv_id>', methods=['GET'])
@handle_errors
def get_nhan_vien_by_id(nv_id):
    """
    GET /api/nhan-vien/<id> — Chi tiết nhân viên.
    """
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, ho_ten, chuc_vu, loai_nhan_su, ngay_vao_lam,
                   ma_so_thue, so_npt, cam_ket_08
            FROM NhanVien WHERE id = %s
        """, (nv_id,))
        r = cursor.fetchone()
    if not r:
        return jsonify({"error": "Không tìm thấy nhân viên"}), 404
    return jsonify({
        "id":           r[0],
        "ho_ten":       r[1],
        "chuc_vu":      r[2] or "",
        "loai_nhan_su": r[3],
        "ngay_vao_lam": r[4].isoformat() if r[4] else None,
        "ma_so_thue":   r[5] or "",
        "so_npt":       r[6] if r[6] is not None else 0,
        "cam_ket_08":   bool(r[7]) if r[7] is not None else False,
    })


@app.route('/api/nhan-vien/<int:nv_id>', methods=['PUT', 'PATCH'])
@handle_errors
def cap_nhat_nhan_vien(nv_id):
    """
    PUT/PATCH /api/nhan-vien/<id> — Cập nhật nhân viên kèm Audit Trail.
    """
    data = request.json or {}
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT chuc_vu, loai_nhan_su, ma_so_thue, so_npt, cam_ket_08, ho_ten
            FROM NhanVien WHERE id = %s
        """, (nv_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Không tìm thấy nhân viên"}), 404

        old_data = {
            "chuc_vu": row[0],
            "loai_nhan_su": row[1],
            "ma_so_thue": row[2],
            "so_npt": row[3],
            "cam_ket_08": row[4]
        }
        ho_ten   = row[5]
        chuc_vu  = data.get('chuc_vu', row[0])
        loai     = int(data.get('loai_nhan_su', row[1]))
        mst      = data.get('ma_so_thue', row[2])
        so_npt   = int(data.get('so_npt', row[3] if row[3] is not None else 0))
        cam_ket  = bool(data.get('cam_ket_08', row[4] if row[4] is not None else False))

        cursor.execute("""
            UPDATE NhanVien
            SET chuc_vu=%s, loai_nhan_su=%s, ma_so_thue=%s, so_npt=%s, cam_ket_08=%s
            WHERE id=%s
        """, (chuc_vu, loai, mst, so_npt, cam_ket, nv_id))

        new_data = {
            "chuc_vu": chuc_vu,
            "loai_nhan_su": loai,
            "ma_so_thue": mst,
            "so_npt": so_npt,
            "cam_ket_08": cam_ket
        }

        record_audit(
            cursor=cursor,
            bang="NhanVien",
            hanh_dong="UPDATE",
            du_lieu_cu=old_data,
            du_lieu_moi=new_data,
            ghi_chu=f"Cập nhật thông tin nhân viên '{ho_ten}' (id={nv_id})"
        )
    conn.commit()
    logger.info("Cập nhật nhân viên id=%d", nv_id)
    return jsonify({"success": True, "id": nv_id})


@app.route('/api/nhan-vien/<int:nv_id>', methods=['DELETE'])
@handle_errors
def xoa_nhan_vien(nv_id):
    """
    DELETE /api/nhan-vien/<id> — Xóa nhân viên kèm Audit Trail (chặn nếu có dữ liệu liên kết).
    """
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT ho_ten FROM NhanVien WHERE id=%s", (nv_id,))
        nv = cursor.fetchone()
        if not nv:
            return jsonify({"error": "Không tìm thấy nhân viên"}), 404
        ho_ten = nv[0]

        for table, label in [
            ("LuongChinhThuc", "Lương chính thức"),
            ("ChiPhiKhoan",    "Chi phí khoán"),
            ("CongNo",         "Công nợ"),
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE nhan_vien_id=%s", (nv_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({"error": f"Không thể xóa: Nhân viên đã có dữ liệu {label}."}), 400

        cursor.execute("DELETE FROM NhanVien WHERE id=%s", (nv_id,))
        record_audit(
            cursor=cursor,
            bang="NhanVien",
            hanh_dong="DELETE",
            du_lieu_cu={"id": nv_id, "ho_ten": ho_ten},
            ghi_chu=f"Xóa nhân viên '{ho_ten}' (id={nv_id})"
        )
    conn.commit()
    logger.info("Xóa nhân viên id=%d (%s)", nv_id, ho_ten)
    return jsonify({"success": True, "message": f"Đã xóa nhân viên '{ho_ten}' khỏi hệ thống."})

# =============================================================================
# LƯƠNG CHÍNH THỨC
# =============================================================================

@app.route('/api/luong', methods=['GET'])
@handle_errors
def get_luong():
    """
    GET /api/luong — Lấy bảng lương.
    Query params: ?nhan_vien_id=X | ?thang=Tháng+9
    """
    nv_id = request.args.get('nhan_vien_id')
    thang = request.args.get('thang')
    params = []
    where  = []
    if nv_id:
        where.append("l.nhan_vien_id = %s")
        params.append(int(nv_id))
    if thang:
        where.append("l.thang = %s")
        params.append(thang)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT l.id, l.nhan_vien_id, n.ho_ten, l.thang,
                   l.gross, l.bhxh_nld, l.thue_tncn, l.thuc_nhan_net, l.ghi_chu
            FROM LuongChinhThuc l
            JOIN NhanVien n ON l.nhan_vien_id = n.id
            {where_sql}
            ORDER BY l.thang DESC, n.ho_ten
        """, params)
        result = []
        for r in cursor.fetchall():
            result.append({
                "id":            r[0],
                "nhan_vien_id":  r[1],
                "ho_ten":        r[2],
                "thang":         r[3],
                "gross":         float(r[4]),
                "bhxh_nld":      float(r[5]),
                "thue_tncn":     float(r[6]),
                "thuc_nhan_net": float(r[7]),
                "ghi_chu":       r[8] or "",
            })
    return jsonify(result)


@app.route('/api/luong', methods=['POST'])
@handle_errors
def nhap_luong():
    """
    POST /api/luong — Nhập hoặc cập nhật lương 1 nhân viên kèm Audit Trail.
    """
    data = request.json or {}
    nv_id  = int(data['nhan_vien_id'])
    thang  = str(data.get('thang', '')).strip()
    gross  = float(data.get('gross', 0))
    bh_nld = float(data.get('bhxh_nld', 0))
    tncn   = float(data.get('thue_tncn', 0))
    net    = float(data.get('thuc_nhan_net', 0))

    if not thang or gross <= 0:
        return jsonify({"error": "Thiếu thông tin bắt buộc (thang, gross > 0)"}), 400

    net_calc = gross - bh_nld - tncn
    ghi_chu  = ""
    if abs(net_calc - net) > 100:
        ghi_chu = f"[!] LỆCH: Excel={net:,.0f}, Tính={net_calc:,.0f}"

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, gross, bhxh_nld, thue_tncn, thuc_nhan_net FROM LuongChinhThuc WHERE nhan_vien_id=%s AND thang=%s", (nv_id, thang))
        existing = cursor.fetchone()
        new_payload = {"nhan_vien_id": nv_id, "thang": thang, "gross": gross, "bhxh_nld": bh_nld, "thue_tncn": tncn, "thuc_nhan_net": net}
        if existing:
            old_payload = {"gross": existing[1], "bhxh_nld": existing[2], "thue_tncn": existing[3], "thuc_nhan_net": existing[4]}
            cursor.execute("""
                UPDATE LuongChinhThuc
                SET gross=%s, bhxh_nld=%s, thue_tncn=%s, thuc_nhan_net=%s, ghi_chu=%s
                WHERE nhan_vien_id=%s AND thang=%s
            """, (gross, bh_nld, tncn, net, ghi_chu, nv_id, thang))
            action = "updated"
            record_audit(cursor, "LuongChinhThuc", "UPDATE", old_payload, new_payload, ghi_chu=f"Cập nhật lương NV {nv_id} kỳ {thang}")
        else:
            cursor.execute("""
                INSERT INTO LuongChinhThuc (nhan_vien_id, thang, gross, bhxh_nld, thue_tncn, thuc_nhan_net, ghi_chu)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nv_id, thang, gross, bh_nld, tncn, net, ghi_chu))
            action = "inserted"
            record_audit(cursor, "LuongChinhThuc", "INSERT", None, new_payload, ghi_chu=f"Nhập lương mới NV {nv_id} kỳ {thang}")
    conn.commit()
    logger.info("POST /api/luong %s NV_ID=%d %s", action, nv_id, thang)
    return jsonify({
        "success":       True,
        "action":        action,
        "ghi_chu":       ghi_chu,
        "net_tinh_toan": net_calc,
    })

# =============================================================================
# CHI PHÍ KHOÁN
# =============================================================================

@app.route('/api/khoan', methods=['GET'])
@handle_errors
def get_khoan():
    """
    GET /api/khoan — Lấy chi phí khoán.
    Query params: ?thang=Tháng+9 | ?nhan_vien_id=X
    """
    nv_id = request.args.get('nhan_vien_id')
    thang = request.args.get('thang')
    params = []
    where  = []
    if nv_id:
        where.append("c.nhan_vien_id = %s")
        params.append(int(nv_id))
    if thang:
        where.append("c.thang = %s")
        params.append(thang)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT c.id, c.nhan_vien_id, n.ho_ten, c.thang, c.so_tien, c.ghi_chu
            FROM ChiPhiKhoan c
            JOIN NhanVien n ON c.nhan_vien_id = n.id
            {where_sql}
            ORDER BY c.thang DESC, n.ho_ten
        """, params)
        result = []
        for r in cursor.fetchall():
            result.append({
                "id":           r[0],
                "nhan_vien_id": r[1],
                "ho_ten":       r[2],
                "thang":        r[3],
                "so_tien":      float(r[4]),
                "ghi_chu":      r[5] or "",
            })
    return jsonify(result)


@app.route('/api/khoan', methods=['POST'])
@handle_errors
def nhap_khoan():
    """
    POST /api/khoan — Nhập chi phí khoán kèm Audit Trail.
    """
    data = request.json or {}
    nv_id   = int(data['nhan_vien_id'])
    thang   = str(data.get('thang', '')).strip()
    so_tien = float(data.get('so_tien', 0))
    ghi_chu = str(data.get('ghi_chu', '')).strip()
    if not thang or so_tien <= 0:
        return jsonify({"error": "Thiếu thông tin bắt buộc (thang, so_tien > 0)"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, so_tien FROM ChiPhiKhoan WHERE nhan_vien_id=%s AND thang=%s", (nv_id, thang))
        existing = cursor.fetchone()
        payload = {"nhan_vien_id": nv_id, "thang": thang, "so_tien": so_tien, "ghi_chu": ghi_chu}
        if existing:
            cursor.execute("""
                UPDATE ChiPhiKhoan SET so_tien=%s, ghi_chu=%s
                WHERE nhan_vien_id=%s AND thang=%s
            """, (so_tien, ghi_chu, nv_id, thang))
            action = "updated"
            record_audit(cursor, "ChiPhiKhoan", "UPDATE", {"so_tien": existing[1]}, payload, ghi_chu=f"Cập nhật khoán NV {nv_id} kỳ {thang}")
        else:
            cursor.execute("""
                INSERT INTO ChiPhiKhoan (nhan_vien_id, thang, so_tien, ghi_chu)
                VALUES (%s, %s, %s, %s)
            """, (nv_id, thang, so_tien, ghi_chu))
            action = "inserted"
            record_audit(cursor, "ChiPhiKhoan", "INSERT", None, payload, ghi_chu=f"Nhập khoán mới NV {nv_id} kỳ {thang}")
    conn.commit()
    return jsonify({"success": True, "action": action})

# =============================================================================
# CÔNG NỢ
# =============================================================================

@app.route('/api/cong-no', methods=['GET'])
@handle_errors
def get_cong_no():
    """
    GET /api/cong-no — Lấy danh sách công nợ.
    Query params: ?trang_thai=Chưa+giải+quyết | ?nhan_vien_id=X
    """
    trang_thai = request.args.get('trang_thai')
    nv_id      = request.args.get('nhan_vien_id')
    params = []
    where  = []
    if trang_thai:
        where.append("cn.trang_thai = %s")
        params.append(trang_thai)
    if nv_id:
        where.append("cn.nhan_vien_id = %s")
        params.append(int(nv_id))
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT cn.id, cn.nhan_vien_id, n.ho_ten,
                   cn.so_tien_no, cn.thang_phat_sinh, cn.nam_phat_sinh,
                   cn.ghi_chu, cn.trang_thai
            FROM CongNo cn
            JOIN NhanVien n ON cn.nhan_vien_id = n.id
            {where_sql}
            ORDER BY cn.nam_phat_sinh DESC, cn.thang_phat_sinh DESC
        """, params)
        result = []
        for r in cursor.fetchall():
            result.append({
                "id":               r[0],
                "nhan_vien_id":     r[1],
                "ho_ten":           r[2],
                "so_tien_no":       float(r[3]),
                "thang_phat_sinh":  r[4],
                "nam_phat_sinh":    r[5],
                "ghi_chu":          r[6] or "",
                "trang_thai":       r[7],
            })
    return jsonify(result)


@app.route('/api/cong-no', methods=['POST'])
@handle_errors
def nhap_cong_no():
    """
    POST /api/cong-no — Nhập công nợ mới kèm Audit Trail.
    """
    data = request.json or {}
    nv_id = int(data['nhan_vien_id'])
    so_no = float(data.get('so_tien_no', 0))
    thang = data.get('thang_phat_sinh', '1')
    nam   = int(data.get('nam_phat_sinh', 2026))
    gc    = str(data.get('ghi_chu', '')).strip()

    if so_no <= 0:
        return jsonify({"error": "Số tiền nợ phải > 0"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO CongNo (nhan_vien_id, so_tien_no, thang_phat_sinh, nam_phat_sinh, ghi_chu, trang_thai)
            VALUES (%s, %s, %s, %s, %s, 'Chưa giải quyết')
            RETURNING id
        """, (nv_id, so_no, str(thang), nam, gc))
        new_id = cursor.fetchone()[0]

        record_audit(
            cursor, "CongNo", "INSERT",
            None,
            {"id": new_id, "nhan_vien_id": nv_id, "so_tien_no": so_no, "thang": thang, "nam": nam},
            ghi_chu=f"Ghi nhận công nợ mới NV {nv_id}: {so_no:,.0f} đ"
        )
    conn.commit()
    logger.info("Nhập công nợ mới id=%d NV_ID=%d %.0f", new_id, nv_id, so_no)
    return jsonify({"success": True, "id": new_id}), 201


@app.route('/api/cong-no/<int:cn_id>', methods=['PATCH'])
@handle_errors
def cap_nhat_cong_no(cn_id):
    """
    PATCH /api/cong-no/<id> — Cập nhật trạng thái công nợ kèm Audit Trail.
    Body: { trang_thai: "Đã giải quyết" | "Chưa giải quyết" }
    """
    data       = request.json or {}
    trang_thai = str(data.get('trang_thai', '')).strip()
    VALID = ("Đã giải quyết", "Chưa giải quyết")
    if trang_thai not in VALID:
        return jsonify({"error": f"trang_thai phải là một trong: {VALID}"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, trang_thai, nhan_vien_id, so_tien_no FROM CongNo WHERE id=%s", (cn_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Không tìm thấy công nợ"}), 404
        old_tt = row[1]
        cursor.execute("UPDATE CongNo SET trang_thai=%s WHERE id=%s", (trang_thai, cn_id))

        record_audit(
            cursor, "CongNo", "UPDATE",
            {"trang_thai": old_tt},
            {"trang_thai": trang_thai},
            ghi_chu=f"Đổi trạng thái công nợ #{cn_id} từ '{old_tt}' -> '{trang_thai}'"
        )
    conn.commit()
    return jsonify({"success": True, "id": cn_id, "trang_thai": trang_thai})

# =============================================================================
# NHẬT KÝ KIỂM TOÁN (AUDIT TRAIL)
# =============================================================================

@app.route('/api/nhat-ky', methods=['GET'])
@handle_errors
def get_audit_log():
    """
    GET /api/nhat-ky — Truy vấn nhật ký thay đổi dữ liệu của hệ thống.
    Query params: ?limit=50&offset=0
    """
    limit  = min(int(request.args.get('limit', 50)), 200)
    offset = max(int(request.args.get('offset', 0)), 0)

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auditlog")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT id, bang_lien_quan, hanh_dong, du_lieu_cu, du_lieu_moi,
                   nguoi_thuc_hien, thoi_gian, ghi_chu
            FROM auditlog
            ORDER BY thoi_gian DESC, id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        logs = []
        for r in cursor.fetchall():
            logs.append({
                "id":              r[0],
                "bang_lien_quan":  r[1],
                "hanh_dong":       r[2],
                "du_lieu_cu":      json.loads(r[3]) if r[3] else None,
                "du_lieu_moi":     json.loads(r[4]) if r[4] else None,
                "nguoi_thuc_hien": r[5] or "Hệ thống",
                "thoi_gian":       r[6].isoformat() if r[6] else None,
                "ghi_chu":          r[7] or "",
            })
    return jsonify({
        "tong_so": logs and total or 0,
        "limit":   limit,
        "offset":  offset,
        "nhat_ky": logs
    })

# =============================================================================
# THỐNG KÊ TỔNG HỢP
# =============================================================================

@app.route('/api/thong-ke', methods=['GET'])
@handle_errors
def thong_ke():
    """
    GET /api/thong-ke — Thống kê tổng quan tình hình nhân sự, tiền lương, công nợ.
    Query param: ?thang=Tháng+9
    """
    thang = request.args.get('thang')
    conn = get_conn()
    with conn.cursor() as cursor:
        # Nhân sự
        cursor.execute("SELECT loai_nhan_su, COUNT(*) FROM NhanVien GROUP BY loai_nhan_su")
        nv_counts = {r[0]: r[1] for r in cursor.fetchall()}

        # Lương chính thức
        if thang:
            cursor.execute("""
                SELECT COUNT(*), SUM(gross), SUM(bhxh_nld), SUM(thue_tncn), SUM(thuc_nhan_net)
                FROM LuongChinhThuc WHERE thang = %s
            """, (thang,))
        else:
            cursor.execute("""
                SELECT COUNT(*), SUM(gross), SUM(bhxh_nld), SUM(thue_tncn), SUM(thuc_nhan_net)
                FROM LuongChinhThuc
            """)
        lr = cursor.fetchone()

        # Công nợ
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(so_tien_no), 0) FROM CongNo WHERE trang_thai = 'Chưa giải quyết'")
        cr = cursor.fetchone()

        # Chi phí khoán
        if thang:
            cursor.execute("SELECT COALESCE(SUM(so_tien), 0) FROM ChiPhiKhoan WHERE thang = %s", (thang,))
        else:
            cursor.execute("SELECT COALESCE(SUM(so_tien), 0) FROM ChiPhiKhoan")
        tong_khoan = cursor.fetchone()[0]

    return jsonify({
        "nhan_vien": {
            "hdld":  nv_counts.get(1, 0),
            "khoan": nv_counts.get(2, 0),
            "tong":  sum(nv_counts.values()),
        },
        "luong": {
            "so_ban_ghi":   int(lr[0]) if lr[0] else 0,
            "tong_gross":   float(lr[1]) if lr[1] else 0,
            "tong_bhxh":    float(lr[2]) if lr[2] else 0,
            "tong_tncn":    float(lr[3]) if lr[3] else 0,
            "tong_net":     float(lr[4]) if lr[4] else 0,
        },
        "khoan": {
            "tong_chi_phi": float(tong_khoan),
        },
        "cong_no": {
            "so_khoan_chua_giai_quyet": int(cr[0]),
            "tong_tien_no":             float(cr[1]),
        },
        "thang_filter": thang or "Tất cả",
    })

# =============================================================================
# BÁO CÁO THÁNG
# =============================================================================

@app.route('/api/bao-cao/<thang>', methods=['GET'])
@handle_errors
def bao_cao_thang(thang):
    """
    GET /api/bao-cao/<thang> — Báo cáo bảng lương chi tiết theo tháng (JSON).
    """
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT n.id, n.ho_ten, n.chuc_vu, n.loai_nhan_su,
                   l.gross, l.bhxh_nld, l.thue_tncn, l.thuc_nhan_net, l.ghi_chu,
                   COALESCE(k.so_tien, 0) AS tien_khoan
            FROM NhanVien n
            LEFT JOIN LuongChinhThuc l ON l.nhan_vien_id = n.id AND l.thang = %s
            LEFT JOIN ChiPhiKhoan k   ON k.nhan_vien_id = n.id AND k.thang = %s
            ORDER BY n.loai_nhan_su, n.ho_ten
        """, (thang, thang))
        rows = cursor.fetchall()

    ds = []
    tong = {"gross": 0, "bhxh": 0, "tncn": 0, "net": 0, "khoan": 0}
    for r in rows:
        g  = float(r[4]) if r[4] else 0
        bh = float(r[5]) if r[5] else 0
        tc = float(r[6]) if r[6] else 0
        nt = float(r[7]) if r[7] else 0
        kh = float(r[9]) if r[9] else 0
        tong["gross"] += g
        tong["bhxh"]  += bh
        tong["tncn"]  += tc
        tong["net"]   += nt
        tong["khoan"] += kh
        ds.append({
            "id":            r[0],
            "ho_ten":        r[1],
            "chuc_vu":       r[2] or "",
            "loai_nhan_su":  r[3],
            "gross":         g,
            "bhxh_nld":      bh,
            "thue_tncn":     tc,
            "thuc_nhan_net": nt,
            "tien_khoan":    kh,
            "ghi_chu":       r[8] or "",
        })
    return jsonify({
        "thang":        thang,
        "so_nhan_vien": len([x for x in ds if x["gross"] > 0]),
        "chi_tiet":     ds,
        "tong_cong":    tong,
    })

# =============================================================================
# KIỂM TRA BẤT THƯỜNG (ANOMALY DETECTION)
# =============================================================================

@app.route('/api/kiem-tra', methods=['GET'])
@handle_errors
def kiem_tra_bat_thuong():
    """
    GET /api/kiem-tra — Chạy quét toàn diện rủi ro thuế và bất thường lương.
    """
    from tax_engine import run_anomaly_detection
    anomalies = run_anomaly_detection()
    return jsonify({
        "so_canh_bao": len(anomalies),
        "canh_bao":    anomalies,
    })

# =============================================================================
# DASHBOARD HTML
# =============================================================================

@app.route('/', methods=['GET'])
@handle_errors
def render_dashboard():
    """
    GET / — Render Dashboard HTML tương tác trực quan.
    """
    html = generate_html()
    return html

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  [API] Server running at http://localhost:5055")
    print("  [API] Press CTRL+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5055, debug=False)
