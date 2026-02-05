# scripts/_ports.ps1

function Get-RepoRoot {
  # scripts folder is at repo_root\scripts
  return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-ListeningPids([int]$Port) {
  $pids = @()

  # Try modern way first (sometimes requires admin on some setups)
  try {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    return $pids
  } catch {
    # fallback to netstat parse (works everywhere)
    $lines = netstat -ano | Select-String ":$Port\s+.*LISTENING\s+\d+"
    foreach ($l in $lines) {
      $parts = ($l.Line -split "\s+") | Where-Object { $_ -ne "" }
      $pid = [int]$parts[-1]
      $pids += $pid
    }
    return ($pids | Sort-Object -Unique)
  }
}

function Stop-Port([int]$Port) {
  $pids = Get-ListeningPids -Port $Port
  if (-not $pids -or $pids.Count -eq 0) {
    Write-Host "OK: Port $Port is free." -ForegroundColor Green
    return
  }

  Write-Host "WARNING: Port $Port is in use by PID(s): $($pids -join ', ')" -ForegroundColor Yellow
  foreach ($pid in $pids) {
    try {
      Stop-Process -Id $pid -Force -ErrorAction Stop
      Write-Host "Killed PID $pid (port $Port)." -ForegroundColor Green
    } catch {
        $errMsg = $_.Exception.Message
        Write-Host "ERROR: Failed to kill PID $pid : $errMsg" -ForegroundColor Red
    }
  }

  Start-Sleep -Milliseconds 800

  $check = Get-ListeningPids -Port $Port
  if ($check -and $check.Count -gt 0) {
    throw "Port $Port is STILL listening (PID(s): $($check -join ', ')). Close manually or reboot."
  }

  Write-Host "OK: Port $Port cleared." -ForegroundColor Green
}
