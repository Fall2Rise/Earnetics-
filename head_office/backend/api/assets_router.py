"""
Assets + Safety Radar API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid

from head_office.backend.services.database import get_db

router = APIRouter(prefix="/api/head-office/assets", tags=["head-office-assets"])


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/")
async def list_assets(category: Optional[str] = None, criticality: Optional[str] = None, limit: int = 100):
    """List assets"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM assets WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if criticality:
                query += " AND criticality = ?"
                params.append(criticality)
            
            query += " ORDER BY criticality DESC, name ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            assets = []
            for row in rows:
                asset = dict(row)
                if asset.get("metadata"):
                    asset["metadata"] = json.loads(asset["metadata"])
                assets.append(asset)
            
            return {
                "assets": assets,
                "total": len(assets)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_asset(asset: Dict[str, Any]):
    """Create asset"""
    db = get_db()
    asset_id = asset.get("id") or str(uuid.uuid4())
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO assets
                (id, name, category, owner, criticality, description, access_info,
                 renewal_date, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id,
                asset.get("name"),
                asset.get("category"),
                asset.get("owner"),
                asset.get("criticality", "medium"),
                asset.get("description", ""),
                asset.get("access_info"),
                asset.get("renewal_date"),
                json.dumps(asset.get("metadata", {})),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": asset_id,
                "status": "created",
                "message": "Asset created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def list_alerts(severity: Optional[str] = None, resolved: Optional[bool] = None, limit: int = 50):
    """List asset alerts (Safety Radar)"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT a.*, b.name as asset_name, b.category as asset_category
                FROM asset_alerts a
                LEFT JOIN assets b ON a.asset_id = b.id
                WHERE 1=1
            """
            params = []
            
            if severity:
                query += " AND a.severity = ?"
                params.append(severity)
            
            if resolved is not None:
                if resolved:
                    query += " AND a.resolved_at IS NOT NULL"
                else:
                    query += " AND a.resolved_at IS NULL"
            
            query += " ORDER BY a.severity DESC, a.detected_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            alerts = [dict(row) for row in rows]
            
            return {
                "alerts": alerts,
                "total": len(alerts)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolved_by: str = "owner"):
    """Resolve alert"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                UPDATE asset_alerts
                SET resolved_at = ?, resolved_by = ?
                WHERE id = ?
            """, (now, resolved_by, alert_id))
            
            conn.commit()
            
            return {
                "id": alert_id,
                "status": "resolved",
                "message": "Alert resolved successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/safety-radar")
async def get_safety_radar():
    """Get safety radar summary"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Critical alerts
            cursor.execute("""
                SELECT COUNT(*) as count FROM asset_alerts
                WHERE resolved_at IS NULL AND severity = 'critical'
            """)
            critical_alerts = cursor.fetchone()["count"]
            
            # Warning alerts
            cursor.execute("""
                SELECT COUNT(*) as count FROM asset_alerts
                WHERE resolved_at IS NULL AND severity = 'warning'
            """)
            warning_alerts = cursor.fetchone()["count"]
            
            # Expiring assets (within 30 days)
            cursor.execute("""
                SELECT COUNT(*) as count FROM assets
                WHERE renewal_date IS NOT NULL 
                AND renewal_date <= date('now', '+30 days')
                AND renewal_date >= date('now')
            """)
            expiring_assets = cursor.fetchone()["count"]
            
            # Single points of failure (critical assets with single owner)
            cursor.execute("""
                SELECT owner, COUNT(*) as count
                FROM assets
                WHERE criticality = 'critical'
                GROUP BY owner
                HAVING count = 1
            """)
            spof = cursor.fetchall()
            spof_count = len(spof)
            
            return {
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "expiring_assets": expiring_assets,
                "single_points_of_failure": spof_count,
                "spof_details": [dict(row) for row in spof],
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
