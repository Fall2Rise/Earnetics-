# Head Office (Owner Ops OS)

Enterprise-grade owner operations module for Earnetics Command Center.

## Overview

The Head Office module provides everything the owner needs for business operations at arm's reach: governance, legality, capital, finance, operations, knowledge libraries, assets, security, reinvestment, and a private master AI assistant.

## Features

### MVP Components (Implemented)

1. **Executive Launchpad**
   - Owner Brief (Daily/Weekly)
   - Today Board (deadlines, approvals, money events, risks, blocked items)
   - Global Search + Command Palette (Ctrl+K)
   - Favorites / Pinned Playbooks

2. **Decision Queue**
   - Approval requests (spend, publish, DNS, legal filings drafts, payouts changes)
   - Each item includes: recommendation, upside, cost, risk, reversibility, alternatives, required_by
   - Actions: approve/deny/request_info

3. **Legal + Contracts**
   - Contract lifecycle management
   - **Contract Loophole Scanner**: Rule-based contract analysis
   - **Signature Capacity Assistant**: Detects guarantees, recommends signature blocks
   - Contract storage and versioning

4. **Tax Desk**
   - Filing calendar (fed/state/local)
   - Monthly close checklist
   - Document capture + categorization
   - CPA Packet Generator (export-ready)

5. **Assets + Safety Radar**
   - Asset Inventory (digital, financial, IP, physical, access)
   - Safety Radar alerts (domain/SSL expiry, DNS changes, suspicious logins, etc.)
   - Single point of failure detector

6. **Law Library**
   - Universal Law Library with shelves (contract_law, corporate, employment, etc.)
   - UCC Library (indexed)
   - Black's Law Dictionary Library (indexed definitions)
   - Each entry includes: jurisdiction, applicability tags, plain-English summary, compliance checklist, risk level

7. **Master AI (Owner Assistant)**
   - Modes: Advisor (recommend only), Operator (low-risk execute), Executive (requires approval tokens)
   - Approval tokens: Spend, Publish, Legal, DNS
   - Two-step approval for Execute-High
   - Kill switch support
   - Always-on audit logging

## Setup

### 1. Database Initialization

The database is created automatically on first use. To initialize manually:

```python
from head_office.backend.services.database import get_db
db = get_db()  # Creates head_office.db
```

### 2. Start Backend Server

The Head Office routers are automatically registered when the backend starts:

```bash
python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. Seed Sample Data

```bash
python head_office/scripts/seed_data.py
```

## Usage

### Import a Contract

```python
import requests

# Create contract
contract = {
    "title": "Service Agreement",
    "party_name": "Your Company Inc.",
    "counterparty": "Client Corp",
    "contract_type": "service",
    "status": "draft"
}

response = requests.post(
    "http://localhost:8000/api/head-office/legal/contracts",
    json=contract
)

contract_id = response.json()["id"]

# Scan contract (paste contract text)
contract_text = "Contract text here..."
scan_response = requests.post(
    f"http://localhost:8000/api/head-office/legal/contracts/{contract_id}/scan",
    json={"contract_text": contract_text}
)

scan_result = scan_response.json()
print(f"Risk Level: {scan_result['scan_result']['risk_level']}")
print(f"Guarantee Detected: {scan_result['signature_analysis']['guarantee_detected']}")
```

### Add Compliance Deadline

```python
import requests
from datetime import datetime, timedelta

compliance_item = {
    "title": "Annual Report Filing",
    "category": "filing",
    "jurisdiction": "Delaware",
    "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
    "status": "on_track",
    "obligation_source": "corporate_law"
}

response = requests.post(
    "http://localhost:8000/api/head-office/compliance",
    json=compliance_item
)
```

### Create Decision Queue Item

```python
import requests
from datetime import datetime, timedelta

decision = {
    "title": "Approve Marketing Campaign Spend",
    "category": "spend",
    "recommendation": "Approve $5,000 marketing campaign",
    "upside": "Expected 10x ROI based on historical data",
    "cost": 5000.0,
    "risk": "Low - standard campaign",
    "reversibility": "Can pause campaign if needed",
    "alternatives": ["Lower budget option: $2,500", "Defer to next quarter"],
    "required_by": (datetime.now() + timedelta(days=2)).isoformat(),
    "status": "pending"
}

response = requests.post(
    "http://localhost:8000/api/head-office/decisions",
    json=decision
)
```

### Use Master AI

```python
import requests

# Advisor mode (recommend only)
action = {
    "request": "Should we launch Product X next week?",
    "mode": "advisor",
    "action_type": "recommendation"
}

response = requests.post(
    "http://localhost:8000/api/head-office/master-ai/action",
    json=action
)

# Executive mode (requires approval token)
action = {
    "request": "Publish blog post about Product X",
    "mode": "executive",
    "action_type": "publish",
    "approval_token": "your_approval_token_here"
}

response = requests.post(
    "http://localhost:8000/api/head-office/master-ai/action",
    json=action
)
```

## API Endpoints

### Executive Launchpad
- `GET /api/head-office/executive/brief` - Get owner brief
- `GET /api/head-office/executive/today-board` - Get today's board
- `GET /api/head-office/executive/search?query=...` - Global search

### Decision Queue
- `GET /api/head-office/decisions` - List decisions
- `GET /api/head-office/decisions/{id}` - Get decision
- `POST /api/head-office/decisions` - Create decision
- `POST /api/head-office/decisions/{id}/approve` - Approve decision
- `POST /api/head-office/decisions/{id}/deny` - Deny decision

### Legal + Contracts
- `GET /api/head-office/legal/contracts` - List contracts
- `POST /api/head-office/legal/contracts` - Create contract
- `POST /api/head-office/legal/contracts/{id}/scan` - Scan contract
- `GET /api/head-office/legal/contracts/{id}/scan` - Get scan result
- `POST /api/head-office/legal/contracts/{id}/signature-analysis` - Analyze signature

### Tax Desk
- `GET /api/head-office/tax/tasks` - List tax tasks
- `POST /api/head-office/tax/tasks` - Create tax task
- `GET /api/head-office/tax/calendar` - Get filing calendar
- `GET /api/head-office/tax/tasks/{id}/cpa-packet` - Generate CPA packet

### Assets + Safety Radar
- `GET /api/head-office/assets` - List assets
- `POST /api/head-office/assets` - Create asset
- `GET /api/head-office/assets/alerts` - List alerts
- `POST /api/head-office/assets/alerts/{id}/resolve` - Resolve alert
- `GET /api/head-office/assets/safety-radar` - Get safety radar summary

### Law Library
- `GET /api/head-office/law-library` - List law entries
- `GET /api/head-office/law-library/shelves` - List shelves
- `GET /api/head-office/law-library/{id}` - Get entry
- `POST /api/head-office/law-library` - Create entry

### Master AI
- `GET /api/head-office/master-ai/status` - Get status
- `POST /api/head-office/master-ai/action` - Execute action
- `GET /api/head-office/master-ai/actions` - List actions
- `POST /api/head-office/master-ai/kill-switch/toggle` - Toggle kill switch

## Contract Scanner

The contract scanner uses rule-based pattern detection (no paid APIs) to identify:

**High-Risk Patterns:**
- Uncapped liability
- One-way indemnity
- IP assignment clauses
- Termination without compensation
- Sole discretion language
- Personal guarantee language

**Medium-Risk Patterns:**
- Auto-renew clauses
- Long net terms
- Changeable terms
- Venue traps
- Attorney fee clauses

The scanner generates:
1. Executive summary
2. Risk map (by category)
3. Missing items checklist
4. Redline suggestions (strong/medium/light)
5. Negotiation playbook

## Signature Capacity Assistant

The signature assistant:
1. Detects the party name from contract text
2. Recommends signature block format (company vs individual)
3. Detects personal guarantee language and flags as HIGH RISK
4. Warns that "without prejudice" notes don't replace negotiating terms

If a personal guarantee is detected, the contract is automatically escalated to the Decision Queue as HIGH RISK.

## Master AI Safety

- **Modes:**
  - Advisor: Recommend only (no execution)
  - Operator: Low-risk execute (automated tasks)
  - Executive: Requires approval tokens

- **Approval Tokens:**
  - Required for: spend, publish, legal, dns
  - Two-step approval for Execute-High actions

- **Kill Switch:**
  - Pause all automations/ads/publishing/payout changes
  - Rotate keys checklist

- **Audit Logging:**
  - Every action logged with: actor, action_type, resource, timestamp, diff, metadata
  - Always visible in UI

## Data Models

All data models are defined in `head_office/backend/models/schemas.py`:
- DecisionQueueItem
- Contract, ContractScanResult
- ComplianceItem
- TaxTask
- Asset, AssetAlert
- LawLibraryEntry
- MasterAIAction
- AuditLogEvent

## File Structure

```
head_office/
├── backend/
│   ├── models/
│   │   ├── schemas.py          # Data models
│   │   └── __init__.py
│   ├── services/
│   │   ├── database.py         # Database service
│   │   ├── contract_scanner.py # Contract loophole scanner
│   │   ├── signature_assistant.py # Signature capacity assistant
│   │   └── __init__.py
│   └── api/
│       ├── executive_router.py    # Executive Launchpad
│       ├── decisions_router.py    # Decision Queue
│       ├── legal_router.py        # Legal + Contracts
│       ├── tax_router.py          # Tax Desk
│       ├── assets_router.py       # Assets + Safety Radar
│       ├── law_library_router.py  # Law Library
│       ├── master_ai_router.py    # Master AI
│       └── __init__.py
├── frontend/                    # (To be implemented)
├── scripts/
│   └── seed_data.py            # Seed sample data
└── README.md                   # This file
```

## Constraints

- **Local-first by default**: All data stored locally in SQLite
- **No paid APIs required**: Contract scanner is rule-based
- **Lawful and professional**: No tax evasion, no fabrication, no "magic" legal phrases
- **Modular and extendable**: Clear separation of concerns

## Next Steps

1. Frontend components (React + TypeScript)
2. Command palette (Ctrl+K) integration
3. Additional modules (Capital & Partnerships, Compliance Monitor, etc.)
4. PDF export functionality
5. Full Master AI implementation
