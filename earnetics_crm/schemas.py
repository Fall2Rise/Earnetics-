from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Base schemas ---------------------------------------------------------
class ContactBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class Contact(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DealBase(BaseModel):
    contact_id: Optional[int] = None
    title: str
    pipeline: str
    stage: str
    value_estimate: Optional[float] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    contact_id: Optional[int] = None
    title: Optional[str] = None
    pipeline: Optional[str] = None
    stage: Optional[str] = None
    value_estimate: Optional[float] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class Deal(DealBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InteractionBase(BaseModel):
    contact_id: int
    deal_id: Optional[int] = None
    channel: str
    direction: Optional[str] = None
    content: str
    timestamp: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    pass


class Interaction(InteractionBase):
    id: int

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = Field(default="pending")
    owner: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = None
    owner: Optional[str] = None


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Pipeline(BaseModel):
    name: str
    stages: List[str]

    class Config:
        orm_mode = True
