from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from backend.corporate_memory import BUSINESS_DB_PATH
from backend.audit_log import log_event

router = APIRouter(prefix="/api/library", tags=["library"])


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(BUSINESS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema() -> None:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS library_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                description TEXT,
                detailed_playbook TEXT,
                tags TEXT,
                created_by_agent TEXT,
                last_updated TEXT
            )
            """
        )
        conn.commit()


_ensure_schema()


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    if not row:
        return {}
    tags = []
    try:
        tags = json.loads(row["tags"] or "[]")
    except Exception:
        tags = []
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row["category"],
        "description": row["description"],
        "detailed_playbook": row["detailed_playbook"],
        "tags": tags,
        "created_by_agent": row["created_by_agent"],
        "last_updated": row["last_updated"],
    }


@router.get("/")
def list_items(q: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    sql = "SELECT * FROM library_items"
    clauses: List[str] = []
    params: List[Any] = []
    if q:
        clauses.append("(title LIKE ? OR description LIKE ? OR detailed_playbook LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if category:
        clauses.append("category = ?")
        params.append(category)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY last_updated DESC"
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
    return {"items": [_row_to_dict(r) for r in rows]}


@router.post("/")
def create_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = payload.get("title")
    if not required:
        raise HTTPException(status_code=400, detail="title is required")
    now = datetime.utcnow().isoformat()
    tags = payload.get("tags") or []
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO library_items (title, category, description, detailed_playbook, tags, created_by_agent, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("title"),
                payload.get("category"),
                payload.get("description"),
                payload.get("detailed_playbook"),
                json.dumps(tags),
                payload.get("created_by_agent"),
                now,
            ),
        )
        item_id = cur.lastrowid
        conn.commit()
    log_event("library.created", status="success", details={"id": item_id, "title": payload.get("title")})
    return get_item(item_id)


@router.get("/{item_id}")
def get_item(item_id: int) -> Dict[str, Any]:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM library_items WHERE id=?", (item_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": _row_to_dict(row)}


@router.put("/{item_id}")
def update_item(item_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM library_items WHERE id=?", (item_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        tags = payload.get("tags") or []
        now = datetime.utcnow().isoformat()
        cur.execute(
            """
            UPDATE library_items
            SET title=?, category=?, description=?, detailed_playbook=?, tags=?, created_by_agent=?, last_updated=?
            WHERE id=?
            """,
            (
                payload.get("title", row["title"]),
                payload.get("category", row["category"]),
                payload.get("description", row["description"]),
                payload.get("detailed_playbook", row["detailed_playbook"]),
                json.dumps(tags),
                payload.get("created_by_agent", row["created_by_agent"]),
                now,
                item_id,
            ),
        )
        conn.commit()
    log_event("library.updated", status="success", details={"id": item_id})
    return get_item(item_id)
