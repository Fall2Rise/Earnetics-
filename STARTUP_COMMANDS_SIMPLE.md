# 🚀 STARTUP COMMANDS - Copy & Paste

## Quick Start (2 Terminals)

---

## **TERMINAL 1: Backend Server**

Open PowerShell and copy/paste these commands **one at a time**:

```powershell
cd C:\AI_Projects\Fallat_CrewAI
```

```powershell
.\venv\Scripts\Activate.ps1
```

```powershell
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**✅ Wait for:** `INFO: Uvicorn running on http://127.0.0.1:8000`

**Keep this terminal open!**

---

## **TERMINAL 2: Frontend Dashboard**

Open a **NEW PowerShell** window and copy/paste:

```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
```

```powershell
npm run dev
```

**✅ Wait for:** `Local: http://localhost:5173/`

**Keep this terminal open!**

---

## **BROWSER**

Open your browser and go to:

```
http://localhost:5173
```

---

## 🎯 All-in-One Commands (Alternative)

If you prefer single-line commands:

### **Terminal 1 - Backend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI; .\venv\Scripts\Activate.ps1; python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

### **Terminal 2 - Frontend:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard; npm run dev
```

---

## ✅ What You Should See

### **Terminal 1 (Backend):**
```
INFO: Vector memory store initialised
INFO: Corporate memory tables initialised
INFO: Credential vault ready
INFO: Audit log wired to Event Bus
INFO: Autonomy worker autonomy-worker started
INFO: Factory engine started
INFO: Autonomous Financial Processor started
INFO: Uvicorn running on http://127.0.0.1:8000
```

### **Terminal 2 (Frontend):**
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### **Browser:**
- 3D Command Center loads
- 9 department zones visible
- 30+ agent nodes displayed
- Real-time updates working

---

## 🔧 If Something Doesn't Work

### **Backend Issues:**

1. **Virtual environment not activated?**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Python not found?**
   ```powershell
   python --version
   ```
   Should show Python 3.11+

3. **Port 8000 in use?**
   ```powershell
   Get-NetTCPConnection -LocalPort 8000
   ```
   If something is using it, stop that process first.

### **Frontend Issues:**

1. **Node.js not found?**
   ```powershell
   node --version
   ```
   Should show Node.js 18+

2. **Dependencies not installed?**
   ```powershell
   cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
   npm install
   ```

3. **Port 5173 in use?**
   ```powershell
   Get-NetTCPConnection -LocalPort 5173
   ```

---

## 📋 Complete Step-by-Step

### **Step 1: Open Terminal 1**
- Press `Win + X`
- Select "Windows PowerShell" or "Terminal"
- Copy/paste backend commands above

### **Step 2: Open Terminal 2**
- Press `Win + X` again
- Select "Windows PowerShell" or "Terminal" (new window)
- Copy/paste frontend commands above

### **Step 3: Open Browser**
- Press `Win + R`
- Type: `http://localhost:5173`
- Press Enter

---

## 🎉 That's It!

Once both terminals show success messages:
- ✅ Backend is running
- ✅ Frontend is running
- ✅ Browser shows 3D Command Center
- ✅ Autonomous systems are active

**Total time: ~10-20 seconds**

---

## 🛑 To Stop Everything

### **Stop Backend:**
- In Terminal 1, press `Ctrl + C`

### **Stop Frontend:**
- In Terminal 2, press `Ctrl + C`

---

## 📞 Quick Reference

**Backend URL:** http://127.0.0.1:8000  
**Frontend URL:** http://localhost:5173  
**API Docs:** http://127.0.0.1:8000/docs  
**Health Check:** http://127.0.0.1:8000/health

---

**🚀 Ready to launch!**

