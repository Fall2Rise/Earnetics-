# scripts/stop_all.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\_ports.ps1"

Write-Host "🧨 Stopping Earnetics services..."
try { Stop-Port -Port 8000 } catch { Write-Host "Backend stop warning: $($_.Exception.Message)" }
try { Stop-Port -Port 5173 } catch { Write-Host "Frontend stop warning: $($_.Exception.Message)" }

Write-Host "✅ Stop complete."
