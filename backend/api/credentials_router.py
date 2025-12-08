from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.audit_log import log_event
from backend.credential_vault import CredentialVault, CredentialVaultError

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

vault: Optional[CredentialVault] = None


def configure_credential_vault(store: CredentialVault) -> None:
    global vault
    vault = store


def _get_vault() -> CredentialVault:
    if vault is None:  # pragma: no cover - defensive
        raise RuntimeError("Credential vault not configured")
    return vault


class CredentialPayload(BaseModel):
    service: str = Field(..., description="Logical group or integration name")
    name: str = Field(..., description="Credential identifier (e.g., API key label)")
    secret: str = Field(..., min_length=1, description="Sensitive value to store")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context (account id, notes)")


class CredentialIdentifier(BaseModel):
    service: str
    name: str


@router.post("/store")
def store_credential(payload: CredentialPayload) -> Dict[str, Any]:
    store = _get_vault()
    try:
        record = store.store_secret(
            payload.service,
            payload.name,
            payload.secret,
            metadata=payload.metadata,
        )
        log_event(
            "credentials.store",
            status="success",
            user=None,
            service=payload.service,
            name=payload.name,
            metadata=payload.metadata or {},
        )
    except CredentialVaultError as exc:
        log_event(
            "credentials.store",
            status="error",
            message=str(exc),
            service=payload.service,
            name=payload.name,
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {
        "status": "stored",
        "credential": {
            "service": record.service,
            "name": record.name,
            "metadata": record.metadata,
            "updated_at": record.updated_at,
        },
    }


@router.post("/retrieve")
def retrieve_credential(identifier: CredentialIdentifier) -> Dict[str, Any]:
    store = _get_vault()
    try:
        secret = store.get_secret(identifier.service, identifier.name)
    except CredentialVaultError as exc:
        log_event(
            "credentials.retrieve",
            status="error",
            message=str(exc),
            service=identifier.service,
            name=identifier.name,
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if secret is None:
        log_event(
            "credentials.retrieve",
            status="error",
            message="not found",
            service=identifier.service,
            name=identifier.name,
        )
        raise HTTPException(status_code=404, detail="Credential not found")

    log_event(
        "credentials.retrieve",
        status="success",
        service=identifier.service,
        name=identifier.name,
    )
    return {"service": identifier.service, "name": identifier.name, "secret": secret}


@router.get("/list")
def list_credentials(service: Optional[str] = None) -> Dict[str, Any]:
    store = _get_vault()
    try:
        records = store.list_secrets(service=service)
    except CredentialVaultError as exc:
        log_event(
            "credentials.list",
            status="error",
            message=str(exc),
            service=service,
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    log_event(
        "credentials.list",
        status="success",
        service=service,
        count=len(records),
    )
    return {
        "credentials": [
            {
                "service": record.service,
                "name": record.name,
                "metadata": record.metadata,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }
            for record in records
        ]
    }


@router.delete("/delete")
def delete_credential(identifier: CredentialIdentifier) -> Dict[str, Any]:
    store = _get_vault()
    removed = store.delete_secret(identifier.service, identifier.name)
    if not removed:
        log_event(
            "credentials.delete",
            status="error",
            message="not found",
            service=identifier.service,
            name=identifier.name,
        )
        raise HTTPException(status_code=404, detail="Credential not found")
    log_event(
        "credentials.delete",
        status="success",
        service=identifier.service,
        name=identifier.name,
    )
    return {"status": "deleted", "service": identifier.service, "name": identifier.name}


@router.delete("/services/{service}")
def delete_service(service: str) -> Dict[str, Any]:
    store = _get_vault()
    removed = store.delete_service(service)
    log_event(
        "credentials.delete_service",
        status="success",
        service=service,
        removed=removed,
    )
    return {"status": "deleted", "service": service, "removed": removed}
