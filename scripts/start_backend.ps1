# Deterministic Backend Startup Script
# Usage: .\scripts\start_backend.ps1 [-Port 8000] [-NoReload]

param(
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"

# Navigate to project root
$scriptDir = Split-Path -Parent $PSCommandPath
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EARNETICS COMMAND CENTER - Backend Startup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Determine Python interpreter
Write-Host "[1/5] Detecting Python interpreter..." -ForegroundColor Yellow

$pythonExe = $null
$venvPaths = @(
    ".\. venv\Scripts\python.exe",
    ".\venv\Scripts\python.exe"
)

foreach ($path in $venvPaths) {
    if (Test-Path $path) {
        $pythonExe = $path
        Write-Host "  ✓ Found venv: $path" -ForegroundColor Green
        break
    }
}

if (-not $pythonExe) {
    # Fallback to system Python 3.11
    try {
        $pyVersion = & py -3.11 --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = "py"
            $pythonArgs = @("-3.11")
            Write-Host "  ✓ Using system Python 3.11" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ No venv found and py -3.11 not available" -ForegroundColor Red
        Write-Host "  Please create a venv: python -m venv .venv" -ForegroundColor Red
        exit 1
    }
} else {
    $pythonArgs = @()
}

# Verify Python version
$pythonVersion = & $pythonExe @pythonArgs --version
Write-Host "  Python: $pythonVersion" -ForegroundColor Gray

# Step 2: Create logs directory
Write-Host ""
Write-Host "[2/5] Setting up logging..." -ForegroundColor Yellow

$logsDir = Join-Path $projectRoot "backend\logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "  ✓ Created logs directory" -ForegroundColor Green
} else {
    Write-Host "  ✓ Logs directory exists" -ForegroundColor Green
}

$logFile = Join-Path $logsDir "backend_boot_latest.log"
Write-Host "  Log file: $logFile" -ForegroundColor Gray

# Step 3: Verify backend module
Write-Host ""
Write-Host "[3/5] Verifying backend module..." -ForegroundColor Yellow

$testImport = & $pythonExe @pythonArgs -c "import backend.main_server; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to import backend.main_server" -ForegroundColor Red
    Write-Host "  Error: $testImport" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Try installing requirements:" -ForegroundColor Yellow
    Write-Host "  $pythonExe -m pip install -r requirements.txt" -ForegroundColor Gray
    exit 1
}
Write-Host "  ✓ Backend module imports successfully" -ForegroundColor Green

# Step 4: Check if port is available
Write-Host ""
Write-Host "[4/5] Checking port availability..." -ForegroundColor Yellow

$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "  ⚠ Port $Port is already in use" -ForegroundColor Yellow
    Write-Host "  Process: $($portInUse.OwningProcess)" -ForegroundColor Gray
    $continue = Read-Host "  Continue anyway? (y/N)"
    if ($continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "  ✓ Port $Port is available" -ForegroundColor Green
}

# Step 5: Start uvicorn
Write-Host ""
Write-Host "[5/5] Starting backend server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  API URL:  http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "  WS URL:   ws://127.0.0.1:$Port/ws" -ForegroundColor Cyan
Write-Host "  Docs:     http://127.0.0.1:$Port/docs" -ForegroundColor Cyan
Write-Host "  Health:   http://127.0.0.1:$Port/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

$uvicornArgs = @(
    "-m", "uvicorn",
    "backend.main_server:app",
    "--host", "127.0.0.1",
    "--port", $Port.ToString(),
    "--log-level", "info"
)

if (-not $NoReload) {
    $uvicornArgs += @("--reload", "--reload-exclude", ".venv", "--reload-exclude", "venv")
}

# Start with output tee'd to log file
$process = Start-Process -FilePath $pythonExe -ArgumentList ($pythonArgs + $uvicornArgs) -NoNewWindow -PassThru -RedirectStandardOutput $logFile -RedirectStandardError $logFile

Write-Host "  ✓ Backend started (PID: $($process.Id))" -ForegroundColor Green
Write-Host "  ✓ Logs: $logFile" -ForegroundColor Green
Write-Host ""

# Wait for process
$process.WaitForExit()
