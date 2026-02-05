from __future__ import annotations

import os
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Dict, Any

from backend.core.runtime_mode import ModeManager, RuntimeMode
from backend.core.governance import build_policies
from backend.core.tool_executor import ToolExecutor


def _require_admin(x_ops_token: str | None):
    expected = os.getenv("OPS_ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=500, detail="OPS_ADMIN_TOKEN not set in environment")
    if not x_ops_token or x_ops_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


class ModeSetRequest(BaseModel):
    mode: RuntimeMode
    reason: str = ""


def build_ops_router(mode_mgr: ModeManager, executor: ToolExecutor):
    router = APIRouter(prefix="/ops", tags=["ops"])
    policies = build_policies()

    @router.get("/mode")
    def get_mode():
        s = mode_mgr.get()
        return {"mode": s.mode.value, "changed_by": s.changed_by, "reason": s.reason}

    @router.post("/mode")
    def set_mode(req: ModeSetRequest, x_ops_token: str | None = Header(default=None, alias="X-Ops-Token")):
        _require_admin(x_ops_token)
        s = mode_mgr.set(req.mode, changed_by="admin", reason=req.reason)
        return {"mode": s.mode.value, "changed_by": s.changed_by, "reason": s.reason}

    @router.get("/policy")
    def get_policy():
        s = mode_mgr.get()
        return {"mode": s.mode.value, "policy": policies[s.mode].to_dict()}

    @router.get("/approvals")
    def list_approvals(status: str = "pending", limit: int = 50):
        items = executor.approvals.list(status=status, limit=limit)
        return {"count": len(items), "items": [i.__dict__ for i in items]}

    @router.post("/approvals/{request_id}/approve")
    def approve(request_id: str, x_ops_token: str | None = Header(default=None, alias="X-Ops-Token")):
        _require_admin(x_ops_token)
        return executor.execute_approved(request_id, decided_by="admin")

    @router.post("/approvals/{request_id}/reject")
    def reject(request_id: str, x_ops_token: str | None = Header(default=None, alias="X-Ops-Token")):
        _require_admin(x_ops_token)
        req = executor.approvals.get(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Not found")
        if req.status != "pending":
            raise HTTPException(status_code=400, detail=f"Not pending: {req.status}")
        executor.approvals.update_status(request_id, "rejected", decided_by="admin", result={"rejected": True})
        return {"status": "rejected", "request_id": request_id}

    @router.get("/tools")
    def list_tools():
        """List all registered tools (dev/testing endpoint)."""
        tools = executor.registry.list()
        return {
            "count": len(tools),
            "tools": [
                {
                    "name": spec.name,
                    "category": spec.category,
                    "description": spec.description,
                }
                for spec in tools.values()
            ],
        }

    class ToolExecuteRequest(BaseModel):
        tool_name: str
        args: Dict[str, Any] = {}
        actor: str = "admin"
        autonomous: bool = False

    @router.post("/execute")
    def execute_tool(
        req: ToolExecuteRequest,
        x_ops_token: str | None = Header(default=None, alias="X-Ops-Token"),
    ):
        """Execute a tool directly (dev/testing endpoint, requires OPS_ADMIN_TOKEN)."""
        _require_admin(x_ops_token)
        result = executor.execute(
            tool_name=req.tool_name,
            args=req.args,
            actor=req.actor,
            autonomous=req.autonomous,
        )
        return result

    @router.get("/ready")
    def ready(request: Request):
        """Readiness check: mode, tool_count, approvals_db_ok, memory_ok, stripe_ok (non-blocking)."""
        app = request.app
        mode_mgr = getattr(app.state, "mode_mgr", None)
        tool_registry = getattr(app.state, "tool_registry", None)
        approvals_store = getattr(app.state, "approvals", None)
        
        approvals_ok = True
        memory_ok = True
        stripe_ok = None
        
        # Approvals DB quick check (non-blocking)
        if approvals_store:
            try:
                # Simple ping: try to list one item
                approvals_store.list(limit=1)
            except Exception:
                approvals_ok = False
        
        # Memory quick check (non-blocking)
        memory_store = getattr(app.state, "vector_memory", None)
        if memory_store:
            try:
                # Simple ping: check if ready
                if hasattr(memory_store, "is_ready"):
                    memory_ok = memory_store.is_ready()
                else:
                    memory_ok = True  # Assume OK if no check method
            except Exception:
                memory_ok = False
        
        # Stripe is optional (don't block readiness if offline)
        stripe_ok = None
        try:
            tool_executor = getattr(app.state, "tool_executor", None)
            if tool_executor:
                # Non-blocking check: try to get account (will return error if not configured, but won't block)
                result = tool_executor.execute(
                    tool_name="stripe.get_account",
                    args={},
                    actor="OpsReady",
                    autonomous=False,
                    meta={"reason": "ready_check"},
                )
                if result.get("status") == "executed":
                    stripe_ok = result.get("result", {}).get("status") == "success"
                else:
                    stripe_ok = False  # Tool blocked or unavailable
        except Exception:
            stripe_ok = False
        
        # Get mode
        mode_value = None
        if mode_mgr:
            try:
                mode_state = mode_mgr.get()
                mode_value = mode_state.mode.value
            except Exception:
                pass
        
        # Get tool count
        tool_count = None
        if tool_registry:
            try:
                tool_count = tool_registry.count()
            except Exception:
                try:
                    tool_count = len(tool_registry.list())
                except Exception:
                    pass
        
        return {
            "ok": True,
            "pid": os.getpid(),
            "mode": mode_value,
            "tool_count": tool_count,
            "approvals_db_ok": approvals_ok,
            "memory_ok": memory_ok,
            "stripe_ok": stripe_ok,
        }

    return router
