from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.audit_log import log_event

@dataclass
class ClientAccount:
    name: str
    contact_email: str
    services: List[str] = field(default_factory=list)
    monthly_retainer: float = 0.0
    active: bool = True


@dataclass
class ServiceTask:
    id: str
    client_name: str
    description: str
    due_date: datetime
    assigned_to: Optional[str] = None
    status: str = "pending"
    billable_hours: float = 0.0


@dataclass
class Invoice:
    id: str
    client_name: str
    amount: float
    issued_date: datetime
    status: str = "draft"


class AgencyWorkflowManager:
    def __init__(self):
        self.clients: Dict[str, ClientAccount] = {}
        self.tasks: Dict[str, ServiceTask] = {}
        self.invoices: Dict[str, Invoice] = {}

    def add_client(self, client: ClientAccount) -> None:
        self.clients[client.name] = client
        log_event("services.client_added", client=client.name)

    def create_task(self, task: ServiceTask) -> None:
        self.tasks[task.id] = task
        log_event("services.task_created", task=task.id, client=task.client_name)

    def mark_task_complete(self, task_id: str, billable_hours: float) -> None:
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = "complete"
        task.billable_hours = billable_hours
        log_event("services.task_completed", task=task.id, hours=billable_hours)

    def create_invoice(self, invoice: Invoice) -> None:
        self.invoices[invoice.id] = invoice
        log_event("services.invoice_created", invoice=invoice.id, amount=invoice.amount)

agency_manager = AgencyWorkflowManager()
