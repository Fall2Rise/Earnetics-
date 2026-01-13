# Kill All Backend and Frontend Processes
Write-Host "🧹 Killing all backend and frontend processes...`n" -ForegroundColor Red

# Kill all Python processes (backend)
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "Found $($pythonProcs.Count) Python processes - killing..." -ForegroundColor Yellow
    $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Python processes killed" -ForegroundColor Green
} else {
    Write-Host "No Python processes found" -ForegroundColor Gray
}

# Kill all Node processes (frontend)
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Write-Host "Found $($nodeProcs.Count) Node processes - killing..." -ForegroundColor Yellow
    $nodeProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Node processes killed" -ForegroundColor Green
} else {
    Write-Host "No Node processes found" -ForegroundColor Gray
}

Write-Host "`n✅ Cleanup complete!`n" -ForegroundColor Green
Write-Host "Now you can start fresh:" -ForegroundColor Cyan
Write-Host "  1. .\start_backend.ps1 (wait for 'Application startup complete')" -ForegroundColor White
Write-Host "  2. .\start_frontend.ps1 (in a NEW window)`n" -ForegroundColor White

