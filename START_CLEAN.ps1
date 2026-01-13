# Clean Startup Script - Kills all existing processes and starts fresh
Write-Host "🧹 Cleaning up existing processes...`n" -ForegroundColor Cyan

# Kill all Python processes (backend)
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*main_server*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill all Node processes (frontend)
Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*5173*" -or $_.CommandLine -like "*5174*" -or $_.CommandLine -like "*5175*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup complete!`n" -ForegroundColor Green
Write-Host "Now start services one at a time:" -ForegroundColor Yellow
Write-Host "1. Run: .\start_backend.ps1 (wait for it to start)" -ForegroundColor Cyan
Write-Host "2. Run: .\start_frontend.ps1 (in a NEW window)`n" -ForegroundColor Cyan

