"""
tax_engine.py — Thuật toán thuế & kiểm tra bất thường
Công Ty TNHH XD SX TM Nhôm Kính Hoàng Anh

Phiên bản 2.0:
  - Xóa dead code SQL Server (đã chuyển sang PostgreSQL/Supabase)
  - Sửa công thức TNCN lũy tiến 7 bậc (tích lũy đúng)
  - Anomaly detection hỗ trợ cam_ket_08 từ Supabase
"""
import db_config

# =========================================================================
# THUẬT TOÁN 1: THUẾ THU NHẬP CÁ NHÂN (TNCN) — Lũy tiến 7 bậc
# Căn cứ: Luật số 04/2007/QH12 sửa đổi theo Nghị quyết 954/2020/UBTVQH14
# Mức giảm trừ bản thân: 11.000.000 đ/tháng
# Mức giảm trừ NPT:      4.400.000 đ/người/tháng
# =========================================================================

# Bảng lũy tiến theo bậc: (ngưỡng_tích_lũy_tới, thuế_tích_lũy_tới_bậc_này, thuế_suất_bậc_tiếp)
_TNCN_BRACKETS = [
    (5_000_000,    0,          0.05),   # Bậc 1: 0  → 5tr       : 5%
    (10_000_000,   250_000,    0.10),   # Bậc 2: 5tr → 10tr     : 10%
    (18_000_000,   750_000,    0.15),   # Bậc 3: 10tr → 18tr    : 15%
    (32_000_000,   1_950_000,  0.20),   # Bậc 4: 18tr → 32tr    : 20%
    (52_000_000,   4_750_000,  0.25),   # Bậc 5: 32tr → 52tr    : 25%
    (80_000_000,   9_750_000,  0.30),   # Bậc 6: 52tr → 80tr    : 30%
    (float('inf'), 18_150_000, 0.35),   # Bậc 7: > 80tr         : 35%
]


def calc_tncn_luy_tien(thu_nhap_chiu_thue: float) -> float:
    """
    Tính thuế TNCN lũy tiến 7 bậc cho nhân sự Hợp Đồng Lao Động.

    Args:
        thu_nhap_chiu_thue: Thu nhập chịu thuế sau khi trừ BHXH và giảm trừ gia cảnh.
    Returns:
        Số thuế TNCN phải nộp (VNĐ).

    Kiểm tra nhanh (phải đúng):
        5.000.000  → 250.000
        10.000.000 → 750.000
        18.000.000 → 1.950.000
        32.000.000 → 4.750.000
        52.000.000 → 9.750.000
        80.000.000 → 18.150.000
    """
    if thu_nhap_chiu_thue <= 0:
        return 0.0

    prev_limit = 0
    for limit, tax_accumulated, rate in _TNCN_BRACKETS:
        if thu_nhap_chiu_thue <= limit:
            return tax_accumulated + (thu_nhap_chiu_thue - prev_limit) * rate
        prev_limit = limit

    # Không bao giờ tới đây (bậc 7 có limit = inf)
    return 0.0


def tinh_thue_cho_nhan_vien(gross: float, bhxh: float, so_npt: int) -> float:
    """
    Tính thuế TNCN từ Gross, BHXH NLĐ và số người phụ thuộc.

    Thu nhập chịu thuế = Gross − BHXH − Giảm trừ bản thân − Giảm trừ NPT
    """
    GIAM_TRU_BAN_THAN = 11_000_000
    GIAM_TRU_NPT      =  4_400_000
    thu_nhap_chiu_thue = gross - bhxh - GIAM_TRU_BAN_THAN - GIAM_TRU_NPT * so_npt
    return calc_tncn_luy_tien(thu_nhap_chiu_thue)


# =========================================================================
# THUẬT TOÁN 2: THUẾ KHOÁN 10% (Vãng Lai / Đội Khoán)
# Luật: Khấu trừ 10% nếu thu nhập từ 2.000.000 đ trở lên,
#        trừ khi cá nhân đã nộp Bản cam kết 08/CK-TNCN.
# =========================================================================
def calc_thue_khoan(so_tien_khoan: float, co_cam_ket_08: bool = False) -> float:
    """
    Tính thuế TNCN khoán việc / vãng lai.

    Returns:
        Số thuế phải khấu trừ (10% nếu >= 2tr và không có cam kết 08).
    """
    if so_tien_khoan >= 2_000_000 and not co_cam_ket_08:
        return so_tien_khoan * 0.10
    return 0.0


# =========================================================================
# THUẬT TOÁN 3: PHÁT HIỆN BẤT THƯỜNG (ANOMALY DETECTION)
# =========================================================================
def run_anomaly_detection() -> list:
    """
    Quét CSDL Supabase để tìm các dấu hiệu bất thường về lương, thuế, công nợ.
    Trả về danh sách các cảnh báo (list of dicts: {loai, msg}).
    """
    anomalies = []
    conn = None
    cursor = None
    try:
        conn = db_config.get_db_connection()
        cursor = conn.cursor()

        # 1. Thực lĩnh âm
        cursor.execute("""
            SELECT l.id, n.ho_ten, l.thang, l.thuc_nhan_net
            FROM LuongChinhThuc l
            JOIN NhanVien n ON l.nhan_vien_id = n.id
            WHERE l.thuc_nhan_net < 0
        """)
        for row in cursor.fetchall():
            anomalies.append({
                "loai": "LỖI ÂM",
                "msg":  f"{row[1]} có thực lĩnh âm ({row[3]:,.0f} đ) vào {row[2]}"
            })

        # 2. Chi phí khoán >= 2tr: kiểm tra cam_ket_08
        #    Nếu loai_nhan_su = 2 (khoán) và không có cam_ket_08 → cảnh báo thuế
        cursor.execute("""
            SELECT c.nhan_vien_id, n.ho_ten, c.thang, c.so_tien,
                   COALESCE(n.cam_ket_08, FALSE) AS cam_ket_08
            FROM ChiPhiKhoan c
            JOIN NhanVien n ON c.nhan_vien_id = n.id
            WHERE c.so_tien >= 2000000 AND n.loai_nhan_su = 2
        """)
        for row in cursor.fetchall():
            co_cam_ket = bool(row[4])
            thue = calc_thue_khoan(row[3], co_cam_ket)
            if thue > 0:
                anomalies.append({
                    "loai": "RỦI RO THUẾ",
                    "msg":  (
                        f"{row[1]} nhận {row[3]:,.0f} đ ({row[2]}). "
                        f"Phải khấu trừ 10% TNCN ({thue:,.0f} đ) "
                        f"hoặc bổ sung Cam kết 08/CK-TNCN."
                    )
                })

        # 3. Công nợ tồn đọng > 3 tháng
        cursor.execute("""
            SELECT cn.id, n.ho_ten, cn.thang_phat_sinh, cn.nam_phat_sinh, cn.so_tien_no
            FROM CongNo cn
            JOIN NhanVien n ON cn.nhan_vien_id = n.id
            WHERE cn.trang_thai = 'Chưa giải quyết'
              AND (cn.nam_phat_sinh::int * 12 + cn.thang_phat_sinh::int)
                  < (EXTRACT(YEAR FROM NOW())::int * 12 + EXTRACT(MONTH FROM NOW())::int - 3)
        """)
        for row in cursor.fetchall():
            anomalies.append({
                "loai": "CÔNG NỢ TỒN",
                "msg":  (
                    f"{row[1]} còn nợ {row[4]:,.0f} đ từ "
                    f"tháng {row[2]}/{row[3]} (> 3 tháng chưa giải quyết)."
                )
            })

        # 4. Lương gross = 0 nhưng vẫn có bản ghi
        cursor.execute("""
            SELECT l.id, n.ho_ten, l.thang
            FROM LuongChinhThuc l
            JOIN NhanVien n ON l.nhan_vien_id = n.id
            WHERE l.gross = 0 OR l.gross IS NULL
        """)
        for row in cursor.fetchall():
            anomalies.append({
                "loai": "DỮ LIỆU TRỐNG",
                "msg":  f"{row[1]} có bản ghi lương nhưng Gross = 0 vào {row[2]}."
            })

    except Exception as e:
        anomalies.append({"loai": "HỆ THỐNG", "msg": f"Lỗi truy vấn DB: {e}"})
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

    return anomalies


# =========================================================================
# SELF-TEST (chạy trực tiếp để kiểm tra)
# =========================================================================
if __name__ == "__main__":
    print("=== KIỂM TRA THUẾ TNCN LŨY TIẾN ===")
    test_cases = [
        (5_000_000,   250_000),
        (10_000_000,  750_000),
        (18_000_000,  1_950_000),
        (32_000_000,  4_750_000),
        (52_000_000,  9_750_000),
        (80_000_000,  18_150_000),
    ]
    all_pass = True
    for income, expected in test_cases:
        result = calc_tncn_luy_tien(income)
        ok = abs(result - expected) < 1
        status = "✓ OK" if ok else f"✗ LỖI (expected {expected:,.0f})"
        print(f"  {income/1e6:.0f}tr → {result:,.0f} đ  {status}")
        if not ok:
            all_pass = False
    print("Tất cả test cases:", "ĐẠT ✓" if all_pass else "CÓ LỖI ✗")

    print("\n=== KIỂM TRA THUẾ KHOÁN ===")
    print(f"  2.5tr, không cam kết → {calc_thue_khoan(2_500_000, False):,.0f} đ  (phải = 250.000)")
    print(f"  2.5tr, có cam kết    → {calc_thue_khoan(2_500_000, True):,.0f} đ   (phải = 0)")
    print(f"  1.5tr, không cam kết → {calc_thue_khoan(1_500_000, False):,.0f} đ  (phải = 0)")

    print("\n=== PHÁT HIỆN BẤT THƯỜNG ===")
    anomalies = run_anomaly_detection()
    if anomalies:
        for a in anomalies:
            print(f"  [{a['loai']}] {a['msg']}")
    else:
        print("  Không phát hiện bất thường.")
