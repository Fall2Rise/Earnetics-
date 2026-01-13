# EARNETICS COMMAND CENTER - RUNBOOK

## Quick Start (Windows 11)

### Prerequisites
- **Python 3.11** (recommended) or 3.12
- **Node.js 18+** (for frontend)
- **Git** (for version control)

### One-Time Setup

1. **Clone and navigate**:
   ```powershell
   cd C:\AI_Projects\Fallat_CrewAI
   ```

2. **Create Python virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate venv and install dependencies**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```powershell
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Configure frontend**:
   ```powershell
   cd earnetics-command-center-v3
   cp .env.example .env
   cd ..
   ```

6. **Run system check**:
   ```powershell
   .\scripts\doctor.ps1
   ```

---

## Starting the System

### Option 1: Start Backend and Frontend Separately (Recommended)

**Terminal 1 - Backend**:
```powershell
.\scripts\start_backend.ps1
```

**Terminal 2 - Frontend**:
```powershell
.\scripts\start_frontend.ps1
```

### Option 2: Use Batch Files

```cmd
scripts\start_backend.bat
scripts\start_frontend.bat
```

---

## System URLs

Once running:
- **API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **WebSocket**: ws://127.0.0.1:8000/ws
- **Frontend**: http://localhost:5173 (or port shown in terminal)

---

## Canonical Folder Structure

```
C:\AI_Projects\Fallat_CrewAI\
├── backend\                          # Backend API (FastAPI)
│   ├── __init__.py                   # Package marker
│   ├── main_server.py                # ⭐ ENTRYPOINT (app = FastAPI())
│   ├── config\
│   │   ├── __init__.py
│   │   └── settings.py               # Centralized configuration
│   ├── api\                          # API routers
│   ├── services\                     # Business logic
│   ├── logs\                         # Auto-created logs
│   │   └── backend_boot_latest.log
│   └── requirements.txt
│
├── earnetics-command-center-v3\      # ⭐ CANONICAL FRONTEND
│   ├── .env                          # Frontend config (create from .env.example)
│   ├── .env.example
│   ├── package.json
│   └── packages\
│       ├── renderer\                 # Main UI (React + Zustand)
│       ├── main\                     # Electron main process
│       ├── ui\                       # Shared components
│       ├── scene\                    # 3D view
│       └── core\                     # Shared logic
│
├── scripts\
│   ├── start_backend.ps1             # ⭐ Backend startup
│   ├── start_backend.bat
│   ├── start_frontend.ps1            # ⭐ Frontend startup
│   ├── start_frontend.bat
│   └── doctor.ps1                    # ⭐ System diagnostics
│
├── .env                              # Backend config
├── .env.example
├── requirements.txt
└── RUNBOOK.md                        # ⭐ THIS FILE
```

---

## Configuration

### Backend (.env)
```bash
# Required
FALLAT_API_TOKEN=your_token_here
RESEND_API_KEY=re_xxxxx              # For email sending
RESEND_FROM_EMAIL=noreply@earnetics.live

# Optional
FALLAT_HOST=127.0.0.1
FALLAT_PORT=8000
STRIPE_SECRET_KEY=sk_xxxxx           # For payments
```

### Frontend (earnetics-command-center-v3/.env)
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws
```

---

## Python Version Management

### Recommended: Python 3.11

The system is tested with Python 3.11. Python 3.12 should also work.

### Check Your Version
```powershell
.\.venv\Scripts\python.exe --version
```

### If You Have Multiple Pythons
The startup scripts automatically detect and use `.venv\Scripts\python.exe` if it exists.

**CRITICAL**: Always use `python -m pip` instead of `pip` directly:
```powershell
# ✅ CORRECT
.\.venv\Scripts\python.exe -m pip install package_name

# ❌ WRONG (may use wrong Python)
pip install package_name
```

---

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Make sure you're running from the project root:
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\start_backend.ps1
```

---

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install requirements:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

**Problem**: Port 8000 already in use

**Solution**: Find and kill the process:
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill it (replace PID with actual process ID)
Stop-Process -Id PID -Force
```

---

**Problem**: `uvicorn: command not found`

**Solution**: Use the full module path:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000
```

---

### Frontend Won't Start

**Problem**: `node: command not found`

**Solution**: Install Node.js from https://nodejs.org

---

**Problem**: `npm install` fails

**Solution**: Delete `node_modules` and try again:
```powershell
cd earnetics-command-center-v3
Remove-Item -Recurse -Force node_modules
npm install
```

---

**Problem**: TypeScript errors about missing React types

**Solution**: Install type definitions:
```powershell
cd earnetics-command-center-v3/packages/renderer
npm install --save-dev @types/react @types/react-dom
```

---

### WebSocket Not Connecting

**Problem**: Frontend shows "OFFLINE" status

**Checklist**:
1. Is backend running? Check http://127.0.0.1:8000/health
2. Is WebSocket endpoint correct? Should be `ws://127.0.0.1:8000/ws`
3. Check browser console for errors
4. Verify CORS allows your frontend origin

**Solution**: Restart both backend and frontend

---

### Python Version Mismatch

**Problem**: `pip` installs to Python 3.12 but script runs Python 3.11

**Solution**: Always use venv python explicitly:
```powershell
# Check which Python pip uses
.\.venv\Scripts\python.exe -m pip --version

# Should show path containing .venv
```

---

### Environment Variables Not Loading

**Problem**: `RESEND_API_KEY` not found even though it's in `.env`

**Solution**: Make sure `.env` is in the project root (not in `backend/`)

---

## Development Workflow

### Making Changes

1. **Backend changes**: Server auto-reloads (if started with `--reload`)
2. **Frontend changes**: Vite auto-reloads
3. **Config changes**: Restart both backend and frontend

### Running Tests

```powershell
# Backend tests
.\.venv\Scripts\python.exe -m pytest

# Frontend tests
cd earnetics-command-center-v3
npm test
```

### Checking System Health

```powershell
.\scripts\doctor.ps1
```

This checks:
- Python version and venv
- Pip alignment
- Required packages
- Backend imports
- Port availability
- Node.js installation
- Frontend structure
- Environment configuration

---

## Production Deployment

### Backend

```powershell
# Use production settings
$env:APP_ENV="production"
$env:FALLAT_RELOAD="false"

# Start with multiple workers (Windows: use --workers 1)
.\.venv\Scripts\python.exe -m uvicorn backend.main_server:app --host 0.0.0.0 --port 8000 --workers 1
```

### Frontend

```powershell
cd earnetics-command-center-v3
npm run build
# Serve the dist/ folder with a web server
```

---

## Logs

### Backend Logs
- **Location**: `backend/logs/backend_boot_latest.log`
- **Content**: Uvicorn startup, requests, errors

### Audit Logs
- **Location**: `audit_log.db` (SQLite database)
- **View**: Use SQLite browser or query via API

---

## Support

### Common Commands Reference

```powershell
# Start backend
.\scripts\start_backend.ps1

# Start frontend
.\scripts\start_frontend.ps1

# Run diagnostics
.\scripts\doctor.ps1

# Install backend deps
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Install frontend deps
cd earnetics-command-center-v3 && npm install

# Check backend health
curl http://127.0.0.1:8000/health

# View API docs
start http://127.0.0.1:8000/docs
```

---

## Architecture Notes

### Backend
- **Framework**: FastAPI (ASGI)
- **Server**: Uvicorn
- **WebSocket**: Native FastAPI WebSocket support
- **Database**: SQLite (business_database.db, audit_log.db)
- **Email**: Resend API
- **Payments**: Stripe API

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **State**: Zustand
- **Styling**: TailwindCSS
- **3D**: Three.js + React Three Fiber
- **Desktop**: Electron (optional)

### Communication
- **REST API**: HTTP/JSON
- **Real-time**: WebSocket (event bus)
- **CORS**: Configured for localhost dev servers

---

**Last Updated**: 2025-12-21
**Version**: 1.0.0
