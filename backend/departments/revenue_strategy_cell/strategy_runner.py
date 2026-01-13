"""Revenue Strategy Cell Runner

Runs strategy generation cycles using local LLM via Ollama.

HOW TO RUN MANUALLY:
    from backend.departments.revenue_strategy_cell import StrategyRunner
    runner = StrategyRunner()
    result = runner.run_cycle(cash_collected_to_date=0.0)

WHERE OUTPUTS ARE SAVED:
    - Database: strategy_runs, strategy_play_cards, strategy_experiments, dispatch_packets tables
    - JSON file: backend/reports/strategy/latest_strategy.json

HOW TO VIEW LATEST:
    - API: GET /strategy/latest
    - Database: SELECT * FROM strategy_runs ORDER BY created_at DESC LIMIT 1
    - File: backend/reports/strategy/latest_strategy.json
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.llm_client import LLMClient, LLMNotConfiguredError
from backend.telemetry.signal_collector import SignalCollector
from backend.telemetry.bottleneck_detector import BottleneckDetector
from backend.playbooks.renderer import PlaybookRenderer
from backend.departments.revenue_strategy_cell.experiment_registry import ExperimentRegistry
from backend.departments.revenue_strategy_cell.artifact_factory import ArtifactFactory

from .storage.strategy_store import StrategyStore

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_DIR = Path(__file__).parent / "prompts"
REPORTS_DIR = PROJECT_ROOT / "backend" / "reports" / "strategy"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class StrategyRunner:
    """Runs strategy generation cycles."""

    def __init__(self):
        self.store = StrategyStore()
        self.llm_client = None
        self.signal_collector = SignalCollector()
        self.bottleneck_detector = BottleneckDetector()
        self.playbook_renderer = PlaybookRenderer()
        self.experiment_registry = ExperimentRegistry()
        self.artifact_factory = ArtifactFactory()
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize LLM client."""
        try:
            self.llm_client = LLMClient(provider=os.getenv("LLM_PROVIDER", "ollama"))
            if not self.llm_client.configured:
                logger.warning(
                    "LLM client not configured: %s", self.llm_client.init_error
                )
                self.llm_client = None
        except LLMNotConfiguredError as e:
            logger.warning("LLM client not configured: %s", e)
            self.llm_client = None

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts directory."""
        prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _calculate_math(self, cash_collected_to_date: float, goal_deadline: str) -> Dict[str, Any]:
        """Calculate required metrics."""
        goal_cash_target = 150000.0
        
        try:
            deadline = datetime.fromisoformat(goal_deadline.replace("Z", "+00:00"))
        except ValueError:
            deadline = datetime(2026, 1, 31, tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        days_remaining = max(1, (deadline - now).days)
        
        cash_remaining = max(0, goal_cash_target - cash_collected_to_date)
        required_daily_cash_pace = cash_remaining / days_remaining if days_remaining > 0 else 0
        pipeline_target = required_daily_cash_pace * 3
        
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "cash_collected_to_date": cash_collected_to_date,
            "cash_remaining": cash_remaining,
            "required_daily_cash_pace": required_daily_cash_pace,
            "pipeline_target": pipeline_target,
        }

    def _format_prompt(
        self,
        prompt_template: str,
        math_data: Dict[str, Any],
        signals: Dict[str, Any],
        bottleneck: Dict[str, Any],
        active_experiments: List[Dict[str, Any]],
        available_templates: Dict[str, List[str]],
    ) -> str:
        """Format prompt template with all context data."""
        # Build context section
        context_section = f"""
## CURRENT PERFORMANCE SIGNALS (Last 24h)
- Leads created: {signals.get('leads_created_24h', 0)}
- Replies: {signals.get('replies_24h', 0)}
- Calls booked: {signals.get('calls_booked_24h', 0)}
- Closes: {signals.get('closes_24h', 0)}
- Cash collected: ${signals.get('cash_collected_24h', 0):,.2f}
- Top objections: {', '.join(signals.get('top_objections', [])[:3]) if signals.get('top_objections') else 'None'}
- Top hooks: {', '.join(signals.get('top_hooks', [])[:3]) if signals.get('top_hooks') else 'None'}

## CURRENT BOTTLENECK
- Bottleneck: {bottleneck.get('bottleneck', 'UNKNOWN')}
- Explanation: {bottleneck.get('explanation', 'N/A')}
- Recommended Focus: {bottleneck.get('recommended_focus', 'N/A')}

## ACTIVE EXPERIMENTS (WIP: {len(active_experiments)}/{MAX_ACTIVE_EXPERIMENTS})
"""
        if active_experiments:
            for exp in active_experiments[:2]:
                context_section += f"- {exp.get('experiment_id', 'unknown')}: {exp.get('status', 'unknown')} (Play: {exp.get('play_id', 'N/A')})\n"
        else:
            context_section += "- None\n"
        
        context_section += f"""
## AVAILABLE PLAYBOOK TEMPLATES
- Offers: {', '.join(available_templates.get('offers', [])[:5]) if available_templates.get('offers') else 'None'}
- Outreach: {', '.join(available_templates.get('outreach', [])[:5]) if available_templates.get('outreach') else 'None'}
- Landing: {', '.join(available_templates.get('landing', [])[:3]) if available_templates.get('landing') else 'None'}
- Objections: {', '.join(available_templates.get('objections', [])[:3]) if available_templates.get('objections') else 'None'}

When generating plays, reference template IDs when applicable (e.g., "template_id": "DFY_48H_LAUNCH_KIT").
"""
        
        # Format main prompt with math data first
        formatted = prompt_template.format(**math_data)
        
        # Insert context after the PRIMARY OBJECTIVE section
        if "## PRIMARY OBJECTIVE" in formatted:
            parts = formatted.split("## PRIMARY OBJECTIVE", 1)
            if len(parts) == 2:
                after_objective = parts[1]
                # Find where CURRENT CONTEXT section starts
                if "## CURRENT CONTEXT" in after_objective:
                    # Replace CURRENT CONTEXT with our enhanced context
                    context_parts = after_objective.split("## CURRENT CONTEXT", 1)
                    if len(context_parts) == 2:
                        # Find end of CURRENT CONTEXT section (next ##)
                        rest = context_parts[1]
                        next_section_idx = rest.find("\n##")
                        if next_section_idx > 0:
                            formatted = parts[0] + "## PRIMARY OBJECTIVE" + context_parts[0] + context_section + "\n" + rest[next_section_idx:]
                        else:
                            formatted = parts[0] + "## PRIMARY OBJECTIVE" + context_parts[0] + context_section + rest
                    else:
                        formatted = parts[0] + "## PRIMARY OBJECTIVE" + context_section + "\n\n" + after_objective
                else:
                    # No CURRENT CONTEXT section, insert after PRIMARY OBJECTIVE
                    formatted = parts[0] + "## PRIMARY OBJECTIVE" + context_section + "\n\n" + after_objective
        else:
            # If structure is different, prepend context
            formatted = context_section + "\n\n" + formatted
        
        return formatted

    def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt."""
        if not self.llm_client:
            raise RuntimeError("LLM client not configured")
        
        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            
            if isinstance(response, dict):
                return response.get("content", "") or response.get("message", "") or str(response)
            return str(response)
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            raise

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response."""
        # Try to find JSON in the response
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to parse as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx : end_idx + 1])
                except json.JSONDecodeError:
                    pass
        
        return None

    def _repair_json(self, invalid_json: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair invalid JSON using LLM."""
        if not self.llm_client:
            return None
        
        repair_prompt = f"""Fix this JSON. Return ONLY valid JSON, no explanations, no markdown:

{invalid_json}

Return the fixed JSON:"""
        
        try:
            response = self._call_llm(repair_prompt)
            return self._extract_json(response)
        except Exception as e:
            logger.error("JSON repair failed: %s", e)
            return None

    def _validate_output(self, output: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate strategy output structure."""
        required_keys = ["scoreboard", "top_plays", "dispatch_packets", "today_execution_sprint", "fail_safes", "next_data_needed"]
        
        for key in required_keys:
            if key not in output:
                return False, f"Missing required key: {key}"
        
        if not isinstance(output.get("top_plays"), list):
            return False, "top_plays must be a list"
        
        if len(output["top_plays"]) != 3:
            return False, f"top_plays must contain exactly 3 plays, got {len(output['top_plays'])}"
        
        if not isinstance(output.get("dispatch_packets"), dict):
            return False, "dispatch_packets must be a dict"
        
        return True, None

    def run_cycle(
        self,
        cash_collected_to_date: float = 0.0,
        goal_deadline: str = "2026-01-31",
        force: bool = False,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run one strategy generation cycle."""
        start_time = time.time()
        run_id = f"strategy_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        logger.info("Starting strategy cycle: run_id=%s", run_id)
        
        try:
            # Check idempotency (prevent duplicate runs within 15 minutes unless forced)
            if not force:
                latest_run = self.store.get_latest_run()
                if latest_run:
                    latest_time = datetime.fromisoformat(latest_run["created_at"].replace("Z", "+00:00"))
                    time_diff = (datetime.now(timezone.utc) - latest_time).total_seconds()
                    if time_diff < 900:  # 15 minutes
                        logger.warning(
                            "Skipping run - last run was %d seconds ago (use force=True to override)",
                            time_diff
                        )
                        return {
                            "run_id": run_id,
                            "status": "skipped",
                            "message": "Last run was less than 15 minutes ago",
                            "latest_run": latest_run,
                        }
            
            # Collect signals
            signals = self.signal_collector.collect_24h_signals()
            self.signal_collector.save_signals(signals)
            
            # Detect bottleneck
            latest_strategy = self.store.get_latest_run()
            recent_output = None
            if latest_strategy:
                import json
                recent_output = json.loads(latest_strategy.get("output_json", "{}"))
            bottleneck = self.bottleneck_detector.detect(signals, recent_output)
            
            # Get active experiments
            active_experiments = self.experiment_registry.list_active_experiments()
            
            # Get available templates
            available_templates = self.playbook_renderer.list_templates()
            
            # Calculate math
            math_data = self._calculate_math(cash_collected_to_date, goal_deadline)
            
            # Load and format prompt
            prompt_template = self._load_prompt("director")
            prompt = self._format_prompt(
                prompt_template,
                math_data,
                signals,
                bottleneck,
                active_experiments,
                available_templates,
            )
            
            # Call LLM
            logger.info("Calling LLM for strategy generation...")
            raw_response = self._call_llm(prompt)
            
            # Extract JSON
            output = self._extract_json(raw_response)
            
            if not output:
                # Try repair
                logger.warning("Failed to extract JSON, attempting repair...")
                output = self._repair_json(raw_response)
            
            if not output:
                # Store error
                error_msg = "Failed to extract valid JSON from LLM response"
                logger.error(error_msg)
                
                self.store.create_run(
                    run_id=run_id,
                    output_json={"error": error_msg, "raw_response": raw_response[:1000]},
                    cash_collected_to_date=cash_collected_to_date,
                    goal_deadline=goal_deadline,
                    duration_ms=int((time.time() - start_time) * 1000),
                    status="failed",
                    error_message=error_msg,
                )
                
                return {
                    "run_id": run_id,
                    "status": "failed",
                    "error": error_msg,
                }
            
            # Validate output
            is_valid, validation_error = self._validate_output(output)
            if not is_valid:
                error_msg = f"Validation failed: {validation_error}"
                logger.error(error_msg)
                
                self.store.create_run(
                    run_id=run_id,
                    output_json=output,
                    cash_collected_to_date=cash_collected_to_date,
                    goal_deadline=goal_deadline,
                    duration_ms=int((time.time() - start_time) * 1000),
                    status="failed",
                    error_message=error_msg,
                )
                
                return {
                    "run_id": run_id,
                    "status": "failed",
                    "error": error_msg,
                }
            
            # Store in database
            duration_ms = int((time.time() - start_time) * 1000)
            stored_run = self.store.create_run(
                run_id=run_id,
                output_json=output,
                cash_collected_to_date=cash_collected_to_date,
                goal_deadline=goal_deadline,
                duration_ms=duration_ms,
                status="completed",
            )
            
            # Write to latest file
            latest_file = REPORTS_DIR / "latest_strategy.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump({
                    "run_id": run_id,
                    "created_at": stored_run["created_at"],
                    "output": output,
                }, f, indent=2)
            
            logger.info(
                "Strategy cycle completed: run_id=%s, duration_ms=%d, plays=%d",
                run_id,
                duration_ms,
                len(output.get("top_plays", [])),
            )
            
            return {
                "run_id": run_id,
                "status": "completed",
                "output": output,
                "duration_ms": duration_ms,
                "stored_run": stored_run,
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.exception("Strategy cycle failed: run_id=%s", run_id)
            
            self.store.create_run(
                run_id=run_id,
                output_json={"error": error_msg},
                cash_collected_to_date=cash_collected_to_date,
                goal_deadline=goal_deadline,
                duration_ms=duration_ms,
                status="failed",
                error_message=error_msg,
            )
            
            return {
                "run_id": run_id,
                "status": "failed",
                "error": error_msg,
                "duration_ms": duration_ms,
            }

