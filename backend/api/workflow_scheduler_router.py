from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workflow_scheduler import OrchestrationScheduler
from backend.approval_queue import approval_queue

router = APIRouter(prefix="/api/workflows/scheduler", tags=["workflow-scheduler"])
scheduler = OrchestrationScheduler()


class ScheduleRequest(BaseModel):
    job_id: str
    handler: str
    payload: Dict[str, Any]
    schedule_type: str
    schedule_value: str
    start_at: str | None = None


def _parse_start_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=400, detail=f"Invalid start_at value: {exc}") from exc


@router.post("/jobs")
def create_job(request: ScheduleRequest):
    start_at = _parse_start_at(request.start_at)
    try:
        job = scheduler.add_job(
            job_id=request.job_id,
            handler=request.handler,
            payload=request.payload,
            schedule_type=request.schedule_type,
            schedule_value=request.schedule_value,
            start_at=start_at,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"job": job.to_record()}


@router.get("/jobs")
def list_jobs():
    jobs = [job.to_record() for job in scheduler.list_jobs()]
    return {"jobs": jobs}


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    if not scheduler.remove_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "deleted", "job_id": job_id}


@router.get("/due")
def due_jobs():
    jobs = [job.to_record() for job in scheduler.due_jobs()]
    return {"jobs": jobs}


@router.post("/jobs/{job_id}/run")
async def run_job(job_id: str):
    result = await scheduler.execute_job(job_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "run failed"))
    return result


@router.post("/run-due")
async def run_due_jobs():
    results = await scheduler.run_due_jobs()
    return {"results": results}
