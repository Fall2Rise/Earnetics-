"""
API Key Guardian Router
Exposes API endpoints for key management and health monitoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from backend.services.api_key_guardian import APIKeyGuardian

router = APIRouter(prefix="/api/guardian", tags=["API Key Guardian"])

class HealthCheckResponse(BaseModel):
    timestamp: str
    stripe: Dict
    google: Dict
    smtp: Dict

class RotateKeyRequest(BaseModel):
    service: str  # "stripe", "google", etc.

@router.get("/health", response_model=HealthCheckResponse)
async def check_api_health():
    """Run comprehensive health check on all API keys."""
    guardian = APIKeyGuardian()
    results = guardian.run_health_check()
    return results

@router.post("/rotate")
async def rotate_key(request: RotateKeyRequest):
    """Manually trigger key rotation for a specific service."""
    guardian = APIKeyGuardian()
    
    if request.service == "stripe":
        result = guardian.rotate_stripe_key()
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Auto-rotation not supported for {request.service}"
        )

@router.post("/auto-fix")
async def auto_fix():
    """Attempt to automatically fix all detected key issues."""
    guardian = APIKeyGuardian()
    fixes = guardian.auto_fix_issues()
    return {
        "fixes_applied": fixes,
        "count": len(fixes)
    }

@router.get("/status/{service}")
async def check_service_status(service: str):
    """Check health status of a specific service."""
    guardian = APIKeyGuardian()
    
    if service == "stripe":
        return guardian.check_stripe_key_health()
    elif service == "google":
        return guardian.check_google_key_health()
    elif service == "smtp":
        return guardian.check_smtp_health()
    else:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service}")
