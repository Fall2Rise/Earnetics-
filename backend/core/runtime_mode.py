from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class RuntimeMode(str, Enum):
    SAFE_AUTONOMY = "SAFE_AUTONOMY"   # Option 1 (default)
    COMMANDER = "COMMANDER"           # Option 3 in your earlier naming
    FULL_AUTONOMY = "FULL_AUTONOMY"   # Option 2 in your earlier naming


@dataclass
class ModeState:
    mode: RuntimeMode
    changed_by: str = "system"
    reason: str = ""


class ModeManager:
    """
    Thread-safe mode manager with simple JSON persistence.
    """
    def __init__(self, data_dir: str = "backend/data", filename: str = "runtime_mode.json"):
        self._lock = threading.RLock()
        self._data_path = Path(data_dir) / filename
        self._data_path.parent.mkdir(parents=True, exist_ok=True)

        # default mode
        env_mode = os.getenv("EARNETICS_MODE", "").strip().upper()
        default = RuntimeMode.SAFE_AUTONOMY
        if env_mode in RuntimeMode.__members__:
            default = RuntimeMode[env_mode]

        self._state = ModeState(mode=default)
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        if not self._data_path.exists():
            self._persist()
            return
        try:
            payload = json.loads(self._data_path.read_text(encoding="utf-8"))
            mode_str = str(payload.get("mode", RuntimeMode.SAFE_AUTONOMY.value)).upper()
            mode = RuntimeMode(mode_str) if mode_str in RuntimeMode._value2member_map_ else RuntimeMode.SAFE_AUTONOMY
            self._state = ModeState(
                mode=mode,
                changed_by=str(payload.get("changed_by", "system")),
                reason=str(payload.get("reason", "")),
            )
        except Exception:
            # If corrupted, reset safely
            self._state = ModeState(mode=RuntimeMode.SAFE_AUTONOMY, changed_by="system", reason="reset_corrupt_file")
            self._persist()

    def _persist(self) -> None:
        payload = {"mode": self._state.mode.value, "changed_by": self._state.changed_by, "reason": self._state.reason}
        self._data_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self) -> ModeState:
        with self._lock:
            return ModeState(mode=self._state.mode, changed_by=self._state.changed_by, reason=self._state.reason)

    def set(self, mode: RuntimeMode, changed_by: str, reason: str = "") -> ModeState:
        with self._lock:
            self._state = ModeState(mode=mode, changed_by=changed_by, reason=reason)
            self._persist()
            return self.get()
