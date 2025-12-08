from __future__ import annotations

from typing import Any, Dict

from .wealth_portfolio import WealthPortfolio


class WealthFeedback:
    def __init__(self, portfolio: WealthPortfolio) -> None:
        self.portfolio = portfolio

    def collect(self, play_id: str) -> Dict[str, Any]:
        play = next((p for p in self.portfolio.list_plays() if p.get("id") == play_id), None)
        if not play:
            raise ValueError("Play not found")
        return play.get("metrics_snapshot", {})
