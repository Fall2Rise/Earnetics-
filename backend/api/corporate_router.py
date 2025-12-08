from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

# SWITCHED TO REAL AGENTS
from backend import real_ai_agents as agents
from backend.audit_log import log_event
try:
    from backend.stripe_integration import StripePaymentProcessor
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    StripePaymentProcessor = None  # type: ignore

router = APIRouter(prefix="/api", tags=["corporate"])
logger = logging.getLogger(__name__)


class RevenueRequest(BaseModel):
    amount: float = Field(..., gt=0)
    source: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    description: Optional[str] = None


class DirectiveRequest(BaseModel):
    directive: str = Field(..., min_length=1)
    priority: str = Field(default="high")
    departments: Optional[List[str]] = None

    @validator("priority")
    def normalise_priority(cls, value: str) -> str:
        allowed = {"low", "medium", "high", "urgent"}
        lowered = value.lower()
        if lowered not in allowed:
            return "high"
        return lowered


class ProductRequest(BaseModel):
    product_type: str = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    price_point: float = Field(..., gt=0)
    description: Optional[str] = None


class MarketResearchRequest(BaseModel):
    industry: str = Field(..., min_length=1)
    target_market: str = Field(..., min_length=1)
    research_depth: Optional[str] = None


@router.post("/process_revenue")
async def process_revenue_endpoint(request: RevenueRequest):
    try:
        result = await agents.process_revenue(
            amount=request.amount,
            source=request.source,
            category=request.category,
            description=request.description or "",
        )
        log_event(
            "revenue.process",
            status="success",
            agent="corporate_router",
            message="Revenue transaction processed",
            details={
                "amount": request.amount,
                "source": request.source,
                "category": request.category,
            },
        )
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "revenue.process",
            status="error",
            agent="corporate_router",
            message=str(exc),
            details={
                "amount": request.amount,
                "source": request.source,
                "category": request.category,
            },
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "processed", "result": result}


@router.post("/execute_directive")
async def execute_directive_endpoint(request: DirectiveRequest):
    try:
        result = await agents.execute_directive(request.directive, request.priority)
        log_event(
            "directive.execute",
            status="queued",
            agent="corporate_router",
            message=request.directive,
            details={"priority": request.priority, "departments": request.departments or []},
        )
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "directive.execute",
            status="error",
            agent="corporate_router",
            message=str(exc),
            details={"directive": request.directive},
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    payload = {"status": "queued", "result": result}
    if request.departments:
        payload["departments"] = request.departments
    return payload


@router.post("/create_digital_product")
async def create_product_endpoint(request: ProductRequest):
    try:
        result = await agents.create_product(
            product_type=request.product_type,
            target_audience=request.target_audience,
            price_point=request.price_point,
            description=request.description or "",
        )
        log_event(
            "product.create",
            status="success",
            agent="corporate_router",
            message=request.product_type,
            details={
                "target_audience": request.target_audience,
                "price_point": request.price_point,
            },
        )
        stripe_info = _sync_product_to_stripe(request)
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "product.create",
            status="error",
            agent="corporate_router",
            message=str(exc),
            details={
                "product_type": request.product_type,
                "target_audience": request.target_audience,
            },
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    payload: Dict[str, Any] = {"status": "created", "product": result}
    if stripe_info:
        payload["stripe"] = stripe_info
    return payload


@router.post("/market_research")
async def market_research_endpoint(request: MarketResearchRequest):
    try:
        result = await agents.market_research(
            industry=request.industry, target_market=request.target_market
        )
        log_event(
            "market.research",
            status="success",
            agent="corporate_router",
            message="Market research generated",
            details={
                "industry": request.industry,
                "target_market": request.target_market,
                "depth": request.research_depth,
            },
        )
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "market.research",
            status="error",
            agent="corporate_router",
            message=str(exc),
            details={
                "industry": request.industry,
                "target_market": request.target_market,
                "depth": request.research_depth,
            },
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    payload = {"status": "completed", "research": result}
    if request.research_depth:
        payload["requested_depth"] = request.research_depth
    return payload


def _sync_product_to_stripe(request: ProductRequest) -> Optional[Dict[str, Any]]:
    if not os.getenv("STRIPE_SECRET_KEY"):
        return None
    if StripePaymentProcessor is None:
        return None
    processor = StripePaymentProcessor()
    config = processor.configure_from_environment()
    if not config.get("success"):
        logger.warning("Stripe sync skipped: %s", config.get("error"))
        return None
    try:
        return processor.create_product_with_price(
            name=request.product_type,
            description=request.description,
            unit_amount=request.price_point,
            currency="usd",
            interval="month",
        )
    except Exception as exc:
        logger.warning("Stripe product sync failed: %s", exc)
        return None


@router.get("/system_status")
def system_status_endpoint():
    try:
        status = agents.system_status()
        log_event(
            "system.status",
            status="success",
            agent="corporate_router",
            message="System status retrieved",
        )
        return status
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "system.status",
            status="error",
            agent="corporate_router",
            message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/financial_summary")
async def financial_summary_endpoint():
    try:
        summary = await agents.financial_summary()
        log_event(
            "financial.summary",
            status="success",
            agent="corporate_router",
            message="Financial summary retrieved",
        )
        return summary
    except Exception as exc:  # pragma: no cover - defensive path
        log_event(
            "financial.summary",
            status="error",
            agent="corporate_router",
            message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
