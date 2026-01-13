# Fix Prime Directive HMAC Script

Write-Host "Starting Prime Directive Fix..." -ForegroundColor Cyan

# 1. Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 2. Check/Set PRIME_DIRECTIVE_HMAC_SECRET
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "PRIME_DIRECTIVE_HMAC_SECRET") {
    Write-Host "Adding PRIME_DIRECTIVE_HMAC_SECRET to .env..." -ForegroundColor Yellow
    # Generate random secret
    $secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | % { [char]$_ })
    Add-Content ".env" "`nPRIME_DIRECTIVE_HMAC_SECRET=$secret"
    Write-Host "Secret generated." -ForegroundColor Green
}
else {
    Write-Host "PRIME_DIRECTIVE_HMAC_SECRET already exists in .env." -ForegroundColor Green
}

# 3. Check/Set WEB_CONCURRENCY
if ($envContent -notmatch "WEB_CONCURRENCY") {
    Write-Host "Adding WEB_CONCURRENCY=1 to .env..." -ForegroundColor Yellow
    Add-Content ".env" "`nWEB_CONCURRENCY=1"
}

# 4. Restart Docker
Write-Host "Restarting Docker containers..." -ForegroundColor Cyan
docker compose down --remove-orphans
docker compose up -d --build

# 5. Wait for health check
Write-Host "Waiting for service health..." -ForegroundColor Cyan
$maxRetries = 30
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            Write-Host "Service is HEALTHY!" -ForegroundColor Green
            Write-Host $response.Content
            break
        }
    }
    catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
        $retryCount++
    }
}

if (-not $healthy) {
    Write-Host "`nService failed to become healthy." -ForegroundColor Red
    Write-Host "Fetching logs..." -ForegroundColor Yellow
    docker compose logs --tail 200
}
