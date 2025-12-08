from __future__ import annotations

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, EmailStr, Field


class DFYLeadCreate(BaseModel):
    """
    Payload used when a user submits a new DFY lead from the dashboard.
    The backend will generate id, status, and timestamps.
    """
    name: str
    email: EmailStr
    offer_type: str  # e.g. "affiliate", "course", "service"
    niche: str | None = None
    goal: str | None = None


class DFYLead(BaseModel):
    """
    Core DFY lead model for the Done-For-You Income Engine.

    This is what flows through the DFY pipeline:
      - created via POST /api/dashboard/dfy/leads
      - processed by the DFY worker
      - inspected via GET endpoints
    """

    id: str
    name: str
    email: EmailStr

    offer_type: str
    niche: str | None = None
    goal: str | None = None

    # DFY engine control
    status: str = Field(
        default="new",
        description="new|analyzing|building|deployed|completed|failed",
    )
    strategy_summary: str | None = None
    owning_department: str | None = None  # e.g. "affiliate_stack", "digital_products"
    error: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Simple in-memory store for DFY leads.
# Later this can be replaced with a real database, but all modules should import THIS.
dfy_leads_store: Dict[str, DFYLead] = {}

