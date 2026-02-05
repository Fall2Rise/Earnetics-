# scripts/kill_all_listeners.ps1
# Kills all processes listening on common Earnetics ports (8000, 5173, etc.)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🧹 Killing all Earnetics listeners..." -ForegroundColor Yellow

$ports = @(8000, 5173)  # Backend and Frontend ports

foreach ($port in $ports) {
    Write-Host "`nChecking port $port..." -ForegroundColor Cyan
    
    # Get PIDs listening on this port
    $pids = @()
    $lines = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
    foreach ($line in $lines) {
        $parts = ($line.Line -split "\s+") | Where-Object { $_ -ne "" }
        $procId = $parts[-1]
        if ($procId -match "^\d+$") {
            $pids += [int]$procId
        }
    }
    $pids = $pids | Sort-Object -Unique

    if ($null -eq $pids -or (($pids -is [array]) -and ($pids.Count -eq 0)) -or (($pids -isnot [array]) -and ($pids -eq 0))) {
        Write-Host "  OK: Port $port is free" -ForegroundColor Green
        continue
    }
    
    # Ensure $pids is an array
    if ($pids -isnot [array]) {
        $pids = @($pids)
    }

    # Kill all PIDs
    $killed = 0
    $zombies = 0
    foreach ($procId in $pids) {
        # Check if process actually exists
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Killing PID $procId ($($proc.ProcessName)) (LISTENING on :$port)" -ForegroundColor Red
            try {
                # Try taskkill first
                taskkill /F /PID $procId 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    # Fallback to Stop-Process
                    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                }
                $killed++
            } catch {
                $errMsg = $_.Exception.Message
                Write-Host "    WARNING: Failed to kill PID $procId : $errMsg" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  PID $procId : Process not found (zombie socket - will clear automatically)" -ForegroundColor Yellow
            $zombies++
        }
    }
    
    # Wait for processes to terminate
    if ($killed -gt 0) {
        Start-Sleep -Milliseconds 600
    }
    
    # Verify port is free
    $still = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
    if ($still) {
        if ($zombies -gt 0) {
            Write-Host "  INFO: Port $port has $zombies zombie socket(s) - processes already dead, will clear automatically" -ForegroundColor Cyan
            Write-Host "  (You can bind to this port - Windows will handle cleanup)" -ForegroundColor Gray
        } else {
            Write-Host "  WARNING: Port $port still has LISTENING entries" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  OK: Port $port is now free" -ForegroundColor Green
    }
}

Write-Host "`n✅ Done. All common ports checked." -ForegroundColor Green
