from __future__ import annotations

from typing import Any, Dict

from .wealth_covenant import WealthCovenant


class RiskGuard:
    def __init__(self, covenant: WealthCovenant) -> None:
        self.covenant = covenant

    def validate_play(self, play: Dict[str, Any]) -> Dict[str, Any]:
        constraints = self.covenant.constraints()
        capital_limits = constraints.get("capital", {})
        budget = play.get("budget", {}).get("max_allocation_usd", 0)
        if budget and capital_limits.get("max_single_bet_usd") and budget > capital_limits["max_single_bet_usd"]:
            return {
                "approved": False,
                "reason": "Budget exceeds covenant max_single_bet_usd",
            }
        legal = constraints.get("legal", {})
        prohibited_tags = [
            "sanctioned_jurisdiction",
            "tax_evasion",
            "money_laundering",
            "fraud",
        ]
        for tag in play.get("tags", []):
            if tag in prohibited_tags:
                return {"approved": False, "reason": f"Prohibited tag {tag}"}
        return {"approved": True}
