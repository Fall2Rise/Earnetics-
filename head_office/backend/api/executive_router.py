"""
Executive Launchpad API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
import json

from head_office.backend.services.database import get_db
from head_office.backend.models.schemas import DecisionQueueItem, DecisionStatus

router = APIRouter(prefix="/api/head-office/executive", tags=["head-office-executive"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None  # Simplified for MVP


@router.get("/brief")
async def get_owner_brief(period: str = "daily"):
    """Get owner brief (daily/weekly)"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get pending decisions
            cursor.execute("""
                SELECT COUNT(*) as count FROM decision_queue 
                WHERE status = 'pending' AND required_by <= date('now', '+7 days')
            """)
            pending_decisions = cursor.fetchone()["count"]
            
            # Get overdue compliance
            cursor.execute("""
                SELECT COUNT(*) as count FROM compliance_items 
                WHERE status = 'overdue' OR (status = 'at_risk' AND deadline <= date('now', '+7 days'))
            """)
            compliance_issues = cursor.fetchone()["count"]
            
            # Get critical assets
            cursor.execute("""
                SELECT COUNT(*) as count FROM assets WHERE criticality = 'critical'
            """)
            critical_assets = cursor.fetchone()["count"]
            
            # Get active alerts
            cursor.execute("""
                SELECT COUNT(*) as count FROM asset_alerts 
                WHERE resolved_at IS NULL AND severity = 'critical'
            """)
            critical_alerts = cursor.fetchone()["count"]
            
            return {
                "period": period,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "pending_decisions": pending_decisions,
                    "compliance_issues": compliance_issues,
                    "critical_assets": critical_assets,
                    "critical_alerts": critical_alerts
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/today-board")
async def get_today_board():
    """Get today's board (deadlines, approvals, money events, risks, blocked items)"""
    db = get_db()
    today = datetime.utcnow().date().isoformat()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Deadlines
            cursor.execute("""
                SELECT id, title, deadline, category, status
                FROM compliance_items
                WHERE deadline <= date('now', '+7 days')
                ORDER BY deadline ASC
                LIMIT 10
            """)
            deadlines = [dict(row) for row in cursor.fetchall()]
            
            # Approvals
            cursor.execute("""
                SELECT id, title, category, required_by, status
                FROM decision_queue
                WHERE status = 'pending'
                ORDER BY required_by ASC
                LIMIT 10
            """)
            approvals = [dict(row) for row in cursor.fetchall()]
            
            # Risks (critical alerts)
            cursor.execute("""
                SELECT a.id, a.asset_id, a.alert_type, a.severity, a.message, b.name as asset_name
                FROM asset_alerts a
                LEFT JOIN assets b ON a.asset_id = b.id
                WHERE a.resolved_at IS NULL AND a.severity IN ('critical', 'warning')
                ORDER BY a.severity DESC, a.detected_at DESC
                LIMIT 10
            """)
            risks = [dict(row) for row in cursor.fetchall()]
            
            return {
                "deadlines": deadlines,
                "approvals": approvals,
                "risks": risks,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def global_search(query: str, limit: int = 20):
    """Global search across all Head Office modules"""
    db = get_db()
    results = []
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search decisions
            cursor.execute("""
                SELECT 'decision' as type, id, title, category, status
                FROM decision_queue
                WHERE title LIKE ? OR recommendation LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit // 4))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            # Search contracts
            cursor.execute("""
                SELECT 'contract' as type, id, title, counterparty, status
                FROM contracts
                WHERE title LIKE ? OR counterparty LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit // 4))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            # Search compliance
            cursor.execute("""
                SELECT 'compliance' as type, id, title, category, deadline, status
                FROM compliance_items
                WHERE title LIKE ? OR category LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit // 4))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            # Search law library
            cursor.execute("""
                SELECT 'law' as type, id, title, shelf, jurisdiction
                FROM law_library
                WHERE title LIKE ? OR summary LIKE ? OR shelf LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit // 4))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            return {
                "query": query,
                "results": results[:limit],
                "total": len(results)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
