# Start Both Backend and Frontend
Write-Host "🚀 Starting Fallat CrewAI System..." -ForegroundColor Green
Write-Host ""

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_backend.ps1"

Write-Host "✅ Backend starting in new window..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_frontend.ps1"

Write-Host "✅ Frontend starting in new window..." -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Wait 10-15 seconds for both servers to start..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Then open: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

