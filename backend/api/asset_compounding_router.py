"""API routes for the Earnetics Asset Compounding Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.asset_compounding_engine import (
    AssetClass,
    OpportunityInput,
    WealthWeights,
    build_ranked_default_playbook,
    rank_opportunities,
    score_opportunity,
)

router = APIRouter(prefix="/api/asset-compounding", tags=["asset-compounding"])


class WealthWeightsPayload(BaseModel):
    ownership: float = Field(default=0.22, ge=0, le=1)
    scalability: float = Field(default=0.18, ge=0, le=1)
    automation: float = Field(default=0.14, ge=0, le=1)
    recurring_revenue: float = Field(default=0.14, ge=0, le=1)
    margin: float = Field(default=0.10, ge=0, le=1)
    speed_to_cash: float = Field(default=0.08, ge=0, le=1)
    defensibility: float = Field(default=0.08, ge=0, le=1)
    reinvestment_potential: float = Field(default=0.06, ge=0, le=1)

    def to_weights(self) -> WealthWeights:
        return WealthWeights(**self.model_dump())


class OpportunityPayload(BaseModel):
    name: str
    description: str
    asset_class: AssetClass | str
    startup_cost: float = 0.0
    estimated_monthly_cashflow: float = 0.0
    time_to_first_cash_days: int = 30
    owner_required_hours_per_week: float = 20.0
    ownership_score: float = Field(default=0.0, ge=0, le=10)
    scalability_score: float = Field(default=0.0, ge=0, le=10)
    automation_score: float = Field(default=0.0, ge=0, le=10)
    recurring_revenue_score: float = Field(default=0.0, ge=0, le=10)
    margin_score: float = Field(default=0.0, ge=0, le=10)
    defensibility_score: float = Field(default=0.0, ge=0, le=10)
    reinvestment_score: float = Field(default=0.0, ge=0, le=10)
    evidence: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_input(self) -> OpportunityInput:
        return OpportunityInput(**self.model_dump())


class ScoreOpportunityRequest(BaseModel):
    opportunity: OpportunityPayload
    weights: Optional[WealthWeightsPayload] = None


class RankOpportunitiesRequest(BaseModel):
    opportunities: List[OpportunityPayload]
    weights: Optional[WealthWeightsPayload] = None


@router.get("/playbook")
def get_default_asset_playbook() -> Dict[str, Any]:
    """Return the default wealth playbook ranked by asset mechanics."""

    return {
        "formula": "Wealth = Ownership x Scale x Time",
        "principle": "Prioritize assets that compound without constant owner labor.",
        "plays": build_ranked_default_playbook(),
    }


@router.post("/score")
def score_asset_play(request: ScoreOpportunityRequest) -> Dict[str, Any]:
    """Score one opportunity against durable wealth criteria."""

    weights = request.weights.to_weights() if request.weights else None
    play = score_opportunity(request.opportunity.to_input(), weights=weights)
    return {"play": play.to_dict()}


@router.post("/rank")
def rank_asset_plays(request: RankOpportunitiesRequest) -> Dict[str, Any]:
    """Rank multiple opportunities from strongest to weakest."""

    weights = request.weights.to_weights() if request.weights else None
    plays = rank_opportunities([item.to_input() for item in request.opportunities], weights=weights)
    return {"plays": [play.to_dict() for play in plays]}
