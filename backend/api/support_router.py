from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.support.support_workflows import CRMContact, SupportTicket, support_manager

router = APIRouter(prefix='/api/support', tags=['support'])


class TicketPayload(BaseModel):
    id: str
    customer: str
    subject: str
    notes: str | None = None


class TicketUpdatePayload(BaseModel):
    status: str
    notes: str | None = None


class ContactPayload(BaseModel):
    name: str
    email: str
    stage: str = 'prospect'


@router.get('/tickets')
def list_tickets(status: str | None = None):
    tickets = support_manager.list_tickets(status=status)
    return {'tickets': [ticket.__dict__ for ticket in tickets]}


@router.post('/tickets')
def create_ticket(payload: TicketPayload):
    try:
        support_manager.create_ticket(SupportTicket(**payload.dict()))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'created'}


@router.post('/tickets/{ticket_id}/status')
def update_ticket(ticket_id: str, payload: TicketUpdatePayload):
    try:
        support_manager.update_ticket(ticket_id, payload.status, notes=payload.notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'updated'}


@router.get('/contacts')
def list_contacts(stage: str | None = None):
    contacts = support_manager.list_contacts(stage=stage)
    return {'contacts': [contact.__dict__ for contact in contacts]}


@router.post('/contacts')
def add_contact(payload: ContactPayload):
    try:
        support_manager.add_contact(CRMContact(**payload.dict()))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'added'}
