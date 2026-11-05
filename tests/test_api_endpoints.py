# -*- coding: utf-8 -*-
"""
test_api_endpoints.py - Kiểm thử toàn diện tất cả endpoints của api_server.py
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import app

def test_all():
    client = app.test_client()
    passed = 0
    total = 0

    def assert_test(name, cond, details=""):
        nonlocal passed, total
        total += 1
        if cond:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {details}")

    print("=== BAT DAU KIEM THU BACKEND API ===")

    # 1. Health check
    res = client.get('/api/health')
    assert_test("GET /api/health", res.status_code == 200 and res.json.get("status") == "ok", str(res.json))

    # 2. Get nhân viên
    res = client.get('/api/nhan-vien')
    assert_test("GET /api/nhan-vien", res.status_code == 200 and isinstance(res.json, list) and len(res.json) > 0, f"count={len(res.json) if res.json else 0}")
    
    # 3. Thống kê tổng hợp
    res = client.get('/api/thong-ke')
    assert_test("GET /api/thong-ke", res.status_code == 200 and "nhan_vien" in res.json and "luong" in res.json, str(res.json))

    # 4. Thống kê theo tháng
    res = client.get('/api/thong-ke?thang=Th%C3%A1ng%209')
    assert_test("GET /api/thong-ke?thang=Tháng 9", res.status_code == 200 and res.json.get("thang_filter") == "Tháng 9")

    # 5. Báo cáo bảng lương tháng 9
    res = client.get('/api/bao-cao/Th%C3%A1ng%209')
    assert_test("GET /api/bao-cao/Tháng 9", res.status_code == 200 and "chi_tiet" in res.json and "tong_cong" in res.json)

    # 6. Danh sách lương
    res = client.get('/api/luong?thang=Th%C3%A1ng%209')
    assert_test("GET /api/luong?thang=Tháng 9", res.status_code == 200 and isinstance(res.json, list))

    # 7. Danh sách chi phí khoán
    res = client.get('/api/khoan')
    assert_test("GET /api/khoan", res.status_code == 200 and isinstance(res.json, list))

    # 8. Danh sách công nợ
    res = client.get('/api/cong-no')
    assert_test("GET /api/cong-no", res.status_code == 200 and isinstance(res.json, list) and len(res.json) > 0)

    # 9. Kiểm tra phát hiện bất thường
    res = client.get('/api/kiem-tra')
    assert_test("GET /api/kiem-tra (Anomaly Detection)", res.status_code == 200 and "canh_bao" in res.json)

    # 10. Test CRUD Nhân viên: Tạo thử, đọc, sửa, xóa
    test_nv_name = "__NV_TEST_TEMPORARY__"
    res = client.post('/api/nhan-vien', json={
        "ho_ten": test_nv_name,
        "chuc_vu": "Nhan Vien Test",
        "loai_nhan_su": 1,
        "so_npt": 1,
        "cam_ket_08": False
    })
    assert_test("POST /api/nhan-vien (Tao moi)", res.status_code == 201 and res.json.get("success") is True, str(res.json))
    
    if res.status_code == 201:
        nv_id = res.json["id"]

        # Chi tiết nhân viên
        res_get = client.get(f'/api/nhan-vien/{nv_id}')
        assert_test("GET /api/nhan-vien/<id>", res_get.status_code == 200 and res_get.json.get("ho_ten") == test_nv_name)

        # Cập nhật nhân viên
        res_patch = client.patch(f'/api/nhan-vien/{nv_id}', json={"chuc_vu": "Truong Phong Test", "so_npt": 2})
        assert_test("PATCH /api/nhan-vien/<id>", res_patch.status_code == 200 and res_patch.json.get("success") is True)

        # Xóa nhân viên test (vì chưa có bảng lương liên kết nên phải xóa thành công)
        res_del = client.delete(f'/api/nhan-vien/{nv_id}')
        assert_test("DELETE /api/nhan-vien/<id>", res_del.status_code == 200 and res_del.json.get("success") is True)

    # 11. Test Audit Log
    res_audit = client.get('/api/nhat-ky?limit=5')
    assert_test("GET /api/nhat-ky (Audit Trail)", res_audit.status_code == 200 and "nhat_ky" in res_audit.json and len(res_audit.json["nhat_ky"]) > 0)

    # 11. Test Validation: Thêm nhân viên họ tên trống
    res_val = client.post('/api/nhan-vien', json={"ho_ten": ""})
    assert_test("Validation: Ho ten trong -> 400", res_val.status_code == 400)

    # 12. Test Validation: Nhập lương số âm / trống
    res_luong_val = client.post('/api/luong', json={"nhan_vien_id": 1, "thang": "", "gross": -100})
    assert_test("Validation: Luong gross <= 0 -> 400", res_luong_val.status_code == 400)

    # 13. Test Render Dashboard
    res_dash = client.get('/')
    assert_test("GET / (Render Dashboard HTML)", res_dash.status_code == 200 and b"<!DOCTYPE html>" in res_dash.data)

    print("=" * 45)
    print(f"KET QUA: {passed}/{total} test cases PASSED")
    print("=" * 45)
    return passed == total

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
