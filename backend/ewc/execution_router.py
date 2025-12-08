from __future__ import annotations

from typing import Any, Dict

from .wealth_portfolio import WealthPortfolio


class ExecutionRouter:
    def __init__(self, portfolio: WealthPortfolio) -> None:
        self.portfolio = portfolio

    def launch_play(self, play: Dict[str, Any]) -> None:
        play.setdefault("execution", {})
        play["execution"].update({"routed": True})
