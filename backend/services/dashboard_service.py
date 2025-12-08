from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    # BUSINESS_DB_PATH and (optionally) AUDIT_LOG_DB from your existing memory module
    from backend.corporate_memory import BUSINESS_DB_PATH, AUDIT_LOG_DB  # type: ignore[attr-defined]
except ImportError:
    from backend.corporate_memory import BUSINESS_DB_PATH  # type: ignore[no-redef]
    AUDIT_LOG_DB = Path("audit_log.db")  # fallback if not exported

# Hard-coded Fallat agent roster so the dashboard is NEVER empty
FALLAT_AGENT_NAMES: List[str] = [
    "Akasha",
    "Atlas",
    "Omen",
    "Obsidian",
    "Noir",
    "Nova",
    "Mercury",
    "Forge",
    "Vega",
    "Orion",
    "Vortex",
    "Lumen",
    "Beacon",
    "Quill",
    "Keeper",
    "Sentinel",
    "Pulse",
    "Relay",
    "Harbor",
    "Muse",
    "Lex",
    "Seraph",
]

AUDIT_DB_PATH = Path(str(AUDIT_LOG_DB)) if "AUDIT_LOG_DB" in globals() else Path("audit_log.db")


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_ts(value: Any) -> str:
    """Normalize timestamps to ISO8601 strings."""
    if not value:
        return datetime.utcnow().isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        text = str(value).strip()
        if not text:
            return datetime.utcnow().isoformat()
        # Let datetime parse whatever it can
        return datetime.fromisoformat(text.replace("Z", "")).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()


def _fetch_audit_events(limit: int) -> List[Dict[str, Any]]:
    """Try to pull events from audit-related tables if they exist."""
    if not AUDIT_DB_PATH.exists():
        return []

    events: List[Dict[str, Any]] = []
    conn = sqlite3.connect(AUDIT_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1) Primary guess: audit_log table
    try:
        cur.execute(
            """
            SELECT
                timestamp,
                COALESCE(actor, agent_name, department, source, 'system') AS actor,
                COALESCE(department, '') AS department,
                COALESCE(event_type, action, 'event') AS event_type,
                COALESCE(details, message, '') AS details
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        for row in cur.fetchall():
            events.append(
                {
                    "timestamp": _parse_ts(row["timestamp"]),
                    "actor": row["actor"],
                    "department": row["department"],
                    "event_type": row["event_type"],
                    "summary": row["details"],
                }
            )
    except sqlite3.OperationalError:
        # Table might not exist – fall back to the business DB if needed
        pass

    conn.close()
    return events


def _fallback_events(limit: int) -> List[Dict[str, Any]]:
    """If there is no audit data yet, create synthetic 'standing by' events."""
    now = datetime.utcnow().isoformat()
    events: List[Dict[str, Any]] = []

    for name in FALLAT_AGENT_NAMES[: min(limit, len(FALLAT_AGENT_NAMES))]:
        events.append(
            {
                "timestamp": now,
                "actor": name,
                "department": "system",
                "event_type": "status",
                "summary": f"{name} is online in the AI Revenue Command Center.",
            }
        )

    return events[:limit]


def get_recent_events(limit: int = 40) -> List[Dict[str, Any]]:
    """
    Public API for the dashboard router.

    Returns a list of events of the form:
    {
        "timestamp": "...",
        "actor": "Akasha",
        "department": "marketing",
        "event_type": "task_completed",
        "summary": "Completed lead magnet campaign for Systeme.io"
    }
    """
    # First try to pull real events from the audit DB
    events = _fetch_audit_events(limit)

    # If there are no real events yet, return synthetic status lines
    if not events:
        events = _fallback_events(limit)

    # Ensure the list is at most `limit` items
    return events[:limit]


def get_agent_roster(limit_events: int = 200) -> List[Dict[str, Any]]:
    """
    Returns a roster of agents plus their recent events.

    Shape:
    {
        "name": "Akasha",
        "role": "Strategy Architect",
        "department": "Executive",
        "status": "online",
        "last_event": {...} or None,
        "recent_events": [...]
    }
    """
    events = get_recent_events(limit_events)
    by_actor: Dict[str, List[Dict[str, Any]]] = {}

    for ev in events:
        actor = ev.get("actor") or "system"
        by_actor.setdefault(actor, []).append(ev)

    roster: List[Dict[str, Any]] = []

    # Basic department mapping just for flavor in the UI
    department_map: Dict[str, str] = {
        "Akasha": "Executive",
        "Atlas": "Operations",
        "Omen": "Analytics",
        "Obsidian": "System",
        "Noir": "Security",
        "Nova": "Marketing",
        "Mercury": "Sales",
        "Forge": "Product",
        "Vega": "Affiliate",
        "Orion": "Innovation",
        "Vortex": "Engineering",
        "Lumen": "Customer Success",
        "Beacon": "Reinvestment",
        "Quill": "Strategy",
        "Keeper": "Knowledge",
        "Sentinel": "System",
        "Pulse": "Analytics",
        "Relay": "Comms",
        "Harbor": "Support",
        "Muse": "Creative",
        "Lex": "Legal",
        "Seraph": "Guardian",
    }

    for name in FALLAT_AGENT_NAMES:
        agent_events = by_actor.get(name, [])
        roster.append(
            {
                "name": name,
                "role": f"{department_map.get(name, 'Agent')} Agent",
                "department": department_map.get(name, "System"),
                "status": "online",  # we treat all as online for now
                "last_event": agent_events[0] if agent_events else None,
                "recent_events": agent_events,
            }
        )

    return roster
