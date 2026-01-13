"""
Legal + Contracts API Router
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
import uuid
import re

from head_office.backend.services.database import get_db
from head_office.backend.services.contract_scanner import ContractScanner
from head_office.backend.services.signature_assistant import SignatureAssistant
from head_office.backend.models.schemas import Contract, ContractStatus, ContractScanResult

router = APIRouter(prefix="/api/head-office/legal", tags=["head-office-legal"])

scanner = ContractScanner()
signature_assistant = SignatureAssistant()


def verify_request_token(request, x_fallat_token: Optional[str] = None, x_api_token: Optional[str] = None):
    """Allow localhost without token"""
    return None


@router.get("/contracts")
async def list_contracts(status: Optional[str] = None, limit: int = 50):
    """List contracts"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM contracts WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            contracts = []
            for row in rows:
                contract = dict(row)
                if contract.get("metadata"):
                    contract["metadata"] = json.loads(contract["metadata"])
                contracts.append(contract)
            
            return {
                "contracts": contracts,
                "total": len(contracts)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts")
async def create_contract(contract: Dict[str, Any]):
    """Create new contract"""
    db = get_db()
    contract_id = contract.get("id") or str(uuid.uuid4())
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO contracts
                (id, title, party_name, counterparty, contract_type, status, version,
                 file_path, signed_date, expiry_date, value, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract_id,
                contract.get("title"),
                contract.get("party_name"),
                contract.get("counterparty"),
                contract.get("contract_type"),
                contract.get("status", "draft"),
                contract.get("version", 1),
                contract.get("file_path"),
                contract.get("signed_date"),
                contract.get("expiry_date"),
                contract.get("value"),
                json.dumps(contract.get("metadata", {})),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": contract_id,
                "status": "created",
                "message": "Contract created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/{contract_id}/scan")
async def scan_contract(contract_id: str, contract_text: str):
    """Scan contract for loopholes and risks"""
    db = get_db()
    
    try:
        # Get contract
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            contract_dict = dict(row)
            
            # Scan contract
            scan_result = scanner.scan(contract_text, contract_id)
            
            # Signature analysis
            contract_obj = Contract(
                id=contract_dict["id"],
                title=contract_dict["title"],
                party_name=contract_dict["party_name"],
                counterparty=contract_dict["counterparty"],
                contract_type=contract_dict["contract_type"],
                status=ContractStatus(contract_dict["status"])
            )
            
            signature_analysis = signature_assistant.analyze_contract(contract_text, contract_obj)
            
            # Update scan result with signature analysis
            scan_result.signature_recommendation = signature_analysis.get("recommended_signature")
            if signature_analysis.get("guarantee_detected"):
                scan_result.guarantee_detected = True
            
            # Store scan result
            cursor.execute("""
                INSERT OR REPLACE INTO contract_scans
                (contract_id, risk_level, executive_summary, risk_map, missing_items,
                 redline_suggestions, negotiation_playbook, guarantee_detected,
                 signature_recommendation, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract_id,
                scan_result.risk_level,
                scan_result.executive_summary,
                json.dumps(scan_result.risk_map),
                json.dumps(scan_result.missing_items),
                json.dumps(scan_result.redline_suggestions),
                json.dumps(scan_result.negotiation_playbook),
                1 if scan_result.guarantee_detected else 0,
                scan_result.signature_recommendation,
                scan_result.scanned_at
            ))
            
            conn.commit()
            
            # If guarantee detected, create decision queue item
            if signature_analysis.get("guarantee_detected"):
                decision_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO decision_queue
                    (id, title, category, recommendation, upside, cost, risk, reversibility,
                     alternatives, required_by, status, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision_id,
                    f"Contract Signature: {contract_dict['title']}",
                    "legal",
                    "Review personal guarantee language - HIGH RISK",
                    "Protect against personal liability",
                    None,
                    "HIGH: Personal guarantee detected",
                    "Cannot reverse once signed",
                    json.dumps([]),
                    datetime.utcnow().isoformat(),
                    "pending",
                    json.dumps({"contract_id": contract_id, "guarantee_detected": True}),
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
            
            return {
                "contract_id": contract_id,
                "scan_result": scan_result.to_dict(),
                "signature_analysis": signature_analysis
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/{contract_id}/scan")
async def get_scan_result(contract_id: str):
    """Get contract scan result"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contract_scans WHERE contract_id = ?", (contract_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Scan result not found")
            
            scan = dict(row)
            scan["risk_map"] = json.loads(scan["risk_map"]) if scan["risk_map"] else {}
            scan["missing_items"] = json.loads(scan["missing_items"]) if scan["missing_items"] else []
            scan["redline_suggestions"] = json.loads(scan["redline_suggestions"]) if scan["redline_suggestions"] else []
            scan["negotiation_playbook"] = json.loads(scan["negotiation_playbook"]) if scan["negotiation_playbook"] else []
            scan["guarantee_detected"] = bool(scan["guarantee_detected"])
            
            return scan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/{contract_id}/signature-analysis")
async def analyze_signature(contract_id: str, contract_text: str):
    """Analyze contract for signature capacity"""
    db = get_db()
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            contract_dict = dict(row)
            contract_obj = Contract(
                id=contract_dict["id"],
                title=contract_dict["title"],
                party_name=contract_dict["party_name"],
                counterparty=contract_dict["counterparty"],
                contract_type=contract_dict["contract_type"],
                status=ContractStatus(contract_dict["status"])
            )
            
            analysis = signature_assistant.analyze_contract(contract_text, contract_obj)
            
            return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
