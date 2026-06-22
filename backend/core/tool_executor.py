from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from backend.core.approvals_store import ApprovalsStore
from backend.core.governance import build_policies
from backend.core.runtime_mode import ModeManager, RuntimeMode
from backend.tools.tool_registry import ToolRegistry, ToolSpec


class ToolExecutor:
    """
    Central enforcement point. EVERYTHING goes through this.
    """
    def __init__(self, mode_mgr: ModeManager, approvals: ApprovalsStore, registry: ToolRegistry, audit_cb: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        self.mode_mgr = mode_mgr
        self.approvals = approvals
        self.registry = registry
        self.policies = build_policies()
        self.audit_cb = audit_cb

    def _audit(self, event: str, data: Dict[str, Any]):
        if self.audit_cb:
            self.audit_cb(event, data)

    def execute(self, tool_name: str, args: Dict[str, Any], *, actor: str, autonomous: bool = True, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool through the governance system.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments/payload
            actor: Who is executing (agent name, "AutomationWorker", etc.)
            autonomous: Whether this is an autonomous execution (default: True)
            meta: Optional metadata (department, job_id, etc.)
        """
        state = self.mode_mgr.get()
        spec = self.registry.get(tool_name)
        policy = self.policies[state.mode]
        
        audit_meta = {"mode": state.mode.value, "tool": tool_name, "category": spec.category, "actor": actor, "autonomous": autonomous}
        if meta:
            audit_meta.update(meta)

        # COMMANDER mode blocks autonomous execution entirely
        if state.mode == RuntimeMode.COMMANDER and autonomous:
            self._audit("tool_blocked", {**audit_meta, "reason": "commander_mode"})
            return {"status": "blocked", "reason": "COMMANDER_MODE_BLOCKS_AUTONOMOUS", "tool": tool_name, "category": spec.category}

        # Category allowed?
        if spec.category not in policy.allowed:
            self._audit("tool_blocked", {**audit_meta, "reason": "category_not_allowed"})
            return {"status": "blocked", "reason": "CATEGORY_NOT_ALLOWED", "tool": tool_name, "category": spec.category}

        # Approval required?
        if spec.category in policy.approval_required and autonomous:
            req = self.approvals.create(
                requested_by=actor,
                tool_name=tool_name,
                tool_category=spec.category,
                payload=args,
                reason=f"Approval required in {state.mode.value}",
            )
            self._audit("approval_requested", {**audit_meta, "request_id": req.id})
            return {"status": "needs_approval", "request_id": req.id, "tool": tool_name, "category": spec.category}

        # Execute now
        self._audit("tool_executing", audit_meta)
        try:
            result = spec.handler(args)
            self._audit("tool_executed", {**audit_meta, "result": result})
            return {"status": "executed", "tool": tool_name, "category": spec.category, "result": result}
        except Exception as e:
            self._audit("tool_failed", {**audit_meta, "error": str(e)})
            return {"status": "failed", "tool": tool_name, "error": str(e)}

    def execute_approved(self, request_id: str, *, decided_by: str) -> Dict[str, Any]:
        req = self.approvals.get(request_id)
        if not req:
            return {"status": "error", "reason": "NOT_FOUND", "request_id": request_id}
        if req.status != "pending":
            return {"status": "error", "reason": f"NOT_PENDING({req.status})", "request_id": request_id}

        spec = self.registry.get(req.tool_name)
        payload = __import__("json").loads(req.payload_json)

        try:
            self.approvals.update_status(request_id, "approved", decided_by=decided_by, result={"approved": True})
            result = spec.handler(payload)
            self.approvals.update_status(request_id, "executed", decided_by=decided_by, result={"result": result})
            self._audit("approval_executed", {"request_id": request_id, "tool": req.tool_name, "decided_by": decided_by})
            return {"status": "executed", "request_id": request_id, "tool": req.tool_name, "result": result}
        except Exception as e:
            self.approvals.update_status(request_id, "failed", decided_by=decided_by, result={"error": str(e)})
            self._audit("approval_failed", {"request_id": request_id, "tool": req.tool_name, "decided_by": decided_by, "error": str(e)})
            return {"status": "failed", "request_id": request_id, "error": str(e)}
