import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path("config/wealth_covenant.json")


class WealthCovenant:
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.path = config_path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError("wealth covenant config not found")
        return json.loads(self.path.read_text())

    @property
    def config(self) -> Dict[str, Any]:
        return self._data

    def constraints(self) -> Dict[str, Any]:
        return {
            "legal": self._data.get("legal_constraints", {}),
            "capital": self._data.get("capital_limits", {}),
            "risk": self._data.get("risk_profile", {}),
        }
