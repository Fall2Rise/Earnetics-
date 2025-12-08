@echo off
echo --- STARTING AI REVENUE COMMAND CENTER (PRODUCTION) ---
echo.
echo 1. Loading Environment Variables...
set PYTHONUTF8=1

echo 2. Checking System Readiness...
python check_system.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ SYSTEM CHECK FAILED. Aborting launch.
    pause
    exit /b %errorlevel%
)

echo.
echo 3. Launching Server (Port 8000)...
echo    - Mode: Production
echo    - Workers: 4
echo    - Interface: http://localhost:8080
echo.

:: Use uvicorn with workers for Windows production compatibility
uvicorn backend.main_server:app --host 127.0.0.1 --port 8080 --workers 4 --no-access-log

pause
