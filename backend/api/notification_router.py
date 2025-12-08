from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.notification_service import notification_service, NotificationSettings

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationSettingsPayload(BaseModel):
    email_enabled: bool
    email_recipients: list[str]
    desktop_log: bool


@router.get("/settings")
def get_settings():
    settings = notification_service.get_settings()
    return settings.to_dict()


@router.post("/settings")
def update_settings(payload: NotificationSettingsPayload):
    try:
        settings = NotificationSettings(
            email_enabled=payload.email_enabled,
            email_recipients=payload.email_recipients,
            desktop_log=payload.desktop_log,
        )
        notification_service.save_settings(settings)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "updated", "settings": settings.to_dict()}
