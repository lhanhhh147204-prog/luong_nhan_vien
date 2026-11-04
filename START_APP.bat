@echo off
chcp 65001 > nul
echo ======================================================================
echo   HE THONG KE TOAN LUONG HOANG ANH - KHOI DONG HE THONG
echo ======================================================================
echo.
echo [1/2] Dang mo trinh duyet Dashboard: http://localhost:5055...
start http://localhost:5055
echo [2/2] Dang khoi dong API Server tren cong 5055...
echo Nhan Ctrl+C de dung server.
echo.
python api_server.py
pause
