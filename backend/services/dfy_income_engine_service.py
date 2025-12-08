from typing import List
from backend.models.dfy_income_engine import DFYLead, dfy_leads_store

def create_dfy_lead(lead: DFYLead) -> DFYLead:
    """Store a new DFY lead."""
    dfy_leads_store[lead.id] = lead
    return lead

def list_dfy_leads() -> List[DFYLead]:
    """Retrieve all DFY leads."""
    return list(dfy_leads_store.values())
