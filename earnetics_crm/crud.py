from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from earnetics_crm import models, schemas
from earnetics_crm.config import DEFAULT_PIPELINES


# Contacts -------------------------------------------------------------
def create_contact(db: Session, contact: schemas.ContactCreate) -> models.CRMContact:
    db_obj = models.CRMContact(**contact.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_contact(db: Session, contact_id: int) -> Optional[models.CRMContact]:
    return db.query(models.CRMContact).filter(models.CRMContact.id == contact_id).first()


def list_contacts(
    db: Session,
    *,
    type: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
) -> List[models.CRMContact]:
    query = db.query(models.CRMContact)
    if type:
        query = query.filter(models.CRMContact.type == type)
    if source:
        query = query.filter(models.CRMContact.source == source)
    if tags:
        query = query.filter(models.CRMContact.tags.like(f"%{tags}%"))
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(models.CRMContact.name.like(like), models.CRMContact.email.like(like), models.CRMContact.phone.like(like))
        )
    return query.order_by(models.CRMContact.created_at.desc()).all()


def update_contact(db: Session, contact_id: int, payload: schemas.ContactUpdate) -> Optional[models.CRMContact]:
    obj = get_contact(db, contact_id)
    if not obj:
        return None
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_contact(db: Session, contact_id: int) -> bool:
    obj = get_contact(db, contact_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Deals -----------------------------------------------------------------
def create_deal(db: Session, deal: schemas.DealCreate) -> models.CRMDeal:
    db_obj = models.CRMDeal(**deal.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_deal(db: Session, deal_id: int) -> Optional[models.CRMDeal]:
    return db.query(models.CRMDeal).filter(models.CRMDeal.id == deal_id).first()


def list_deals(
    db: Session,
    *,
    pipeline: Optional[str] = None,
    stage: Optional[str] = None,
    priority: Optional[str] = None,
    contact_id: Optional[int] = None,
) -> List[models.CRMDeal]:
    query = db.query(models.CRMDeal)
    if pipeline:
        query = query.filter(models.CRMDeal.pipeline == pipeline)
    if stage:
        query = query.filter(models.CRMDeal.stage == stage)
    if priority:
        query = query.filter(models.CRMDeal.priority == priority)
    if contact_id:
        query = query.filter(models.CRMDeal.contact_id == contact_id)
    return query.order_by(models.CRMDeal.created_at.desc()).all()


def update_deal(db: Session, deal_id: int, payload: schemas.DealUpdate) -> Optional[models.CRMDeal]:
    obj = get_deal(db, deal_id)
    if not obj:
        return None
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_deal(db: Session, deal_id: int) -> bool:
    obj = get_deal(db, deal_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def move_deal_stage(db: Session, deal_id: int, stage: str) -> Optional[models.CRMDeal]:
    obj = get_deal(db, deal_id)
    if not obj:
        return None
    obj.stage = stage
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


# Interactions ----------------------------------------------------------
def create_interaction(db: Session, interaction: schemas.InteractionCreate) -> models.CRMInteraction:
    payload = interaction.dict()
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.utcnow()
    db_obj = models.CRMInteraction(**payload)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def list_interactions(
    db: Session,
    *,
    contact_id: Optional[int] = None,
    deal_id: Optional[int] = None,
    channel: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[models.CRMInteraction]:
    query = db.query(models.CRMInteraction)
    if contact_id:
        query = query.filter(models.CRMInteraction.contact_id == contact_id)
    if deal_id:
        query = query.filter(models.CRMInteraction.deal_id == deal_id)
    if channel:
        query = query.filter(models.CRMInteraction.channel == channel)
    if start:
        query = query.filter(models.CRMInteraction.timestamp >= start)
    if end:
        query = query.filter(models.CRMInteraction.timestamp <= end)
    return query.order_by(models.CRMInteraction.timestamp.desc()).all()


def delete_interaction(db: Session, interaction_id: int) -> bool:
    obj = db.query(models.CRMInteraction).filter(models.CRMInteraction.id == interaction_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Tasks -----------------------------------------------------------------
def create_task(db: Session, task: schemas.TaskCreate) -> models.CRMTask:
    db_obj = models.CRMTask(**task.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_task(db: Session, task_id: int) -> Optional[models.CRMTask]:
    return db.query(models.CRMTask).filter(models.CRMTask.id == task_id).first()


def list_tasks(
    db: Session,
    *,
    status: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    owner: Optional[str] = None,
    contact_id: Optional[int] = None,
    deal_id: Optional[int] = None,
) -> List[models.CRMTask]:
    query = db.query(models.CRMTask)
    if status:
        query = query.filter(models.CRMTask.status == status)
    if owner:
        query = query.filter(models.CRMTask.owner == owner)
    if contact_id:
        query = query.filter(models.CRMTask.contact_id == contact_id)
    if deal_id:
        query = query.filter(models.CRMTask.deal_id == deal_id)
    if due_before:
        query = query.filter(models.CRMTask.due_at <= due_before)
    if due_after:
        query = query.filter(models.CRMTask.due_at >= due_after)
    return query.order_by(models.CRMTask.created_at.desc()).all()


def update_task(db: Session, task_id: int, payload: schemas.TaskUpdate) -> Optional[models.CRMTask]:
    obj = get_task(db, task_id)
    if not obj:
        return None
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


def delete_task(db: Session, task_id: int) -> bool:
    obj = get_task(db, task_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Pipelines -------------------------------------------------------------
def ensure_default_pipelines(db: Session) -> None:
    for name, stages in DEFAULT_PIPELINES.items():
        exists = db.query(models.CRMPipeline).filter(models.CRMPipeline.name == name).first()
        if not exists:
            db_obj = models.CRMPipeline(name=name, stages=",".join(stages))
            db.add(db_obj)
    db.commit()


def list_pipelines(db: Session) -> List[models.CRMPipeline]:
    return db.query(models.CRMPipeline).order_by(models.CRMPipeline.name).all()


def get_pipeline(db: Session, name: str) -> Optional[models.CRMPipeline]:
    return db.query(models.CRMPipeline).filter(models.CRMPipeline.name == name).first()
