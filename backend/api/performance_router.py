"""
Performance Monitoring API Router
Provides endpoints for performance metrics, health status, and bottlenecks
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from backend.services.performance_monitor import get_performance_monitor
from backend.services.intelligent_cache import get_cache
from backend.middleware.rate_limiter import rate_limit

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/health")
def get_health_status(
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get overall system health status"""
    monitor = get_performance_monitor()
    return monitor.get_health_status()

@router.get("/bottlenecks")
def get_bottlenecks(
    timeframe_hours: int = 24,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get detected performance bottlenecks"""
    monitor = get_performance_monitor()
    bottlenecks = monitor.detect_bottlenecks(timeframe_hours=timeframe_hours)
    return {
        "bottlenecks": [b.__dict__ for b in bottlenecks],
        "count": len(bottlenecks),
        "timeframe_hours": timeframe_hours
    }

@router.get("/success-rates")
def get_success_rates(
    agent_name: Optional[str] = None,
    action_type: Optional[str] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get success rates for agents/actions"""
    monitor = get_performance_monitor()
    
    if agent_name and action_type:
        return {
            "agent": agent_name,
            "action": action_type,
            "metrics": monitor.get_success_rate(agent_name, action_type)
        }
    else:
        return {
            "top_performers": monitor.get_top_performers(limit=20)
        }

@router.get("/cache/stats")
def get_cache_stats(
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get cache statistics"""
    cache = get_cache()
    return cache.get_stats()

@router.post("/cache/invalidate")
def invalidate_cache(
    pattern: Optional[str] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Invalidate cache entries"""
    cache = get_cache()
    cache.invalidate(pattern)
    return {"status": "success", "message": f"Cache invalidated for pattern: {pattern or 'all'}"}
