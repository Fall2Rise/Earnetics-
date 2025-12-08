from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.trading.trading_engine import RiskProfile, Strategy, TradeOrder, trading_engine

router = APIRouter(prefix='/api/trading', tags=['trading'])


class RiskPayload(BaseModel):
    max_daily_loss: float
    max_position_size: float
    leverage: float = 1.0


class StrategyPayload(BaseModel):
    name: str
    description: str
    parameters: dict[str, float]
    active: bool = True


class OrderPayload(BaseModel):
    id: str
    asset: str
    side: str
    quantity: float
    price: float
    strategy: str | None = None


@router.get('/risk')
def get_risk_profile():
    return trading_engine.risk_profile.__dict__


@router.post('/risk')
def update_risk_profile(payload: RiskPayload):
    try:
        trading_engine.set_risk_profile(RiskProfile(**payload.dict()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'updated'}


@router.get('/strategies')
def list_strategies():
    return {'strategies': [strategy.__dict__ for strategy in trading_engine.strategies.values()]}


@router.post('/strategies')
def register_strategy(payload: StrategyPayload):
    try:
        trading_engine.register_strategy(Strategy(**payload.dict()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'registered'}


@router.get('/orders')
def list_orders():
    return {'orders': [order.__dict__ for order in trading_engine.orders.values()]}


@router.post('/orders')
def submit_order(payload: OrderPayload):
    try:
        trading_engine.submit_order(TradeOrder(**payload.dict()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'submitted'}


@router.post('/orders/{order_id}/status')
def update_order_status(order_id: str, status: str):
    try:
        trading_engine.update_order_status(order_id, status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'updated'}
