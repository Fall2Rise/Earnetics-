from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from backend.audit_log import log_event

TRADING_STORE = Path(os.getenv('TRADING_ENGINE_STORE', 'trading_state.json'))


@dataclass
class RiskProfile:
    max_daily_loss: float
    max_position_size: float
    leverage: float = 1.0


@dataclass
class Strategy:
    name: str
    description: str
    parameters: Dict[str, float]
    active: bool = True


@dataclass
class TradeOrder:
    id: str
    asset: str
    side: str  # buy or sell
    quantity: float
    price: float
    timestamp: str = datetime.utcnow().isoformat()
    status: str = 'pending'
    strategy: Optional[str] = None


class TradingEngine:
    def __init__(self, store_path: Path = TRADING_STORE):
        self.store_path = store_path
        self.risk_profile = RiskProfile(max_daily_loss=1000.0, max_position_size=10000.0)
        self.strategies: Dict[str, Strategy] = {}
        self.orders: Dict[str, TradeOrder] = {}
        self._load()

    def _load(self) -> None:
        if self.store_path.exists():
            data = json.loads(self.store_path.read_text())
            risk = data.get('risk_profile')
            if risk:
                self.risk_profile = RiskProfile(**risk)
            self.strategies = {entry['name']: Strategy(**entry) for entry in data.get('strategies', [])}
            self.orders = {entry['id']: TradeOrder(**entry) for entry in data.get('orders', [])}

    def _save(self) -> None:
        data = {
            'risk_profile': asdict(self.risk_profile),
            'strategies': [asdict(strategy) for strategy in self.strategies.values()],
            'orders': [asdict(order) for order in self.orders.values()],
        }
        self.store_path.write_text(json.dumps(data, indent=2))

    def set_risk_profile(self, profile: RiskProfile) -> None:
        self.risk_profile = profile
        self._save()
        log_event('trading.risk_updated', profile=asdict(profile))

    def register_strategy(self, strategy: Strategy) -> None:
        self.strategies[strategy.name] = strategy
        self._save()
        log_event('trading.strategy_registered', strategy=strategy.name)

    def submit_order(self, order: TradeOrder) -> None:
        if order.quantity > self.risk_profile.max_position_size:
            raise ValueError('Order exceeds max position size')
        self.orders[order.id] = order
        self._save()
        log_event('trading.order_submitted', order=order.id, asset=order.asset)

    def update_order_status(self, order_id: str, status: str) -> None:
        order = self.orders.get(order_id)
        if not order:
            raise ValueError('Order not found')
        order.status = status
        self._save()
        log_event('trading.order_updated', order=order.id, status=status)

trading_engine = TradingEngine()
