from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.database import get_db

router = APIRouter(prefix="/crm/contacts", tags=["crm-contacts"])


@router.post("", response_model=schemas.Contact)
def create_contact(payload: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, payload)


@router.get("", response_model=List[schemas.Contact])
def list_contacts(
    type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_contacts(db, type=type, source=source, tags=tags, search=search)


@router.get("/{contact_id}", response_model=schemas.Contact)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    obj = crud.get_contact(db, contact_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")
    return obj


@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, payload: schemas.ContactUpdate, db: Session = Depends(get_db)):
    obj = crud.update_contact(db, contact_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")
    return obj


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_contact(db, contact_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"status": "deleted"}


@router.get("/{contact_id}/deals", response_model=List[schemas.Deal])
def contact_deals(contact_id: int, db: Session = Depends(get_db)):
    return crud.list_deals(db, contact_id=contact_id)


@router.get("/{contact_id}/interactions", response_model=List[schemas.Interaction])
def contact_interactions(contact_id: int, db: Session = Depends(get_db)):
    return crud.list_interactions(db, contact_id=contact_id)


@router.get("/{contact_id}/tasks", response_model=List[schemas.Task])
def contact_tasks(contact_id: int, db: Session = Depends(get_db)):
    return crud.list_tasks(db, contact_id=contact_id)
