from __future__ import annotations

from typing import Any, Dict, List


class SensingHub:
    def __init__(self) -> None:
        self.sensors: List[str] = []

    def register_sensor(self, name: str) -> None:
        if name not in self.sensors:
            self.sensors.append(name)

    def collect(self) -> Dict[str, Any]:
        return {"feeds": self.sensors, "signals": []}
