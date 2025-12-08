from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from backend.model_registry import ModelEntry, model_registry

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelPayload(BaseModel):
    name: str
    family: str  # embedding or llm
    version: str
    local_path: Optional[str] = None


@router.get("/{family}")
def list_models(family: str):
    try:
        models = model_registry.list_models(family)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"models": [entry.__dict__ for entry in models]}


@router.post("/register")
def register_model(payload: ModelPayload):
    entry = ModelEntry(
        name=payload.name,
        family=payload.family,
        version=payload.version,
        local_path=payload.local_path,
        active=False,
    )
    try:
        model_registry.register_model(entry)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "registered", "model": entry.__dict__}


@router.post("/{family}/{name}/activate")
def activate_model(family: str, name: str):
    try:
        model_registry.set_active(family, name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    active = model_registry.get_active(family)
    return {"status": "activated", "active": active.__dict__ if active else None}


@router.post("/{family}/{name}/upload")
async def upload_model_file(family: str, name: str, file: UploadFile):
    target_dir = Path("models") / family
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{name}.bin"
    try:
        with target_path.open("wb") as dst:
            dst.write(await file.read())
        model_registry.register_model(
            ModelEntry(name=name, family=family, version="uploaded", local_path=str(target_path), active=False)
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "uploaded", "path": str(target_path)}

