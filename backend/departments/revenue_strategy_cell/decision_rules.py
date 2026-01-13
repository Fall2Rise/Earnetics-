"""Decision Rules - applies rules to experiments and plays."""

from typing import Any, Dict

from .experiment_registry import ExperimentRegistry


class DecisionRules:
    """Applies decision rules to experiments."""

    def __init__(self):
        self.registry = ExperimentRegistry()

    def evaluate_experiment(self, experiment_id: str, result: Dict[str, Any]) -> str:
        """Evaluate experiment result and return decision."""
        # Update experiment with result
        self.registry.update_experiment(experiment_id, result=result, status="completed")
        
        # Apply decision rules
        decision = self.registry.apply_decision_rules(experiment_id)
        
        if decision:
            return decision
        
        # Default: continue if first attempt
        exp = self.registry.get_experiment(experiment_id)
        if exp and exp.get("attempts", 0) < 2:
            return "CONTINUE"
        
        return "REDESIGN_REQUIRED"

