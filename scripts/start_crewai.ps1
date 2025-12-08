param(
    [switch]$NoReload,
    [int]$Port = 8000,
    [string]$ListenHost = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptRoot "..")

Set-Location $projectRoot

$pythonFromVenv = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonExe = if (Test-Path $pythonFromVenv) { $pythonFromVenv } else { "python" }

$uvicornArgs = @(
    "-m", "uvicorn",
    "backend.main_server:app",
    "--host", $ListenHost,
    "--port", $Port.ToString()
)

if (-not $NoReload) {
    $uvicornArgs += @("--reload", "--reload-exclude", ".venv")
}

$envFile = Join-Path $projectRoot ".env"
if (Test-Path $envFile) {
    $uvicornArgs += @("--env-file", $envFile)
}

Write-Host "Launching CrewAI backend..."
Write-Host (" Python : {0}" -f $pythonExe)
Write-Host (" Host   : {0}" -f $ListenHost)
Write-Host (" Port   : {0}" -f $Port)
if (Test-Path $envFile) {
    Write-Host (" Using .env : {0}" -f $envFile)
}
if (-not $NoReload) {
    Write-Host " Hot reload enabled (excluding .venv)"
} else {
    Write-Host " Hot reload disabled"
}
Write-Host ""

& $pythonExe @uvicornArgs
