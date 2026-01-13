from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.audit_log import log_event
from backend.credential_vault import CredentialVault, CredentialVaultError
from backend.services.credential_suggestions_service import CredentialSuggestionsService

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

suggestions_service = CredentialSuggestionsService()

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


@router.get("/suggestions")
def get_credential_suggestions(
    revenue_stream: Optional[str] = None,
    min_priority: Optional[int] = None
) -> Dict[str, Any]:
    """Get suggested credentials based on revenue opportunities"""
    store = _get_vault()
    
    # Get all suggestions
    suggestions = suggestions_service.get_suggestions(
        revenue_stream=revenue_stream,
        min_priority=min_priority
    )
    
    # Check which credentials are already added
    existing_credentials = {}
    try:
        records = store.list_secrets()
        for record in records:
            key = f"{record.service}/{record.name}"
            existing_credentials[key] = True
    except Exception:
        pass  # If vault is not available, continue without checking
    
    # Mark suggestions as added if credential exists
    enriched_suggestions = []
    for suggestion in suggestions:
        key = f"{suggestion['service']}/{suggestion['name']}"
        is_added = key in existing_credentials
        enriched_suggestions.append({
            **suggestion,
            "is_added": is_added,
            "status": "added" if is_added else suggestion.get("status", "suggested")
        })
    
    return {
        "suggestions": enriched_suggestions,
        "total": len(enriched_suggestions),
        "added_count": sum(1 for s in enriched_suggestions if s["is_added"]),
        "pending_count": sum(1 for s in enriched_suggestions if not s["is_added"])
    }


@router.post("/suggestions/discover")
def discover_revenue_credentials(
    revenue_stream: str,
    required_credentials: list[Dict[str, str]],
    discovered_by: str = "Agent"
) -> Dict[str, Any]:
    """Discover and add credential suggestions for a new revenue stream"""
    result = suggestions_service.discover_revenue_stream_credentials(
        revenue_stream=revenue_stream,
        required_credentials=required_credentials,
        discovered_by=discovered_by
    )
    log_event(
        "credentials.discover",
        status="success",
        revenue_stream=revenue_stream,
        suggestions_added=result.get("suggestions_added", 0)
    )
    return result


@router.post("/suggestions/mark-added")
def mark_suggestion_added(identifier: CredentialIdentifier) -> Dict[str, Any]:
    """Mark a suggestion as added"""
    suggestions_service.mark_as_added(identifier.service, identifier.name)
    return {"status": "marked", "service": identifier.service, "name": identifier.name}


@router.post("/suggestions/dismiss")
def dismiss_suggestion(identifier: CredentialIdentifier) -> Dict[str, Any]:
    """Dismiss a credential suggestion"""
    suggestions_service.dismiss_suggestion(identifier.service, identifier.name)
    return {"status": "dismissed", "service": identifier.service, "name": identifier.name}
