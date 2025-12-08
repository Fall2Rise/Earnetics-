from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

try:
    from crewai import Agent as CrewAgent, Crew, Process, Task as CrewTask
except ImportError:  # pragma: no cover - optional dependency
    CrewAgent = None
    Crew = None
    Process = None
    CrewTask = None

logger = logging.getLogger(__name__)

AGENTS_CONFIG_PATH = Path("backend/agents/agents.yaml")
CREWS_CONFIG_PATH = Path("backend/agents/crews.yaml")


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _ensure_crewai_available() -> None:
    """Ensure CrewAI is installed and importable."""
    if CrewAgent is None or Crew is None or CrewTask is None or Process is None:
        raise RuntimeError(
            "CrewAI is not installed. Install it in your virtual env to run the revenue loop "
            "(e.g. `pip install crewai crewai-tools`)."
        )


def _llm_configured() -> bool:
    """
    Check for a generic LLM configuration.

    This is intentionally vendor-agnostic. Earnetics expects *some* language
    model configuration via one of the following:

    - LLM_PROVIDER (e.g. 'ollama', 'local', 'openrouter', 'grok', 'google', etc.)
    - LLM_MODEL
    - OLLAMA_BASE_URL / OLLAMA_HOST
    - LOCAL_LLM_ENDPOINT
    """
    return bool(
        os.getenv("LLM_PROVIDER")
        or os.getenv("LLM_MODEL")
        or os.getenv("OLLAMA_BASE_URL")
        or os.getenv("OLLAMA_HOST")
        or os.getenv("LOCAL_LLM_ENDPOINT")
    )


def _describe_llm_env() -> str:
    """Return a short description of the current LLM-related environment."""
    keys = [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "OLLAMA_BASE_URL",
        "OLLAMA_HOST",
        "LOCAL_LLM_ENDPOINT",
    ]
    parts = []
    for key in keys:
        val = os.getenv(key)
        if val:
            parts.append(f"{key}={val}")
    return ", ".join(parts) if parts else "no LLM-related env vars set"


@dataclass
class RevenueLoopResult:
    """
    Structured outcome of a full revenue loop iteration.

    These keys map to the outputs declared in crews.yaml under the
    `flows.revenue_loop` definition.
    """
    product_roadmap: Dict[str, Any]
    validated_opportunity: Dict[str, Any]
    automation_module_spec: Dict[str, Any]
    approved_module: Dict[str, Any]
    revenue_play_report: Dict[str, Any]


class RevenueLoopRunner:
    """
    Earnetics Revenue Loop Orchestrator.

    This class wires together:
    - agents.yaml  → defines your specialist agents
    - crews.yaml   → defines crews, tasks, and the "revenue_loop" flow

    It does NOT talk directly to any specific LLM vendor. All LLM handling is
    delegated to CrewAI and whatever provider you configure via environment
    variables (local Ollama, remote gateway, etc.).
    """

    def __init__(self) -> None:
        logger.info("Initializing RevenueLoopRunner...")
        self.agents_cfg = _load_yaml(AGENTS_CONFIG_PATH)
        self.crews_cfg = _load_yaml(CREWS_CONFIG_PATH)

        self.flows: Dict[str, Any] = self.crews_cfg.get("flows", {})
        self.crews_meta: Dict[str, Any] = self.crews_cfg.get("crews", {})
        self.tasks_cfg: Dict[str, Any] = self.crews_cfg.get("tasks", {})

        if "revenue_loop" not in self.flows:
            raise ValueError(
                "crews.yaml is missing a 'revenue_loop' flow definition under 'flows'."
            )

        logger.info("RevenueLoopRunner initialized. Flows available: %s", list(self.flows.keys()))

    def run(self, market_context: Dict[str, Any]) -> RevenueLoopResult:
        """
        Execute the full revenue loop for a given market context.

        `market_context` is injected as shared state; each crew step can read it
        and enrich the state with its own outputs.
        """
        _ensure_crewai_available()

        if not _llm_configured():
            env_desc = _describe_llm_env()
            raise RuntimeError(
                "Language model provider is not configured.\n"
                "Set a generic LLM configuration (for example):\n"
                "  LLM_PROVIDER=ollama\n"
                "  LLM_MODEL=llama3.1:8b\n"
                "  OLLAMA_BASE_URL=http://localhost:11434\n\n"
                f"Current LLM-related environment: {env_desc}"
            )

        logger.info("Starting Earnetics revenue loop with market context: %s", market_context)

        state: Dict[str, Any] = {"market_context": market_context}

        for step in self.flows.get("revenue_loop", []):
            step_name = step.get("name", "<unnamed>")
            logger.info("-" * 80)
            logger.info("▶ Running revenue loop step: %s", step_name)
            state_update = self._run_step(step, state)
            logger.debug("Step %s state update: %s", step_name, state_update)
            state.update(state_update)

        logger.info("✅ Revenue loop completed. Assembling result object.")

        return RevenueLoopResult(
            product_roadmap=state.get("product_roadmap", {}),
            validated_opportunity=state.get("validated_opportunity", {}),
            automation_module_spec=state.get("automation_module_spec", {}),
            approved_module=state.get("approved_module", {}),
            revenue_play_report=state.get("revenue_play_report", {}),
        )

    def _run_step(self, step: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single flow step by instantiating the configured crew and tasks."""
        crew_name = step["crew"]
        if crew_name not in self.crews_meta:
            raise KeyError(f"Crew '{crew_name}' not found in crews.yaml under 'crews'.")

        crew_def = self.crews_meta[crew_name]

        # Build agents and tasks for this crew
        agents = [self._build_agent(agent_key) for agent_key in crew_def.get("agents", [])]
        tasks = [self._build_task(task_key) for task_key in crew_def.get("tasks", [])]

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            max_rpm=crew_def.get("max_rpm", 4),
            verbose=True,
        )

        logger.info("Running crew '%s' for step '%s'", crew_name, step.get("name", crew_name))
        result = crew.kickoff(inputs=state)
        logger.debug("Crew '%s' raw result: %s", crew_name, result)

        return self._extract_outputs(step.get("outputs", []), result)

    def _build_agent(self, key: str) -> CrewAgent:
        """Instantiate a CrewAI agent from agents.yaml configuration."""
        if key not in self.agents_cfg:
            raise KeyError(f"Agent '{key}' not found in agents.yaml.")

        cfg = self.agents_cfg[key]

        # Note: LLM configuration is handled globally by CrewAI via env vars.
        # We keep the agent focused on role/goal/backstory and delegation flags.
        agent = CrewAgent(
            name=key,
            role=cfg.get("role", key),
            goal=cfg.get("goal", ""),
            backstory=cfg.get("backstory", ""),
            verbose=cfg.get("verbose", False),
            allow_delegation=cfg.get("allow_delegation", False),
        )

        logger.debug("Built agent '%s' with config: %s", key, cfg)
        return agent

    def _build_task(self, key: str) -> CrewTask:
        """Instantiate a CrewAI task from crews.yaml task configuration."""
        if key not in self.tasks_cfg:
            raise KeyError(f"Task '{key}' not found in crews.yaml under 'tasks'.")

        cfg = self.tasks_cfg[key]
        description = cfg.get("description", "")
        expected_output_schema = cfg.get("expected_output", {})

        task = CrewTask(
            description=description,
            expected_output=json.dumps(expected_output_schema),
            agent=self._build_agent(cfg["agent"]),
            # We intentionally keep `context=None` and rely on the shared `inputs`
            # passed to `crew.kickoff(inputs=state)` to avoid schema drift issues.
            context=None,
        )

        logger.debug("Built task '%s' with config: %s", key, cfg)
        return task

    def _extract_outputs(self, keys: List[str], result: Any) -> Dict[str, Any]:
        """
        Extract declared outputs from the crew result.

        The flow step lists which keys it expects (`outputs` in crews.yaml).
        We pull those out into the global `state` dict that flows through the loop.
        """
        outputs: Dict[str, Any] = {}

        if isinstance(result, dict):
            for key in keys:
                if key in result:
                    outputs[key] = result[key]
        else:
            # Some CrewAI versions may return non-dict types; log for debugging.
            logger.warning(
                "Crew result for expected outputs %s is not a dict (type=%s). "
                "Nothing extracted.",
                keys,
                type(result),
            )

        logger.debug("Extracted outputs: %s", outputs)
        return outputs
