"""Dispatcher - converts dispatch packets into queue jobs."""

import logging
from typing import Any, Dict, List, Optional

from backend.corporate_memory import CorporateMemory
from autonomous.workflow_queue import WorkflowQueueRepository

logger = logging.getLogger(__name__)

# Map department names to job types
DEPARTMENT_JOB_TYPES = {
    "growth": "DISPATCH_GROWTH_TASKS",
    "domains_webops": "DISPATCH_WEBOPS_TASKS",
    "domains": "DISPATCH_WEBOPS_TASKS",
    "webops": "DISPATCH_WEBOPS_TASKS",
    "community": "DISPATCH_COMMUNITY_TASKS",
    "tools_product": "DISPATCH_TOOLS_TASKS",
    "tools": "DISPATCH_TOOLS_TASKS",
    "product": "DISPATCH_TOOLS_TASKS",
    "ops": "DISPATCH_OPS_TASKS",
    "operations": "DISPATCH_OPS_TASKS",
    "revenue_execution": "DISPATCH_EXECUTION_TASKS",
    "execution": "DISPATCH_EXECUTION_TASKS",
    "revenue_strategy_cell": "DISPATCH_STRATEGY_TASKS",
    "strategy": "DISPATCH_STRATEGY_TASKS",
}


import hashlib
from datetime import datetime, timezone

class Dispatcher:
    """Dispatches strategy tasks to department queues."""

    def __init__(self):
        self.queue_repo = WorkflowQueueRepository()
        self.corp_mem = CorporateMemory()
        self._recent_dispatches = {}  # In-memory cache for idempotency

    def _generate_idempotency_key(
        self, run_id: str, department_name: str, play_ids: List[str]
    ) -> str:
        """Generate idempotency key for dispatch."""
        # Use run_id + department + play_ids + current hour
        now = datetime.now(timezone.utc)
        hour_key = now.strftime("%Y%m%d%H")
        content = f"{run_id}:{department_name}:{':'.join(sorted(play_ids))}:{hour_key}"
        return hashlib.md5(content.encode()).hexdigest()

    def dispatch_run(
        self, run_id: str, dispatch_packets: Dict[str, List[Dict[str, Any]]], force: bool = False
    ) -> Dict[str, Any]:
        """Dispatch all packets for a run with idempotency protection."""
        results = {
            "run_id": run_id,
            "jobs_created": [],
            "errors": [],
            "skipped": [],
        }
        
        # Extract play IDs from dispatch packets metadata if available
        play_ids = []
        for tasks in dispatch_packets.values():
            for task in tasks:
                if isinstance(task, dict) and "play_id" in task.get("metadata", {}):
                    play_ids.append(task["metadata"]["play_id"])
        
        for department_name, tasks in dispatch_packets.items():
            if not tasks:
                continue
            
            # Check idempotency (15-minute window unless forced)
            if not force:
                idempotency_key = self._generate_idempotency_key(run_id, department_name, play_ids)
                
                # Check in-memory cache
                if idempotency_key in self._recent_dispatches:
                    last_time = self._recent_dispatches[idempotency_key]
                    time_diff = (datetime.now(timezone.utc) - last_time).total_seconds()
                    if time_diff < 900:  # 15 minutes
                        logger.info(
                            "Skipping duplicate dispatch for %s (last dispatch %d seconds ago)",
                            department_name,
                            int(time_diff),
                        )
                        results["skipped"].append({
                            "department": department_name,
                            "reason": "duplicate_within_15min",
                        })
                        continue
                
                # Update cache
                self._recent_dispatches[idempotency_key] = datetime.now(timezone.utc)
                # Clean old entries (older than 1 hour)
                cutoff = datetime.now(timezone.utc).timestamp() - 3600
                self._recent_dispatches = {
                    k: v for k, v in self._recent_dispatches.items()
                    if v.timestamp() > cutoff
                }
            
            try:
                job_id = self.dispatch_department(run_id, department_name, tasks)
                if job_id:
                    results["jobs_created"].append({
                        "department": department_name,
                        "job_id": job_id,
                        "tasks_count": len(tasks),
                    })
            except Exception as e:
                logger.error(
                    "Failed to dispatch department %s: %s", department_name, e
                )
                results["errors"].append({
                    "department": department_name,
                    "error": str(e),
                })
        
        logger.info(
            "Dispatched run %s: %d jobs created, %d errors, %d skipped",
            run_id,
            len(results["jobs_created"]),
            len(results["errors"]),
            len(results["skipped"]),
        )
        
        return results

    def dispatch_department(
        self, run_id: str, department_name: str, tasks: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Dispatch tasks for a single department."""
        job_type = DEPARTMENT_JOB_TYPES.get(department_name.lower(), f"DISPATCH_{department_name.upper()}_TASKS")
        
        # Create task in corporate memory
        task_title = f"Strategy Dispatch: {department_name} ({len(tasks)} tasks)"
        task_description = "\n".join([
            f"- {task.get('task', 'Unknown task')} (Priority: {task.get('priority', 'medium')}, Deadline: {task.get('deadline', 'TBD')})"
            for task in tasks
        ])
        
        # Create department task
        task_record = self.corp_mem.create_task({
            "objective_id": None,
            "title": task_title,
            "department": department_name,
            "assigned_agent": None,
            "status": "pending",
            "priority": "high" if any(t.get("priority") == "high" for t in tasks) else "medium",
            "due_date": None,
            "description": task_description,
            "dependencies": [],
            "metadata": {
                "run_id": run_id,
                "job_type": job_type,
                "tasks": tasks,
            },
        })
        
        # Enqueue in workflow queue
        job = self.queue_repo.enqueue_from_task(task_record)
        job_id = job.get("id") if isinstance(job, dict) else str(job) if job else None
        
        logger.info(
            "Dispatched %s: %d tasks, job_id=%s",
            department_name,
            len(tasks),
            job_id,
        )
        
        return job_id

