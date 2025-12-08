from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from backend.audit_log import log_event

SUPPORT_STORE = Path(os.getenv('SUPPORT_WORKFLOW_STORE', 'support_workflows.json'))


@dataclass
class SupportTicket:
    id: str
    customer: str
    subject: str
    status: str = 'open'
    created_at: str = datetime.utcnow().isoformat()
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CRMContact:
    name: str
    email: str
    stage: str = 'prospect'
    last_touch: Optional[str] = None


class SupportWorkflowManager:
    def __init__(self, store_path: Path = SUPPORT_STORE):
        self.store_path = store_path
        self.tickets: Dict[str, SupportTicket] = {}
        self.contacts: Dict[str, CRMContact] = {}
        self._load()

    def _load(self) -> None:
        if self.store_path.exists():
            data = json.loads(self.store_path.read_text())
            self.tickets = {entry['id']: SupportTicket(**entry) for entry in data.get('tickets', [])}
            self.contacts = {entry['email']: CRMContact(**entry) for entry in data.get('contacts', [])}

    def _save(self) -> None:
        data = {
            'tickets': [asdict(ticket) for ticket in self.tickets.values()],
            'contacts': [asdict(contact) for contact in self.contacts.values()],
        }
        self.store_path.write_text(json.dumps(data, indent=2))

    def create_ticket(self, ticket: SupportTicket) -> None:
        self.tickets[ticket.id] = ticket
        self._save()
        log_event('support.ticket_created', ticket=ticket.id)

    def update_ticket(self, ticket_id: str, status: str, notes: Optional[str] = None) -> None:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise ValueError('Ticket not found')
        ticket.status = status
        ticket.notes = notes
        self._save()
        log_event('support.ticket_updated', ticket=ticket.id, status=status)

    def add_contact(self, contact: CRMContact) -> None:
        self.contacts[contact.email] = contact
        self._save()
        log_event('support.contact_added', contact=contact.email)

    def list_tickets(self, status: Optional[str] = None) -> List[SupportTicket]:
        tickets = list(self.tickets.values())
        if status:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        return tickets

    def list_contacts(self, stage: Optional[str] = None) -> List[CRMContact]:
        contacts = list(self.contacts.values())
        if stage:
            contacts = [contact for contact in contacts if contact.stage == stage]
        return contacts

support_manager = SupportWorkflowManager()
