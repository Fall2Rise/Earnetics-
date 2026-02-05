import yaml
from pathlib import Path
from copy import deepcopy
from typing import Dict, Any, List


CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


def load_yaml(name: str) -> dict:
  path = CONFIG_DIR / name
  with path.open("r", encoding="utf-8") as f:
    return yaml.safe_load(f)


class AgentSpec:
  def __init__(self, name: str, cfg: Dict[str, Any]):
    self.name = name
    self.cfg = cfg

  def __repr__(self):
    return f"<AgentSpec {self.name}: {self.cfg.get('role')}>"


class TaskSpec:
  def __init__(self, name: str, cfg: Dict[str, Any]):
    self.name = name
    self.cfg = cfg

  def __repr__(self):
    return f"<TaskSpec {self.name}: {self.cfg.get('description')[:40]}...>"


class CrewSpec:
  def __init__(self, name: str, cfg: Dict[str, Any]):
    self.name = name
    self.cfg = cfg

  @property
  def agents(self) -> List[str]:
    return self.cfg.get("agents", [])

  @property
  def tasks(self) -> List[str]:
    return self.cfg.get("tasks", [])

  def __repr__(self):
    return f"<CrewSpec {self.name}: {len(self.agents)} agents, {len(self.tasks)} tasks>"


class RevenueFlowRunner:
  """
  Bare-bones orchestrator for the Earnetics revenue loop using YAML specs.

  Later, you can replace `run_crew_phase` with actual CrewAI / MetaGPT
  invocations while keeping the same config files.
  """
  def __init__(self):
    agents_cfg = load_yaml("agents.yaml")
    tasks_cfg = load_yaml("tasks.yaml")
    crews_cfg = load_yaml("crews.yaml")

    self.agent_specs: Dict[str, AgentSpec] = {
      name: AgentSpec(name, cfg) for name, cfg in agents_cfg.items()
    }
    self.task_specs: Dict[str, TaskSpec] = {
      name: TaskSpec(name, cfg) for name, cfg in tasks_cfg.items()
    }

    self.crews: Dict[str, CrewSpec] = {
      name: CrewSpec(name, cfg) for name, cfg in crews_cfg["crews"].items()
    }
    self.flows = crews_cfg.get("flows", {})

  def run(self, flow_name: str = "revenue_loop", initial_state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if flow_name not in self.flows:
      raise ValueError(f"Flow '{flow_name}' not defined in crews.yaml")

    state: Dict[str, Any] = initial_state.copy() if initial_state else {}
    steps = self.flows[flow_name]

    print(f"\n=== Starting flow: {flow_name} ===\n")

    for step in steps:
      phase_name = step["name"]
      crew_name = step["crew"]
      inputs = step.get("inputs", [])
      outputs = step.get("outputs", [])

      crew_spec = self.crews[crew_name]

      print(f"\n--- PHASE: {phase_name} | CREW: {crew_name} ---")
      print(f"Agents: {crew_spec.agents}")
      print(f"Tasks: {crew_spec.tasks}")
      print(f"Inputs expected: {inputs}")
      print(f"Outputs produced: {outputs}")

      state = self.run_crew_phase(crew_spec, inputs, outputs, state)

    print("\n=== Flow complete ===\n")
    return state

  def run_crew_phase(
    self,
    crew_spec: CrewSpec,
    inputs: List[str],
    outputs: List[str],
    state: Dict[str, Any],
  ) -> Dict[str, Any]:
    """
    Placeholder "engine" for a crew phase.

    Right now:
      - Logs what would be done.
      - Synthesizes dummy outputs into the state.

    Upgrade path:
      - Replace this with real CrewAI crew initialization that uses
        self.agent_specs and self.task_specs for config.
    """
    phase_state = deepcopy(state)

    # Log input availability
    missing = [key for key in inputs if key not in phase_state]
    if missing:
      print(f"[WARN] Missing inputs for phase: {missing} (continuing anyway)")

    # Stub execution: in the real version, youd:
    #  1. Build a Crew from agents + tasks.
    #  2. Pass `phase_state` to that crew as context.
    #  3. Run and collect its structured outputs.
    for task_name in crew_spec.tasks:
      task_spec = self.task_specs[task_name]
      agent_name = task_spec.cfg["agent"]
      agent_spec = self.agent_specs[agent_name]

      print(f"  -> Task '{task_name}' executed by agent '{agent_name}' ({agent_spec.cfg['role']})")

    # Fake outputs for now  just mark them as generated
    for out_key in outputs:
      phase_state[out_key] = {
        "status": "generated",
        "by_crew": crew_spec.name,
      }

    return phase_state


if __name__ == "__main__":
  runner = RevenueFlowRunner()
  final_state = runner.run(
    flow_name="revenue_loop",
    initial_state={
      "current_revenue_state": {
        "daily_revenue": 0,
        "active_plays": [],
      },
      "historical_metrics": {
        "last_30_days": [],
      },
    },
  )
  print("\nFinal state keys:", list(final_state.keys()))
