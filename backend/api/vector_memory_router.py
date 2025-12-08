from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, model_validator

from backend.embedding_service import embed_text
from backend.vector_memory import (
    MemoryRecord,
    VectorMemoryError,
    VectorMemoryStore,
    record_from_dict,
)

router = APIRouter(prefix="/api/memory", tags=["memory"])

memory_store: Optional[VectorMemoryStore] = None


def configure_memory_store(store: VectorMemoryStore) -> None:
    global memory_store
    memory_store = store


def _get_store() -> VectorMemoryStore:
    if memory_store is None:  # pragma: no cover - defensive
        raise RuntimeError("Vector memory store not configured")
    return memory_store


class MemoryRecordRequest(BaseModel):
    id: str
    namespace: str
    embedding: Optional[List[float]] = None
    text: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_embedding_or_text(self) -> "MemoryRecordRequest":
        if self.embedding is None and not self.text:
            raise ValueError("Either embedding or text must be provided")
        return self

class MemorySearchRequest(BaseModel):
    namespace: str
    embedding: Optional[List[float]] = None
    text: Optional[str] = None
    limit: int = 5
    min_score: float = 0.0

    @model_validator(mode="after")
    def validate_embedding_or_text(self) -> "MemorySearchRequest":
        if self.embedding is None and not self.text:
            raise ValueError("Either embedding or text must be provided")
        return self


def _record_to_dict(record: MemoryRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "namespace": record.namespace,
        "content": record.content,
        "metadata": record.metadata,
        "embedding": list(record.embedding),
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@router.post("/records")
def upsert_memory_record(request: MemoryRecordRequest) -> Dict[str, Any]:
    store = _get_store()
    try:
        data = request.model_dump()
        if data.get("embedding") is None and data.get("text"):
            data["embedding"] = embed_text(data["text"])
        record = record_from_dict(data)
        store.upsert(record)
        stored = store.get(record.id)
    except VectorMemoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Unable to persist memory record") from exc

    if stored is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Memory record not persisted")

    return {"status": "success", "record": _record_to_dict(stored)}


@router.post("/search")
def search_memory(request: MemorySearchRequest) -> Dict[str, Any]:
    store = _get_store()
    try:
        query_embedding = request.embedding
        if query_embedding is None and request.text:
            query_embedding = embed_text(request.text)
        matches = store.search(
            namespace=request.namespace,
            query_embedding=query_embedding,
            limit=request.limit,
            min_score=request.min_score,
        )
    except VectorMemoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Unable to search memory store") from exc

    return {
        "status": "success",
        "matches": [
            {**_record_to_dict(match.record), "score": match.score}
            for match in matches
        ],
    }


@router.delete("/records/{record_id}")
def delete_memory_record(record_id: str) -> Dict[str, Any]:
    store = _get_store()
    existing = store.get(record_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Memory record not found")

    try:
        store.delete(record_id)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Unable to delete memory record") from exc

    return {"status": "deleted", "id": record_id}


@router.delete("/namespaces/{namespace}")
def delete_namespace(namespace: str) -> Dict[str, Any]:
    store = _get_store()
    try:
        removed = store.delete_namespace(namespace)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Unable to delete namespace") from exc

    return {"status": "deleted", "namespace": namespace, "removed": removed}


@router.get("/namespaces")
def list_namespaces(prefix: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=500)) -> Dict[str, Any]:
    store = _get_store()
    try:
        with store._connection() as conn:  # type: ignore[attr-defined]
            cur = conn.cursor()
            if prefix:
                cur.execute(
                    "SELECT DISTINCT namespace FROM memory_records WHERE namespace LIKE ? ORDER BY namespace LIMIT ?",
                    (f"{prefix}%", limit),
                )
            else:
                cur.execute(
                    "SELECT DISTINCT namespace FROM memory_records ORDER BY namespace LIMIT ?",
                    (limit,),
                )
            rows = cur.fetchall()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Unable to list namespaces: {exc}") from exc

    return {"namespaces": [row[0] for row in rows]}


@router.get("/namespace/{namespace}")
def list_namespace_records(namespace: str, limit: int = Query(50, ge=1, le=500)) -> Dict[str, Any]:
    store = _get_store()
    try:
        records = store.list_namespace(namespace, limit=limit)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Unable to load namespace records: {exc}") from exc

    return {
        "records": [
            {
                "id": record.id,
                "namespace": record.namespace,
                "content": record.content,
                "metadata": record.metadata,
                "embedding": record.embedding,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }
            for record in records
        ]
    }
