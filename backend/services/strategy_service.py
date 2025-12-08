from datetime import datetime
import json
from backend.executive_reasoning import ExecutiveDatabase
from typing import Dict, Any, List
from backend.corporate_memory import CorporateMemory
from autonomous.workflow_queue import WorkflowQueueRepository
from backend.audit_log import log_event

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)

def _enqueue_strategy_task(department: str, title: str, description: str, intent: str) -> str:
    corp_mem = CorporateMemory()
    queue_repo = WorkflowQueueRepository()
    
    now = _utcnow()
    
    task_record = {
        "title": title,
        "department": department,
        "status": "pending",
        "priority": "high",
        "description": description,
        "objective_id": None,
        "assigned_agent": None,
        "due_date": None,
        "dependencies": [],
        "metadata": {
            "intent": intent,
            "source": "command_center_strategy"
        },
        "created_at": now,
        "updated_at": now
    }
    
    created_task = corp_mem.create_task(task_record)
    queue_repo.enqueue_from_task(created_task)
    
    log_event(
        action="strategy_task_queued",
        status="success",
        log_message=f"Queued {intent} for {department}",
        details={"task_id": created_task["id"], "department": department, "intent": intent}
    )
    
    return str(created_task["id"])

async def run_strategic_vision() -> Dict[str, Any]:
    task_ids: List[str] = []
    departments = ["executive", "product", "marketing", "sales", "finance"]
    
    for dept in departments:
        task_id = _enqueue_strategy_task(
            department=dept,
            title="Strategic Vision Pulse",
            description="Generate updated strategic vision, key initiatives, and revenue priorities.",
            intent="run_strategic_vision"
        )
        task_ids.append(task_id)

    # Upsert the Earnetics vision directive
    payload = {
        "name": "Earnetics Core Income Engine",
        "description": "Multi-stream AI-powered revenue system for Joshua Fallat.",
        "streams": [
            {
                "code": "systeme_affiliate_funnel",
                "name": "Systeme.io Affiliate Funnel",
                "type": "affiliate",
                "estimated_setup_days": 3,
                "projected_monthly_revenue": 3000,
                "status": "planned"
            },
            {
                "code": "hustleplug_ai",
                "name": "HustlePlug AI Mobile App",
                "type": "product",
                "estimated_setup_days": 7,
                "projected_monthly_revenue": 5000,
                "status": "planned"
            },
            {
                "code": "the_609_machine",
                "name": "The 609 Machine Credit Repair System",
                "type": "product",
                "estimated_setup_days": 7,
                "projected_monthly_revenue": 4000,
                "status": "planned"
            }
        ],
        "total_projected_monthly_revenue": 12000
    }
    # Use ExecutiveDatabase connection for upsert
    exec_db = ExecutiveDatabase()
    with exec_db._get_conn() as conn:
        directive_id = upsert_earnetics_vision_directive(conn, payload)
    return {
        "status": "queued",
        "strategy": "vision",
        "task_ids": task_ids,
        "directive_id": directive_id,
    }

async def run_csuite_coordination() -> Dict[str, Any]:
    task_ids: List[str] = []
    departments = ["executive", "operations", "marketing", "sales", "finance"]
    
    for dept in departments:
        task_id = _enqueue_strategy_task(
            department=dept,
            title="C-Suite Coordination Sync",
            description="Sync C-suite departments on priorities, blockers, and next revenue moves.",
            intent="coordinate_csuite"
        )
        task_ids.append(task_id)

    return {
        "status": "queued",
        "strategy": "csuite_coordination",
        "task_ids": task_ids,
    }

async def run_revenue_cycle() -> Dict[str, Any]:
    task_ids: List[str] = []
    departments = ["marketing", "sales", "operations", "payments"]
    
    for dept in departments:
        task_id = _enqueue_strategy_task(
            department=dept,
            title="Revenue Cycle Activation",
            description="Run full revenue cycle: traffic -> leads -> offers -> checkout -> follow-up.",
            intent="fire_revenue_cycle"
        )
        task_ids.append(task_id)

    return {
        "status": "queued",
        "strategy": "revenue_cycle",
        "task_ids": task_ids,
    }

def upsert_earnetics_vision_directive(conn, payload: dict) -> int:
    """Create or update a single canonical executive_directive row.
    Returns the directive id.
    """
    cursor = conn.cursor()
    # Look for existing directive by type or title
    cursor.execute(
        "SELECT id FROM executive_directives WHERE directive_type = ? OR title = ?",
        ("earnetics_vision", "Earnetics Core Income Engine")
    )
    row = cursor.fetchone()
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    payload_json = json.dumps(payload, ensure_ascii=False)
    if row:
        directive_id = row["id"] if isinstance(row, dict) else row[0]
        cursor.execute(
            "UPDATE executive_directives SET payload = ?, updated_at = ? WHERE id = ?",
            (payload_json, now_iso, directive_id)
        )
    else:
        cursor.execute(
            "INSERT INTO executive_directives (title, directive_type, owner, priority, status, description, payload, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "Earnetics Core Income Engine",
                "earnetics_vision",
                "system",
                "high",
                "pending",
                "Earnetics revenue plan",
                payload_json,
                now_iso,
                now_iso,
            ),
        )
        directive_id = cursor.lastrowid
    conn.commit()
    return directive_id
