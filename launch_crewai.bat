@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\start_crewai.ps1" %*
echo.
echo ---------------------------------------------------------
echo   SERVER IS RUNNING. DO NOT CLOSE THIS WINDOW.
echo   To control the system, run 'run_launchpad.bat'
echo   in a NEW terminal window.
echo ---------------------------------------------------------
echo.
endlocal
