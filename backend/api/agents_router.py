from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.real_ai_agents import get_real_agent_status, AI_AGENT_CORPORATION
from backend.vector_memory import VectorMemoryStore
from backend.audit_log import list_events

router = APIRouter(prefix="/api/agents", tags=["agents"])
memory_store = VectorMemoryStore()


class AgentUpdatePayload(BaseModel):
    agent_name: str
    role: str | None = None
    division: str | None = None
    prompt: str | None = None
    memory_namespace: str | None = None


class MemoryPurgePayload(BaseModel):
    namespace: str


@router.get("/status")
def agent_status():
    return {"agent_status": get_real_agent_status()}


@router.post("/update")
def update_agent(payload: AgentUpdatePayload):
    agent = AI_AGENT_CORPORATION.agents.get(payload.agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if payload.role is not None:
        agent.role = payload.role
    if payload.division is not None:
        agent.division = payload.division
    if payload.prompt is not None:
        setattr(agent, "custom_prompt", payload.prompt)
    if payload.memory_namespace is not None:
        setattr(agent, "memory_namespace", payload.memory_namespace)
    return {"status": "updated", "agent": {"name": payload.agent_name, "role": getattr(agent, "role", None), "division": getattr(agent, "division", None)}}


@router.delete("/memory")
def purge_agent_memory(payload: MemoryPurgePayload):
    try:
        removed = memory_store.delete_namespace(payload.namespace)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "purged", "namespace": payload.namespace, "removed": removed}


@router.get("/roster")
def agent_roster():
    """Return a detailed roster for all agents with basic health/stats signals."""
    status = get_real_agent_status()
    agents = []
    for name, data in status.get("agents", {}).items():
        memory_entries = data.get("memory_entries", 0) or 0
        specialties = data.get("specialties") or []
        # Heuristic signals to make the UI useful without blocking on deeper telemetry
        experience = memory_entries
        skill_score = min(100, len(specialties) * 8 + memory_entries // 5)
        health = "operational"
        rank = "executive" if experience > 50 else "senior" if experience > 20 else "associate"
        agents.append(
            {
                "name": name,
                "role": data.get("role"),
                "division": data.get("division"),
                "department": data.get("department"),
                "memory_entries": memory_entries,
                "specialties": specialties,
                "health": health,
                "experience": experience,
                "skill_score": skill_score,
                "rank": rank,
            }
        )
    agents.sort(key=lambda a: (a["experience"], a["skill_score"]), reverse=True)
    return {
        "totals": {
            "total_agents": status.get("total_agents", len(agents)),
            "active_agents": status.get("active_agents", 0),
        },
        "agents": agents,
    }


@router.get("/activity")
def agent_activity(limit: int = 50):
    """Recent audit events (includes agent if present) for live activity feed."""
    events = list_events(limit=limit)
    return {"events": events[:limit]}
