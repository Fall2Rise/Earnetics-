from __future__ import annotations

from typing import Optional, Dict, Any

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Path, Query

from backend.audit_log import get_event, list_events, log_event
from backend.prime_directive_guardian import guardian

router = APIRouter(prefix="/api/audit", tags=["audit"])


class ReasonLogRequest(BaseModel):
    action: str
    reason: str
    directive_ref: str
    risk_level: str
    context: Optional[Dict[str, Any]] = None
    owner_approved: bool = False
    cryptographic_approval: bool = False


@router.get("/events")
def get_audit_events(
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    agent: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
):
    try:
        events = list_events(
            limit=limit,
            status=status,
            action=action,
            agent=agent,
            user=user,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to read audit events: {exc}") from exc
    return {"events": events}


@router.get("/events/{event_id}")
def get_audit_event(event_id: int = Path(..., ge=1)):
    event = get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"event": event}


@router.post("/reason")
def log_reason(payload: ReasonLogRequest):
    validation = guardian.validate_action(
        "command_center",
        payload.action,
        {
            "risk_level": payload.risk_level,
            "directive_ref": payload.directive_ref,
            "reason": payload.reason,
            "owner_approved": payload.owner_approved,
            "cryptographic_approval": payload.cryptographic_approval,
        },
    )
    if not validation.get("approved"):
        raise HTTPException(status_code=403, detail=validation.get("reason", "Denied by directive"))

    log_event(
        payload.action,
        agent="command_center",
        user="dashboard",
        message=payload.reason,
        directive_ref=payload.directive_ref,
        risk_level=payload.risk_level,
        context=payload.context or {},
    )

    return {"status": "logged"}
