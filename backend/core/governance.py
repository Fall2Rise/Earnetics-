from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set

from backend.core.runtime_mode import RuntimeMode


# Keep this simple and explicit. Add categories as your tool registry grows.
TOOL_CATEGORIES = {
    "READ_ONLY",     # safe: reading metrics, listing products, checking status
    "WRITE_LOCAL",   # file/db writes on local system
    "PUBLISH",       # posting content, publishing pages
    "OUTREACH",      # email/DM outreach
    "PAYMENTS",      # Stripe price changes, payouts, refunds
    "SCRAPE",        # scraping/lead collection
    "EXEC_SYSTEM",   # running shell commands / OS automation
    # Sub-categories for granular control (treated as main categories in policy matching)
    "payments.read",  # Stripe read operations
    "scraping.read",  # Scraping read operations
}


@dataclass(frozen=True)
class GovernancePolicy:
    allowed: Set[str]
    approval_required: Set[str]

    def to_dict(self):
        return {"allowed": sorted(self.allowed), "approval_required": sorted(self.approval_required)}


def build_policies() -> Dict[RuntimeMode, GovernancePolicy]:
    # SAFE_AUTONOMY: agents run, but high-risk stuff requires human approval.
    safe_allowed = set(TOOL_CATEGORIES)
    # READ_ONLY and read sub-categories are safe, everything else requires approval
    safe_approval = {"PUBLISH", "OUTREACH", "PAYMENTS", "EXEC_SYSTEM", "SCRAPE", "WRITE_LOCAL"}  # tune this as you like
    # Note: "payments.read" and "scraping.read" are treated as READ_ONLY (safe)

    # COMMANDER: block autonomous execution entirely (only manual execution allowed).
    # We'll enforce this in the executor via a flag (autonomous=False can bypass).
    commander_allowed = set(TOOL_CATEGORIES)
    commander_approval = set(TOOL_CATEGORIES)  # everything requires approval unless it is manual

    # FULL_AUTONOMY: allow all categories with no approval, but still subject to budgets/rate limits elsewhere.
    full_allowed = set(TOOL_CATEGORIES)
    full_approval = set()

    return {
        RuntimeMode.SAFE_AUTONOMY: GovernancePolicy(allowed=safe_allowed, approval_required=safe_approval),
        RuntimeMode.COMMANDER: GovernancePolicy(allowed=commander_allowed, approval_required=commander_approval),
        RuntimeMode.FULL_AUTONOMY: GovernancePolicy(allowed=full_allowed, approval_required=full_approval),
    }
