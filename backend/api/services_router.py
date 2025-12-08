
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/services", tags=["services"])


class ServiceInfo(BaseModel):
    key: str
    name: str
    category: str
    status: str
    description: str
    endpoint: Optional[str] = None
    documentation: Optional[str] = None
    dependencies: Optional[List[str]] = None


_BASE_SERVICES: Dict[str, Dict[str, Any]] = {
    "vector_memory": {
        "name": "Vector Memory",
        "category": "knowledge",
        "description": "Embeddings store for semantic recall and search.",
        "endpoint": "/api/vector-memory",
        "documentation": None,
        "dependencies": ["sentence-transformers", "numpy"],
    },
    "credential_vault": {
        "name": "Credential Vault",
        "category": "security",
        "description": "Encrypted credential storage for platform integrations.",
        "endpoint": "/api/credentials",
        "documentation": None,
        "dependencies": ["cryptography", "keyring"],
    },
    "workflow_scheduler": {
        "name": "Workflow Scheduler",
        "category": "automation",
        "description": "Persistent job orchestration and approval flow management.",
        "endpoint": "/api/workflows/scheduler",
        "documentation": None,
        "dependencies": ["sqlite3"],
    },
    "audit_log": {
        "name": "Audit Log",
        "category": "governance",
        "description": "Structured event logging across corporate agents.",
        "endpoint": "/api/audit",
        "documentation": None,
        "dependencies": ["sqlite3"],
    },
    "integration_registry": {
        "name": "Integration Registry",
        "category": "integrations",
        "description": "Discovery for connected third-party services and APIs.",
        "endpoint": "/api/integrations",
        "documentation": None,
        "dependencies": None,
    },
}


def _service_status(key: str, request: Request) -> str:
    app_state = getattr(request.app, "state", None)

    if key == "vector_memory":
        vector_store = getattr(app_state, "vector_store", None) if app_state else None
        return "online" if vector_store is not None else "offline"

    if key == "credential_vault":
        vault = getattr(app_state, "credential_vault", None) if app_state else None
        return "online" if vault is not None else "offline"

    if key == "workflow_scheduler":
        # Scheduler instances are created per-router; treat availability as operational.
        return "operational"

    if key == "audit_log":
        return "operational"

    if key == "integration_registry":
        return "operational"

    return "unknown"


def _collect_service_info(request: Request) -> List[ServiceInfo]:
    services: List[ServiceInfo] = []
    for key, meta in _BASE_SERVICES.items():
        dependencies_value = meta.get("dependencies")
        dependencies: Optional[List[str]]
        if isinstance(dependencies_value, list):
            dependencies = [str(item) for item in dependencies_value]
        elif isinstance(dependencies_value, str):
            dependencies = [dependencies_value]
        else:
            dependencies = None
        info = ServiceInfo(
            key=key,
            name=str(meta.get("name") or key.replace("_", " ").title()),
            category=str(meta.get("category") or "general"),
            description=str(meta.get("description") or ""),
            endpoint=meta.get("endpoint"),
            documentation=meta.get("documentation"),
            dependencies=dependencies,
            status=_service_status(key, request),
        )
        services.append(info)
    return services


@router.get("/", response_model=Dict[str, List[ServiceInfo]])
def list_services(request: Request) -> Dict[str, List[ServiceInfo]]:
    services = _collect_service_info(request)
    return {"services": services}


@router.get("/{service_key}", response_model=ServiceInfo)
def get_service(service_key: str, request: Request) -> ServiceInfo:
    if service_key not in _BASE_SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    services = {service.key: service for service in _collect_service_info(request)}
    return services[service_key]
