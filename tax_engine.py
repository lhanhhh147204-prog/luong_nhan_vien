import db_config

DB_NAME = "QL_LUONG"
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE={DB_NAME};Trusted_Connection=yes;'

# =========================================================================
# THUẬT TOÁN 1: THUẾ THU NHẬP CÁ NHÂN (TNCN) - Lũy tiến 7 bậc
# =========================================================================
def calc_tncn_luy_tien(thu_nhap_chiu_thue):
    """
    Tính thuế TNCN lũy tiến 7 bậc cho nhân sự Hợp Đồng Lao Động.
    """
    if thu_nhap_chiu_thue <= 0: 
        return 0
    tax = 0
    if thu_nhap_chiu_thue <= 5000000:
        tax = thu_nhap_chiu_thue * 0.05
    elif thu_nhap_chiu_thue <= 10000000:
        tax = 5000000 * 0.05 + (thu_nhap_chiu_thue - 5000000) * 0.10
    elif thu_nhap_chiu_thue <= 18000000:
        tax = 250000 + 500000 + (thu_nhap_chiu_thue - 10000000) * 0.15
    elif thu_nhap_chiu_thue <= 32000000:
        tax = 750000 + 1200000 + (thu_nhap_chiu_thue - 18000000) * 0.20
    elif thu_nhap_chiu_thue <= 52000000:
        tax = 1950000 + 2800000 + (thu_nhap_chiu_thue - 32000000) * 0.25
    elif thu_nhap_chiu_thue <= 80000000:
        tax = 4750000 + 5000000 + (thu_nhap_chiu_thue - 52000000) * 0.30
    else:
        tax = 9750000 + 8400000 + (thu_nhap_chiu_thue - 80000000) * 0.35
    return tax

def tinh_thue_cho_nhan_vien(gross, bhxh, so_npt):
    """
    Tính toán Thuế TNCN dựa trên Gross, BHXH và Giảm trừ người phụ thuộc.
    Mức giảm trừ bản thân (Luật 2020+): 11.000.000đ/tháng
    Mức giảm trừ NPT (Luật 2020+): 4.400.000đ/người/tháng
    """
    giam_tru_ban_than = 11000000
    giam_tru_npt = 4400000 * so_npt
    thu_nhap_chiu_thue = gross - bhxh - giam_tru_ban_than - giam_tru_npt
    return calc_tncn_luy_tien(thu_nhap_chiu_thue)

# =========================================================================
# THUẬT TOÁN 2: THUẾ KHOÁN 10% (Vãng Lai / Đội Khoán)
# =========================================================================
def calc_thue_khoan(so_tien_khoan, co_cam_ket_08=False):
    """
    Tính thuế thu nhập cá nhân tự do/khoán việc (10%).
    Luật: Khấu trừ 10% nếu thu nhập từ 2 triệu VNĐ trở lên, trừ khi có Bản cam kết 08.
    """
    if so_tien_khoan >= 2000000 and not co_cam_ket_08:
        return so_tien_khoan * 0.10
    return 0

# =========================================================================
# THUẬT TOÁN 3: PHÁT HIỆN BẤT THƯỜNG (ANOMALY DETECTION)
# =========================================================================
def run_anomaly_detection():
    """
    Quét CSDL để tìm các dấu hiệu bất thường về lương, thuế, công nợ.
    Trả về danh sách các cảnh báo (List of dicts).
    """
    anomalies = []
    try:
        conn = db_config.get_db_connection()
        cursor = conn.cursor()
        
        # 1. Phát hiện thực lĩnh âm
        cursor.execute("SELECT id, nhan_vien_id, thang, thuc_nhan_net FROM LuongChinhThuc WHERE thuc_nhan_net < 0")
        for row in cursor.fetchall():
            anomalies.append({"loai": "LỖI ÂM", "msg": f"Nhân viên ID {row[1]} có thực lĩnh âm ({row[3]:,.0f}) vào {row[2]}"})
            
        # 2. Phát hiện chi phí khoán > 2tr nhưng chưa khấu trừ thuế (Cảnh báo pháp lý)
        # Bỏ qua kiểm tra cam_ket_08 vì chưa đồng bộ lên Cloud
        cursor.execute("""
            SELECT c.nhan_vien_id, n.ho_ten, c.thang, c.so_tien 
            FROM ChiPhiKhoan c
            JOIN NhanVien n ON c.nhan_vien_id = n.id
            WHERE c.so_tien >= 2000000 AND n.loai_nhan_su = 2
        """)
        for row in cursor.fetchall():
            thue_phai_nop = calc_thue_khoan(row[3])
            anomalies.append({"loai": "RỦI RO THUẾ", "msg": f"{row[1]} nhận {row[3]:,.0f} đ vào {row[2]}. Cần khấu trừ 10% TNCN ({thue_phai_nop:,.0f} đ) hoặc bổ sung Cam kết 08."})
            
    except Exception as e:
        anomalies.append({"loai": "HỆ THỐNG", "msg": f"Lỗi truy vấn DB: {str(e)}"})
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
        
    return anomalies

if __name__ == "__main__":
    print("=== TEST TAX ENGINE ===")
    print(f"Thuế lũy tiến cho thu nhập 15,000,000 (đã trừ BHXH): {tinh_thue_cho_nhan_vien(15000000, 0, 0):,.0f} VNĐ")
    print(f"Thuế khoán cho thu nhập 2,500,000 (không cam kết): {calc_thue_khoan(2500000, False):,.0f} VNĐ")
    
    print("\n=== CHẠY PHÁT HIỆN BẤT THƯỜNG ===")
    anomalies = run_anomaly_detection()
    if anomalies:
        for a in anomalies:
            print(f"[{a['loai']}] {a['msg']}")
    else:
        print("Không phát hiện bất thường.")
