@echo off
echo ========================================================
echo   AI REVENUE CORPORATION - AUTONOMOUS AGENT LAUNCHER
echo ========================================================
echo.
echo  WARNING: REAL MODE ENABLED
echo  Agents will perform REAL actions (Emails, Stripe Products)
echo.

set FALLAT_REAL_MODE=True

set "MAX_RETRIES=5"
set "RETRY_DELAY=5"
set "ATTEMPT=0"
:check_loop
set /a ATTEMPT+=1
curl -s http://localhost:8000/api/system/status >nul
if %errorlevel% neq 0 (
    if %ATTEMPT% lss %MAX_RETRIES% (
        echo [Attempt %ATTEMPT%] Backend not ready – waiting %RETRY_DELAY% seconds...
        timeout /t %RETRY_DELAY% >nul
        goto check_loop
    ) else (
        echo ❌ ERROR: Backend server is NOT running after %MAX_RETRIES% attempts.
        pause
        exit /b
    )
)
echo ✅ Backend is ONLINE.

echo.
echo  [2/2] Launching Autonomous Agents...
echo.
.venv\Scripts\python.exe scripts\run_real_agents.py

pause
