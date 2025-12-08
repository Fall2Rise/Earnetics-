from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from .core_plays import CORE_PLAYS_SEED
from .revenue_loop import RevenueLoopRunner

logger = logging.getLogger(__name__)


class WealthPortfolio:
    def __init__(self) -> None:
        self._plays: Dict[str, Dict[str, Any]] = {}
        self._seeded = False
        self.seed_core_plays(CORE_PLAYS_SEED)
        print("WealthPortfolio seeded plays:", list(self._plays.keys()))

    def add_play(self, play_definition: Dict[str, Any]) -> Dict[str, Any]:
        play_id = play_definition.get("id") or str(uuid.uuid4())
        play = {
            **play_definition,
            "id": play_id,
            "created_at": play_definition.get("created_at") or datetime.utcnow().isoformat(),
            "status": play_definition.get("status") or "ACTIVE",
        }
        self._plays[play_id] = play
        return play

    def list_plays(self) -> List[Dict[str, Any]]:
        return list(self._plays.values())

    def get_play(self, play_id: str) -> Dict[str, Any] | None:
        return self._plays.get(play_id)

    def pause_play(self, play_id: str) -> Dict[str, Any]:
        play = self._plays.get(play_id)
        if not play:
            raise ValueError("Play not found")
        play["status"] = "PAUSED"
        return play

    def boost_play(self, play_id: str) -> Dict[str, Any]:
        play = self._plays.get(play_id)
        if not play:
            raise ValueError("Play not found")
        play.setdefault("boosts", 0)
        play["boosts"] += 1
        return play

    def summary(self) -> Dict[str, Any]:
        return {
            "active": sum(1 for play in self._plays.values() if play.get("status") == "ACTIVE"),
            "paused": sum(1 for play in self._plays.values() if play.get("status") == "PAUSED"),
            "total": len(self._plays),
        }

    def seed_core_plays(self, core_plays: List[Dict[str, Any]]) -> int:
        if self._seeded or len(self._plays) > 0:
            logger.debug("Portfolio already seeded or contains plays, skipping core play seeding")
            return 0

        seeded_count = 0
        for play_seed in core_plays:
            try:
                play_id = play_seed["id"]  # use stable ID from seed
                play = {
                    "id": play_id,
                    "name": play_seed["name"],
                    "description": play_seed.get("description"),
                    "status": play_seed.get("status"),
                    "risk_tier": play_seed.get("risk_tier"),
                    "tags": play_seed.get("tags", []),
                    "budget": play_seed.get("budget", {}),
                    "kpis": play_seed.get("kpis", {}),
                    "execution_plan": play_seed.get("execution_plan", {}),
                    "metadata": play_seed.get("metadata", {}),
                    "created_at": datetime.utcnow().isoformat(),
                }
                self._plays[play_id] = play
                seeded_count += 1
            except Exception as exc:
                logger.warning("Failed to seed core play %s: %s", play_seed.get("name"), exc)

        self._seeded = True
        logger.info("Seeded %d core plays into WealthPortfolio", seeded_count)
        return seeded_count

    def run_autonomous_cycle(self, market_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        runner = RevenueLoopRunner()
        loop_result = runner.run(market_snapshot)
        return {
            "product_roadmap": loop_result.product_roadmap,
            "validated_opportunity": loop_result.validated_opportunity,
            "automation_module_spec": loop_result.automation_module_spec,
            "approved_module": loop_result.approved_module,
            "revenue_play_report": loop_result.revenue_play_report,
        }
