from __future__ import annotations

from typing import Any, Dict

from backend.api_integrations import api_manager
from backend.workflow_scheduler import register_handler


async def launch_product_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    opportunity = payload.get("opportunity") or {
        "keyword": payload.get("keyword", "AI automation blueprint"),
        "trend_score": payload.get("trend_score", 0.8),
        "market_size": payload.get("market_size", "$1.2B"),
    }
    return await api_manager.execute_full_product_launch(opportunity)


async def run_affiliate_cycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    category = payload.get("category")
    return await api_manager.run_affiliate_cycle(category=category)


async def run_dropshipping_cycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await api_manager.run_dropshipping_cycle()


def register_default_scheduler_handlers() -> None:
    register_handler("revenue.launch_product", launch_product_pipeline)
    register_handler("revenue.affiliate_cycle", run_affiliate_cycle)
    register_handler("revenue.dropshipping_cycle", run_dropshipping_cycle)


__all__ = ["register_default_scheduler_handlers"]
