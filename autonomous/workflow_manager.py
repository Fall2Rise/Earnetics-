"""Autonomous workflow orchestration utilities.

This module consumes pending executive directives and translates them into
corporate objectives and departmental task plans using the shared memory
layer. It provides a deterministic orchestration pass that can run on a timer
or be triggered manually via API.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from backend.executive_reasoning import DirectiveRegistry
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    from executive_reasoning import DirectiveRegistry

try:
    from backend.corporate_memory import CorporateMemory, Objective, Task
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    from corporate_memory import CorporateMemory, Objective, Task

try:
    from autonomous.workflow_queue import WorkflowQueueRepository
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    try:
        from workflow_queue import WorkflowQueueRepository  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        WorkflowQueueRepository = None  # type: ignore

logger = logging.getLogger("AutonomousWorkflowOrchestrator")


@dataclass
class OrchestrationResult:
    processed_directives: int
    objectives_created: int
    tasks_created: int
    skipped: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "processed_directives": self.processed_directives,
            "objectives_created": self.objectives_created,
            "tasks_created": self.tasks_created,
            "skipped": self.skipped,
        }


class AutonomousWorkflowOrchestrator:
    """Translate directives into actionable objectives and tasks."""

    def __init__(
        self,
        directive_registry: DirectiveRegistry,
        corporate_memory: CorporateMemory,
        queue_repository: Optional["WorkflowQueueRepository"] = None,
    ):
        self.directive_registry = directive_registry
        self.corporate_memory = corporate_memory
        self.queue_repository = queue_repository

    def run_once(self) -> OrchestrationResult:
        directives = self.directive_registry.list_directives()
        processed = 0
        objectives_created = 0
        tasks_created = 0
        skipped = 0

        for directive in directives:
            status = (directive.get("status") or "pending").lower()
            if status not in {"pending", "in_progress"}:
                continue
            processed += 1
            existing_objective = self.corporate_memory.get_objective_by_source(
                directive["id"]
            )
            if existing_objective:
                skipped += 1
                if status == "pending":
                    self.directive_registry.update_status(directive["id"], "in_progress")
                continue

            objective_record = self._create_objective_from_directive(directive)
            objective = self.corporate_memory.create_objective(objective_record)
            objectives_created += 1

            generated_tasks = self._generate_tasks_for_directive(directive, objective)
            for task_record in generated_tasks:
                created_task = self.corporate_memory.create_task(task_record)
                tasks_created += 1
                if self.queue_repository:
                    try:
                        self.queue_repository.enqueue_from_task(
                            created_task, directive_id=directive["id"]
                        )
                    except sqlite3.IntegrityError:
                        logger.debug(
                            "Task already in autonomy queue (task_id=%s)",
                            created_task.get("id"),
                        )
                    except sqlite3.Error as exc:  # pragma: no cover - defensive
                        logger.exception(
                            "Failed to enqueue task %s: %s",
                            created_task.get("id"),
                            exc,
                        )

            self.directive_registry.update_status(directive["id"], "in_progress")

        return OrchestrationResult(
            processed_directives=processed,
            objectives_created=objectives_created,
            tasks_created=tasks_created,
            skipped=skipped,
        )

    # Internal helpers ----------------------------------------------------

    def _create_objective_from_directive(self, directive: Dict) -> Dict:
        payload = directive.get("payload", {})
        description = directive.get("description")
        success_metrics = {}
        if isinstance(payload, dict):
            success_metrics = payload.get("success_metrics") or {}
            if not description:
                description = payload.get("summary")
        objective = Objective(
            title=directive["title"],
            owner=directive["owner"],
            priority=directive.get("priority", "medium"),
            status="in_progress",
            description=description,
            success_metrics=success_metrics if isinstance(success_metrics, dict) else {},
            start_date=payload.get("start_date") if isinstance(payload, dict) else None,
            due_date=directive.get("due_date") or payload.get("due_date") if isinstance(payload, dict) else None,
            source_directive_id=directive["id"],
        )
        return objective.to_record()

    def _generate_tasks_for_directive(
        self, directive: Dict, objective: Dict
    ) -> List[Dict]:
        payload = directive.get("payload") or {}
        directive_type = directive.get("directive_type", "general")
        due_date = directive.get("due_date") or payload.get("due_date")
        tasks: List[Dict] = []

        blueprint = self._task_blueprint_for_type(directive_type, payload)

        for item in blueprint:
            task = Task(
                title=item["title"].format(title=directive["title"]),
                department=item["department"],
                priority=item.get("priority", directive.get("priority", "medium")),
                status="pending",
                objective_id=objective["id"],
                assigned_agent=item.get("assigned_agent"),
                due_date=due_date or item.get("due_date"),
                description=item.get("description"),
                dependencies=item.get("dependencies"),
                metadata={
                    **(item.get("metadata") or {}),
                    "source_directive_id": directive["id"],
                    "directive_type": directive_type,
                },
            )
            tasks.append(task.to_record())

        # If payload contains explicit experiments/tasks list, honor them
        experiments = payload.get("experiments") if isinstance(payload, dict) else None
        if isinstance(experiments, list):
            for experiment in experiments:
                title = experiment if isinstance(experiment, str) else experiment.get("title")
                if not title:
                    continue
                task = Task(
                    title=f"Experiment: {title}",
                    department="marketing",
                    priority=directive.get("priority", "medium"),
                    status="pending",
                    objective_id=objective["id"],
                    due_date=due_date,
                    metadata={
                        "experiment": experiment,
                        "source_directive_id": directive["id"],
                    },
                )
                tasks.append(task.to_record())

        return tasks

    def _task_blueprint_for_type(
        self, directive_type: str, payload: Dict
    ) -> List[Dict[str, Optional[str]]]:
        directive_type = directive_type.lower()
        if directive_type == "growth":
            return [
                {
                    "department": "marketing",
                    "title": "Develop campaign plan for {title}",
                    "description": "Create messaging, channels, and budget recommendations.",
                    "assigned_agent": "Nova",
                },
                {
                    "department": "sales",
                    "title": "Activate sales playbook for {title}",
                    "description": "Build outreach sequence and target account list.",
                    "assigned_agent": "Mercury",
                },
                {
                    "department": "finance",
                    "title": "Model revenue impact for {title}",
                    "description": "Update forecast with projected conversions and costs.",
                    "assigned_agent": "Vega",
                },
            ]
        if directive_type == "product":
            return [
                {
                    "department": "product",
                    "title": "Draft product spec for {title}",
                    "description": "Define requirements, features, and success criteria.",
                    "assigned_agent": "Forge",
                },
                {
                    "department": "design",
                    "title": "Create UX concept for {title}",
                    "description": "Produce initial wireframes and visual explorations.",
                    "assigned_agent": "Aurora",
                },
                {
                    "department": "engineering",
                    "title": "Plan technical implementation for {title}",
                    "description": "Outline architecture, stack decisions, and sprint breakdown.",
                    "assigned_agent": "Titan",
                },
            ]
        if directive_type == "finance":
            return [
                {
                    "department": "finance",
                    "title": "Execute financial review for {title}",
                    "description": "Audit cash flow, revenue, and reinvestment requirements.",
                    "assigned_agent": "Vega",
                },
                {
                    "department": "operations",
                    "title": "Implement compliance checks for {title}",
                    "description": "Verify regulatory and policy guardrails are in place.",
                    "assigned_agent": "Seraph",
                },
            ]
        if directive_type == "affiliate":
            return [
                {
                    "department": "affiliate",
                    "title": "Secure new affiliate offer for {title}",
                    "description": "Identify top offers, review compliance, and capture tracking links.",
                    "assigned_agent": "Orion",
                },
                {
                    "department": "marketing",
                    "title": "Build affiliate funnel for {title}",
                    "description": "Deploy landing page, email sequence, and paid acquisition tests.",
                    "assigned_agent": "Vortex",
                },
                {
                    "department": "affiliate",
                    "title": "Analyze affiliate performance for {title}",
                    "description": "Monitor conversions, payouts, and compliance metrics.",
                    "assigned_agent": "Lumen",
                },
            ]
        if directive_type == "dropshipping":
            return [
                {
                    "department": "dropshipping",
                    "title": "Source suppliers for {title}",
                    "description": "Evaluate suppliers, negotiate terms, and sync product listings.",
                    "assigned_agent": "Cascade",
                },
                {
                    "department": "dropshipping",
                    "title": "Prepare fulfillment workflow for {title}",
                    "description": "Map routing, automation triggers, and customer communication steps.",
                    "assigned_agent": "Torrent",
                },
            ]
        if directive_type == "innovation":
            return [
                {
                    "department": "innovation",
                    "title": "Design pilot for {title}",
                    "description": "Outline MVP scope, success metrics, and launch timeline.",
                    "assigned_agent": "Genesis",
                },
                {
                    "department": "finance",
                    "title": "Model financial viability for {title}",
                    "description": "Build ROI projection and budget guardrails.",
                    "assigned_agent": "Vega",
                },
            ]
        # Default blueprint for general directives
        summary = payload.get("summary") if isinstance(payload, dict) else None
        return [
            {
                "department": "operations",
                "title": "Coordinate execution plan for {title}",
                "description": summary or "Synthesize directive outcomes into roadmap.",
                "assigned_agent": "Atlas",
            }
        ]


__all__ = ["AutonomousWorkflowOrchestrator", "OrchestrationResult"]

