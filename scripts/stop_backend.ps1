# scripts/stop_backend.ps1
$ErrorActionPreference = "SilentlyContinue"

Write-Host "Stopping Earnetics backend (port 8000)..." -ForegroundColor Yellow

# Get PIDs LISTENING on 8000 (server processes only, not client connections)
# Only LISTENING state matters - ESTABLISHED/TIME_WAIT are client connections (browsers, etc.)
$pids = @()
$lines = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
foreach ($line in $lines) {
    $parts = ($line.Line -split "\s+") | Where-Object { $_ -ne "" }
    $pid = $parts[-1]
    if ($pid -match "^\d+$") {
        $pids += [int]$pid
    }
}
$pids = $pids | Sort-Object -Unique

# Filter to only Python processes (actual backend servers)
# Client connections (browsers) will have different PIDs and don't need killing
$pythonPids = @()
foreach ($pid in $pids) {
    try {
        $proc = Get-Process -Id $pid -ErrorAction Stop
        # Only kill Python processes (actual backend servers)
        if ($proc.ProcessName -match "python|pythonw|uvicorn") {
            $pythonPids += $pid
        } else {
            Write-Host "Skipping PID $pid ($($proc.ProcessName)) - not a Python server process" -ForegroundColor Cyan
        }
    } catch {
        # Process doesn't exist (zombie socket)
        Write-Host "PID $pid no longer exists (zombie socket)" -ForegroundColor Gray
    }
}
$pids = $pythonPids

if (-not $pids -or $pids.Count -eq 0) {
    Write-Host "✅ No Python server processes LISTENING on :8000" -ForegroundColor Green
    Write-Host "   (Client connections like browsers are normal and don't need to be killed)" -ForegroundColor Gray
    exit 0
}

# Kill all PIDs
foreach ($pid in $pids) {
    Write-Host "Killing PID $pid (LISTENING on :8000)" -ForegroundColor Red
    taskkill /F /PID $pid 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        # Fallback to Stop-Process
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

# Wait for processes to terminate
Start-Sleep -Milliseconds 600

# Verify port is free (check for zombie sockets)
$still = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if ($still) {
    # Check if processes actually exist (zombie sockets)
    $zombieCount = 0
    $activeCount = 0
    $still | ForEach-Object {
        $parts = ($_ -split "\s+") | Where-Object { $_ -ne "" }
        $procId = [int]$parts[-1]
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            $activeCount++
        } else {
            $zombieCount++
        }
    }
    
    if ($zombieCount -gt 0 -and $activeCount -eq 0) {
        Write-Host "INFO: Port 8000 has $zombieCount zombie socket(s) - processes already dead" -ForegroundColor Cyan
        Write-Host "Waiting up to 5 seconds for Windows to release zombie sockets..." -ForegroundColor Cyan
        
        # Wait for zombie sockets to clear (Windows TCP TIME_WAIT)
        $maxWait = 10
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Milliseconds 500
            $waited += 0.5
            $check = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
            if (-not $check) {
                Write-Host "Port 8000 is now free after $waited seconds" -ForegroundColor Green
                exit 0
            }
        }
        
        # If still not free, warn but allow attempt
        Write-Host "WARNING: Port 8000 still shows zombie sockets after $maxWait seconds" -ForegroundColor Yellow
        Write-Host "Windows may release them during bind attempt. Proceeding..." -ForegroundColor Cyan
        exit 0
    } elseif ($activeCount -gt 0) {
        Write-Host "WARNING: Port 8000 still has $activeCount active listener(s):" -ForegroundColor Red
        $still | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Yellow }
        exit 1
    }
}

Write-Host "✅ OK: :8000 is free." -ForegroundColor Green
exit 0
