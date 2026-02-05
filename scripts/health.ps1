# scripts/health.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$urls = @(
  "http://127.0.0.1:8000/health",
  "http://127.0.0.1:8000/docs"
)

foreach ($u in $urls) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri $u
    Write-Host "✅ HEALTH OK ($u) status=$($r.StatusCode)"
    exit 0
  } catch {
    Write-Host "❌ FAIL ($u) $($_.Exception.Message)"
  }
}

exit 1
