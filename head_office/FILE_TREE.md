# Head Office - File Tree

## Directory Structure

```
head_office/
├── backend/
│   ├── models/
│   │   ├── __init__.py          # Model exports
│   │   └── schemas.py            # Data models (DecisionQueueItem, Contract, etc.)
│   ├── services/
│   │   ├── __init__.py           # Service exports
│   │   ├── database.py           # SQLite database service
│   │   ├── contract_scanner.py   # Contract loophole scanner (rule-based)
│   │   └── signature_assistant.py # Signature capacity assistant
│   └── api/
│       ├── __init__.py           # API router exports
│       ├── executive_router.py   # Executive Launchpad API
│       ├── decisions_router.py   # Decision Queue API
│       ├── legal_router.py       # Legal + Contracts API
│       ├── tax_router.py         # Tax Desk API
│       ├── assets_router.py      # Assets + Safety Radar API
│       ├── law_library_router.py # Law Library API
│       └── master_ai_router.py   # Master AI API
├── frontend/                     # (To be implemented)
│   └── src/
│       ├── components/           # React components
│       └── pages/                # Page components
├── scripts/
│   └── seed_data.py              # Seed sample data script
├── README.md                     # Main documentation
└── FILE_TREE.md                  # This file
```

## Key Routes/Pages (MVP)

### Backend API Routes

**Executive Launchpad:**
- `GET /api/head-office/executive/brief` - Owner brief (daily/weekly)
- `GET /api/head-office/executive/today-board` - Today's board
- `GET /api/head-office/executive/search?query=...` - Global search

**Decision Queue:**
- `GET /api/head-office/decisions` - List decisions
- `GET /api/head-office/decisions/{id}` - Get decision
- `POST /api/head-office/decisions` - Create decision
- `POST /api/head-office/decisions/{id}/approve` - Approve
- `POST /api/head-office/decisions/{id}/deny` - Deny
- `POST /api/head-office/decisions/{id}/request-info` - Request info

**Legal + Contracts:**
- `GET /api/head-office/legal/contracts` - List contracts
- `POST /api/head-office/legal/contracts` - Create contract
- `POST /api/head-office/legal/contracts/{id}/scan` - Scan contract
- `GET /api/head-office/legal/contracts/{id}/scan` - Get scan result
- `POST /api/head-office/legal/contracts/{id}/signature-analysis` - Analyze signature

**Tax Desk:**
- `GET /api/head-office/tax/tasks` - List tax tasks
- `POST /api/head-office/tax/tasks` - Create tax task
- `GET /api/head-office/tax/calendar` - Filing calendar
- `GET /api/head-office/tax/tasks/{id}/cpa-packet` - Generate CPA packet

**Assets + Safety Radar:**
- `GET /api/head-office/assets` - List assets
- `POST /api/head-office/assets` - Create asset
- `GET /api/head-office/assets/alerts` - List alerts
- `POST /api/head-office/assets/alerts/{id}/resolve` - Resolve alert
- `GET /api/head-office/assets/safety-radar` - Safety radar summary

**Law Library:**
- `GET /api/head-office/law-library` - List entries
- `GET /api/head-office/law-library/shelves` - List shelves
- `GET /api/head-office/law-library/{id}` - Get entry
- `POST /api/head-office/law-library` - Create entry

**Master AI:**
- `GET /api/head-office/master-ai/status` - Get status
- `POST /api/head-office/master-ai/action` - Execute action
- `GET /api/head-office/master-ai/actions` - List actions
- `POST /api/head-office/master-ai/kill-switch/toggle` - Toggle kill switch

### Frontend Pages (To be implemented)

1. **Executive Launchpad Page**
   - Owner Brief component
   - Today Board component
   - Global Search (Ctrl+K command palette)
   - Favorites/Pinned section

2. **Decision Queue Page**
   - Decision list with filters
   - Decision detail view
   - Approve/Deny/Request Info actions

3. **Legal + Contracts Page**
   - Contract list
   - Contract detail view
   - Contract scanner interface
   - Signature analysis display

4. **Tax Desk Page**
   - Tax calendar view
   - Task list
   - CPA packet generator

5. **Assets + Safety Radar Page**
   - Asset inventory
   - Alert list
   - Safety radar dashboard

6. **Law Library Page**
   - Library browser (by shelf)
   - Entry detail view
   - Search functionality

7. **Master AI Page**
   - Status display
   - Action history
   - Kill switch controls

## Key Schemas

### DecisionQueueItem
```python
{
    "id": str,
    "title": str,
    "category": str,  # spend, publish, dns, legal, payout
    "recommendation": str,
    "upside": str,
    "cost": float | None,
    "risk": str,
    "reversibility": str,
    "alternatives": List[str],
    "required_by": str,  # ISO date
    "status": DecisionStatus,  # pending, approved, denied, request_info
    "metadata": Dict[str, Any]
}
```

### Contract
```python
{
    "id": str,
    "title": str,
    "party_name": str,
    "counterparty": str,
    "contract_type": str,
    "status": ContractStatus,  # draft, review, redlined, approved, signed, active, expired, terminated
    "version": int,
    "file_path": str | None,
    "signed_date": str | None,  # ISO date
    "expiry_date": str | None,  # ISO date
    "value": float | None,
    "metadata": Dict[str, Any]
}
```

### ContractScanResult
```python
{
    "contract_id": str,
    "risk_level": str,  # high, medium, low
    "executive_summary": str,
    "risk_map": Dict[str, List[str]],  # category -> issues
    "missing_items": List[str],
    "redline_suggestions": List[Dict[str, Any]],
    "negotiation_playbook": List[str],
    "guarantee_detected": bool,
    "signature_recommendation": str | None,
    "scanned_at": str  # ISO datetime
}
```

### ComplianceItem
```python
{
    "id": str,
    "title": str,
    "category": str,  # filing, renewal, policy, obligation
    "jurisdiction": str,
    "deadline": str,  # ISO date
    "status": ComplianceStatus,  # on_track, at_risk, overdue, complete
    "obligation_source": str | None,
    "completed_at": str | None,  # ISO datetime
    "notes": str
}
```

### TaxTask
```python
{
    "id": str,
    "title": str,
    "tax_type": str,  # federal, state, local, payroll
    "filing_period": str,  # 2024, Q1-2024
    "deadline": str,  # ISO date
    "status": str,  # pending, in_progress, completed
    "documents": List[str],
    "notes": str
}
```

### Asset
```python
{
    "id": str,
    "name": str,
    "category": AssetCategory,  # digital, financial, ip, physical, access
    "owner": str,  # email or user_id
    "criticality": str,  # critical, high, medium, low
    "description": str,
    "access_info": str | None,
    "renewal_date": str | None,  # ISO date
    "metadata": Dict[str, Any]
}
```

### AssetAlert
```python
{
    "id": str,
    "asset_id": str,
    "alert_type": str,  # expiry, dns_change, suspicious_login, etc.
    "severity": str,  # critical, warning, info
    "message": str,
    "detected_at": str,  # ISO datetime
    "resolved_at": str | None,
    "resolved_by": str | None
}
```

### LawLibraryEntry
```python
{
    "id": str,
    "title": str,
    "shelf": str,  # contract_law, corporate, employment, etc.
    "jurisdiction": str,
    "applicability_tags": List[str],
    "summary": str,
    "compliance_checklist": List[str],
    "risk_level": str,  # high, medium, low
    "primary_sources": List[str]
}
```

### MasterAIAction
```python
{
    "id": str,
    "request": str,
    "mode": MasterAIMode,  # advisor, operator, executive
    "action_type": str,
    "approval_required": bool,
    "approval_token": str | None,
    "status": str,  # pending, completed, failed
    "result": Dict[str, Any] | None,
    "audit_log_link": str | None
}
```

### AuditLogEvent
```python
{
    "id": str,
    "actor": str,  # user_id or "master_ai"
    "action_type": str,
    "resource": str,  # resource_id or resource_type
    "timestamp": str,  # ISO datetime
    "diff": Dict[str, Any] | None,
    "metadata": Dict[str, Any]
}
```

## Database Schema

Database file: `head_office.db` (created in project root)

Tables:
- `decision_queue` - Decision queue items
- `contracts` - Contracts
- `contract_scans` - Contract scan results
- `compliance_items` - Compliance tracking
- `tax_tasks` - Tax filing tasks
- `assets` - Asset inventory
- `asset_alerts` - Safety radar alerts
- `law_library` - Law library entries
- `master_ai_actions` - Master AI action history
- `audit_log` - Audit log events

All tables include `created_at` and `updated_at` timestamps.
