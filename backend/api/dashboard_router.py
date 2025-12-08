from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.corporate_memory import BUSINESS_DB_PATH, get_latest_earnetics_vision
from backend.services.dashboard_service import (
    get_recent_events,
    get_agent_roster,
)
from backend.models.dfy_income_engine import (
    DFYLead,
    DFYLeadCreate,
    dfy_leads_store,
)
from backend.services.dfy_income_engine import process_new_dfy_leads
from backend.services.rnd_affiliate_research import (
    build_affiliate_research_brief,
    generate_initial_offer_candidates,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(BUSINESS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _revenue_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    cur = conn.cursor()
    statuses = ("completed", "paid", "success", "processed")
    placeholders = ",".join("?" for _ in statuses)

    cur.execute(
        f"""
        SELECT COALESCE(SUM(amount), 0) AS total_revenue,
               COUNT(*) AS transaction_count
        FROM transactions
        WHERE LOWER(status) IN ({placeholders})
        """,
        tuple(statuses),
    )
    row = cur.fetchone()
    row_dict = dict(row) if row else {}
    total_revenue = _safe_float(row_dict.get("total_revenue"))
    transaction_count = int(row_dict.get("transaction_count") or 0)

    cur.execute(
        f"""
        SELECT COALESCE(SUM(amount), 0) AS month_to_date
        FROM transactions
        WHERE LOWER(status) IN ({placeholders})
          AND substr(created_at, 1, 7) = strftime('%Y-%m', 'now')
        """,
        tuple(statuses),
    )
    month_row = cur.fetchone()
    month_dict = dict(month_row) if month_row else {}
    month_to_date = _safe_float(month_dict.get("month_to_date"))

    cur.execute(
        """
        SELECT amount, source, category, created_at
        FROM transactions
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    last_row = cur.fetchone()
    last_transaction: Dict[str, Any] | None = None
    if last_row:
        last_transaction = {
            "amount": _safe_float(last_row["amount"]),
            "source": last_row["source"],
            "category": last_row["category"],
            "created_at": last_row["created_at"],
        }

    return {
        "total": total_revenue,
        "month_to_date": month_to_date,
        "transactions": transaction_count,
        "last_transaction": last_transaction,
    }


def _operations_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products WHERE LOWER(status)='active'")
        row = cur.fetchone()
        active_streams = int(row[0]) if row else 0

        cur.execute("SELECT COUNT(*) FROM products")
        row = cur.fetchone()
        total_products = int(row[0]) if row else 0

        cur.execute("SELECT COALESCE(SUM(revenue_generated), 0) FROM products")
        row = cur.fetchone()
        revenue_generated = _safe_float(row[0]) if row else 0.0

        cur.execute(
            "SELECT COUNT(*) FROM campaigns WHERE LOWER(status) IN ('running','scheduled')"
        )
        row = cur.fetchone()
        active_campaigns = int(row[0]) if row else 0

        return {
            "active_streams": active_streams,
            "total_products": total_products,
            "revenue_generated": revenue_generated,
            "active_campaigns": active_campaigns,
        }
    except sqlite3.OperationalError:
        return {
            "active_streams": 0,
            "total_products": 0,
            "revenue_generated": 0.0,
            "active_campaigns": 0,
        }


def _analytics_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT metric_name, metric_value, metric_date, source
        FROM customer_analytics
        ORDER BY metric_date DESC, id DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if not row:
        return {
            "headline": "Monthly Leads",
            "value": 0,
            "unit": "",
            "source": None,
        }

    try:
        value = float(row["metric_value"])
    except (TypeError, ValueError):
        value = row["metric_value"]

    return {
        "headline": row["metric_name"],
        "value": value,
        "unit": "",
        "source": row["source"],
        "metric_date": row["metric_date"],
    }


def _task_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                SUM(CASE WHEN LOWER(status) IN ('in_progress','pending','queued') THEN 1 ELSE 0 END) AS active_tasks,
                SUM(CASE WHEN LOWER(status) = 'completed' THEN 1 ELSE 0 END) AS completed_tasks
            FROM department_tasks
            """
        )
        row = cur.fetchone()
        row_dict = dict(row) if row else {}
        active_tasks = int(row_dict.get("active_tasks") or 0)
        completed_tasks = int(row_dict.get("completed_tasks") or 0)

        cur.execute(
            """
            SELECT COUNT(*) FROM autonomy_task_queue
            WHERE LOWER(status) IN ('pending','queued','retrying')
            """
        )
        row = cur.fetchone()
        queued = int(row[0]) if row else 0

        return {
            "active": active_tasks,
            "completed": completed_tasks,
            "queued": queued,
        }
    except sqlite3.OperationalError:
        return {"active": 0, "completed": 0, "queued": 0}


def _market_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT payload, due_date, title
            FROM executive_directives
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
        projected = 0.0
        open_directives = 0
        latest_due: str | None = None
        for row in cur.fetchall():
            payload_text = row["payload"] or ""
            payload: Dict[str, Any] | None = None
            try:
                payload = json.loads(payload_text)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                projected += _safe_float(payload.get("projected_monthly_revenue"))
            if row["due_date"] and not latest_due:
                latest_due = row["due_date"]
            open_directives += 1

        cur.execute(
            """
            SELECT COALESCE(SUM(metric_value), 0)
            FROM department_performance
            WHERE LOWER(metric_name) IN ('pipeline_value','qualified_leads')
            """
        )
        row = cur.fetchone()
        pipeline_value = _safe_float(row[0]) if row else 0.0

        return {
            "projected_monthly": projected,
            "pipeline_value": pipeline_value,
            "open_directives": open_directives,
            "next_due": latest_due,
        }
    except sqlite3.OperationalError:
        return {
            "projected_monthly": 0.0,
            "pipeline_value": 0.0,
            "open_directives": 0,
            "next_due": None,
        }


DEPARTMENT_ALIASES: Dict[str, Tuple[str, ...]] = {
    "Executive": ("executive", "leadership", "strategy", "ceo"),
    "Product": ("product", "innovation", "development", "rd"),
    "Marketing": ("marketing", "growth"),
    "Sales": ("sales", "revenue"),
    "Operations": ("operations", "support"),
    "Finance": ("finance", "cfo"),
}


def _empty_department_status() -> List[Dict[str, Any]]:
    return [
        {"label": label, "completed": 0, "total": 0, "progress": 0.0, "status": "no_data"}
        for label in DEPARTMENT_ALIASES.keys()
    ]


def _department_status(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    results: List[Dict[str, Any]] = []
    for label, aliases in DEPARTMENT_ALIASES.items():
        placeholders = ",".join("?" for _ in aliases)
        try:
            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN LOWER(status) = 'completed' THEN 1 ELSE 0 END) AS completed
                FROM department_tasks
                WHERE LOWER(department) IN ({placeholders})
                """,
                tuple(alias.lower() for alias in aliases),
            )
            row = cur.fetchone()
            row_dict = dict(row) if row else {}
            total = int(row_dict.get("total") or 0)
            completed = int(row_dict.get("completed") or 0)
        except sqlite3.OperationalError:
            total = 0
            completed = 0
        progress = (completed / total * 100) if total else 0.0

        if total == 0:
            status = "no_data"
        elif progress >= 75:
            status = "operational"
        elif progress >= 40:
            status = "monitor"
        else:
            status = "attention"

        results.append(
            {
                "label": label,
                "completed": completed,
                "total": total,
                "progress": round(progress, 1) if total else 0.0,
                "status": status,
            }
        )
    return results


ACTIVITY_SOURCES: Tuple[Tuple[str, str, str], ...] = (
    ("transactions", "created_at", "transaction"),
    ("department_tasks", "updated_at", "task"),
    ("executive_directives", "updated_at", "directive"),
    ("data_collections", "collected_at", "data_collection"),
)


def _recent_activity(conn: sqlite3.Connection, limit: int = 10) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    entries: List[Dict[str, Any]] = []

    for table, timestamp_field, kind in ACTIVITY_SOURCES:
        try:
            cur.execute(
                f"""
                SELECT *, {timestamp_field} AS ts
                FROM {table}
                WHERE {timestamp_field} IS NOT NULL
                ORDER BY {timestamp_field} DESC
                LIMIT ?
                """,
                (limit,),
            )
        except sqlite3.OperationalError:
            continue
        for row in cur.fetchall():
            row_dict = dict(row)
            timestamp = _parse_timestamp(row_dict.get("ts"))
            if not timestamp:
                continue
            entry: Dict[str, Any] = {
                "kind": kind,
                "timestamp": timestamp.isoformat(),
            }
            if kind == "transaction":
                entry["title"] = "Revenue transaction"
                entry["detail"] = f"{row_dict.get('source') or 'Unknown source'} · ${_safe_float(row_dict.get('amount')):,.2f}"
            elif kind == "task":
                entry["title"] = row_dict.get("title") or "Task update"
                department = (row_dict.get("department") or "").title()
                status = (row_dict.get("status") or "").replace("_", " ").title()
                entry["detail"] = f"{department} · {status}".strip(" ·")
            elif kind == "directive":
                entry["title"] = row_dict.get("title") or "Executive directive"
                entry["detail"] = row_dict.get("directive_type") or "initiative"
            else:
                entry["title"] = row_dict.get("data_type") or "Data capture"
                entry["detail"] = row_dict.get("data_source") or "source"
            entries.append(entry)

    entries.sort(
        key=lambda item: _parse_timestamp(item["timestamp"]) or datetime.min,
        reverse=True,
    )
    return entries[:limit]


def _recent_revenue_cycles() -> List[Dict[str, Any]]:
    """Helper to retrieve recent revenue cycles for dashboard snapshot."""
    if not BUSINESS_DB_PATH.exists():
        return []

    with _connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS revenue_cycles (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    projected_revenue REAL
                )
                """
            )
            conn.commit()

            cursor.execute(
                """
                SELECT id, name, status, start_date, end_date, projected_revenue
                FROM revenue_cycles
                ORDER BY start_date DESC
                LIMIT 10
                """
            )
            cycles = []
            for row in cursor.fetchall():
                cycles.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "status": row[2],
                        "start_date": row[3],
                        "end_date": row[4],
                        "projected_revenue": _safe_float(row[5]),
                    }
                )
            return cycles
        except sqlite3.OperationalError:
            return []


@router.get("/snapshot")
def get_dashboard_snapshot() -> Dict[str, Any]:
    if not BUSINESS_DB_PATH.exists():
        return {
            "revenue": {
                "total": 0.0,
                "month_to_date": 0.0,
                "transactions": 0,
                "last_transaction": None,
            },
            "operations": {
                "active_streams": 0,
                "total_products": 0,
                "revenue_generated": 0.0,
                "active_campaigns": 0,
            },
            "analytics": {
                "headline": "Monthly Leads",
                "value": 0,
                "unit": "",
                "source": None,
            },
            "tasks": {"active": 0, "completed": 0, "queued": 0},
            "market": {
                "projected_monthly": 0.0,
                "pipeline_value": 0.0,
                "open_directives": 0,
                "next_due": None,
            },
            "departments": _empty_department_status(),
            "activity": [],
            "revenue_cycles": [],
        }

    with _connect() as conn:
        revenue = _revenue_summary(conn)
        operations = _operations_summary(conn)
        analytics = _analytics_summary(conn)
        tasks = _task_summary(conn)
        # Pull latest Earnetics Core Income Engine vision (if available)
        vision = get_latest_earnetics_vision()

        projected_monthly = 10000.0
        open_directives = 10
        next_due = "2025-11-13"

        if vision and vision.get("payload"):
            payload = vision["payload"] or {}
            projected_monthly = float(
                payload.get("total_projected_monthly_revenue", projected_monthly)
            )

            streams = payload.get("streams") or []
            open_directives = len(streams)

            # Prefer due_date, fall back to created_at
            next_due = vision.get("due_date") or vision.get("created_at") or next_due

        market = {
            "projected_monthly": projected_monthly,
            "pipeline_value": 0.0,
            "open_directives": open_directives,
            "next_due": next_due,
        }
        departments = _department_status(conn)
        activity = _recent_activity(conn)

    revenue_cycles = _recent_revenue_cycles()

    return {
        "revenue": revenue,
        "operations": operations,
        "analytics": analytics,
        "tasks": tasks,
        "market": market,
        "departments": departments,
        "activity": activity,
        "revenue_cycles": revenue_cycles,
    }


@router.get("/activity")
def dashboard_activity(limit: int = 40) -> Dict[str, Any]:
    """Live activity feed for the UI."""
    return {"events": get_recent_events(limit)}


@router.get("/agents")
def dashboard_agents(limit_events: int = 200) -> Dict[str, Any]:
    """Agent roster summary for the UI."""
    return {"agents": get_agent_roster(limit_events)}


# ---------------------------------------------------------------------
# DFY Income Engine Endpoints
# ---------------------------------------------------------------------


@router.post("/dfy/leads", response_model=DFYLead)
def create_new_dfy_lead(lead_in: DFYLeadCreate) -> DFYLead:
    """
    Create a new DFY lead.

    - Accepts the lighter DFYLeadCreate model (so you don't have to send every field).
    - Auto-generates id, status, and timestamps.
    - Stores it in dfy_leads_store.
    - Triggers the DFY engine to process new leads.
    """
    # Start from the incoming data
    data = lead_in.model_dump()

    # Auto-generate id if missing
    if not data.get("id"):
        data["id"] = f"lead-{uuid4().hex[:8]}"

    # Defaults
    now = datetime.utcnow()
    data.setdefault("status", "new")
    data.setdefault("created_at", now)
    data.setdefault("updated_at", now)

    # Build full DFYLead model
    lead = DFYLead(**data)

    # Store
    dfy_leads_store[lead.id] = lead

    # Kick the DFY engine so it can enrich/route this lead
    try:
        process_new_dfy_leads()
    except Exception:
        # Fail-safe: return the stored lead even if background processing hiccups
        pass

    # Return the possibly-updated lead
    return dfy_leads_store.get(lead.id, lead)


@router.get("/dfy/leads", response_model=List[DFYLead])
def get_dfy_leads() -> List[DFYLead]:
    """Return all DFY leads in memory."""
    return list(dfy_leads_store.values())


@router.get("/dfy/leads/{lead_id}", response_model=DFYLead)
def get_dfy_lead(lead_id: str) -> DFYLead:
    """
    Return a single DFY lead, including status and strategy summary.
    """
    lead = dfy_leads_store.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="DFY lead not found")
    return lead


@router.post("/dfy/leads/{lead_id}/process", response_model=DFYLead)
def process_single_dfy_lead(lead_id: str) -> DFYLead:
    """
    Force the DFY engine to process this lead immediately.
    """
    lead = dfy_leads_store.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="DFY lead not found")

    # Mark it as new so the DFY engine picks it up
    lead.status = "new"
    lead.updated_at = datetime.utcnow()
    dfy_leads_store[lead_id] = lead

    process_new_dfy_leads()

    updated = dfy_leads_store.get(lead_id)
    if not updated:
        raise HTTPException(
            status_code=500, detail="DFY lead disappeared after processing"
        )
    return updated


@router.get("/dfy/leads/{lead_id}/research")
def get_dfy_lead_research(lead_id: str) -> Dict[str, Any]:
    """
    Return the R&D research brief + initial offer candidates for this DFY lead.

    This does NOT hit the internet – it gives a structured plan for your agents
    and departments to execute on.
    """
    lead = dfy_leads_store.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="DFY lead not found")

    brief = build_affiliate_research_brief(lead)
    candidates = generate_initial_offer_candidates(lead)

    return {
        "lead_id": lead_id,
        "segment": brief.get("segment"),
        "research_brief": brief,
        "offer_candidates": candidates,
    }
