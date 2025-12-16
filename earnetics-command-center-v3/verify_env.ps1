# verify_env.ps1
Write-Output "Verifying Earnetics Environment..."

$allPassed = $true

function Verify-Step ($name, $block) {
    Write-Output "Verifying $name... "
    try {
        $result = & $block
        if ($result) {
            Write-Output "PASS"
        } else {
            Write-Output "FAIL"
            $global:allPassed = $false
        }
    } catch {
        Write-Output "FAIL ($($_.Exception.Message))"
        $global:allPassed = $false
    }
}

Verify-Step "Tools" {
    (Get-Command node -ErrorAction SilentlyContinue) -and 
    (Get-Command npm -ErrorAction SilentlyContinue) -and 
    (Get-Command python -ErrorAction SilentlyContinue)
}

Verify-Step "better-sqlite3" {
    $script = "try { require('better-sqlite3'); console.log('ok'); } catch(e) { process.exit(1); }"
    $res = node -e $script 2>&1
    $LASTEXITCODE -eq 0
}

Verify-Step "Database" {
    $envContent = Get-Content .env -Raw
    $env = $envContent | ConvertFrom-StringData
    $dbPath = $env.EARNETICS_DB_PATH
    if (-not $dbPath) { $dbPath = "data\earnetics.db" }
    Test-Path $dbPath
}

Verify-Step "Backend HTTP" {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        $response.StatusCode -eq 200
    } catch {
        $false
    }
}

Verify-Step "Backend WebSocket" {
    # Simple check if port is open, full handshake requires more complex script
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", 8000)
        $tcp.Connected
        $tcp.Close()
        $true
    } catch {
        $false
    }
}

if ($allPassed) {
    Write-Output "`nAll checks passed! System is ready."
} else {
    Write-Output "`nSome checks failed. Please review setup."
}
