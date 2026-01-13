"""
Law Library API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid

from head_office.backend.services.database import get_db

router = APIRouter(prefix="/api/head-office/law-library", tags=["head-office-law-library"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/")
async def list_law_entries(shelf: Optional[str] = None, jurisdiction: Optional[str] = None, limit: int = 100):
    """List law library entries"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM law_library WHERE 1=1"
            params = []
            
            if shelf:
                query += " AND shelf = ?"
                params.append(shelf)
            
            if jurisdiction:
                query += " AND jurisdiction = ?"
                params.append(jurisdiction)
            
            query += " ORDER BY shelf, title ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                entry = dict(row)
                if entry.get("applicability_tags"):
                    entry["applicability_tags"] = json.loads(entry["applicability_tags"])
                if entry.get("compliance_checklist"):
                    entry["compliance_checklist"] = json.loads(entry["compliance_checklist"])
                if entry.get("primary_sources"):
                    entry["primary_sources"] = json.loads(entry["primary_sources"])
                entries.append(entry)
            
            return {
                "entries": entries,
                "total": len(entries)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shelves")
async def list_shelves():
    """List available law library shelves"""
    return {
        "shelves": [
            "contract_law",
            "corporate",
            "employment",
            "consumer_protection",
            "advertising",
            "privacy",
            "ip_law",
            "tax",
            "finance",
            "payments",
            "ucc",
            "blacks_law",
            "admiralty"
        ]
    }


@router.get("/{entry_id}")
async def get_law_entry(entry_id: str):
    """Get specific law library entry"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM law_library WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Entry not found")
            
            entry = dict(row)
            if entry.get("applicability_tags"):
                entry["applicability_tags"] = json.loads(entry["applicability_tags"])
            if entry.get("compliance_checklist"):
                entry["compliance_checklist"] = json.loads(entry["compliance_checklist"])
            if entry.get("primary_sources"):
                entry["primary_sources"] = json.loads(entry["primary_sources"])
            
            return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_law_entry(entry: Dict[str, Any]):
    """Create law library entry"""
    db = get_db()
    entry_id = entry.get("id") or str(uuid.uuid4())
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO law_library
                (id, title, shelf, jurisdiction, applicability_tags, summary,
                 compliance_checklist, risk_level, primary_sources, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                entry.get("title"),
                entry.get("shelf"),
                entry.get("jurisdiction"),
                json.dumps(entry.get("applicability_tags", [])),
                entry.get("summary", ""),
                json.dumps(entry.get("compliance_checklist", [])),
                entry.get("risk_level", "medium"),
                json.dumps(entry.get("primary_sources", [])),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": entry_id,
                "status": "created",
                "message": "Law library entry created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
