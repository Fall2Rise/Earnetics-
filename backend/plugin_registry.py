from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

PLUGIN_STORE = Path(os.getenv('PLUGIN_REGISTRY_PATH', 'plugin_registry.json'))
PLUGINS_DIR = Path(os.getenv('PLUGIN_DIRECTORY', 'plugins'))
PLUGINS_DIR.mkdir(exist_ok=True)


@dataclass
class PluginEntry:
    name: str
    version: str
    description: str
    repository: Optional[str] = None
    entrypoint: Optional[str] = None
    active: bool = False


class PluginRegistry:
    def __init__(self, store: Path = PLUGIN_STORE):
        self.store = store
        self.plugins: Dict[str, PluginEntry] = {}
        self._load()

    def _load(self) -> None:
        if self.store.exists():
            data = json.loads(self.store.read_text())
            self.plugins = {name: PluginEntry(**entry) for name, entry in data.items()}

    def _save(self) -> None:
        data = {name: asdict(entry) for name, entry in self.plugins.items()}
        self.store.write_text(json.dumps(data, indent=2))

    def list_plugins(self) -> List[PluginEntry]:
        return list(self.plugins.values())

    def register_plugin(self, entry: PluginEntry) -> None:
        self.plugins[entry.name] = entry
        self._save()

    def activate_plugin(self, name: str) -> PluginEntry:
        entry = self.plugins.get(name)
        if not entry:
            raise ValueError('Plugin not found')
        for plugin in self.plugins.values():
            if plugin.name == name:
                plugin.active = True
            elif plugin.entrypoint == entry.entrypoint:
                plugin.active = False
        self._save()
        return entry

    def deactivate_plugin(self, name: str) -> PluginEntry:
        entry = self.plugins.get(name)
        if not entry:
            raise ValueError('Plugin not found')
        entry.active = False
        self._save()
        return entry


plugin_registry = PluginRegistry()
