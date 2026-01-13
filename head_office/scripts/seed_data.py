"""
Seed Sample Data for Head Office
Creates sample data so UI is not empty
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from head_office.backend.services.database import get_db
import sqlite3
import json


def seed_sample_data():
    """Seed sample data for Head Office"""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Seed Decision Queue Items
        print("Seeding Decision Queue items...")
        decisions = [
            {
                "id": str(uuid.uuid4()),
                "title": "Approve Q1 Marketing Campaign",
                "category": "spend",
                "recommendation": "Approve $10,000 marketing campaign for Q1",
                "upside": "Expected 8x ROI based on Q4 performance",
                "cost": 10000.0,
                "risk": "Medium - new campaign format",
                "reversibility": "Can pause campaign if needed",
                "alternatives": json.dumps(["Lower budget: $5,000", "Defer to Q2"]),
                "required_by": (datetime.now() + timedelta(days=3)).isoformat(),
                "status": "pending",
                "metadata": json.dumps({}),
                "created_at": now,
                "updated_at": now
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Approve Blog Post Publication",
                "category": "publish",
                "recommendation": "Publish '10 Ways to Increase Revenue' blog post",
                "upside": "Expected 500+ views, SEO boost",
                "cost": 0.0,
                "risk": "Low - standard blog post",
                "reversibility": "Can unpublish if needed",
                "alternatives": json.dumps(["Schedule for next week", "Add more examples"]),
                "required_by": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "pending",
                "metadata": json.dumps({}),
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for decision in decisions:
            cursor.execute("""
                INSERT OR IGNORE INTO decision_queue
                (id, title, category, recommendation, upside, cost, risk, reversibility,
                 alternatives, required_by, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision["id"], decision["title"], decision["category"],
                decision["recommendation"], decision["upside"], decision["cost"],
                decision["risk"], decision["reversibility"], decision["alternatives"],
                decision["required_by"], decision["status"], decision["metadata"],
                decision["created_at"], decision["updated_at"]
            ))
        
        # Seed Contracts
        print("Seeding Contracts...")
        contracts = [
            {
                "id": str(uuid.uuid4()),
                "title": "Service Agreement - Client Corp",
                "party_name": "Your Company Inc.",
                "counterparty": "Client Corp",
                "contract_type": "service",
                "status": "draft",
                "version": 1,
                "file_path": None,
                "signed_date": None,
                "expiry_date": None,
                "value": 50000.0,
                "metadata": json.dumps({}),
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for contract in contracts:
            cursor.execute("""
                INSERT OR IGNORE INTO contracts
                (id, title, party_name, counterparty, contract_type, status, version,
                 file_path, signed_date, expiry_date, value, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract["id"], contract["title"], contract["party_name"],
                contract["counterparty"], contract["contract_type"], contract["status"],
                contract["version"], contract["file_path"], contract["signed_date"],
                contract["expiry_date"], contract["value"], contract["metadata"],
                contract["created_at"], contract["updated_at"]
            ))
        
        # Seed Compliance Items
        print("Seeding Compliance items...")
        compliance_items = [
            {
                "id": str(uuid.uuid4()),
                "title": "Annual Report Filing - Delaware",
                "category": "filing",
                "jurisdiction": "Delaware",
                "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "on_track",
                "obligation_source": "corporate_law",
                "completed_at": None,
                "notes": "Due March 1st",
                "created_at": now,
                "updated_at": now
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Business License Renewal",
                "category": "renewal",
                "jurisdiction": "State",
                "deadline": (datetime.now() + timedelta(days=60)).isoformat(),
                "status": "on_track",
                "obligation_source": None,
                "completed_at": None,
                "notes": "",
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for item in compliance_items:
            cursor.execute("""
                INSERT OR IGNORE INTO compliance_items
                (id, title, category, jurisdiction, deadline, status, obligation_source,
                 completed_at, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["title"], item["category"], item["jurisdiction"],
                item["deadline"], item["status"], item["obligation_source"],
                item["completed_at"], item["notes"], item["created_at"], item["updated_at"]
            ))
        
        # Seed Tax Tasks
        print("Seeding Tax tasks...")
        tax_tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Q4 2024 Tax Filing",
                "tax_type": "federal",
                "filing_period": "Q4-2024",
                "deadline": (datetime.now() + timedelta(days=45)).isoformat(),
                "status": "pending",
                "documents": json.dumps(["income_statement", "expense_report"]),
                "notes": "Quarterly filing",
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for task in tax_tasks:
            cursor.execute("""
                INSERT OR IGNORE INTO tax_tasks
                (id, title, tax_type, filing_period, deadline, status, documents, notes,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task["id"], task["title"], task["tax_type"], task["filing_period"],
                task["deadline"], task["status"], task["documents"], task["notes"],
                task["created_at"], task["updated_at"]
            ))
        
        # Seed Assets
        print("Seeding Assets...")
        assets = [
            {
                "id": str(uuid.uuid4()),
                "name": "earnetics.live Domain",
                "category": "digital",
                "owner": "owner@example.com",
                "criticality": "critical",
                "description": "Primary domain",
                "access_info": "Registrar: Namecheap",
                "renewal_date": (datetime.now() + timedelta(days=180)).isoformat(),
                "metadata": json.dumps({}),
                "created_at": now,
                "updated_at": now
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Stripe Account",
                "category": "financial",
                "owner": "owner@example.com",
                "criticality": "critical",
                "description": "Payment processor account",
                "access_info": "Account ID: acct_xxx",
                "renewal_date": None,
                "metadata": json.dumps({}),
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for asset in assets:
            cursor.execute("""
                INSERT OR IGNORE INTO assets
                (id, name, category, owner, criticality, description, access_info,
                 renewal_date, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset["id"], asset["name"], asset["category"], asset["owner"],
                asset["criticality"], asset["description"], asset["access_info"],
                asset["renewal_date"], asset["metadata"], asset["created_at"],
                asset["updated_at"]
            ))
        
        # Seed Law Library Entries
        print("Seeding Law Library entries...")
        law_entries = [
            {
                "id": str(uuid.uuid4()),
                "title": "Contract Formation Basics",
                "shelf": "contract_law",
                "jurisdiction": "US",
                "applicability_tags": json.dumps(["contracts", "formation", "basics"]),
                "summary": "Basic principles of contract formation: offer, acceptance, consideration",
                "compliance_checklist": json.dumps(["Clear offer", "Acceptance", "Consideration", "Legal capacity"]),
                "risk_level": "low",
                "primary_sources": json.dumps(["Restatement (Second) of Contracts"]),
                "created_at": now,
                "updated_at": now
            },
            {
                "id": str(uuid.uuid4()),
                "title": "LLC Formation Requirements",
                "shelf": "corporate",
                "jurisdiction": "Delaware",
                "applicability_tags": json.dumps(["LLC", "formation", "Delaware"]),
                "summary": "Requirements for forming an LLC in Delaware",
                "compliance_checklist": json.dumps(["Articles of Organization", "Registered Agent", "Operating Agreement"]),
                "risk_level": "medium",
                "primary_sources": json.dumps(["Delaware Code Title 6, Chapter 18"]),
                "created_at": now,
                "updated_at": now
            }
        ]
        
        for entry in law_entries:
            cursor.execute("""
                INSERT OR IGNORE INTO law_library
                (id, title, shelf, jurisdiction, applicability_tags, summary,
                 compliance_checklist, risk_level, primary_sources, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["id"], entry["title"], entry["shelf"], entry["jurisdiction"],
                entry["applicability_tags"], entry["summary"], entry["compliance_checklist"],
                entry["risk_level"], entry["primary_sources"], entry["created_at"],
                entry["updated_at"]
            ))
        
        conn.commit()
        print("✅ Sample data seeded successfully!")


if __name__ == "__main__":
    seed_sample_data()
