# 🚀 START HERE - Complete Startup Guide

## ✅ Prerequisites (One-Time Check)

Before starting, verify:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed  
- ✅ Virtual environment exists (`venv/` folder)
- ✅ Frontend dependencies installed (`fallat_crewai_dashboard/node_modules/`)
- ✅ `.env` file exists with API keys

---

## 🎯 Quick Start (2 Terminals)

### **STEP 1: Start Backend** (Terminal 1)

Open **PowerShell** and run:

```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**✅ Wait for:** `INFO: Uvicorn running on http://127.0.0.1:8000`

**You'll see:**
```
INFO: Vector memory store initialised
INFO: Corporate memory tables initialised
INFO: Credential vault ready
INFO: Audit log wired to Event Bus
INFO: Autonomy worker autonomy-worker started  ← AUTONOMOUS OPERATIONS STARTED
INFO: Factory engine started
INFO: Autonomous Financial Processor started
INFO: Uvicorn running on http://127.0.0.1:8000  ← BACKEND READY
```

---

### **STEP 2: Start Frontend** (Terminal 2)

Open a **NEW PowerShell** window and run:

```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

**✅ Wait for:** `Local: http://localhost:5173/`

**You'll see:**
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### **STEP 3: Open Browser**

Open your browser and go to:

**👉 http://localhost:5173**

---

## 🎉 What Happens Next

### Immediately:
- ✅ 3D Command Center loads in browser
- ✅ All 9 departments visible in 3D space
- ✅ 30+ agents displayed as nodes
- ✅ Real-time WebSocket connection established
- ✅ Autonomous systems are running in background

### Within 60 seconds:
- ✅ First revenue cycle runs automatically
- ✅ New tasks/workflows created
- ✅ Agents start processing tasks

### Within 2 minutes:
- ✅ Core play executor runs
- ✅ Department strategies executing
- ✅ System fully operational

---

## 📋 Complete Command Reference

### **Terminal 1 - Backend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

### **Terminal 2 - Frontend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

### **Browser:**
```
http://localhost:5173
```

---

## 🔍 Verification Checklist

After both terminals are running:

- [ ] Backend shows: `Uvicorn running on http://127.0.0.1:8000`
- [ ] Frontend shows: `Local: http://localhost:5173/`
- [ ] Browser opens to 3D Command Center
- [ ] 9 department zones visible
- [ ] Agent nodes displayed
- [ ] No error messages in terminals
- [ ] WebSocket connected (check browser console F12)

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **3D Command Center** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://127.0.0.1:8000 | FastAPI server |
| **API Docs** | http://127.0.0.1:8000/docs | Interactive API docs |
| **Health Check** | http://127.0.0.1:8000/health | System status |
| **WebSocket** | ws://127.0.0.1:8000/ws | Real-time events |

---

## 🔧 Troubleshooting

### Backend Won't Start?

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

4. **Check port 8000:**
   ```powershell
   Get-NetTCPConnection -LocalPort 8000
   ```

### Frontend Won't Start?

1. **Navigate to frontend directory:**
   ```powershell
   cd fallat_crewai_dashboard
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Check Node.js version:**
   ```powershell
   node --version  # Should be 18+
   ```

4. **Check port 5173:**
   ```powershell
   Get-NetTCPConnection -LocalPort 5173
   ```

---

## 🎮 What You'll See

### In the Browser:
- **3D Command Center** with futuristic interface
- **9 Department Zones** arranged in 3D space
- **Agent Nodes** - Click to see details
- **Holographic Panels** - Floating data displays
- **Real-time Updates** - Live activity feed
- **ATOM Console** - AI chat interface (bottom left)

### In Backend Terminal:
- Service initialization logs
- Autonomous worker status
- Scheduled job registrations
- Real-time processing logs

### In Frontend Terminal:
- Vite compilation status
- Hot module replacement
- Build warnings/errors (if any)

---

## ⚡ Quick Reference Card

**Copy & Paste:**

**Terminal 1:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI && .\venv\Scripts\Activate.ps1 && python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard && npm run dev
```

**Browser:**
```
http://localhost:5173
```

---

## 🎊 You're Ready!

**Total startup time: ~10-20 seconds**

Once both terminals show success messages:
1. ✅ Backend is running autonomously
2. ✅ Frontend is serving the 3D Command Center
3. ✅ All systems are operational
4. ✅ Agents are working automatically
5. ✅ Revenue generation has started

**🚀 Your AI Corporation is LIVE!**

---

## 📞 Need Help?

- Check `STARTUP_COMMANDS.md` for detailed commands
- Check `AUTONOMOUS_OPERATIONS_STARTUP.md` for what runs automatically
- Check `COMMAND_NEXUS_READINESS.md` for system status
- Review terminal error messages for specific issues

---

**🎉 Let's get this party started! 🎉**

