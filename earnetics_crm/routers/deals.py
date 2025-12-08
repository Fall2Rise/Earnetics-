from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.database import get_db

router = APIRouter(prefix="/crm/deals", tags=["crm-deals"])


@router.post("", response_model=schemas.Deal)
def create_deal(payload: schemas.DealCreate, db: Session = Depends(get_db)):
    return crud.create_deal(db, payload)


@router.get("", response_model=List[schemas.Deal])
def list_deals(
    pipeline: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    contact_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_deals(db, pipeline=pipeline, stage=stage, priority=priority, contact_id=contact_id)


@router.get("/{deal_id}", response_model=schemas.Deal)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    obj = crud.get_deal(db, deal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    return obj


@router.put("/{deal_id}", response_model=schemas.Deal)
def update_deal(deal_id: int, payload: schemas.DealUpdate, db: Session = Depends(get_db)):
    obj = crud.update_deal(db, deal_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    return obj


@router.delete("/{deal_id}")
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_deal(db, deal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"status": "deleted"}


@router.post("/{deal_id}/move_stage", response_model=schemas.Deal)
def move_stage(deal_id: int, payload: dict, db: Session = Depends(get_db)):
    stage = payload.get("stage")
    if not stage:
        raise HTTPException(status_code=400, detail="stage is required")
    obj = crud.move_deal_stage(db, deal_id, stage)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    return obj
