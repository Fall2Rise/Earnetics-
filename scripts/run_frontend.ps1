# scripts/run_frontend.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

# Frontend folder
$frontPath = Join-Path $root "Frontend"
if (!(Test-Path (Join-Path $frontPath "package.json"))) {
  throw "Frontend not found at Frontend (missing package.json)"
}

Set-Location $frontPath
Write-Host "Frontend path: $frontPath" -ForegroundColor Cyan

# Install if missing
if (-not (Test-Path (Join-Path $frontPath "node_modules"))) {
  Write-Host "node_modules missing - running npm install..." -ForegroundColor Yellow
  npm install
}

Write-Host "Starting frontend dev server..." -ForegroundColor Green
npm run dev
