from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

MODEL_REGISTRY_PATH = Path(os.getenv("MODEL_REGISTRY_PATH", "model_registry.json"))


@dataclass
class ModelEntry:
    name: str
    family: str
    version: str
    local_path: Optional[str] = None
    active: bool = False


class ModelRegistry:
    def __init__(self, path: Path = MODEL_REGISTRY_PATH):
        self.path = path
        self._models: Dict[str, List[ModelEntry]] = {"embedding": [], "llm": []}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = self.path.read_text()
        except OSError:
            return
        if not raw.strip():
            return
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return
        loaded: Dict[str, List[ModelEntry]] = {}
        for family, entries in data.items():
            if not isinstance(entries, list):
                continue
            loaded_family: List[ModelEntry] = []
            for entry in entries:
                if isinstance(entry, dict):
                    try:
                        loaded_family.append(ModelEntry(**entry))
                    except TypeError:
                        continue
            loaded[family] = loaded_family
        if loaded:
            self._models.update(loaded)

    def _save(self) -> None:
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            family: [asdict(entry) for entry in entries]
            for family, entries in self._models.items()
        }
        self.path.write_text(json.dumps(data, indent=2))

    def list_models(self, family: str) -> List[ModelEntry]:
        return list(self._models.get(family, []))

    def register_model(self, entry: ModelEntry) -> None:
        family_entries = self._models.setdefault(entry.family, [])
        family_entries = [model for model in family_entries if model.name != entry.name]
        family_entries.append(entry)
        self._models[entry.family] = family_entries
        self._save()

    def set_active(self, family: str, name: str) -> None:
        family_entries = self._models.setdefault(family, [])
        found = False
        for model in family_entries:
            if model.name == name:
                model.active = True
                found = True
            else:
                model.active = False
        if not found:
            raise ValueError(f"Model {name} not found in family {family}")
        self._models[family] = family_entries
        self._save()

    def get_active(self, family: str) -> Optional[ModelEntry]:
        for model in self._models.get(family, []):
            if model.active:
                return model
        return None


model_registry = ModelRegistry()
