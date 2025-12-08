from typing import List

from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.models import CRMContact


def prioritized_deals(db: Session) -> List[schemas.Deal]:
    deals = crud.list_deals(db)
    # Simple sort: high priority first, then value_estimate desc
    def sort_key(d):
        prio = d.priority or "medium"
        prio_score = {"high": 0, "medium": 1, "low": 2}.get(prio, 1)
        val = d.value_estimate or 0
        return (prio_score, -val)

    deals_sorted = sorted(deals, key=sort_key)
    return [schemas.Deal.from_orm(d) for d in deals_sorted]


def contact_summary(db: Session, contact_id: int) -> schemas.Contact:
    obj = crud.get_contact(db, contact_id)
    if not obj:
        raise ValueError("Contact not found")
    return schemas.Contact.from_orm(obj)
