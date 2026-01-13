from __future__ import annotations

import json
import os
import smtplib
from dataclasses import dataclass, asdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.audit_log import log_event
from backend.credentials_store import get_secret

def _normalize_env_path(env_value: Optional[str], default: str) -> Path:
    """Normalize path from environment variable, converting backslashes to forward slashes."""
    if not env_value:
        return Path(default)
    return Path(env_value.replace("\\", "/"))

SETTINGS_PATH = _normalize_env_path(os.getenv("NOTIFICATION_SETTINGS_PATH"), "notification_settings.json")


@dataclass
class NotificationSettings:
    email_enabled: bool = False
    email_recipients: List[str] = None  # type: ignore[assignment]
    desktop_log: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if result["email_recipients"] is None:
            result["email_recipients"] = []
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationSettings":
        return cls(
            email_enabled=bool(data.get("email_enabled")),
            email_recipients=list(data.get("email_recipients", [])),
            desktop_log=bool(data.get("desktop_log", True)),
        )


class NotificationService:
    def __init__(self, settings_path: Path = SETTINGS_PATH):
        self.settings_path = settings_path
        self.settings = self._load_settings()

    def _load_settings(self) -> NotificationSettings:
        if self.settings_path.exists():
            try:
                data = json.loads(self.settings_path.read_text())
                return NotificationSettings.from_dict(data)
            except Exception:  # pragma: no cover - defensive
                pass
        return NotificationSettings(email_enabled=False, email_recipients=[], desktop_log=True)

    def save_settings(self, settings: NotificationSettings) -> NotificationSettings:
        self.settings = settings
        self.settings_path.write_text(json.dumps(settings.to_dict(), indent=2))
        log_event("notifications.settings_updated")
        return self.settings

    def get_settings(self) -> NotificationSettings:
        return self.settings

    def send_notification(self, subject: str, message: str) -> None:
        if self.settings.desktop_log:
            print(f"[NOTIFY] {subject}: {message}")
        if self.settings.email_enabled and self.settings.email_recipients:
            self._send_email(subject, message)

    def _send_email(self, subject: str, message: str) -> None:
        smtp_server = get_secret("SMTP_SERVER", default="smtp.gmail.com")
        smtp_port = int(get_secret("SMTP_PORT", default="587") or 587)
        smtp_email = get_secret("SMTP_EMAIL")
        smtp_password = get_secret("SMTP_PASSWORD")
        if not smtp_email or not smtp_password:
            log_event("notifications.email_not_configured")
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                for recipient in self.settings.email_recipients:
                    msg["To"] = recipient
                    server.send_message(msg)
        except Exception as exc:  # pragma: no cover - defensive
            log_event("notifications.email_failed", log_message=str(exc))


notification_service = NotificationService()
