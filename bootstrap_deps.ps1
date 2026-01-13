# backend\tools\bootstrap_deps.ps1
# Auto-installs missing Python modules into backend\.venv by repeatedly attempting to import/start the app.

$ErrorActionPreference = "Stop"

$repoRoot = "C:\AI_Projects\Fallat_CrewAI"
$backendDir = Join-Path $repoRoot "backend"
$venvPy = Join-Path $backendDir ".venv\Scripts\python.exe"
$logDir = Join-Path $backendDir "logs"
$logPath = Join-Path $logDir "backend_bootstrap.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (!(Test-Path $venvPy)) {
  Write-Host "ERROR: venv python not found at $venvPy"
  Write-Host "Create venv first:  python -m venv backend\.venv"
  exit 1
}

# Map import-name -> pip package name (the annoying ones)
$pkgMap = @{
  "gtts"            = "gTTS"
  "email_validator" = "email-validator"
  "cv2"             = "opencv-python"
  "PIL"             = "Pillow"
  "sklearn"         = "scikit-learn"
  "yaml"            = "PyYAML"
}

function Get-MissingModuleFromText($text) {
  # Matches: ModuleNotFoundError: No module named 'X'
  $m = [regex]::Match($text, "ModuleNotFoundError:\s+No module named '([^']+)'")
  if ($m.Success) { return $m.Groups[1].Value }
  return $null
}

function Resolve-PipPackage($moduleName) {
  if ($pkgMap.ContainsKey($moduleName)) { return $pkgMap[$moduleName] }
  return $moduleName
}

# Ensure pip tooling is up to date inside venv
& $venvPy -m pip install -U pip setuptools wheel | Out-Null

$maxPasses = 30
for ($i=1; $i -le $maxPasses; $i++) {
  Write-Host "`n=== Pass $i/$maxPasses ==="
  Write-Host "Attempting to import backend.main_server (and trigger imports)..."

  $out = & $venvPy -c "import backend.main_server" 2>&1 | Out-String
  $out | Tee-Object -FilePath $logPath -Append | Out-Null

  if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: backend.main_server imports cleanly."
    Write-Host "Next: start server:"
    Write-Host "  $venvPy -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --log-level debug"
    exit 0
  }

  $missing = Get-MissingModuleFromText $out
  if (-not $missing) {
    Write-Host "STOP: No ModuleNotFoundError detected."
    Write-Host "Check log at: $logPath"
    exit 2
  }

  $pkg = Resolve-PipPackage $missing
  Write-Host "Missing module: $missing  -> Installing pip package: $pkg"

  & $venvPy -m pip install -U $pkg
  if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed for $pkg"
    Write-Host "Check log at: $logPath"
    exit 3
  }
}

Write-Host "STOP: Reached max passes ($maxPasses). Check log at: $logPath"
exit 4
