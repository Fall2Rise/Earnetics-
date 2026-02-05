# backend/tools/tool_registry.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


ToolHandler = Callable[[Dict[str, Any]], Any]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    category: str
    handler: ToolHandler
    description: str = ""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list(self) -> Dict[str, ToolSpec]:
        return dict(self._tools)

    def count(self) -> int:
        return len(self._tools)
