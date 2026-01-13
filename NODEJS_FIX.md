# Node.js Installation Fix

## 🔍 Issue
Node.js is not found in PATH, preventing frontend from starting.

## ✅ Solution Options

### Option 1: Install Node.js (If Not Installed)

1. **Download Node.js:**
   - Go to: https://nodejs.org/
   - Download **LTS version** (recommended: v20.x or v18.x)
   - Choose Windows Installer (.msi)

2. **Install:**
   - Run the installer
   - ✅ Check "Add to PATH" during installation
   - Complete installation

3. **Verify:**
   ```powershell
   node --version
   npm --version
   ```

4. **Restart PowerShell** after installation

---

### Option 2: Fix PATH (If Node.js is Installed)

If Node.js is installed but not in PATH:

1. **Find Node.js location:**
   ```powershell
   Get-ChildItem "C:\Program Files\nodejs\node.exe" -ErrorAction SilentlyContinue
   Get-ChildItem "C:\nvm4w\nodejs\node.exe" -Recurse -ErrorAction SilentlyContinue
   ```

2. **Add to PATH temporarily (this session):**
   ```powershell
   $env:PATH += ";C:\Program Files\nodejs"
   ```

3. **Or add permanently:**
   - Open System Properties → Environment Variables
   - Add `C:\Program Files\nodejs` to PATH
   - Restart PowerShell

---

### Option 3: Use nvm4w (If Using Node Version Manager)

If you have nvm4w installed:

1. **List installed versions:**
   ```powershell
   C:\nvm4w\nvm.exe list
   ```

2. **Use a version:**
   ```powershell
   C:\nvm4w\nvm.exe use 20.0.0
   ```

3. **Or install a version:**
   ```powershell
   C:\nvm4w\nvm.exe install 20.0.0
   C:\nvm4w\nvm.exe use 20.0.0
   ```

---

### Option 4: Use Full Path (Quick Workaround)

If Node.js exists but PATH is broken:

```powershell
# Find node.exe
$nodePath = Get-ChildItem "C:\Program Files\nodejs\node.exe" -ErrorAction SilentlyContinue
if (-not $nodePath) {
    $nodePath = Get-ChildItem "C:\nvm4w\nodejs" -Recurse -Filter "node.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
}

# Use full path
& $nodePath.FullName --version
```

Then use full path for npm:
```powershell
& "C:\Program Files\nodejs\npm.cmd" run dev
```

---

## 🎯 Recommended: Quick Fix

**Try this first:**

```powershell
# Refresh PATH in current session
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Test
node --version
```

If that works, restart PowerShell and try again.

---

## ✅ After Fixing

Once Node.js is working:

```powershell
cd C:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard
npm run dev
```

You should see:
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

