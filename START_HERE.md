# 🚀 START HERE - Single Startup Method

## ✅ Prerequisites (One-Time Check)

Before starting, verify:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Virtual environment exists (`venv/` or `backend/.venv`)
- ✅ `.env` file exists with API keys

---

## 🎯 Quick Start (ONE command)

Open **PowerShell** and run:

```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\scripts\run_all.ps1
```

This launches backend + frontend in separate terminals.

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

### Backend or Frontend Won't Start?

1. **Check Python version:**
   ```powershell
   python --version  # Should be 3.11+
   ```

2. **Install backend dependencies:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```powershell
   cd fallat_crewai_dashboard
   npm install
   ```

4. **Restart the system:**
   ```powershell
   cd C:\AI_Projects\Fallat_CrewAI
   .\scripts\run_all.ps1
   ```
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

