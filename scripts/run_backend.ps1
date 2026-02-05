# scripts/run_backend.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Go to repo root (assumes scripts/ lives at repo_root/scripts)
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host "== Backend Runner ==" -ForegroundColor Cyan

# Activate venv (try both locations)
$venvActivate = Join-Path $repoRoot "venv\Scripts\Activate.ps1"
if (!(Test-Path $venvActivate)) {
  $venvActivate = Join-Path $repoRoot "backend\.venv\Scripts\Activate.ps1"
}
if (!(Test-Path $venvActivate)) {
  throw "Venv not found. Expected: venv\Scripts\Activate.ps1 or backend\.venv\Scripts\Activate.ps1"
}
. $venvActivate

# Load .env if present (simple KEY=VALUE parsing)
$envFile = Join-Path $repoRoot ".env"
if (Test-Path $envFile) {
  Write-Host "Loading .env..." -ForegroundColor Yellow
  Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
      $k, $v = $line.Split("=", 2)
      $k = $k.Trim()
      $v = $v.Trim().Trim('"')
      if ($k) { Set-Item -Path "Env:$k" -Value $v }
    }
  }
}

# Ensure required envs exist (admin token at minimum)
if (-not $env:OPS_ADMIN_TOKEN) {
  Write-Host "WARNING: OPS_ADMIN_TOKEN missing. Setting a temporary token for this session." -ForegroundColor Yellow
  $env:OPS_ADMIN_TOKEN = "dev-token-change-me"
}

# Default runtime mode
if (-not $env:EARNETICS_MODE) { $env:EARNETICS_MODE = "SAFE_AUTONOMY" }

# Ensure no stale listeners (call stop script)
Write-Host "Ensuring port 8000 is free..." -ForegroundColor Yellow
& "$PSScriptRoot\stop_backend.ps1" | Out-Null

$env:WORKERS = "1"
$env:RELOAD = "0"
$env:PORT = "8000"
$env:HOST = "127.0.0.1"

$backendHost = $env:HOST
$backendPort = $env:PORT
Write-Host "Starting backend at http://$backendHost`:$backendPort (mode=$env:EARNETICS_MODE, workers=1, reload=off)" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
python -m backend.run
