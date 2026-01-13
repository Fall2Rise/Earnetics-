# System Health Check and Diagnostic Script
# Usage: .\scripts\doctor.ps1

$ErrorActionPreference = "Continue"

$scriptDir = Split-Path -Parent $PSCommandPath
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EARNETICS COMMAND CENTER - System Doctor" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$issues = 0

# Check 1: Python Version
Write-Host "[1/8] Python Version Check" -ForegroundColor Yellow

$pythonExe = $null
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonExe = ".\.venv\Scripts\python.exe"
} elseif (Test-Path ".\venv\Scripts\python.exe") {
    $pythonExe = ".\venv\Scripts\python.exe"
}

if ($pythonExe) {
    $version = & $pythonExe --version 2>&1
    Write-Host "  ✓ venv Python: $version" -ForegroundColor Green
    
    # Check if it's 3.11 or 3.12
    if ($version -match "3\.11" -or $version -match "3\.12") {
        Write-Host "  ✓ Version is compatible (3.11 or 3.12)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Recommended: Python 3.11 or 3.12" -ForegroundColor Yellow
        $issues++
    }
} else {
    Write-Host "  ✗ No venv found (.venv or venv)" -ForegroundColor Red
    Write-Host "  Create one: python -m venv .venv" -ForegroundColor Gray
    $issues++
}

# Check 2: Pip alignment
Write-Host ""
Write-Host "[2/8] Pip Alignment Check" -ForegroundColor Yellow

if ($pythonExe) {
    $pipVersion = & $pythonExe -m pip --version 2>&1
    Write-Host "  ✓ Pip: $pipVersion" -ForegroundColor Green
    
    # Verify pip path matches python path
    if ($pipVersion -match $pythonExe.Replace(".\", "")) {
        Write-Host "  ✓ Pip and Python are aligned" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Pip may be from different Python install" -ForegroundColor Yellow
        $issues++
    }
} else {
    Write-Host "  ✗ Skipped (no venv)" -ForegroundColor Red
}

# Check 3: Requirements installed
Write-Host ""
Write-Host "[3/8] Requirements Check" -ForegroundColor Yellow

if ($pythonExe -and (Test-Path "requirements.txt")) {
    $testImport = & $pythonExe -c "import fastapi, uvicorn, resend" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Core packages installed (fastapi, uvicorn, resend)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Missing packages" -ForegroundColor Red
        Write-Host "  Run: $pythonExe -m pip install -r requirements.txt" -ForegroundColor Gray
        $issues++
    }
} else {
    Write-Host "  ✗ Skipped (no venv or requirements.txt)" -ForegroundColor Red
}

# Check 4: Backend imports
Write-Host ""
Write-Host "[4/8] Backend Import Check" -ForegroundColor Yellow

if ($pythonExe) {
    $testImport = & $pythonExe -c "from backend.main_server import app; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ backend.main_server imports successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to import backend.main_server" -ForegroundColor Red
        Write-Host "  Error: $testImport" -ForegroundColor Gray
        $issues++
    }
} else {
    Write-Host "  ✗ Skipped (no venv)" -ForegroundColor Red
}

# Check 5: Port availability
Write-Host ""
Write-Host "[5/8] Port Availability Check" -ForegroundColor Yellow

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "  ⚠ Port 8000 is in use (PID: $($port8000.OwningProcess))" -ForegroundColor Yellow
    $issues++
} else {
    Write-Host "  ✓ Port 8000 is available" -ForegroundColor Green
}

# Check 6: Node.js
Write-Host ""
Write-Host "[6/8] Node.js Check" -ForegroundColor Yellow

try {
    $nodeVersion = & node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host "  ✗ Node.js not installed" -ForegroundColor Red
    Write-Host "  Install from: https://nodejs.org" -ForegroundColor Gray
    $issues++
}

# Check 7: Frontend structure
Write-Host ""
Write-Host "[7/8] Frontend Structure Check" -ForegroundColor Yellow

$frontendDir = "earnetics-command-center-v3"
if (Test-Path $frontendDir) {
    Write-Host "  ✓ Frontend directory exists" -ForegroundColor Green
    
    if (Test-Path "$frontendDir\package.json") {
        Write-Host "  ✓ package.json found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ package.json missing" -ForegroundColor Red
        $issues++
    }
    
    if (Test-Path "$frontendDir\node_modules") {
        Write-Host "  ✓ node_modules exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ node_modules missing (run npm install)" -ForegroundColor Yellow
        $issues++
    }
} else {
    Write-Host "  ✗ Frontend directory not found" -ForegroundColor Red
    $issues++
}

# Check 8: Environment file
Write-Host ""
Write-Host "[8/8] Environment Configuration Check" -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    
    # Check for critical vars
    $envContent = Get-Content ".env" -Raw
    $criticalVars = @("FALLAT_API_TOKEN", "RESEND_API_KEY")
    foreach ($var in $criticalVars) {
        if ($envContent -match $var) {
            Write-Host "  ✓ $var is set" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $var not found in .env" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ⚠ .env file missing (copy from .env.example)" -ForegroundColor Yellow
    $issues++
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($issues -eq 0) {
    Write-Host "  ✓ ALL CHECKS PASSED" -ForegroundColor Green
    Write-Host "  System is ready to run!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ FOUND $issues ISSUE(S)" -ForegroundColor Yellow
    Write-Host "  Please fix the issues above before starting" -ForegroundColor Yellow
}

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

exit $issues
