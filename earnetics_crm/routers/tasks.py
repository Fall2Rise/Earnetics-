from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from earnetics_crm import crud, schemas
from earnetics_crm.database import get_db

router = APIRouter(prefix="/crm/tasks", tags=["crm-tasks"])


@router.post("", response_model=schemas.Task)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, payload)


@router.get("", response_model=List[schemas.Task])
def list_tasks(
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    contact_id: Optional[int] = Query(None),
    deal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_tasks(db, status=status, owner=owner, contact_id=contact_id, deal_id=deal_id)


@router.get("/{task_id}", response_model=schemas.Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    obj = crud.get_task(db, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return obj


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    obj = crud.update_task(db, task_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return obj


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}
