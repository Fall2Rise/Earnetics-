from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

PERMISSION_STORE = Path(os.getenv('PERMISSION_STORE_PATH', 'permission_store.json'))


@dataclass
class PermissionEntry:
    subject: str  # agent or plugin name
    scope: str
    granted: bool


class PermissionManager:
    def __init__(self, store: Path = PERMISSION_STORE):
        self.store = store
        self.permissions: Dict[str, List[PermissionEntry]] = {}
        self._load()

    def _load(self) -> None:
        if self.store.exists():
            data = json.loads(self.store.read_text())
            self.permissions = {
                subject: [PermissionEntry(**entry) for entry in entries]
                for subject, entries in data.items()
            }

    def _save(self) -> None:
        data = {
            subject: [asdict(entry) for entry in entries]
            for subject, entries in self.permissions.items()
        }
        self.store.write_text(json.dumps(data, indent=2))

    def list_permissions(self, subject: str) -> List[PermissionEntry]:
        return list(self.permissions.get(subject, []))

    def set_permission(self, subject: str, scope: str, granted: bool) -> None:
        entries = self.permissions.setdefault(subject, [])
        for entry in entries:
            if entry.scope == scope:
                entry.granted = granted
                break
        else:
            entries.append(PermissionEntry(subject=subject, scope=scope, granted=granted))
        self._save()

    def revoke_subject(self, subject: str) -> None:
        if subject in self.permissions:
            del self.permissions[subject]
            self._save()


permission_manager = PermissionManager()
