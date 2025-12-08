from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import logging

from backend.models.dfy_income_engine import DFYLead, dfy_leads_store

# ---------------------------------------------------------------------------
# Logging setup for this module
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
if not logger.handlers:
    # Let the main app configure logging globally; this is a safe fallback.
    logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# DFY PLAYBOOK DEFINITIONS (INLINE VERSION)
# ---------------------------------------------------------------------------

DFY_PLAYBOOKS: List[Dict[str, Any]] = [
    {
        "id": "earn-dfy-playbook-001",
        "name": "DFY Affiliate Engine – Coaches & Course Creators",
        "segment": "coaches_courses",
        "owning_department": "affiliate_stack",
        "trigger_keywords": {
            "offer_type": [
                "affiliate",
                "dfy affiliate",
                "dfy income",
                "dfy funnel",
                "dfy affiliate engine",
            ],
            "niche": [
                "coach",
                "coaching",
                "course",
                "courses",
                "program",
                "education",
                "self build digital",
                "sbd",
                "hustleplug",
                "online business",
            ],
            "goal": [
                "5k",
                "10k",
                "course sales",
                "client",
                "clients",
                "high ticket",
            ],
        },
        "first_moves": [
            "Build a 1-page lead capture funnel with one clear promise aimed at the ideal learner/client.",
            "Create a 5–9 email nurture + affiliate onboarding sequence connected to the funnel.",
            "Launch a 30-day traffic plan focused on one primary channel (shortform or email JV) and simple tracking.",
        ],
        "headline_promise": (
            "We install a DFY affiliate engine around your existing course/offer, "
            "with a clear 90-day traffic and launch plan."
        ),
    },
    {
        "id": "earn-dfy-playbook-002",
        "name": "DFY Local Lead Gen Machine – Home Services",
        "segment": "local_services",
        "owning_department": "affiliate_stack",
        "trigger_keywords": {
            "offer_type": [
                "lead gen",
                "local",
                "appointments",
                "booked calls",
                "home services",
            ],
            "niche": [
                "plumber",
                "plumbing",
                "hvac",
                "roof",
                "roofer",
                "roofing",
                "remodel",
                "contractor",
                "landscaping",
                "electrician",
                "cleaning",
            ],
            "goal": [
                "leads",
                "booked",
                "appointments",
                "calls",
                "jobs",
            ],
        },
        "first_moves": [
            "Define service type, radius, and minimum job value so the lead machine only attracts profitable jobs.",
            "Deploy a simple local lander (call + form) with clear proof and one main call-to-action.",
            "Set up one primary ad channel (Google LSA/Search or FB/IG) and a weekly reporting loop on leads and booked jobs.",
        ],
        "headline_promise": (
            "We turn on a DFY local lead machine that feeds your crew with qualified calls and form leads."
        ),
    },
    {
        "id": "earn-dfy-playbook-003",
        "name": "DFY Data Asset Sale – B2B Packaged List",
        "segment": "b2b_data_asset",
        "owning_department": "data_intelligence_monetization",
        "trigger_keywords": {
            "offer_type": [
                "data",
                "dataset",
                "list",
                "lead list",
                "intel",
                "research",
            ],
            "niche": [
                "b2b",
                "agency",
                "saas",
                "investor",
                "private equity",
            ],
            "goal": [
                "sell data",
                "sell list",
                "lump sum",
                "data asset",
                "package",
            ],
        },
        "first_moves": [
            "Lock in the niche, region, and ideal buyer profile for the dataset (who will pay the most for this intel).",
            "Design the dataset structure (fields, sources, compliance boundaries) and outline the scraping/enrichment pipeline.",
            "Package the asset as a clean CSV + one-page PDF, and define a simple outreach script to sell it to a small set of buyers.",
        ],
        "headline_promise": (
            "We build a proprietary, cleaned dataset in your niche that you can plug directly into your outreach or sell as an asset."
        ),
    },
]


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _normalize(text: Optional[str]) -> str:
    if not text:
        return ""
    return str(text).strip().lower()


def _compute_match_score(lead: DFYLead, playbook: Dict[str, Any]) -> int:
    """
    Basic scoring: count keyword hits across offer_type, niche, goal.
    The playbook with the highest score wins.
    """
    offer_type = _normalize(lead.offer_type)
    niche = _normalize(lead.niche)
    goal = _normalize(lead.goal)

    triggers = playbook.get("trigger_keywords", {})
    score = 0

    # Offer type is strongest signal
    for kw in triggers.get("offer_type", []):
        if kw in offer_type:
            score += 3

    # Niche is next strongest
    for kw in triggers.get("niche", []):
        if kw in niche:
            score += 2

    # Goals are lighter signals
    for kw in triggers.get("goal", []):
        if kw in goal:
            score += 1

    # Small bias for affiliate-style offers into the affiliate stack playbook
    if "affiliate" in offer_type and playbook.get("segment") == "coaches_courses":
        score += 2

    return score


def _select_playbook_for_lead(lead: DFYLead) -> Dict[str, Any]:
    """
    Pick the best matching DFY playbook for a lead.
    If nothing matches, default to the first playbook.
    """
    best_playbook: Optional[Dict[str, Any]] = None
    best_score = -1

    for pb in DFY_PLAYBOOKS:
        score = _compute_match_score(lead, pb)
        if score > best_score:
            best_score = score
            best_playbook = pb

    if not best_playbook:
        best_playbook = DFY_PLAYBOOKS[0]

    return best_playbook


def _build_strategy_summary(lead: DFYLead, playbook: Dict[str, Any]) -> str:
    """
    Build the strategy_summary text that gets stored on the lead.
    This is what you saw in the JSON response.
    """
    name = lead.name or "this client"
    offer_type = lead.offer_type or "offer"
    niche = lead.niche or "unspecified"
    goal = lead.goal or "not specified"

    owning_department = playbook.get("owning_department", "affiliate_stack")
    headline = (playbook.get("headline_promise") or "").strip()
    first_moves: List[str] = playbook.get("first_moves", []) or []

    lines: List[str] = []

    lines.append(f"DFY Strategy for {name} ({offer_type})")
    lines.append("")

    if headline:
        lines.append(headline)
        lines.append("")

    lines.append(f"- Owning department: {owning_department}")
    lines.append(f"- Niche: {niche}")
    lines.append(f"- Goal: {goal}")
    lines.append("")
    lines.append("First 3 moves:")

    if first_moves:
        for idx, move in enumerate(first_moves, start=1):
            lines.append(f"{idx}) {move}")
    else:
        # Generic fallback if no explicit moves
        lines.append("1) Build a 1-page lead capture funnel with one clear promise.")
        lines.append("2) Generate a short follow-up sequence (email/DM) tied to that promise.")
        lines.append("3) Deploy one primary traffic loop and track the core KPIs for 30 days.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PUBLIC ENTRYPOINT – CORE DFY ENGINE
# ---------------------------------------------------------------------------

def process_new_dfy_leads() -> List[DFYLead]:
    """
    Core DFY Income Engine loop.

    - Looks for leads with a 'new'-ish status.
    - Selects the best playbook.
    - Writes strategy_summary, owning_department, status, timestamps, error.
    - Updates dfy_leads_store in-place.

    This is called from:
      - /api/dashboard/dfy/leads/{lead_id}/process
      - Or any background/autonomy loop that wants to hydrate new DFY leads.
    """
    processed: List[DFYLead] = []

    if not dfy_leads_store:
        logger.info("DFY Income Engine: no leads in store yet.")
        return processed

    now = datetime.utcnow()

    for lead_id, lead in list(dfy_leads_store.items()):
        try:
            status = _normalize(lead.status)
        except Exception:
            status = ""

        # Only touch leads that are fresh / flagged for processing
        if status not in ("", "new", "pending", "submitted", "draft", "created"):
            continue

        try:
            playbook = _select_playbook_for_lead(lead)
            strategy = _build_strategy_summary(lead, playbook)

            lead.owning_department = playbook.get("owning_department", "affiliate_stack")
            lead.strategy_summary = strategy
            lead.status = "deployed"
            lead.error = None
            lead.updated_at = now

            dfy_leads_store[lead_id] = lead
            processed.append(lead)

            logger.info(
                "DFY Income Engine: processed lead %s with playbook %s",
                lead_id,
                playbook.get("id"),
            )
        except Exception as exc:
            # Keep engine resilient
            logger.exception("DFY Income Engine: error processing lead %s", lead_id)
            try:
                lead.status = "error"
                lead.error = str(exc)
                lead.updated_at = now
                dfy_leads_store[lead_id] = lead
                processed.append(lead)
            except Exception:
                logger.error(
                    "DFY Income Engine: failed to update error state for lead %s",
                    lead_id,
                )

    return processed


# ---------------------------------------------------------------------------
# BACKGROUND WORKER ENTRYPOINT
# ---------------------------------------------------------------------------

def start_dfy_worker() -> None:
    """
    Simple worker entrypoint used by main_server.

    Right now it just runs a single pass of process_new_dfy_leads()
    and logs the outcome. Later we can turn this into a loop or
    a scheduled job if needed.
    """
    try:
        logger.info("DFY worker starting (single pass).")
        processed = process_new_dfy_leads()
        logger.info("DFY worker finished. Processed %d leads.", len(processed))
    except Exception:
        logger.exception("DFY worker crashed.")
