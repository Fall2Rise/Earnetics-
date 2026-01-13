# START_TONIGHT.ps1 - Clean startup for tonight
# Single script to start everything fresh

Write-Host "=== Starting Fresh for Tonight ===" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$projectPath = "C:\AI_Projects\Fallat_CrewAI"
if (Test-Path $projectPath) {
    Set-Location $projectPath
    Write-Host "Changed to project directory: $projectPath" -ForegroundColor Green
} else {
    Write-Host "Warning: Project directory not found at $projectPath" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
}

Write-Host ""

# Stop any existing processes
Write-Host "Cleaning up..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "python|node|uvicorn|npm|vite"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "=== Ready to Start ===" -ForegroundColor Green
Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Cyan
Write-Host ""

# Start backend
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
