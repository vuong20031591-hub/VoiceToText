@echo off
echo ========================================
echo   CAI DAT CAC THU VIEN CAN THIET
echo ========================================
echo.

echo [INFO] Kiem tra Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python khong duoc cai dat!
    echo Vui long cai dat Python 3.8+ tu https://python.org
    pause
    exit /b 1
)

echo.
echo [INFO] Nang cap pip...
python -m pip install --upgrade pip

echo.
echo [INFO] Cai dat cac thu vien tu requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Co loi khi cai dat thu vien!
    echo.
    echo Cac giai phap co the:
    echo 1. Chay Command Prompt voi quyen Administrator
    echo 2. Kiem tra ket noi internet
    echo 3. Thu cai dat tung thu vien rieng le:
    echo    pip install faster-whisper
    echo    pip install pyaudio
    echo    pip install pynput
    echo    pip install pyperclip
    echo    pip install keyboard
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo        CAI DAT THANH CONG!
echo ========================================
echo.
echo Ban co the chay ung dung bang lenh:
echo python main.py
echo.
pause
