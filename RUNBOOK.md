# Earnetics Command Center — One Way To Run

## ⚠️ IMPORTANT: Single Entrypoint System

**The ONLY supported way to run Earnetics is through the scripts in `/scripts`.**

Direct execution of `python backend/main_server.py` or `python -m backend.main_server` is **blocked**.

---

## 🚀 Quick Start (ONLY)
```powershell
.\scripts\run_all.ps1
```
This opens backend and frontend in separate PowerShell windows.

### Stop Everything
```powershell
.\scripts\stop_all.ps1
```

### Health Check
```powershell
.\scripts\health.ps1
```

---

## 📋 Prerequisites

1. **Python 3.11+** with virtual environment
   - Location: `venv\` or `backend\.venv\`
   - Scripts auto-detect both locations

2. **Node.js 18+** for frontend
   - Frontend folder: `fallat_crewai_dashboard\`
   - Scripts auto-detect and install dependencies if needed

3. **Ollama** (for LLM agents)
   - Must be running locally
   - Default: `http://localhost:11434`

---

## 🔧 Troubleshooting

### Port Conflicts

**Problem**: Port 8000 or 5173 already in use

**Solution**:
```powershell
.\scripts\stop_all.ps1
.\scripts\run_all.ps1
```

The scripts automatically kill processes using these ports before starting.

### Backend Not Starting

**Check**:
1. Virtual environment exists: `venv\Scripts\Activate.ps1` or `backend\.venv\Scripts\Activate.ps1`
2. Dependencies installed: `pip install -r requirements.txt`
3. Port 8000 is free: `.\scripts\stop_all.ps1`

**Verify backend health**:
```powershell
.\scripts\health.ps1
```

Or manually check: http://127.0.0.1:8000/docs

### Frontend Not Starting

**Check**:
1. Frontend folder exists: `fallat_crewai_dashboard\`
2. `package.json` exists in frontend folder
3. Node modules installed: Scripts auto-install if missing

**Verify frontend**:
- Check terminal for port number (usually 5173)
- Open: http://localhost:5173

### "Failed to Fetch" Error

**Causes**:
1. Backend not running
2. Backend still initializing (wait 10-15 seconds)
3. Port conflict

**Solution**:
```powershell
.\scripts\stop_all.ps1
.\scripts\run_all.ps1
```

### Virtual Environment Not Found

**Error**: `backend\.venv not found`

**Solution**:
```powershell
# Create venv at repo root
python -m venv venv

# Or in backend folder
python -m venv backend\.venv

# Then activate and install
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🌐 Access Points

- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Frontend**: http://localhost:5173 (check terminal for exact port)

---

## 📁 Script Details

### `scripts/run_all.ps1`
- Opens backend in new PowerShell window
- Opens frontend in new PowerShell window
- **ONLY approved method to start full system**

### `scripts/stop_all.ps1`
- Kills processes on ports 8000 and 5173
- **ONLY approved method to stop everything**

### `scripts/health.ps1`
- Checks backend health endpoint
- Falls back to `/docs` if `/health` unavailable
- Returns exit code 0 (healthy) or 1 (unhealthy)

### `scripts/_ports.ps1`
- Shared helper for port management
- Used by other scripts
- Do not run directly

---

## 🚫 Deprecated Methods

**DO NOT USE**:
- ❌ `python backend/main_server.py` (blocked)
- ❌ `python -m backend.main_server` (blocked)
- ❌ `uvicorn backend.main_server:app` (use `backend.run` instead)
- ❌ Manual port killing
- ❌ Manual venv activation (scripts handle it)

**These will fail with deprecation message.**

---

## 🔄 Migration Notes

The new system:
- Uses `backend/run.py` as the launcher
- Uses `backend/app.py` as the single import location
- Wraps existing `backend/main_server.py` (no breaking changes)
- Enforces single entrypoint via deprecation blocks

All existing routes, agents, and functionality remain unchanged.

---

## 📞 Support

If scripts fail:
1. Check PowerShell execution policy: `Get-ExecutionPolicy`
2. If restricted, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Check terminal output for specific errors
4. Verify prerequisites (Python, Node, venv, dependencies)
