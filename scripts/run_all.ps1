# scripts/run_all.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "🚀 Launching Fallat CrewAI Command Center (single entrypoint)..." -ForegroundColor Cyan

$backendScript = Join-Path $root "scripts\run_backend.ps1"
$frontendScript = Join-Path $root "scripts\run_frontend.ps1"

if (!(Test-Path $backendScript)) {
  throw "Missing backend runner: $backendScript"
}
if (!(Test-Path $frontendScript)) {
  throw "Missing frontend runner: $frontendScript"
}

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript
Start-Sleep -Milliseconds 700
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript

Write-Host "✅ Backend + Frontend started (separate terminals)." -ForegroundColor Green
Write-Host "Backend: http://127.0.0.1:8000"
Write-Host "Docs:    http://127.0.0.1:8000/docs"
Write-Host "Frontend is usually: http://localhost:5173"