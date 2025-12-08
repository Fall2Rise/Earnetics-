from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.database import get_db
from earnetics_crm.models import CRMPipeline

router = APIRouter(prefix="/crm/pipelines", tags=["crm-pipelines"])


@router.get("", response_model=List[schemas.Pipeline])
def list_pipelines(db: Session = Depends(get_db)):
    crud.ensure_default_pipelines(db)
    rows: List[CRMPipeline] = crud.list_pipelines(db)
    return [
        schemas.Pipeline(name=row.name, stages=row.stages.split(","))
        for row in rows
    ]


@router.get("/{name}", response_model=schemas.Pipeline)
def get_pipeline(name: str, db: Session = Depends(get_db)):
    crud.ensure_default_pipelines(db)
    row = crud.get_pipeline(db, name)
    if not row:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return schemas.Pipeline(name=row.name, stages=row.stages.split(","))
