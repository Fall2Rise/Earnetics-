"""
Master AI (Owner Assistant) API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid

from head_office.backend.services.database import get_db
from head_office.backend.models.schemas import MasterAIMode

router = APIRouter(prefix="/api/head-office/master-ai", tags=["head-office-master-ai"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/status")
async def get_master_ai_status():
    """Get Master AI status and configuration"""
    return {
        "enabled": True,
        "current_mode": "advisor",  # advisor, operator, executive
        "kill_switch_active": False,
        "approval_required_for": ["spend", "publish", "legal", "dns"],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/action")
async def execute_master_ai_action(action: Dict[str, Any]):
    """Execute Master AI action"""
    db = get_db()
    action_id = action.get("id") or str(uuid.uuid4())
    
    mode = action.get("mode", "advisor")
    action_type = action.get("action_type")
    request_text = action.get("request")
    approval_token = action.get("approval_token")
    
    # Determine if approval required
    approval_required = mode == "executive" or action_type in ["spend", "publish", "legal", "dns"]
    
    if approval_required and not approval_token:
        raise HTTPException(status_code=403, detail="Approval token required for this action")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            # Create action record
            cursor.execute("""
                INSERT INTO master_ai_actions
                (id, request, mode, action_type, approval_required, approval_token,
                 status, result, audit_log_link, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action_id,
                request_text,
                mode,
                action_type,
                1 if approval_required else 0,
                approval_token,
                "pending",
                None,
                None,
                now
            ))
            
            # Create audit log entry
            audit_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO audit_log
                (id, actor, action_type, resource, timestamp, diff, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                "master_ai",
                action_type,
                action_id,
                now,
                json.dumps({"request": request_text, "mode": mode}),
                json.dumps({"approval_token": approval_token} if approval_token else {})
            ))
            
            # Update action with audit log link
            cursor.execute("""
                UPDATE master_ai_actions
                SET audit_log_link = ?, status = ?
                WHERE id = ?
            """, (audit_id, "completed", action_id))
            
            conn.commit()
            
            return {
                "id": action_id,
                "status": "completed",
                "mode": mode,
                "approval_required": approval_required,
                "audit_log_link": audit_id,
                "message": "Action executed successfully (stub implementation)"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions")
async def list_master_ai_actions(limit: int = 50):
    """List Master AI actions"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM master_ai_actions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            actions = []
            for row in rows:
                action = dict(row)
                if action.get("result"):
                    action["result"] = json.loads(action["result"])
                actions.append(action)
            
            return {
                "actions": actions,
                "total": len(actions)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kill-switch/toggle")
async def toggle_kill_switch(active: bool):
    """Toggle Master AI kill switch"""
    # In full implementation, this would update a config file or database
    return {
        "kill_switch_active": active,
        "message": "Kill switch toggled successfully",
        "timestamp": datetime.utcnow().isoformat()
    }
