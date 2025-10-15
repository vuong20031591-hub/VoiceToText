@echo off
echo ========================================
echo RUNNING WITHOUT CACHE
echo ========================================
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 1 /nobreak >nul
python -B main.py
