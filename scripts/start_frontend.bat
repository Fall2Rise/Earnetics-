@echo off
REM Deterministic Frontend Startup (Windows Batch)
REM Calls the PowerShell script

setlocal
set "SCRIPT_DIR=%~dp0"
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start_frontend.ps1" %*
endlocal
