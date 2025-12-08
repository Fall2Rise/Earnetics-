from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from backend.models.dfy_income_engine import DFYLead

logger = logging.getLogger(__name__)

# This is your actual Systeme.io affiliate link so R&D can use it *when appropriate*,
# not as a blind default for every lead.
SYSTEME_AFFILIATE_LINK = (
    "https://systeme.io/?sa=sa02351153559aaf6b8c64e0a6e1358fa4dafb2e87"
)


# ---------------------------------------------------------------------------
# Data models for R&D output
# ---------------------------------------------------------------------------


@dataclass
class AffiliateResearchBrief:
    """
    High-level plan the R&D department follows for a specific DFY lead.
    This does NOT hit the internet – it tells your agents *what to research*.
    """

    lead_id: str
    segment: str
    primary_goal: str
    search_queries: List[str]
    networks_to_check: List[str]
    constraints: List[str]
    notes_for_agent: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AffiliateOfferCandidate:
    """
    A concrete offer candidate the R&D team can push.
    Some fields may be placeholders until a human/agent fills in the exact offer.
    """

    id: str
    label: str
    url: str
    network: str
    reason: str
    expected_commission_model: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(text: Optional[str]) -> str:
    if not text:
        return ""
    return str(text).strip().lower()


def _detect_segment(lead: DFYLead) -> str:
    """
    Very simple segment routing based on niche + goal.
    This decides which R&D playbook we use.
    """
    niche = _normalize(lead.niche)
    goal = _normalize(lead.goal)
    offer_type = _normalize(lead.offer_type)

    # Coaches / courses / education
    if any(k in niche for k in ["coach", "course", "program", "education", "online business"]):
        return "coaches_courses"

    # Local home services
    if any(
        k in niche
        for k in [
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
        ]
    ):
        return "local_services"

    # Explicit “data / list / intel” deals
    if any(k in offer_type for k in ["data", "dataset", "list", "intel", "research"]):
        return "b2b_data_asset"
    if "data asset" in goal or "sell list" in goal:
        return "b2b_data_asset"

    # Fallback: generic affiliate / MMO space
    if "affiliate" in offer_type or "commission" in goal or "passive income" in goal:
        return "generic_affiliate"

    return "generic_affiliate"


# ---------------------------------------------------------------------------
# R&D research briefs
# ---------------------------------------------------------------------------


def build_affiliate_research_brief(lead: DFYLead) -> Dict[str, Any]:
    """
    Main entrypoint: generate a research brief for the R&D department so
    they know *exactly* what to go investigate for this lead.

    This does NOT perform any HTTP requests – it just outputs a structured plan.
    """
    segment = _detect_segment(lead)
    goal = lead.goal or "Grow monthly income with a DFY engine."

    base_networks = [
        "Impact",
        "PartnerStack",
        "Digistore24",
        "ClickBank",
        "ShareASale",
        "CJ Affiliate",
    ]

    search_queries: List[str] = []
    constraints: List[str] = [
        "Recurring or high-ticket commissions preferred",
        "Reputable vendor and low refund rate",
        "No scammy, hype-only offers",
        "Geo allowed: US + major English-speaking countries at minimum",
    ]
    notes_for_agent: str

    if segment == "coaches_courses":
        search_queries = [
            "high ticket recurring affiliate offers for online course platforms",
            "affiliate programs for digital course creators and coaches recurring commissions",
            "evergreen funnel builders affiliate program with lifetime revenue share",
        ]
        networks = base_networks + ["Systeme.io (direct partner portal)", "ThriveCart", "Kajabi affiliates"]
        notes_for_agent = (
            "Lead appears to be in the coaches / courses / education lane.\n"
            "- Prioritise 30–40%+ recurring or lifetime revenue share offers.\n"
            "- Look for tools that *directly* help coaches/course creators (funnel, CRM, email, community, etc.).\n"
            "- Build a short-list of 3–5 offers, then pick 1–2 as the primary engine."
        )
    elif segment == "local_services":
        search_queries = [
            "affiliate programs that pay per qualified home service lead (HVAC, roofing, plumbing, contractor)",
            "lead marketplace or pay per call networks for local home services",
            "home services SaaS / CRM with affiliate commissions for agencies and marketers",
        ]
        networks = base_networks + ["Everflow", "RingPartner", "HomeAdvisor / Angi B2B channels"]
        notes_for_agent = (
            "Lead looks like a local home-services or similar real-world business.\n"
            "- Focus on pay-per-lead, pay-per-call, or flat monthly referral retainers.\n"
            "- Check compliance and geographic restrictions carefully.\n"
            "- Target 3–5 partners where we can send consistent local traffic and get paid easily."
        )
    elif segment == "b2b_data_asset":
        search_queries = [
            "b2b data buyers for niche lead lists",
            "private equity funds buying deal flow lead lists",
            "agencies or SaaS tools that pay for exclusive email / prospect datasets",
        ]
        networks = base_networks + ["Private broker networks", "Founder / investor communities"]
        constraints.append("Data must respect all privacy & email regulations (CAN-SPAM, GDPR where relevant).")
        notes_for_agent = (
            "Lead is in a B2B data / list / intel lane.\n"
            "- Clarify niche, region, and buyer persona.\n"
            "- Design a sellable dataset structure (fields, volume, freshness).\n"
            "- Identify 5–10 potential buyers who pay for curated intel, not just scraped lists."
        )
    else:  # generic_affiliate
        search_queries = [
            "high paying evergreen affiliate programs recurring commissions",
            "software affiliate programs with lifetime revenue share",
            "AI tools and automation platforms affiliate programs with tiered commissions",
        ]
        networks = base_networks + ["Direct SaaS partner programs"]
        notes_for_agent = (
            "Generic affiliate / income-engine context.\n"
            "- Hunt for evergreen SaaS tools and AI platforms tied to the lead's niche (if any).\n"
            "- Prefer recurring + sticky tools (email, funnels, CRM, AI automation, hosting, etc.).\n"
            "- Prepare 3–7 strong candidates with clear EPC / average commission data."
        )

    brief = AffiliateResearchBrief(
        lead_id=lead.id,
        segment=segment,
        primary_goal=goal,
        search_queries=search_queries,
        networks_to_check=networks,
        constraints=constraints,
        notes_for_agent=notes_for_agent,
    )

    logger.info(
        "R&D: built affiliate research brief for lead %s (segment=%s)",
        lead.id,
        segment,
    )

    return brief.to_dict()


# ---------------------------------------------------------------------------
# Initial offer candidates
# ---------------------------------------------------------------------------


def generate_initial_offer_candidates(lead: DFYLead) -> List[Dict[str, Any]]:
    """
    Return a *short-list* of starting offers the DFY engine can attach to the lead.

    These are suggestions for the R&D + execution crews:
      - Some are concrete (e.g. your Systeme.io link).
      - Some are placeholders that the R&D team must fill in with a specific program.

    Nothing here calls external APIs. It's a planning layer so the rest of Earnetics
    has something concrete to execute against.
    """
    segment = _detect_segment(lead)
    candidates: List[AffiliateOfferCandidate] = []

    # Shared baseline candidate: a generic 'to be decided' slot
    baseline = AffiliateOfferCandidate(
        id="offer-tbd-001",
        label="Primary niche-aligned SaaS / tool (to be selected by R&D)",
        url="",
        network="TBD",
        reason="Placeholder slot for the strongest program found during R&D.",
        expected_commission_model="Prefer 30%+ recurring or substantial lifetime payout.",
        notes=(
            "This slot MUST be filled by the R&D department after running the research brief. "
            "Do not go live with this as empty – it should represent the star of the stack."
        ),
    )
    candidates.append(baseline)

    # Segment-specific suggestions
    if segment == "coaches_courses":
        # 1) Your Systeme.io link – available, but not forced as the only option.
        candidates.append(
            AffiliateOfferCandidate(
                id="offer-systeme-001",
                label="Systeme.io – Funnel + email + automation stack",
                url=SYSTEME_AFFILIATE_LINK,
                network="Systeme.io direct",
                reason=(
                    "All-in-one funnel + email + automation platform ideal for coaches/courses. "
                    "Pairs naturally with DFY lead-capture funnels."
                ),
                expected_commission_model="Recurring revenue share on subscription payments.",
                notes=(
                    "Use this when the lead *does not* already have a strong funnel/email stack, "
                    "or where migration is easy. R&D should still compare against other tools "
                    "before locking it in as the main engine."
                ),
            )
        )

        # 2) Placeholder for a 'course platform tool'
        candidates.append(
            AffiliateOfferCandidate(
                id="offer-course-tool-001",
                label="Course / coaching platform or scheduling tool (TBD)",
                url="",
                network="TBD",
                reason="Support the client's existing program delivery (course host, scheduler, etc.).",
                expected_commission_model="Recurring or flat bounty per activated account.",
                notes="R&D: fill this with the best-fit tool from the research brief outputs.",
            )
        )

    elif segment == "local_services":
        candidates.append(
            AffiliateOfferCandidate(
                id="offer-local-lead-001",
                label="Pay-per-lead / pay-per-call network (TBD)",
                url="",
                network="Lead marketplace (e.g. PPL network)",
                reason="Monetise qualified home-service leads the engine generates.",
                expected_commission_model="Per lead or per booked call; sometimes rev-share.",
                notes="R&D: pick a reputable network that covers the lead's region & service type.",
            )
        )

        candidates.append(
            AffiliateOfferCandidate(
                id="offer-local-saas-001",
                label="Local services CRM / scheduling SaaS (TBD)",
                url="",
                network="SaaS affiliate program",
                reason="Sticky, recurring SaaS that local businesses need to run jobs.",
                expected_commission_model="Recurring % of subscription.",
                notes="R&D: Look for tools frequently used by contractors (job scheduling, quoting, etc.).",
            )
        )

    elif segment == "b2b_data_asset":
        candidates.append(
            AffiliateOfferCandidate(
                id="offer-data-broker-001",
                label="Data / list buyer or broker (TBD)",
                url="",
                network="Private buyers / broker network",
                reason="Turn curated datasets into up-front lump-sum or rev-share deals.",
                expected_commission_model="Flat purchase price, revenue share, or retainers.",
                notes=(
                    "R&D: Identify a small set of buyers who already purchase lists or lead intel. "
                    "This candidate represents the primary buyer profile."
                ),
            )
        )

    else:  # generic_affiliate
        candidates.append(
            AffiliateOfferCandidate(
                id="offer-generic-saas-001",
                label="Evergreen SaaS in the lead's niche (TBD)",
                url="",
                network="SaaS affiliate/partner program",
                reason="Recurring commissions from a tool tied directly to the niche/problem.",
                expected_commission_model="Monthly recurring % or lifetime revenue share.",
                notes="R&D: Match this to the niche and pain the lead described.",
            )
        )

        candidates.append(
            AffiliateOfferCandidate(
                id="offer-ai-tool-001",
                label="AI automation / productivity tool (TBD)",
                url="",
                network="AI tool partner program",
                reason="Leverage current demand for AI tools as part of the stack.",
                expected_commission_model="Recurring or high one-time bounty.",
                notes="R&D: find a legit AI tool with stable payouts and real usage.",
            )
        )

    logger.info(
        "R&D: generated %d initial offer candidates for lead %s (segment=%s)",
        len(candidates),
        lead.id,
        segment,
    )

    return [c.to_dict() for c in candidates]
