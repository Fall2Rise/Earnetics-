"""Signal Collector - gathers performance metrics for Strategy Cell."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.corporate_memory import BUSINESS_DB_PATH
from backend.audit_log import list_events

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SIGNALS_DIR = PROJECT_ROOT / "backend" / "reports" / "signals"
SIGNALS_DIR.mkdir(parents=True, exist_ok=True)


class SignalCollector:
    """Collects performance signals from various sources."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path

    def collect_24h_signals(self) -> Dict[str, Any]:
        """Collect signals from the last 24 hours."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        
        signals = {
            "collected_at": now.isoformat(),
            "period_hours": 24,
            "leads_created_24h": 0,
            "replies_24h": 0,
            "calls_booked_24h": 0,
            "closes_24h": 0,
            "cash_collected_24h": 0.0,
            "top_objections": [],
            "top_hooks": [],
            "pipeline_by_stage": {
                "leads": 0,
                "replies": 0,
                "calls": 0,
                "closes": 0,
            },
            "last_24h_failures": [],
        }
        
        # Collect from audit log
        try:
            events = list_events(limit=1000)
            for event in events:
                event_time = event.get("timestamp")
                if not event_time:
                    continue
                
                try:
                    event_dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
                    if event_dt < cutoff:
                        continue
                except (ValueError, TypeError):
                    continue
                
                action = event.get("action", "").lower()
                message = event.get("message", "").lower()
                
                # Count leads
                if "lead" in action or "lead" in message:
                    signals["leads_created_24h"] += 1
                    signals["pipeline_by_stage"]["leads"] += 1
                
                # Count replies
                if "reply" in action or "reply" in message or "response" in action:
                    signals["replies_24h"] += 1
                    signals["pipeline_by_stage"]["replies"] += 1
                
                # Count calls
                if "call" in action or "call" in message or "booked" in message:
                    signals["calls_booked_24h"] += 1
                    signals["pipeline_by_stage"]["calls"] += 1
                
                # Count closes
                if "close" in action or "sale" in action or "purchase" in message:
                    signals["closes_24h"] += 1
                    signals["pipeline_by_stage"]["closes"] += 1
                
                # Extract objections
                if "objection" in message or "concern" in message or "hesitant" in message:
                    signals["top_objections"].append(message[:100])
                
                # Extract hooks (positive signals)
                if "interested" in message or "yes" in message or "book" in message:
                    signals["top_hooks"].append(message[:100])
                
                # Track failures
                if event.get("status") == "error" or "fail" in action:
                    signals["last_24h_failures"].append({
                        "action": action,
                        "message": message[:200],
                        "timestamp": event_time,
                    })
        except Exception as e:
            # If audit log fails, continue with defaults
            pass
        
        # Collect cash from financial operations
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(gross_revenue) 
                    FROM financial_operations 
                    WHERE created_at >= ?
                """, (cutoff.isoformat(),))
                result = cursor.fetchone()
                if result and result[0]:
                    signals["cash_collected_24h"] = float(result[0])
        except Exception:
            pass
        
        # Deduplicate and limit lists
        signals["top_objections"] = list(set(signals["top_objections"]))[:10]
        signals["top_hooks"] = list(set(signals["top_hooks"]))[:10]
        signals["last_24h_failures"] = signals["last_24h_failures"][:10]
        
        return signals

    def save_signals(self, signals: Dict[str, Any]) -> Path:
        """Save signals to latest_signals.json."""
        latest_file = SIGNALS_DIR / "latest_signals.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2)
        return latest_file

    def load_latest_signals(self) -> Dict[str, Any]:
        """Load latest signals from file."""
        latest_file = SIGNALS_DIR / "latest_signals.json"
        if not latest_file.exists():
            return self.collect_24h_signals()
        
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.collect_24h_signals()

