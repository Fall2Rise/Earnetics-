import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from backend.system_state import global_state
from backend.audit_log import log_event
from backend.prime_directive import load_prime_directive

logger = logging.getLogger(__name__)

class PrimeDirectiveGuardian:
    def __init__(self, directive_path: str = "prime_directive.json"):
        self.directive_path = directive_path
        self.directive = self._load_directive()
        self._directive_mtime: Optional[float] = self._get_directive_mtime()
        self.kill_switch_active = False

    def _get_directive_mtime(self) -> Optional[float]:
        try:
            return Path(self.directive_path).stat().st_mtime
        except Exception:
            return None

    def _load_directive(self) -> Dict[str, Any]:
        try:
            return load_prime_directive(self.directive_path).data
        except Exception as e:
            logger.error(f"Failed to load prime directive: {e}")
            return {}

    def _refresh_if_needed(self) -> None:
        current_mtime = self._get_directive_mtime()
        if current_mtime and self._directive_mtime != current_mtime:
            self.directive = self._load_directive()
            self._directive_mtime = current_mtime

    def _risk_level(self, action: str, context: Dict[str, Any]) -> str:
        explicit = context.get("risk_level")
        if isinstance(explicit, str) and explicit:
            return explicit.upper()
        action_lower = action.lower()
        if any(term in action_lower for term in ["delete", "transfer", "exfiltrate", "override"]):
            return "RED"
        if any(term in action_lower for term in ["modify", "rotate", "pause", "disable"]):
            return "YELLOW"
        return "GREEN"

    def _context_flag(self, context: Dict[str, Any], *keys: str) -> bool:
        return any(bool(context.get(key)) for key in keys)

    def _deny(self, agent_name: str, action: str, reason: str, context: Dict[str, Any]) -> Dict[str, Any]:
        log_event(
            "guardian_violation",
            agent=agent_name,
            action=action,
            context={"reason": reason, "context": context, "timestamp": datetime.utcnow().isoformat()},
        )
        return {"approved": False, "reason": reason}

    def validate_action(self, agent_name: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an agent's proposed action against the prime directive.
        """
        self._refresh_if_needed()
        if self.kill_switch_active:
            logger.warning("Guardian: Action blocked by Kill Switch")
            return {"approved": False, "reason": "Emergency Kill Switch Active"}

        if not self.directive:
            logger.error("Guardian: Prime Directive unavailable (load failed or empty)")
            return {"approved": False, "reason": "Prime Directive unavailable"}

        non_negotiables = self.directive.get("non_negotiables", {})
        risks = context.get("risks", [])
        risk_level = self._risk_level(action, context)

        if non_negotiables.get("protect_human_life") and self._context_flag(context, "harm", "violence"):
            return self._deny(agent_name, action, "Violation: protect_human_life", context)
        if non_negotiables.get("protect_owner_and_family") and ("family" in risks or self._context_flag(context, "family_risk")):
            return self._deny(agent_name, action, "Violation: protect_owner_and_family", context)
        if non_negotiables.get("respect_lawful_boundaries") and self._context_flag(context, "illegal", "unlawful"):
            return self._deny(agent_name, action, "Violation: respect_lawful_boundaries", context)
        if non_negotiables.get("avoid_deception_or_manipulation") and self._context_flag(context, "deception", "manipulation"):
            return self._deny(agent_name, action, "Violation: avoid_deception_or_manipulation", context)
        if non_negotiables.get("maintain_transparency_with_owner") and self._context_flag(context, "covert", "hidden"):
            return self._deny(agent_name, action, "Violation: maintain_transparency_with_owner", context)
        if non_negotiables.get("halt_if_alignment_uncertain") and self._context_flag(context, "alignment_uncertain"):
            return self._deny(agent_name, action, "Alignment uncertain — halting", context)

        access_control = self.directive.get("access_control", {})
        if access_control.get("duplication_prohibited") and self._context_flag(context, "duplicate", "replicate"):
            return self._deny(agent_name, action, "Violation: duplication_prohibited", context)
        if access_control.get("external_use_prohibited") and self._context_flag(context, "external_use", "third_party"):
            return self._deny(agent_name, action, "Violation: external_use_prohibited", context)
        if access_control.get("public_distribution_denied") and self._context_flag(context, "public_distribution", "publish"):
            return self._deny(agent_name, action, "Violation: public_distribution_denied", context)

        # Risk governance: require explicit approval for higher tiers.
        if risk_level == "YELLOW" and not self._context_flag(context, "owner_approved"):
            return {"approved": False, "reason": "YELLOW risk requires owner confirmation", "risk_level": risk_level}
        if risk_level == "RED" and not self._context_flag(context, "cryptographic_approval"):
            return {"approved": False, "reason": "RED risk requires cryptographic approval", "risk_level": risk_level}

        return {"approved": True, "risk_level": risk_level}

    def activate_kill_switch(self):
        """Halts all autonomous operations."""
        self.kill_switch_active = True
        global_state["AGENT_EXECUTION_PAUSED"] = True
        global_state["MAIL_SENDING_PAUSED"] = True
        log_event("kill_switch", agent="SYSTEM", action="ACTIVATE", context="Emergency Kill Switch Engaged")
        logger.warning("EMERGENCY KILL SWITCH ACTIVATED")

    def deactivate_kill_switch(self):
        """Resumes autonomous operations."""
        self.kill_switch_active = False
        global_state["AGENT_EXECUTION_PAUSED"] = False
        global_state["MAIL_SENDING_PAUSED"] = False
        log_event("kill_switch", agent="SYSTEM", action="DEACTIVATE", context="Emergency Kill Switch Disengaged")
        logger.info("Emergency Kill Switch Deactivated")

guardian = PrimeDirectiveGuardian()
