"""
Decision Queue API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid

from head_office.backend.services.database import get_db
from head_office.backend.models.schemas import DecisionQueueItem, DecisionStatus

router = APIRouter(prefix="/api/head-office/decisions", tags=["head-office-decisions"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/")
async def list_decisions(status: Optional[str] = None, category: Optional[str] = None, limit: int = 50):
    """List decision queue items"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM decision_queue WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY required_by ASC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            decisions = []
            for row in rows:
                decision = dict(row)
                # Parse JSON fields
                if decision.get("alternatives"):
                    decision["alternatives"] = json.loads(decision["alternatives"])
                if decision.get("metadata"):
                    decision["metadata"] = json.loads(decision["metadata"])
                decisions.append(decision)
            
            return {
                "decisions": decisions,
                "total": len(decisions)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{decision_id}")
async def get_decision(decision_id: str):
    """Get specific decision"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM decision_queue WHERE id = ?", (decision_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Decision not found")
            
            decision = dict(row)
            if decision.get("alternatives"):
                decision["alternatives"] = json.loads(decision["alternatives"])
            if decision.get("metadata"):
                decision["metadata"] = json.loads(decision["metadata"])
            
            return decision
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_decision(decision: Dict[str, Any]):
    """Create new decision queue item"""
    db = get_db()
    decision_id = decision.get("id") or str(uuid.uuid4())
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO decision_queue
                (id, title, category, recommendation, upside, cost, risk, reversibility,
                 alternatives, required_by, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id,
                decision.get("title"),
                decision.get("category"),
                decision.get("recommendation"),
                decision.get("upside"),
                decision.get("cost"),
                decision.get("risk"),
                decision.get("reversibility"),
                json.dumps(decision.get("alternatives", [])),
                decision.get("required_by"),
                decision.get("status", "pending"),
                json.dumps(decision.get("metadata", {})),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": decision_id,
                "status": "created",
                "message": "Decision created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str, note: Optional[str] = None):
    """Approve decision"""
    return await _update_decision_status(decision_id, "approved", note)


@router.post("/{decision_id}/deny")
async def deny_decision(decision_id: str, note: Optional[str] = None):
    """Deny decision"""
    return await _update_decision_status(decision_id, "denied", note)


@router.post("/{decision_id}/request-info")
async def request_info(decision_id: str, note: Optional[str] = None):
    """Request more information"""
    return await _update_decision_status(decision_id, "request_info", note)


async def _update_decision_status(decision_id: str, status: str, note: Optional[str] = None):
    """Update decision status"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            # Get existing metadata
            cursor.execute("SELECT metadata FROM decision_queue WHERE id = ?", (decision_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Decision not found")
            
            metadata = json.loads(row[0]) if row[0] else {}
            if note:
                metadata["status_note"] = note
                metadata["status_updated_at"] = now
            
            cursor.execute("""
                UPDATE decision_queue
                SET status = ?, updated_at = ?, metadata = ?
                WHERE id = ?
            """, (status, now, json.dumps(metadata), decision_id))
            
            conn.commit()
            
            return {
                "id": decision_id,
                "status": status,
                "message": f"Decision {status} successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
