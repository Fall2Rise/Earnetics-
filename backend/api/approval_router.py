from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.approval_queue import approval_queue

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


class ApprovalAction(BaseModel):
  note: Optional[str] = None


@router.get("")
def list_approvals(status: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=500)):
  try:
    requests = approval_queue.list_requests(status=status, limit=limit)
  except Exception as exc:  # pragma: no cover - defensive
    raise HTTPException(status_code=500, detail=str(exc)) from exc
  return {"approvals": [request.to_record() for request in requests]}


@router.post("/{request_id}/approve")
def approve_request(request_id: int, action: ApprovalAction):
  try:
    request = approval_queue.approve(request_id, note=action.note)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from exc
  except Exception as exc:  # pragma: no cover - defensive
    raise HTTPException(status_code=500, detail=str(exc)) from exc
  if not request:
    raise HTTPException(status_code=404, detail="Approval request not found")
  return {"status": "approved", "request": request.to_record()}


@router.post("/{request_id}/reject")
def reject_request(request_id: int, action: ApprovalAction):
  try:
    request = approval_queue.reject(request_id, reason=action.note)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from exc
  except Exception as exc:  # pragma: no cover - defensive
    raise HTTPException(status_code=500, detail=str(exc)) from exc
  if not request:
    raise HTTPException(status_code=404, detail="Approval request not found")
  return {"status": "rejected", "request": request.to_record()}
