
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.real_estate.leads import RealEstateLead, lead_pipeline

router = APIRouter(prefix="/api/real_estate", tags=["real_estate"])


class LeadPayload(BaseModel):
    id: str
    address: str
    seller_name: str
    seller_contact: str
    source: str = "manual"
    notes: str | None = None


class LeadStatusPayload(BaseModel):
    status: str
    notes: str | None = None


@router.get("/leads")
def list_leads(status: str | None = None):
    leads = lead_pipeline.list_leads(status=status)
    return {"leads": [lead.__dict__ for lead in leads]}


@router.post("/leads")
def create_lead(payload: LeadPayload):
    try:
        lead_pipeline.add_lead(
            RealEstateLead(
                id=payload.id,
                address=payload.address,
                seller_name=payload.seller_name,
                seller_contact=payload.seller_contact,
                source=payload.source,
                notes=payload.notes,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "created"}


@router.post("/leads/{lead_id}/status")
def update_lead_status(lead_id: str, payload: LeadStatusPayload):
    try:
        lead_pipeline.update_status(lead_id, payload.status, notes=payload.notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "updated"}
