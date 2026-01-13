import json
import logging
from typing import Dict, Any, List
from backend.system_state import global_state
from backend.audit_log import log_event

logger = logging.getLogger(__name__)

class PrimeDirectiveGuardian:
    def __init__(self, directive_path: str = "prime_directive.json"):
        self.directive_path = directive_path
        self.directive = self._load_directive()
        self.kill_switch_active = False

    def _load_directive(self) -> Dict[str, Any]:
        try:
            with open(self.directive_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load prime directive: {e}")
            return {}

    def validate_action(self, agent_name: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an agent's proposed action against the prime directive.
        """
        if self.kill_switch_active:
            return {"approved": False, "reason": "Emergency Kill Switch Active"}

        # Check non-negotiables
        non_negotiables = self.directive.get("non_negotiables", {})
        
        # Example: Anti-harm check
        if "harm" in action.lower() or "family" in context.get("risks", []):
            if non_negotiables.get("anti_harm_family"):
                log_event("guardian_violation", agent=agent_name, action=action, context="VIOLATION: Potential harm detected")
                return {"approved": False, "reason": "Violation of Anti-Harm Non-Negotiable"}

        # Check risk tiers
        risk_tiers = self.directive.get("risk_governance", {}).get("tiers", {})
        # Simple heuristic for risk classification
        risk_level = "GREEN"
        if "delete" in action.lower() or "transfer" in action.lower():
            risk_level = "RED"
        elif "modify" in action.lower():
            risk_level = "YELLOW"

        if risk_level == "RED":
            # In a real system, this would trigger a cryptographic approval request
            return {"approved": False, "reason": "RED Tier action requires cryptographic human approval"}

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
