from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.database import get_db

router = APIRouter(prefix="/crm/interactions", tags=["crm-interactions"])


@router.post("", response_model=schemas.Interaction)
def create_interaction(payload: schemas.InteractionCreate, db: Session = Depends(get_db)):
    return crud.create_interaction(db, payload)


@router.get("", response_model=List[schemas.Interaction])
def list_interactions(
    contact_id: Optional[int] = Query(None),
    deal_id: Optional[int] = Query(None),
    channel: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_interactions(db, contact_id=contact_id, deal_id=deal_id, channel=channel)


@router.get("/{interaction_id}", response_model=schemas.Interaction)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    obj = db.query(crud.models.CRMInteraction).filter(crud.models.CRMInteraction.id == interaction_id).first()  # type: ignore
    if not obj:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return obj


@router.delete("/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_interaction(db, interaction_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return {"status": "deleted"}
