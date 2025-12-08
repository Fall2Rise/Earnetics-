from __future__ import annotations

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/autonomy/worker", tags=["autonomy-worker"])


def _get_or_create_worker(request: Request):
    worker = getattr(request.app.state, "autonomy_worker", None)
    if worker is None:
        factory = getattr(request.app.state, "autonomy_worker_factory", None)
        if factory:
            worker = factory()
            request.app.state.autonomy_worker = worker
    return worker


@router.get("/status")
async def worker_status(request: Request) -> Dict[str, Any]:
    worker = _get_or_create_worker(request)
    if worker is None:
        raise HTTPException(status_code=503, detail="Autonomy worker not configured")
    queue_repo = getattr(worker, "queue_repository", None)
    pending = queue_repo.count_pending() if queue_repo else None
    return {
        "running": worker.is_running(),
        "pending": pending,
        "worker_id": getattr(worker, "worker_id", "autonomy-worker"),
    }


@router.post("/start")
async def start_worker(request: Request) -> Dict[str, Any]:
    worker = _get_or_create_worker(request)
    if worker is None:
        raise HTTPException(status_code=503, detail="Autonomy worker not configured")

    if worker.is_running():
        queue_repo = getattr(worker, "queue_repository", None)
        pending = queue_repo.count_pending() if queue_repo else None
        return {"status": "running", "pending": pending, "worker_id": worker.worker_id}

    queue_repo = getattr(worker, "queue_repository", None)
    if queue_repo:
        try:
            queue_repo.recover_in_progress_items(claimed_by=worker.worker_id)
        except Exception:
            # Non-fatal; continue to start the worker
            pass

    request.app.state.autonomy_worker_task = asyncio.create_task(worker.start())
    return {"status": "started", "worker_id": worker.worker_id}


@router.post("/stop")
async def stop_worker(request: Request) -> Dict[str, Any]:
    worker = getattr(request.app.state, "autonomy_worker", None)
    if worker is None or not worker.is_running():
        return {"status": "stopped"}
    await worker.stop()
    task = getattr(request.app.state, "autonomy_worker_task", None)
    if task:
        task.cancel()
    return {"status": "stopped"}
