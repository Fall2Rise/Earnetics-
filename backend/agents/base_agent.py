from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.autonomous_ai_system import (
    ActionStatus,
    AutonomousAIAgent,
    BusinessAction,
    Priority,
)

ORGANIZATION_MISSION = (
    "Autonomously design, build, deploy, test, and grow revenue-generating systems with minimal "
    "human input while protecting the Fallat family brand and assets."
)

PRIORITY_SEQUENCE = [
    Priority.CRITICAL,
    Priority.HIGH,
    Priority.MEDIUM,
    Priority.MEDIUM,
]

IMPACT_SEQUENCE = [8000.0, 5000.0, 2500.0, 1000.0]


class OrganizationAgent(AutonomousAIAgent):
    def __init__(
        self,
        org_id: str,
        name: str,
        pod: str,
        role_summary: str,
        responsibilities: List[str],
        reports_to: Optional[List[str]] = None,
        manages: Optional[List[str]] = None,
        mission: str = ORGANIZATION_MISSION,
    ) -> None:
        super().__init__(
            role=name,
            goal=role_summary,
            backstory=f"{name} safeguards the {pod} pod for Earnetics Swarm.",
            specialties=[resp.replace("_", " ") for resp in responsibilities],
        )
        self.org_id = org_id
        self.pod = pod
        self.role_summary = role_summary
        self.responsibilities = responsibilities
        self.reports_to = reports_to or []
        self.manages = manages or []
        self.mission = mission

    def profile(self) -> Dict[str, Any]:
        return {
            "id": self.org_id,
            "role": self.role,
            "pod": self.pod,
            "summary": self.role_summary,
            "reports_to": self.reports_to,
            "manages": self.manages,
            "responsibilities": self.responsibilities,
            "mission": self.mission,
        }

    def plan_focus(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        return {
            "agent": self.org_id,
            "pod": self.pod,
            "responsibility_queue": self._responsibility_queue(context),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def make_autonomous_decisions(self, business_context: Dict[str, Any]) -> List[BusinessAction]:
        actions = super().make_autonomous_decisions(business_context)
        actions.extend(self._responsibility_actions(business_context))
        return actions

    def _responsibility_queue(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        queue = []
        for idx, responsibility in enumerate(self.responsibilities):
            queue.append(
                {
                    "responsibility": responsibility,
                    "priority": PRIORITY_SEQUENCE[min(idx, len(PRIORITY_SEQUENCE) - 1)].value,
                    "context": context,
                }
            )
        return queue

    def _responsibility_actions(self, context: Dict[str, Any]) -> List[BusinessAction]:
        if not self.responsibilities:
            return []

        actions: List[BusinessAction] = []
        now = datetime.utcnow()
        delegate_pool = self.manages or [self.org_id]

        for idx, responsibility in enumerate(self.responsibilities[:4]):
            assigned_agent = delegate_pool[idx % len(delegate_pool)]
            priority = PRIORITY_SEQUENCE[min(idx, len(PRIORITY_SEQUENCE) - 1)]
            impact = IMPACT_SEQUENCE[min(idx, len(IMPACT_SEQUENCE) - 1)]
            deadline = now + timedelta(days=idx + 1)
            actions.append(
                BusinessAction(
                    id=f"{self.org_id.upper()}_{responsibility.upper()}_{now.strftime('%Y%m%d%H%M%S')}_{idx}",
                    title=responsibility.replace("_", " ").title(),
                    description=f"Ensure '{responsibility}' remains on track for the {self.pod} pod.",
                    assigned_agent=assigned_agent,
                    priority=priority,
                    deadline=deadline,
                    status=ActionStatus.PLANNED,
                    expected_revenue_impact=impact,
                    dependencies=[],
                )
            )

        return actions

    def escalation(self, issue: str, severity: Priority = Priority.HIGH) -> Dict[str, Any]:
        return {
            "agent": self.org_id,
            "issue": issue,
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat(),
            "route_to": self.reports_to or ["ceo"],
        }
