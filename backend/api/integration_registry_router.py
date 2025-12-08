from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.integration_registry import connectors_by_slug, summarize_connectors

router = APIRouter(prefix="/api/integration-registry", tags=["integrations"])


@router.get("")
def list_all_connectors():
    """Return readiness information for all registered integrations."""
    return {"connectors": summarize_connectors()}


@router.get("/{category}")
def list_category_connectors(category: str):
    connectors = summarize_connectors(category=category)
    if not connectors:
        raise HTTPException(status_code=404, detail=f"No connectors registered for category '{category}'")
    return {"category": category, "connectors": connectors}


@router.get("/connector/{slug}")
def get_connector(slug: str):
    connector = connectors_by_slug(slug)
    if connector is None:
        raise HTTPException(status_code=404, detail=f"Connector '{slug}' not found")
    return connector

