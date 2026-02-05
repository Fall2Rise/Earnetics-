# Single Entrypoint System — Current Standard

Only one startup method is supported:

```powershell
.\scripts\run_all.ps1
```

This script launches:
- Backend on `http://127.0.0.1:8000`
- Frontend (3D Command Center) on `http://localhost:5173`

Other startup scripts have been removed to eliminate confusion.
