import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from backend.system_state import is_mail_paused
from backend.audit_log import log_event

def _normalize_env_path(env_value: Optional[str], default: str) -> Path:
    """Normalize path from environment variable, converting backslashes to forward slashes."""
    if not env_value:
        return Path(default)
    return Path(env_value.replace("\\", "/"))

BUSINESS_DB_PATH = _normalize_env_path(os.getenv("BUSINESS_DB_PATH"), "business_database.db")
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)

@dataclass
class Subscriber:
    email: str
    first_name: Optional[str] = None
    status: str = "active"  # active, unsubscribed, bounced
    tags: List[str] = None
    source: Optional[str] = None
    
    def to_record(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "first_name": self.first_name,
            "status": self.status,
            "tags": json.dumps(self.tags or []),
            "source": self.source,
            "created_at": _utcnow(),
            "updated_at": _utcnow()
        }

class MailOpsService:
    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mailops_subscribers (
                    email TEXT PRIMARY KEY,
                    first_name TEXT,
                    status TEXT NOT NULL,
                    tags TEXT,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mailops_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL, -- draft, scheduled, sending, completed, failed
                    target_segment JSON,
                    stats JSON,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mailops_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    subscriber_email TEXT,
                    event_type TEXT NOT NULL, -- sent, opened, clicked, bounced
                    timestamp TEXT NOT NULL,
                    metadata JSON
                )
            """)
            conn.commit()

    # Subscribers
    def add_subscriber(self, subscriber: Subscriber) -> Dict[str, Any]:
        with self._connection() as conn:
            cur = conn.cursor()
            record = subscriber.to_record()
            try:
                cur.execute("""
                    INSERT INTO mailops_subscribers (email, first_name, status, tags, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record["email"], record["first_name"], record["status"], 
                    record["tags"], record["source"], record["created_at"], record["updated_at"]
                ))
                conn.commit()
                log_event("mailops_subscriber_added", email=subscriber.email, source=subscriber.source)
                return record
            except sqlite3.IntegrityError:
                # Update existing
                cur.execute("""
                    UPDATE mailops_subscribers 
                    SET first_name = COALESCE(?, first_name),
                        tags = ?,
                        updated_at = ?
                    WHERE email = ?
                """, (record["first_name"], record["tags"], record["updated_at"], record["email"]))
                conn.commit()
                log_event("mailops_subscriber_updated", email=subscriber.email)
                return self.get_subscriber(subscriber.email)

    def get_subscriber(self, email: str) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM mailops_subscribers WHERE email = ?", (email,))
            row = cur.fetchone()
            if row:
                d = dict(row)
                d["tags"] = json.loads(d["tags"] or "[]")
                return d
            return None

    def list_subscribers(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM mailops_subscribers ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                d["tags"] = json.loads(d["tags"] or "[]")
                results.append(d)
            return results

    # Campaigns
    def create_campaign(self, subject: str, body: str, target_segment: Dict = None) -> Dict[str, Any]:
        record = {
            "subject": subject,
            "body": body,
            "status": "draft",
            "target_segment": json.dumps(target_segment or {}),
            "stats": json.dumps({"sent": 0, "failed": 0}),
            "created_at": _utcnow(),
            "updated_at": _utcnow()
        }
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO mailops_campaigns (subject, body, status, target_segment, stats, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record["subject"], record["body"], record["status"], 
                record["target_segment"], record["stats"], record["created_at"], record["updated_at"]
            ))
            campaign_id = cur.lastrowid
            conn.commit()
        record["id"] = campaign_id
        record["target_segment"] = target_segment or {}
        record["stats"] = {"sent": 0, "failed": 0}
        log_event("mailops_campaign_created", campaign_id=campaign_id, subject=subject)
        return record

    def send_campaign(self, campaign_id: int) -> Dict[str, Any]:
        if is_mail_paused():
            log_event("mailops_send_blocked", campaign_id=campaign_id, reason="MAIL_SENDING_PAUSED")
            raise RuntimeError("Mail sending is paused globally.")

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM mailops_campaigns WHERE id = ?", (campaign_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Campaign not found")
            
            campaign = dict(row)
            campaign["target_segment"] = json.loads(campaign["target_segment"] or "{}")
            campaign["stats"] = json.loads(campaign["stats"] or "{}")
            
            # Update status to sending
            cur.execute("UPDATE mailops_campaigns SET status = 'sending', updated_at = ? WHERE id = ?", (_utcnow(), campaign_id))
            conn.commit()
            
            # Get active subscribers
            cur.execute("SELECT email, first_name FROM mailops_subscribers WHERE status = 'active'")
            subscribers = cur.fetchall()
            
            sent_count = 0
            failed_count = 0
            
            # Check if Resend is configured
            resend_api_key = os.getenv("RESEND_API_KEY")
            
            if resend_api_key:
                # Real sending via Resend
                try:
                    import resend
                    resend.api_key = resend_api_key
                    
                    for sub in subscribers:
                        try:
                            # Personalize email body
                            body = campaign["body"]
                            if sub["first_name"]:
                                body = body.replace("{{first_name}}", sub["first_name"])
                            
                            # Send via Resend
                            resend.Emails.send({
                                "from": os.getenv("RESEND_FROM_EMAIL", "noreply@earnetics.live"),
                                "to": sub["email"],
                                "subject": campaign["subject"],
                                "html": body
                            })
                            
                            # Log success
                            cur.execute("""
                                INSERT INTO mailops_events (campaign_id, subscriber_email, event_type, timestamp)
                                VALUES (?, ?, 'sent', ?)
                            """, (campaign_id, sub["email"], _utcnow()))
                            sent_count += 1
                            
                        except Exception as e:
                            # Log failure
                            cur.execute("""
                                INSERT INTO mailops_events (campaign_id, subscriber_email, event_type, timestamp, metadata)
                                VALUES (?, ?, 'failed', ?, ?)
                            """, (campaign_id, sub["email"], _utcnow(), json.dumps({"error": str(e)})))
                            failed_count += 1
                            
                except ImportError:
                    log_event("mailops_error", campaign_id=campaign_id, error="resend package not installed")
                    raise RuntimeError("Resend package not installed. Run: pip install resend")
                    
            else:
                # Simulated sending (for testing without Resend)
                log_event("mailops_simulated_send", campaign_id=campaign_id, message="RESEND_API_KEY not set, simulating send")
                for sub in subscribers:
                    cur.execute("""
                        INSERT INTO mailops_events (campaign_id, subscriber_email, event_type, timestamp)
                        VALUES (?, ?, 'sent', ?)
                    """, (campaign_id, sub["email"], _utcnow()))
                    sent_count += 1
            
            # Update campaign stats and status
            stats = {"sent": sent_count, "failed": failed_count}
            cur.execute("""
                UPDATE mailops_campaigns 
                SET status = 'completed', stats = ?, updated_at = ? 
                WHERE id = ?
            """, (json.dumps(stats), _utcnow(), campaign_id))
            conn.commit()
            
            log_event("mailops_campaign_sent", campaign_id=campaign_id, sent_count=sent_count, failed_count=failed_count)
            return {"status": "completed", "sent": sent_count, "failed": failed_count}

    def list_campaigns(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM mailops_campaigns ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                d["target_segment"] = json.loads(d["target_segment"] or "{}")
                d["stats"] = json.loads(d["stats"] or "{}")
                results.append(d)
            return results

    def _update_subscriber_status(self, email: str, status: str) -> None:
        """Update subscriber status (for webhook handlers)"""
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE mailops_subscribers 
                SET status = ?, updated_at = ? 
                WHERE email = ?
            """, (status, _utcnow(), email))
            conn.commit()
            log_event("mailops_subscriber_status_updated", email=email, status=status)

