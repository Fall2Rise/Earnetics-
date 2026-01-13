"""Task Engine Router for managing corporate tasks."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.corporate_memory import CorporateMemory, Task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
memory = CorporateMemory()

class TaskCreateRequest(BaseModel):
    title: str
    department: str
    priority: str = "medium"
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}

class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("")
def create_task(req: TaskCreateRequest):
    task = Task(
        title=req.title,
        department=req.department,
        priority=req.priority,
        description=req.description,
        metadata=req.metadata
    )
    return memory.create_task(task.to_record())

@router.get("")
def list_tasks(department: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    tasks = memory.list_tasks(department=department, status=status)
    return {"tasks": tasks[:limit]}

@router.get("/{task_id}")
def get_task(task_id: int):
    task = memory.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/claim")
def claim_task(task_id: int, agent: str):
    # This is a bit of a hack since claim_next_task claims by department, 
    # but we want to claim a specific task.
    # We'll use mark_task_in_progress which allows setting agent/claimed_by
    try:
        return memory.mark_task_in_progress(task_id, claimed_by=agent, assigned_agent=agent)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{task_id}/complete")
def complete_task(task_id: int):
    try:
        memory.mark_task_complete(task_id)
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{task_id}/block")
def block_task(task_id: int, reason: str):
    try:
        memory.mark_task_blocked(task_id, reason=reason)
        return {"status": "blocked"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
