from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.factory_engine import FACTORY_ENGINE

router = APIRouter(prefix="/api/factory", tags=["factory"])

class StreamCreate(BaseModel):
    name: str
    note: str = ""


@router.get("/status")
def factory_status() -> Dict[str, Any]:
    return FACTORY_ENGINE.status()


@router.post("/power")
async def factory_power(action: str):
    if action not in {"start", "stop"}:
        raise HTTPException(status_code=400, detail="action must be start or stop")
    if action == "start":
        await FACTORY_ENGINE.start()
    else:
        await FACTORY_ENGINE.stop()
    return FACTORY_ENGINE.status()


@router.get("/streams")
def list_streams() -> Dict[str, Any]:
    return {"streams": FACTORY_ENGINE.list_streams()}


@router.post("/streams")
def create_stream(payload: StreamCreate | None = None, name: str = "", note: str = "") -> Dict[str, Any]:
    """Create a new stream; supports JSON body or query params."""
    stream_name = (payload.name if payload else name or "").strip()
    stream_note = (payload.note if payload else note or "").strip()
    if not stream_name:
        raise HTTPException(status_code=400, detail="name is required")
    try:
        stream = FACTORY_ENGINE.create_stream(stream_name, stream_note)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to create stream: {exc}") from exc
    return {"stream": stream}


@router.post("/streams/{stream_id}/advance")
def advance_stream(stream_id: int, note: str = "") -> Dict[str, Any]:
    try:
        stream = FACTORY_ENGINE.advance_stage(stream_id, note)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to advance stream: {exc}") from exc
    return {"stream": stream}


@router.get("/streams/{stream_id}")
def get_stream(stream_id: int) -> Dict[str, Any]:
    stream = FACTORY_ENGINE.get_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return {"stream": stream}
