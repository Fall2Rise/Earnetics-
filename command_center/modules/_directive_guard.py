from __future__ import annotations

from typing import Any, Dict

from backend.prime_directive import load_prime_directive
from backend.prime_directive_guardian import guardian


def prime_directive_snapshot() -> Dict[str, Any]:
    """Read-only directive snapshot for module guards."""
    return load_prime_directive().data


def enforce_directive(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an action against the Prime Directive."""
    return guardian.validate_action("command_center_module", action, context)
