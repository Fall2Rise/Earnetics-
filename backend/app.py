# backend/app.py
"""
Single source of truth for the FastAPI `app`.

Right now we import the existing app from backend.main_server
to avoid breaking anything. Later, we migrate the full app definition
into this file and keep main_server as legacy-only.
"""

from fastapi import FastAPI

# 1) Try to import the existing app (current system)
try:
    from backend.main_server import app as _existing_app  # type: ignore
    app: FastAPI = _existing_app
except Exception as e:
    # 2) Fallback minimal app so backend/run.py doesn't explode
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"ok": True, "mode": "fallback", "error": str(e)}
