# START_FRESH.ps1
# Clean startup script for Earnetics system

Write-Host "=== Stopping All Processes ===" -ForegroundColor Yellow

# Stop Python processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Node processes
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop any uvicorn processes
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "All processes stopped!" -ForegroundColor Green
Write-Host ""

Write-Host "=== Starting Fresh ===" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Red
}

Write-Host ""
Write-Host "Ready to start!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the backend server, run:" -ForegroundColor Cyan
Write-Host "  python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "To start the frontend (in a new terminal), run:" -ForegroundColor Cyan
Write-Host "  cd fallat_crewai_dashboard" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
