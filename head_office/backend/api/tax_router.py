"""
Tax Desk API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid

from head_office.backend.services.database import get_db

router = APIRouter(prefix="/api/head-office/tax", tags=["head-office-tax"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/tasks")
async def list_tax_tasks(status: Optional[str] = None, limit: int = 50):
    """List tax tasks"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM tax_tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY deadline ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                task = dict(row)
                if task.get("documents"):
                    task["documents"] = json.loads(task["documents"])
                tasks.append(task)
            
            return {
                "tasks": tasks,
                "total": len(tasks)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks")
async def create_tax_task(task: Dict[str, Any]):
    """Create tax task"""
    db = get_db()
    task_id = task.get("id") or str(uuid.uuid4())
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO tax_tasks
                (id, title, tax_type, filing_period, deadline, status, documents, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                task.get("title"),
                task.get("tax_type"),
                task.get("filing_period"),
                task.get("deadline"),
                task.get("status", "pending"),
                json.dumps(task.get("documents", [])),
                task.get("notes", ""),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": task_id,
                "status": "created",
                "message": "Tax task created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar")
async def get_filing_calendar():
    """Get tax filing calendar"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get upcoming deadlines
            cursor.execute("""
                SELECT * FROM tax_tasks
                WHERE deadline >= date('now')
                ORDER BY deadline ASC
                LIMIT 20
            """)
            rows = cursor.fetchall()
            
            calendar = []
            for row in rows:
                task = dict(row)
                if task.get("documents"):
                    task["documents"] = json.loads(task["documents"])
                calendar.append(task)
            
            return {
                "calendar": calendar,
                "total": len(calendar)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/cpa-packet")
async def generate_cpa_packet(task_id: str):
    """Generate CPA packet (export-ready documents)"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tax_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Tax task not found")
            
            task = dict(row)
            if task.get("documents"):
                task["documents"] = json.loads(task["documents"])
            
            # Generate packet summary
            packet = {
                "task_id": task_id,
                "title": task["title"],
                "tax_type": task["tax_type"],
                "filing_period": task["filing_period"],
                "deadline": task["deadline"],
                "documents": task.get("documents", []),
                "notes": task.get("notes", ""),
                "generated_at": datetime.utcnow().isoformat(),
                "export_ready": True
            }
            
            return packet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
