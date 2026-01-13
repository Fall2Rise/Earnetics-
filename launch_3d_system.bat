@echo off
echo ═══════════════════════════════════════════════════════
echo   EARNETICS COMMAND CENTER - 3D GUI STARTUP
echo ═══════════════════════════════════════════════════════
echo.

echo 1. Starting Backend Server...
start "Earnetics Backend" cmd /c "set PYTHONPATH=.&& python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000"

echo 2. Waiting for Backend to initialize...
timeout /t 5 /nobreak > nul

echo 3. Starting 3D GUI...
cd earnetics-command-center-v3
start "Earnetics 3D GUI" cmd /c "run_demo.bat"

echo.
echo ═══════════════════════════════════════════════════════
echo   SYSTEM LAUNCHED
echo   - Backend: http://localhost:8000
echo   - 3D GUI: (Opening in new window)
echo ═══════════════════════════════════════════════════════
echo.
pause
