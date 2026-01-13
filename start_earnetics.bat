@echo off
ECHO "Starting Earnetics..."

REM Start the backend
ECHO "Starting Backend Server..."
start "Earnetics Backend" cmd /c "c:\AI_Projects\Fallat_CrewAI\.venv\Scripts\activate.bat && python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000"

REM Wait a few seconds for the backend to initialize
timeout /t 5

REM Start the frontend
ECHO "Starting Earnetics Command Center..."
cd "c:\AI_Projects\Fallat_CrewAI\earnetics-command-center-v3"
start "Earnetics Frontend" cmd /c "npm start"

ECHO "Done."
