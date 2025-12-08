from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from backend.audit_log import log_event

LEAD_STORE = Path(os.getenv('REALESTATE_LEAD_STORE', 'real_estate_leads.json'))


@dataclass
class RealEstateLead:
    id: str
    address: str
    seller_name: str
    seller_contact: str
    status: str = 'new'
    source: str = 'manual'
    created_at: str = datetime.utcnow().isoformat()
    notes: Optional[str] = None


class LeadPipeline:
    def __init__(self, store_path: Path = LEAD_STORE):
        self.store_path = store_path
        self.leads: Dict[str, RealEstateLead] = {}
        self._load()

    def _load(self) -> None:
        if self.store_path.exists():
            data = json.loads(self.store_path.read_text())
            self.leads = {entry['id']: RealEstateLead(**entry) for entry in data}

    def _save(self) -> None:
        data = [asdict(lead) for lead in self.leads.values()]
        self.store_path.write_text(json.dumps(data, indent=2))

    def add_lead(self, lead: RealEstateLead) -> None:
        self.leads[lead.id] = lead
        self._save()
        log_event('real_estate.lead_added', lead_id=lead.id)

    def update_status(self, lead_id: str, status: str, notes: Optional[str] = None) -> None:
        lead = self.leads.get(lead_id)
        if not lead:
            raise ValueError('Lead not found')
        lead.status = status
        lead.notes = notes
        self._save()
        log_event('real_estate.lead_updated', lead_id=lead.id, status=status)

    def list_leads(self, status: Optional[str] = None) -> List[RealEstateLead]:
        leads = list(self.leads.values())
        if status:
            leads = [lead for lead in leads if lead.status == status]
        return leads

lead_pipeline = LeadPipeline()
