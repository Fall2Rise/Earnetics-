# Complete Startup Commands - Fallat CrewAI

## 🚀 Quick Start (Recommended Method)

### Prerequisites Check
✅ Virtual environment exists: `venv/`  
✅ Frontend dependencies installed: `fallat_crewai_dashboard/node_modules/`  
✅ `.env` file configured with API keys

---

## 📋 Step-by-Step Startup

### **Terminal 1: Backend Server**

Open PowerShell and run:

```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\start_backend.ps1
```

**OR** manually (if script doesn't work):

```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
```
═══════════════════════════════════════════════════════
  EARNETICS COMMAND CENTER - Backend Startup
═══════════════════════════════════════════════════════

[1/5] Detecting Python interpreter...
  ✓ Found venv: .\venv\Scripts\python.exe
  Python: Python 3.11.x

[2/5] Setting up logging...
  ✓ Logs directory exists

[3/5] Verifying backend module...
  ✓ Backend module imports successfully

[4/5] Checking port availability...
  ✓ Port 8000 is available

[5/5] Starting backend server...

  API URL:  http://127.0.0.1:8000
  WS URL:   ws://127.0.0.1:8000/ws
  Docs:     http://127.0.0.1:8000/docs
  Health:   http://127.0.0.1:8000/health

INFO:     Started server process
INFO:     Vector memory store initialised
INFO:     Corporate memory tables initialised
INFO:     Credential vault ready
INFO:     Audit log wired to Event Bus
INFO:     Autonomy worker started
INFO:     Factory engine started
INFO:     Autonomous Financial Processor started
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**✅ Backend is ready when you see:** `Uvicorn running on http://127.0.0.1:8000`

---

### **Terminal 2: Frontend Dashboard**

Open a **NEW** PowerShell window and run:

```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

**Expected Output:**
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**✅ Frontend is ready when you see:** `Local: http://localhost:5173/`

---

## 🎯 Alternative: Batch Files (Simpler)

### **Terminal 1: Backend**
```cmd
cd C:\AI_Projects\Fallat_CrewAI
scripts\start_backend.bat
```

### **Terminal 2: Frontend**
```cmd
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

---

## 🌐 Access Points

Once both are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | 3D Command Center Dashboard |
| **Backend API** | http://127.0.0.1:8000 | FastAPI Server |
| **API Docs** | http://127.0.0.1:8000/docs | Interactive API Documentation |
| **Health Check** | http://127.0.0.1:8000/health | System Health Status |
| **WebSocket** | ws://127.0.0.1:8000/ws | Real-time Event Stream |

---

## 📝 Complete Command Reference

### **Method 1: Using Startup Scripts (Easiest)**

**Terminal 1 - Backend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\start_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

---

### **Method 2: Manual Commands**

**Terminal 1 - Backend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

---

### **Method 3: Command Prompt (CMD)**

**Terminal 1 - Backend:**
```cmd
cd C:\AI_Projects\Fallat_CrewAI
venv\Scripts\activate
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```cmd
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

---

## 🔧 Troubleshooting

### If Backend Won't Start:

1. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Check Python version:**
   ```powershell
   python --version  # Should be 3.11+
   ```

3. **Install dependencies:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. **Verify .env file exists:**
   ```powershell
   Test-Path .env  # Should return True
   ```

5. **Check if port 8000 is in use:**
   ```powershell
   Get-NetTCPConnection -LocalPort 8000
   ```

### If Frontend Won't Start:

1. **Navigate to frontend directory:**
   ```powershell
   cd fallat_crewai_dashboard
   ```

2. **Install dependencies (if needed):**
   ```powershell
   npm install
   ```

3. **Check Node.js version:**
   ```powershell
   node --version  # Should be 18+
   ```

4. **Check if port 5173 is in use:**
   ```powershell
   Get-NetTCPConnection -LocalPort 5173
   ```

---

## ✅ Verification Checklist

After starting both terminals:

- [ ] Backend shows "Uvicorn running on http://127.0.0.1:8000"
- [ ] Frontend shows "Local: http://localhost:5173/"
- [ ] Can access http://localhost:5173 in browser
- [ ] Can access http://127.0.0.1:8000/docs in browser
- [ ] 3D Command Center loads in browser
- [ ] No error messages in either terminal
- [ ] WebSocket connection established (check browser console)

---

## 🎉 You're Ready!

Once both terminals show success messages:

1. **Open browser to:** http://localhost:5173
2. **You'll see:** 3D Command Center with 9 department zones
3. **All 30+ agents** are active and visible
4. **Real-time updates** are streaming via WebSocket
5. **Autonomous systems** are running in background

**Total startup time: ~10-20 seconds**

---

## 📌 Quick Reference Card

**Copy & Paste These Commands:**

**Terminal 1:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\start_backend.ps1
```

**Terminal 2:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

**Then open:** http://localhost:5173
