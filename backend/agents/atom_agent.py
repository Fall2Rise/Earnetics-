from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.autonomous_ai_system import (
    ActionStatus,
    AutonomousAIAgent,
    BusinessAction,
    Priority,
)


@dataclass
class PodAlignment:
    pod: str
    focus: List[str]
    reports_to: List[str] = field(default_factory=list)


class AtomAgent(AutonomousAIAgent):
    def __init__(self) -> None:
        super().__init__(
            role="Chief Executive Officer",
            goal="Keep Earnetics Swarm aligned to the prime directive while scaling autonomous revenue",
            backstory=(
                "ATOM is the president-level controller that interprets the prime directive,"
                " routes plays, and rebalances pods whenever metrics drift."
            ),
            specialties=[
                "strategic_alignment",
                "pod_coordination",
                "risk_balancing",
                "pivot_triggering",
            ],
        )
        self.identity = "ATOM"
        self.mission = (
            "Autonomously design, build, deploy, test, and grow revenue systems with minimal"
            " human input while protecting the Fallat family brand and assets."
        )
        self.pod_alignment = PodAlignment(
            pod="executive",
            focus=[
                "define_global_revenue_targets",
                "approve_new_strategic_plays",
                "allocate_focus_between_pods",
                "trigger_pivots_when_required",
            ],
            reports_to=[],
        )

    def strategic_brief(self, signal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        priorities = self._prioritize_pods(context)
        return {
            "signal": signal,
            "priorities": priorities,
            "mission_alignment": self.mission,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def make_autonomous_decisions(self, business_context: Dict[str, Any]) -> List[BusinessAction]:
        directives = super().make_autonomous_decisions(business_context)
        if business_context.get("total_revenue", 0) < 10000:
            directives.append(
                BusinessAction(
                    id=f"ATOM_GROWTH_SURGE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    title="Initiate growth surge",
                    description="Push growth pod to double demand until revenue passes $10k",
                    assigned_agent="growth_head",
                    priority=Priority.CRITICAL,
                    deadline=datetime.utcnow(),
                    status=ActionStatus.IN_PROGRESS,
                    expected_revenue_impact=5000.0,
                    dependencies=[],
                )
            )
        return directives

    def _prioritize_pods(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        revenue = context.get("total_revenue", 0)
        backlog = context.get("active_projects", 0)
        priorities = [
            {
                "pod": "research",
                "focus": "surface two fresh validated niches",
                "reason": "feed product pipeline",
            },
            {
                "pod": "engineering",
                "focus": "ship failsafes on active automations",
                "reason": "stability",
            },
        ]
        if revenue < 5000:
            priorities.insert(
                0,
                {
                    "pod": "growth",
                    "focus": "scale proven playbook",
                    "reason": "revenue gap",
                },
            )
        if backlog > 5:
            priorities.append(
                {
                    "pod": "qa",
                    "focus": "parallelize coverage",
                    "reason": "backlog relief",
                }
            )
        return priorities

    async def execute_business_function(self, context: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = data or {}
        assessment = self.analyze_situation(
            {
                "total_revenue": data.get("total_revenue", 0),
                "monthly_target": data.get("monthly_target", 150000),
                "active_customers": data.get("active_customers", 0),
            }
        )
        return {
            "agent": self.identity,
            "context": context,
            "assessment": assessment,
            "directive": self.strategic_brief(context, data),
        }
