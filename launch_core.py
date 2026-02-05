from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from backend.prime_directive import load_prime_directive

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "command_center_config.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("launch_core")


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing command center config: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def main() -> None:
    directive = load_prime_directive().data
    config = load_config()

    logger.info("Prime Directive loaded: %s", directive.get("version", "unknown"))
    logger.info("System: %s", config.get("system_name", "unknown"))
    logger.info("Modules configured: %s", len(config.get("modules", [])))

    blocked = [m for m in config.get("modules", []) if not m.get("enabled", False)]
    if blocked:
        logger.info("Disabled modules (policy/review): %s", ", ".join(m["id"] for m in blocked))


if __name__ == "__main__":
    main()
