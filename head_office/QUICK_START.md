# Head Office - Quick Start Guide

## ✅ MVP Implementation Complete (Backend)

The Head Office backend is **100% complete** and ready for use!

### What's Implemented

✅ **7 API Routers:**
- Executive Launchpad (brief, today board, search)
- Decision Queue (CRUD + approve/deny)
- Legal + Contracts (contracts + scanner + signature analysis)
- Tax Desk (tasks + calendar + CPA packet)
- Assets + Safety Radar (inventory + alerts)
- Law Library (entries + shelves)
- Master AI (status + actions + kill switch)

✅ **Core Services:**
- Contract Loophole Scanner (rule-based, no paid APIs)
- Signature Capacity Assistant (detects guarantees, recommends signatures)
- Database Service (SQLite, local-first)

✅ **Documentation:**
- README.md (usage examples)
- FILE_TREE.md (structure + schemas)
- IMPLEMENTATION_SUMMARY.md (status)
- Seed data script

### Quick Start

1. **Start Backend:**
   ```bash
   python -m uvicorn backend.main_server:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Seed Sample Data:**
   ```bash
   python head_office/scripts/seed_data.py
   ```

3. **Test API:**
   ```bash
   # Get owner brief
   curl http://localhost:8000/api/head-office/executive/brief
   
   # List decisions
   curl http://localhost:8000/api/head-office/decisions
   
   # List contracts
   curl http://localhost:8000/api/head-office/legal/contracts
   ```

### Key Features

**Contract Scanner:**
- Rule-based pattern detection (no paid APIs)
- Detects high-risk clauses (uncapped liability, guarantees, etc.)
- Generates negotiation playbooks
- Escalates guarantees to Decision Queue

**Signature Assistant:**
- Detects party names from contract text
- Recommends signature blocks (company vs individual)
- Flags personal guarantees as HIGH RISK
- Warns about "without prejudice" notes

**Master AI:**
- Three modes: Advisor (recommend), Operator (low-risk execute), Executive (requires approval)
- Approval tokens for sensitive actions
- Kill switch support
- Always-on audit logging

### File Structure

```
head_office/
├── backend/
│   ├── models/schemas.py         # Data models
│   ├── services/
│   │   ├── database.py            # Database service
│   │   ├── contract_scanner.py    # Contract scanner
│   │   └── signature_assistant.py # Signature assistant
│   └── api/                       # 7 API routers
├── scripts/seed_data.py           # Seed sample data
└── README.md                      # Full documentation
```

### Next Steps

⚠️ **Frontend components are not yet implemented.** To complete the MVP:

1. Implement React components for each module
2. Add navigation entry to Command Center
3. Implement Ctrl+K command palette
4. Add PDF export functionality

The backend is production-ready and can be used via API calls!
