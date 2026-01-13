# Troubleshooting: Frontend Not Loading Fully

## 🔍 Common Issues & Fixes

### Issue 1: API Connection Problems

**Symptom:** Frontend loads but data doesn't appear, errors in browser console

**Check:**
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Look for errors like:
   - `Failed to fetch`
   - `CORS error`
   - `Network error`
   - `404 Not Found`

**Fix:**
The frontend uses relative URLs by default. If you see CORS errors, you need to configure a proxy.

**Add proxy to `vite.config.ts`:**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      }
    }
  }
});
```

Then restart the frontend dev server.

---

### Issue 2: WebSocket Connection Failing

**Symptom:** Real-time updates not working, WebSocket errors

**Check Browser Console:**
- Look for WebSocket connection errors
- Check if `ws://localhost:8000/ws` is accessible

**Fix:**
Some frontend files hardcode `ws://localhost:8000/ws`. If using proxy, update to relative URL or configure proxy.

---

### Issue 3: 3D Components Not Loading

**Symptom:** 3D scene doesn't render, blank area where 3D should be

**Possible Causes:**
1. Three.js/React Three Fiber not loading
2. WebGL not supported in browser
3. Missing dependencies

**Fix:**
1. Check browser console for Three.js errors
2. Verify WebGL support: https://get.webgl.org/
3. Reinstall dependencies:
   ```powershell
   cd fallat_crewai_dashboard
   npm install
   ```

---

### Issue 4: Environment Variables Not Set

**Symptom:** API calls failing, empty responses

**Check:**
Frontend might need `VITE_API_BASE_URL` set.

**Fix:**
Create `.env` file in `fallat_crewai_dashboard/`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then restart the dev server.

---

### Issue 5: CORS Errors

**Symptom:** Browser console shows CORS policy errors

**Backend CORS is configured**, but if you see errors:

**Check backend is allowing frontend origin:**
- Backend should allow `http://localhost:5173`
- Check backend logs for CORS errors

**Quick Fix:**
Use the proxy configuration above (Issue 1) to avoid CORS entirely.

---

## 🔧 Step-by-Step Diagnosis

### 1. Check Backend is Running
```powershell
curl http://127.0.0.1:8000/health
```
Should return: `{"status":"degraded" or "online",...}`

### 2. Check Frontend is Running
```powershell
curl http://localhost:5173
```
Should return HTML content

### 3. Check Browser Console
- Press F12 in browser
- Go to Console tab
- Look for red errors
- Note any failed network requests

### 4. Check Network Tab
- Press F12 → Network tab
- Refresh page
- Look for failed requests (red)
- Check which API calls are failing

### 5. Check API Endpoints
```powershell
# Test system status
curl http://127.0.0.1:8000/api/system/status

# Test agents
curl http://127.0.0.1:8000/api/agents/real_status
```

---

## 🎯 Quick Fixes

### Fix 1: Add Vite Proxy (Recommended)

Edit `fallat_crewai_dashboard/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      }
    }
  }
});
```

Then restart frontend: `Ctrl+C` and `npm run dev` again

---

### Fix 2: Set Environment Variable

Create `fallat_crewai_dashboard/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart frontend dev server.

---

### Fix 3: Check Browser Compatibility

- Use Chrome, Edge, or Firefox (latest versions)
- Enable WebGL (usually enabled by default)
- Disable ad blockers that might block API calls

---

## 📋 What to Check Right Now

1. **Open Browser Console (F12)**
   - What errors do you see?
   - Any failed network requests?

2. **Check Network Tab**
   - Are API calls returning 200 OK?
   - Or are they failing with errors?

3. **Verify Backend**
   - Is it still running?
   - Can you access http://127.0.0.1:8000/docs?

4. **Verify Frontend**
   - Is it still running?
   - Can you see the page at all, or is it blank?

---

## 🚨 Most Common Issue

**CORS/API Connection:** Frontend can't reach backend API

**Solution:** Add the proxy configuration above to `vite.config.ts`

This will route all `/api` requests through the Vite dev server to the backend, avoiding CORS issues.

