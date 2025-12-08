from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from earnetics_crm import schemas
from earnetics_crm.database import get_db
from earnetics_crm.services import crm_service

router = APIRouter(prefix="/crm/insights", tags=["crm-insights"])


@router.get("/deals/prioritized", response_model=List[schemas.Deal])
def prioritized_deals(db: Session = Depends(get_db)):
    return crm_service.prioritized_deals(db)
