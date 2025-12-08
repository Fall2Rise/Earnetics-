from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from earnetics_crm.database import Base


class CRMContact(Base):
    __tablename__ = "crm_contacts"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # comma separated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    deals: List["CRMDeal"] = relationship("CRMDeal", back_populates="contact", cascade="all,delete")
    interactions: List["CRMInteraction"] = relationship("CRMInteraction", back_populates="contact", cascade="all,delete")
    tasks: List["CRMTask"] = relationship("CRMTask", back_populates="contact", cascade="all,delete")


class CRMDeal(Base):
    __tablename__ = "crm_deals"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id"), nullable=True)
    title = Column(String, nullable=False)
    pipeline = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    value_estimate = Column(Float, nullable=True)
    priority = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact = relationship("CRMContact", back_populates="deals")
    interactions: List["CRMInteraction"] = relationship("CRMInteraction", back_populates="deal", cascade="all,delete")
    tasks: List["CRMTask"] = relationship("CRMTask", back_populates="deal", cascade="all,delete")


class CRMInteraction(Base):
    __tablename__ = "crm_interactions"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id"), nullable=False)
    deal_id = Column(Integer, ForeignKey("crm_deals.id"), nullable=True)
    channel = Column(String, nullable=False)
    direction = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    contact = relationship("CRMContact", back_populates="interactions")
    deal = relationship("CRMDeal", back_populates="interactions")


class CRMTask(Base):
    __tablename__ = "crm_tasks"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    owner = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact = relationship("CRMContact", back_populates="tasks")
    deal = relationship("CRMDeal", back_populates="tasks")


class CRMPipeline(Base):
    __tablename__ = "crm_pipelines"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    stages = Column(Text, nullable=False)  # JSON-encoded list of stages
