# Connection Troubleshooting Guide

## 🔴 Issue: "AWAITING TELEMETRY SYNC" and "Error: Failed to reach ATOM"

This means the frontend cannot connect to the backend API.

---

## ✅ Quick Fix Steps

### **Step 1: Verify Backend is Running**

Open PowerShell and check if backend is running:

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

**If nothing shows up, the backend is NOT running!**

Start it:
```powershell
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Wait for:** `INFO: Uvicorn running on http://127.0.0.1:8000`

---

### **Step 2: Test Backend Connection**

Open a new browser tab and go to:
```
http://127.0.0.1:8000/health
```

**You should see:** JSON response with system status

**If you see:** "This site can't be reached" or connection error
- Backend is NOT running
- Go back to Step 1

---

### **Step 3: Check Frontend Configuration**

The frontend `.env` file should have:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Location:** `fallat_crewai_dashboard/.env`

**If missing or wrong:**
1. Create/update the file
2. Restart the frontend dev server (Ctrl+C, then `npm run dev`)

---

### **Step 4: Restart Frontend**

After fixing configuration:

1. **Stop frontend:** Press `Ctrl+C` in Terminal 2
2. **Restart frontend:**
   ```powershell
   cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
   npm run dev
   ```

---

## 🔍 Detailed Diagnosis

### **Check Browser Console**

1. Open browser (F12 or Right-click → Inspect)
2. Go to **Console** tab
3. Look for errors:
   - `Failed to fetch`
   - `NetworkError`
   - `WebSocket connection failed`

**Common Errors:**

**Error: "Failed to fetch"**
- Backend is not running
- Backend is on wrong port
- CORS issue (shouldn't happen with proxy)

**Error: "WebSocket connection failed"**
- Backend WebSocket endpoint not available
- Backend not running
- Firewall blocking connection

---

### **Check Network Tab**

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh page (F5)
4. Look for requests to `/api/system/status` or `/api/atom/chat`

**What to check:**
- **Status Code:** Should be `200` (not `404`, `500`, or `ERR_CONNECTION_REFUSED`)
- **Request URL:** Should be `http://127.0.0.1:8000/api/...` or `/api/...`
- **Response:** Should be JSON, not HTML error page

---

## 🛠️ Common Fixes

### **Fix 1: Backend Not Running**

**Symptoms:**
- "AWAITING TELEMETRY SYNC"
- All data shows "LOADING..."
- ATOM console shows "Error: Failed to reach ATOM"

**Solution:**
```powershell
# Terminal 1
cd C:\AI_Projects\Fallat_CrewAI
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

---

### **Fix 2: Wrong Port**

**Symptoms:**
- Backend running but frontend can't connect
- Connection refused errors

**Check:**
```powershell
# Check what port backend is actually on
Get-NetTCPConnection -LocalPort 8000
```

**If backend is on different port:**
1. Update `.env` file:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:YOUR_PORT
   ```
2. Restart frontend

---

### **Fix 3: Frontend Using Wrong URL**

**Symptoms:**
- Backend is running and accessible
- Frontend still can't connect

**Check `.env` file:**
```powershell
Get-Content fallat_crewai_dashboard\.env
```

**Should show:**
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**If wrong or missing:**
```powershell
Set-Content -Path "fallat_crewai_dashboard\.env" -Value "VITE_API_BASE_URL=http://127.0.0.1:8000"
```

Then restart frontend.

---

### **Fix 4: Vite Proxy Not Working**

**Symptoms:**
- Backend running
- Direct URL works (`http://127.0.0.1:8000/health`)
- Frontend still can't connect

**Check `vite.config.ts`:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      secure: false,
    },
    '/ws': {
      target: 'ws://127.0.0.1:8000',
      ws: true,
      changeOrigin: true,
    }
  }
}
```

**If missing or wrong:**
1. Update `vite.config.ts`
2. Restart frontend

---

## ✅ Verification Checklist

After fixing, verify:

- [ ] Backend shows: `INFO: Uvicorn running on http://127.0.0.1:8000`
- [ ] `http://127.0.0.1:8000/health` returns JSON
- [ ] Frontend `.env` has `VITE_API_BASE_URL=http://127.0.0.1:8000`
- [ ] Frontend restarted after `.env` change
- [ ] Browser console shows no connection errors
- [ ] Network tab shows successful API calls (status 200)
- [ ] Dashboard shows "Last sync [timestamp]" instead of "AWAITING TELEMETRY SYNC"
- [ ] ATOM console can send messages without errors

---

## 🚨 Still Not Working?

### **Check Backend Logs**

Look at Terminal 1 (backend) for errors:
- Import errors
- Database errors
- Port already in use
- Missing dependencies

### **Check Frontend Logs**

Look at Terminal 2 (frontend) for errors:
- Compilation errors
- Module not found
- Port already in use

### **Test Direct API Call**

Open browser console and run:
```javascript
fetch('http://127.0.0.1:8000/api/system/status')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**If this works:** Frontend configuration issue
**If this fails:** Backend issue

---

## 📞 Quick Reference

**Backend URL:** http://127.0.0.1:8000  
**Frontend URL:** http://localhost:5173  
**Health Check:** http://127.0.0.1:8000/health  
**API Docs:** http://127.0.0.1:8000/docs

**Backend Command:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI; .\venv\Scripts\Activate.ps1; python -m uvicorn backend.main_server:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend Command:**
```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard; npm run dev
```

---

**Most common issue: Backend is not running!**

Start the backend first, then the frontend.

