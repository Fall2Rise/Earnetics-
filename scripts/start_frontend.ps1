# Deterministic Frontend Startup Script
# Usage: .\scripts\start_frontend.ps1

$ErrorActionPreference = "Stop"

# Navigate to frontend directory
$scriptDir = Split-Path -Parent $PSCommandPath
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
$frontendDir = Join-Path $projectRoot "earnetics-command-center-v3"

if (-not (Test-Path $frontendDir)) {
    Write-Host "✗ Frontend directory not found: $frontendDir" -ForegroundColor Red
    exit 1
}

Set-Location $frontendDir

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EARNETICS COMMAND CENTER - Frontend Startup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for Node.js
Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = & node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "  ✗ Node.js not installed" -ForegroundColor Red
    Write-Host "  Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check for package.json
Write-Host ""
Write-Host "[2/4] Verifying project structure..." -ForegroundColor Yellow

if (-not (Test-Path "package.json")) {
    Write-Host "  ✗ package.json not found in $frontendDir" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ package.json found" -ForegroundColor Green

# Step 3: Install dependencies if needed
Write-Host ""
Write-Host "[3/4] Checking dependencies..." -ForegroundColor Yellow

if (-not (Test-Path "node_modules")) {
    Write-Host "  ⚠ node_modules not found, installing..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ npm install failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ node_modules exists" -ForegroundColor Green
}

# Step 4: Start dev server
Write-Host ""
Write-Host "[4/4] Starting development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Frontend will be available at the URL shown below" -ForegroundColor Cyan
Write-Host "  Make sure backend is running at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Run npm run dev (or npm start, depending on package.json)
npm run dev

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ✗ Failed to start dev server" -ForegroundColor Red
    Write-Host "  Try: npm run dev or npm start" -ForegroundColor Yellow
    exit 1
}
