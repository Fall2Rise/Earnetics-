"""Asset Compounding Engine for Earnetics.

This module converts raw income ideas into wealth-building plays by scoring them
against the universal wealth pattern:

    Wealth = Ownership x Scale x Time

It intentionally avoids preference-based recommendations. The engine ranks
opportunities by durable wealth mechanics: ownership, scalability, automation,
recurring revenue, defensibility, and reinvestment potential.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


class AssetClass(str, Enum):
    """Supported wealth-building asset classes."""

    BUSINESS = "business"
    SOFTWARE = "software"
    MEDIA = "media"
    REAL_ESTATE = "real_estate"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    FINANCIAL_ASSET = "financial_asset"
    ACQUISITION = "acquisition"
    LEAD_GEN = "lead_gen"
    DATA_ASSET = "data_asset"
    SERVICE_TO_ASSET = "service_to_asset"


class WealthStage(str, Enum):
    """Execution stage for a wealth play."""

    CASHFLOW = "cashflow"
    SYSTEMIZE = "systemize"
    OWNERSHIP = "ownership"
    COMPOUND = "compound"


@dataclass(frozen=True)
class WealthWeights:
    """Scoring weights for durable wealth mechanics.

    The weights add to 1.0. They intentionally favor ownership and scale over
    pure short-term cash because the goal is family wealth, not another job.
    """

    ownership: float = 0.22
    scalability: float = 0.18
    automation: float = 0.14
    recurring_revenue: float = 0.14
    margin: float = 0.10
    speed_to_cash: float = 0.08
    defensibility: float = 0.08
    reinvestment_potential: float = 0.06


@dataclass(frozen=True)
class OpportunityInput:
    """Raw opportunity data submitted by an agent, user, or signal collector."""

    name: str
    description: str
    asset_class: AssetClass | str
    startup_cost: float = 0.0
    estimated_monthly_cashflow: float = 0.0
    time_to_first_cash_days: int = 30
    owner_required_hours_per_week: float = 20.0
    ownership_score: float = 0.0
    scalability_score: float = 0.0
    automation_score: float = 0.0
    recurring_revenue_score: float = 0.0
    margin_score: float = 0.0
    defensibility_score: float = 0.0
    reinvestment_score: float = 0.0
    evidence: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WealthPlay:
    """Ranked wealth play produced by the engine."""

    name: str
    description: str
    asset_class: str
    stage: str
    wealth_score: float
    leverage_score: float
    freedom_score: float
    payback_months: Optional[float]
    estimated_monthly_cashflow: float
    startup_cost: float
    time_to_first_cash_days: int
    owner_required_hours_per_week: float
    verdict: str
    allocation_priority: str
    evidence: List[str]
    risks: List[str]
    next_actions: List[str]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _clamp_score(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def _speed_score(days: int) -> float:
    """Convert time-to-cash into a 0-10 score."""

    if days <= 7:
        return 10.0
    if days <= 14:
        return 8.5
    if days <= 30:
        return 7.0
    if days <= 60:
        return 5.0
    if days <= 120:
        return 3.0
    return 1.0


def _payback_months(startup_cost: float, monthly_cashflow: float) -> Optional[float]:
    if startup_cost <= 0 and monthly_cashflow > 0:
        return 0.0
    if monthly_cashflow <= 0:
        return None
    return round(startup_cost / monthly_cashflow, 2)


def _stage_for(play: OpportunityInput, wealth_score: float) -> WealthStage:
    if play.estimated_monthly_cashflow <= 0 or play.time_to_first_cash_days <= 30:
        return WealthStage.CASHFLOW
    if play.owner_required_hours_per_week > 10:
        return WealthStage.SYSTEMIZE
    if wealth_score >= 7.0:
        return WealthStage.OWNERSHIP
    return WealthStage.COMPOUND


def _allocation_priority(score: float, payback: Optional[float]) -> str:
    if score >= 8.0 and (payback is None or payback <= 6):
        return "deploy_capital_and_agents"
    if score >= 6.5:
        return "test_fast"
    if score >= 5.0:
        return "watchlist"
    return "reject_or_rework"


def _verdict(score: float) -> str:
    if score >= 8.0:
        return "High-leverage asset play. Prioritize execution."
    if score >= 6.5:
        return "Promising. Run a controlled validation test."
    if score >= 5.0:
        return "Useful but not yet a strong wealth engine. Improve leverage."
    return "Weak wealth mechanics. Do not chase without redesign."


def score_opportunity(
    opportunity: OpportunityInput,
    weights: WealthWeights | None = None,
) -> WealthPlay:
    """Score a single opportunity against asset-building principles."""

    weights = weights or WealthWeights()
    speed = _speed_score(opportunity.time_to_first_cash_days)

    weighted_score = (
        _clamp_score(opportunity.ownership_score) * weights.ownership
        + _clamp_score(opportunity.scalability_score) * weights.scalability
        + _clamp_score(opportunity.automation_score) * weights.automation
        + _clamp_score(opportunity.recurring_revenue_score) * weights.recurring_revenue
        + _clamp_score(opportunity.margin_score) * weights.margin
        + speed * weights.speed_to_cash
        + _clamp_score(opportunity.defensibility_score) * weights.defensibility
        + _clamp_score(opportunity.reinvestment_score) * weights.reinvestment_potential
    )

    leverage_score = round(
        (
            _clamp_score(opportunity.ownership_score)
            + _clamp_score(opportunity.scalability_score)
            + _clamp_score(opportunity.automation_score)
            + _clamp_score(opportunity.defensibility_score)
        )
        / 4,
        2,
    )
    freedom_score = round(
        (
            _clamp_score(opportunity.automation_score)
            + _clamp_score(opportunity.recurring_revenue_score)
            + max(0.0, 10.0 - min(10.0, opportunity.owner_required_hours_per_week / 4))
        )
        / 3,
        2,
    )
    payback = _payback_months(opportunity.startup_cost, opportunity.estimated_monthly_cashflow)
    wealth_score = round(weighted_score, 2)
    stage = _stage_for(opportunity, wealth_score)

    return WealthPlay(
        name=opportunity.name,
        description=opportunity.description,
        asset_class=str(opportunity.asset_class.value if isinstance(opportunity.asset_class, AssetClass) else opportunity.asset_class),
        stage=stage.value,
        wealth_score=wealth_score,
        leverage_score=leverage_score,
        freedom_score=freedom_score,
        payback_months=payback,
        estimated_monthly_cashflow=float(opportunity.estimated_monthly_cashflow),
        startup_cost=float(opportunity.startup_cost),
        time_to_first_cash_days=int(opportunity.time_to_first_cash_days),
        owner_required_hours_per_week=float(opportunity.owner_required_hours_per_week),
        verdict=_verdict(wealth_score),
        allocation_priority=_allocation_priority(wealth_score, payback),
        evidence=list(opportunity.evidence),
        risks=list(opportunity.risks),
        next_actions=list(opportunity.next_actions),
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=dict(opportunity.metadata),
    )


def rank_opportunities(
    opportunities: Iterable[OpportunityInput],
    weights: WealthWeights | None = None,
) -> List[WealthPlay]:
    """Score and rank opportunities from strongest to weakest."""

    scored = [score_opportunity(item, weights=weights) for item in opportunities]
    return sorted(
        scored,
        key=lambda play: (
            play.wealth_score,
            play.leverage_score,
            play.freedom_score,
            -(play.payback_months or 999999),
        ),
        reverse=True,
    )


def build_default_playbook() -> List[OpportunityInput]:
    """Default proven wealth playbook independent of personal preferences."""

    return [
        OpportunityInput(
            name="Boring Business Acquisition Pipeline",
            description="Find small profitable service businesses with retiring owners, seller financing potential, and repeat customers.",
            asset_class=AssetClass.ACQUISITION,
            startup_cost=2500,
            estimated_monthly_cashflow=3000,
            time_to_first_cash_days=90,
            owner_required_hours_per_week=8,
            ownership_score=9.5,
            scalability_score=7.0,
            automation_score=6.5,
            recurring_revenue_score=8.0,
            margin_score=7.0,
            defensibility_score=7.0,
            reinvestment_score=9.0,
            evidence=["Existing customers and cashflow reduce startup risk", "Seller financing can create leveraged ownership"],
            risks=["Bad books or hidden liabilities", "Operator dependency"],
            next_actions=["Build acquisition criteria", "Source 50 owner leads", "Request financials from qualified sellers"],
        ),
        OpportunityInput(
            name="Lead Generation Asset Network",
            description="Build niche lead sites that sell verified calls/forms to local service providers.",
            asset_class=AssetClass.LEAD_GEN,
            startup_cost=750,
            estimated_monthly_cashflow=1500,
            time_to_first_cash_days=45,
            owner_required_hours_per_week=5,
            ownership_score=8.0,
            scalability_score=8.5,
            automation_score=8.0,
            recurring_revenue_score=7.5,
            margin_score=8.5,
            defensibility_score=5.5,
            reinvestment_score=8.0,
            evidence=["Owned digital property", "Can replicate across niches and cities"],
            risks=["SEO/ads volatility", "Requires reliable buyer relationships"],
            next_actions=["Pick one urgent buyer niche", "Launch one landing page", "Sell first 10 leads manually"],
        ),
        OpportunityInput(
            name="Digital Product + Affiliate Funnel",
            description="Package a painful problem into a low-ticket product, then monetize traffic with backend affiliate offers.",
            asset_class=AssetClass.INTELLECTUAL_PROPERTY,
            startup_cost=300,
            estimated_monthly_cashflow=1000,
            time_to_first_cash_days=21,
            owner_required_hours_per_week=6,
            ownership_score=8.5,
            scalability_score=9.0,
            automation_score=8.5,
            recurring_revenue_score=5.5,
            margin_score=9.5,
            defensibility_score=5.0,
            reinvestment_score=7.0,
            evidence=["Near-zero marginal cost", "Can use paid or organic distribution"],
            risks=["Distribution failure", "Low trust if offer is weak"],
            next_actions=["Choose pain point", "Build checkout + delivery", "Run 7-day traffic test"],
        ),
        OpportunityInput(
            name="Service-to-Asset Rollup",
            description="Use a cashflow service as the front-end, then convert customers, data, templates, and workflows into sellable assets.",
            asset_class=AssetClass.SERVICE_TO_ASSET,
            startup_cost=500,
            estimated_monthly_cashflow=4000,
            time_to_first_cash_days=14,
            owner_required_hours_per_week=18,
            ownership_score=6.5,
            scalability_score=6.0,
            automation_score=5.5,
            recurring_revenue_score=6.0,
            margin_score=7.5,
            defensibility_score=6.0,
            reinvestment_score=8.0,
            evidence=["Fast cash can fund asset acquisition", "Repeatable workflows can become products"],
            risks=["Can become another job if not systemized", "Labor bottlenecks"],
            next_actions=["Define one repeatable offer", "Document SOP", "Reinvest 30% into owned assets"],
        ),
    ]


def build_ranked_default_playbook() -> List[Dict[str, Any]]:
    """Return the default playbook as serializable ranked dictionaries."""

    return [play.to_dict() for play in rank_opportunities(build_default_playbook())]
