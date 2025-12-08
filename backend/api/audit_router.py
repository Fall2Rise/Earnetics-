from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query

from backend.audit_log import get_event, list_events

router = APIRouter(prefix="/api/audit", tags=["audit"])


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
