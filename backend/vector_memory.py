"""Lightweight vector memory store for Fallat_CrewAI.

This module provides a minimal persistent embedding index that stores vectors
inside a local SQLite database. It is designed for fully offline operation and
gives autonomous agents a shared long-term memory surface without depending on
external services.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "MemoryRecord",
    "MemoryMatch",
    "VectorMemoryStore",
    "VectorMemoryError",
]

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_DB_PATH = Path(os.getenv("VECTOR_MEMORY_DB", "vector_memory.db"))


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


class VectorMemoryError(RuntimeError):
    """Raised when a vector memory operation fails."""


@dataclass
class MemoryRecord:
    """Represents an embedding stored in the memory index."""

    id: str
    namespace: str
    embedding: Sequence[float]
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_row(self) -> Tuple[str, str, str, str, str, str]:
        created = self.created_at or _utcnow()
        updated = self.updated_at or created
        embedding_json = json.dumps(list(self.embedding))
        metadata_json = json.dumps(self.metadata or {})
        return (
            self.id,
            self.namespace,
            self.content or "",
            metadata_json,
            embedding_json,
            created,
            updated,
        )

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "MemoryRecord":
        return cls(
            id=row["id"],
            namespace=row["namespace"],
            content=row["content"],
            metadata=json.loads(row["metadata"] or "{}"),
            embedding=json.loads(row["embedding"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class MemoryMatch:
    """Result returned by search operations."""

    record: MemoryRecord
    score: float


class VectorMemoryStore:
    """Simple persistent vector store with cosine-similarity search."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    # ------------------------------------------------------------------ utils
    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    id TEXT PRIMARY KEY,
                    namespace TEXT NOT NULL,
                    content TEXT,
                    metadata TEXT,
                    embedding TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_namespace ON memory_records(namespace)"
            )
            conn.commit()

    @staticmethod
    def _to_vector(values: Sequence[float]) -> np.ndarray:
        try:
            array = np.asarray(values, dtype=np.float32)
        except Exception as exc:  # pragma: no cover - defensive
            raise VectorMemoryError(f"Invalid embedding values: {exc}") from exc
        if array.ndim != 1:
            raise VectorMemoryError("Embedding must be a one-dimensional vector")
        return array

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        if a.shape != b.shape:
            raise VectorMemoryError("Embeddings must have equal dimensions for comparison")
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-12
        return float(np.dot(a, b) / denom)

    # --------------------------------------------------------------- operations
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO memory_records (
                    id, namespace, content, metadata, embedding, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    namespace = excluded.namespace,
                    content = excluded.content,
                    metadata = excluded.metadata,
                    embedding = excluded.embedding,
                    updated_at = excluded.updated_at
                """,
                record.to_row(),
            )
            conn.commit()
        return record

    def upsert_many(self, records: Iterable[MemoryRecord]) -> int:
        rows = [record.to_row() for record in records]
        if not rows:
            return 0
        with self._connection() as conn:
            cur = conn.cursor()
            cur.executemany(
                """
                INSERT INTO memory_records (
                    id, namespace, content, metadata, embedding, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    namespace = excluded.namespace,
                    content = excluded.content,
                    metadata = excluded.metadata,
                    embedding = excluded.embedding,
                    updated_at = excluded.updated_at
                """,
                rows,
            )
            conn.commit()
        return len(rows)

    def delete(self, record_id: str) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM memory_records WHERE id = ?", (record_id,))
            conn.commit()

    def delete_namespace(self, namespace: str) -> int:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM memory_records WHERE namespace = ?", (namespace,))
            deleted = cur.rowcount
            conn.commit()
        return deleted

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM memory_records WHERE id = ?", (record_id,))
            row = cur.fetchone()
        return MemoryRecord.from_row(row) if row else None

    def list_namespace(self, namespace: str, limit: int = 100) -> List[MemoryRecord]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM memory_records
                WHERE namespace = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (namespace, limit),
            )
            rows = cur.fetchall()
        return [MemoryRecord.from_row(row) for row in rows]

    def search(
        self,
        namespace: str,
        query_embedding: Sequence[float],
        limit: int = 5,
        min_score: float = 0.0,
    ) -> List[MemoryMatch]:
        query_vector = self._to_vector(query_embedding)

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM memory_records WHERE namespace = ?",
                (namespace,),
            )
            rows = cur.fetchall()

        results: List[MemoryMatch] = []
        for row in rows:
            record = MemoryRecord.from_row(row)
            stored_vector = self._to_vector(record.embedding)
            score = self._cosine_similarity(query_vector, stored_vector)
            if score >= min_score:
                results.append(MemoryMatch(record=record, score=score))

        results.sort(key=lambda match: match.score, reverse=True)
        return results[:limit]


def record_from_dict(data: Dict[str, Any]) -> MemoryRecord:
    """Helper to construct MemoryRecord from loosely structured dicts."""
    required_fields = ("id", "namespace", "embedding")
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise VectorMemoryError(f"Missing required fields: {', '.join(missing)}")
    return MemoryRecord(
        id=str(data["id"]),
        namespace=str(data["namespace"]),
        embedding=data["embedding"],
        content=data.get("content"),
        metadata=data.get("metadata", {}),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )

