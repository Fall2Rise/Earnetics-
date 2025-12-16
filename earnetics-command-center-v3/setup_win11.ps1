# setup_win11.ps1
Write-Host "Starting Earnetics Command Center V3 Setup..." -ForegroundColor Cyan

# 1. Check Prerequisites
function Check-Command ($cmd, $name) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        Write-Host "  [+] $name found" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [-] $name NOT found" -ForegroundColor Red
        return $false
    }
}

Write-Host "`nChecking Prerequisites..."
$hasNode = Check-Command "node" "Node.js"
$hasNpm = Check-Command "npm" "npm"
$hasGit = Check-Command "git" "Git"
$hasPython = Check-Command "python" "Python"
$hasCl = Check-Command "cl" "Visual Studio Build Tools (cl.exe)"

if (-not ($hasNode -and $hasNpm -and $hasGit -and $hasPython -and $hasCl)) {
    Write-Host "`nMissing prerequisites! Please install:" -ForegroundColor Yellow
    if (-not $hasNode) { Write-Host "  - Node.js LTS: https://nodejs.org/" }
    if (-not $hasGit) { Write-Host "  - Git: https://git-scm.com/" }
    if (-not $hasPython) { Write-Host "  - Python 3.x: https://www.python.org/ (Add to PATH)" }
    if (-not $hasCl) { 
        Write-Host "  - Visual Studio 2022 Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        Write-Host "    Select 'Desktop development with C++'"
    }
    exit 1
}

# 2. Install Dependencies
Write-Host "`nInstalling Dependencies..."
npm install --ignore-scripts
if ($LASTEXITCODE -ne 0) {
    Write-Host "npm install failed!" -ForegroundColor Red
    exit 1
}

# 3. Rebuild Native Modules
Write-Host "`nRebuilding better-sqlite3..."
npm rebuild better-sqlite3 --build-from-source
if ($LASTEXITCODE -ne 0) {
    Write-Host "Native build failed! Attempting electron-rebuild..." -ForegroundColor Yellow
    npx electron-rebuild -f -w better-sqlite3
    if ($LASTEXITCODE -ne 0) {
        Write-Host "electron-rebuild failed!" -ForegroundColor Red
        exit 1
    }
}

# 4. Configure Environment
Write-Host "`nConfiguring Environment..."
$envFile = ".env"
$envContent = @"
EARNETICS_BACKEND_HTTP=http://localhost:8000
EARNETICS_BACKEND_WS=ws://localhost:8000/ws
EARNETICS_DB_PATH=$PWD\data\earnetics.db
EARNETICS_MODE=OFFLINE
EARNETICS_ONLINE_ALLOWED=false
EARNETICS_EVENT_BATCH_SIZE=100
EARNETICS_LOG_LEVEL=info
"@

if (-not (Test-Path $envFile)) {
    Set-Content -Path $envFile -Value $envContent
    Write-Host "  [+] Created .env file" -ForegroundColor Green
} else {
    Write-Host "  [!] .env file already exists, skipping creation" -ForegroundColor Yellow
}

# Create data directory
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "  [+] Created data directory" -ForegroundColor Green
}

# Create .env.example
$envExampleFile = ".env.example"
if (-not (Test-Path $envExampleFile)) {
    Set-Content -Path $envExampleFile -Value $envContent
    Write-Host "  [+] Created .env.example file" -ForegroundColor Green
}

Write-Host "`nSetup Complete! Run 'npm start' to launch." -ForegroundColor Cyan
