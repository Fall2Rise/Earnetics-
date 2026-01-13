# Start Backend Server
Write-Host "🚀 Starting Fallat CrewAI Backend..." -ForegroundColor Cyan
Write-Host ""

cd $PSScriptRoot
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload

