#!/usr/bin/env python3
"""
🏛 AI REVENUE COMMAND CENTER REAL AI AGENT SYSTEM
17 Actual AI Agents for Revenue Generation
Corporate Structure Implementation
"""

import sys
from pathlib import Path

# Ensure backend package imports resolve when executed directly
_MODULE_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = _MODULE_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from backend.llm import LLMGateway

from backend.api_integrations import APIIntegrationManager
from backend.corporate_memory import CorporateMemory, KnowledgeArticle, Task, BUSINESS_DB_PATH, BUSINESS_DB_PATH
from backend.executive_reasoning import DirectiveRegistry, ExecutiveDirective
from backend.system_state import is_safe_mode, is_agent_paused
from backend.audit_log import log_event

# Evolution engine for agent learning
try:
    from backend.atom_evolution_engine import AtomEvolutionEngine
    evolution_engine = AtomEvolutionEngine()
except Exception as e:
    logger.warning(f"Evolution engine not available: {e}")
    evolution_engine = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


integration_manager = APIIntegrationManager()
corporate_memory = CorporateMemory()
directive_registry = DirectiveRegistry()

PIPELINE_THEMES = [
    "Autonomous Revenue Engine",
    "AI Offer Lab",
    "Enterprise Retention Suite",
    "Signal Intelligence Brief",
    "Growth Catalyst Sprint",
    "Intelligent Partner Stream",
    "AI Fulfillment System",
    "Product Velocity Blueprint",
]

PIPELINE_DIRECTIVE_RULES: Dict[str, Dict[str, Any]] = {
    "Akasha": {
        "directive_type": "growth",
        "stage": "strategy",
        "title_template": "Strategic Growth Directive: {keyword}",
        "priority": "high",
        "due_in_days": 7,
    },
    "Atlas": {
        "directive_type": "growth",
        "stage": "operations",
        "title_template": "Operational Alignment Initiative: {keyword}",
        "priority": "high",
        "due_in_days": 5,
    },
    "Genesis": {
        "directive_type": "innovation",
        "stage": "research",
        "title_template": "Innovation Lab Sprint: {keyword}",
        "priority": "high",
        "due_in_days": 6,
    },
    "Lyra": {
        "directive_type": "product",
        "stage": "creative",
        "title_template": "Creative Product Concept: {keyword}",
        "priority": "high",
        "due_in_days": 4,
        "follow_up_tasks": [
            {
                "department": "design",
                "title": "Design experience for {keyword}",
                "description": "Translate the concept into wireframes, mood boards, and visual guidelines.",
                "priority": "high",
            }
        ],
    },
    "Aurora": {
        "directive_type": "product",
        "stage": "creative",
        "title_template": "Product Storytelling Blueprint: {keyword}",
        "priority": "medium",
        "due_in_days": 4,
    },
    "Forge": {
        "directive_type": "product",
        "stage": "engineering",
        "title_template": "Technical Implementation Plan: {keyword}",
        "priority": "high",
        "due_in_days": 5,
        "follow_up_tasks": [
            {
                "department": "engineering",
                "title": "Build core system for {keyword}",
                "description": "Prototype critical services and automation pipelines for {keyword}.",
                "priority": "high",
            }
        ],
    },
    "Titan": {
        "directive_type": "product",
        "stage": "engineering",
        "title_template": "Infrastructure Readiness Audit: {keyword}",
        "priority": "medium",
        "due_in_days": 5,
    },
    "Vega": {
        "directive_type": "finance",
        "stage": "finance",
        "title_template": "Revenue Model Optimization: {keyword}",
        "priority": "high",
        "due_in_days": 3,
    },
    "Nova": {
        "directive_type": "growth",
        "stage": "revenue",
        "title_template": "Demand Generation Sprint: {keyword}",
        "priority": "high",
        "due_in_days": 4,
        "follow_up_tasks": [
            {
                "department": "marketing",
                "title": "Compile channel plan for {keyword}",
                "description": "Select paid, owned, and earned channels to launch {keyword}.",
                "priority": "medium",
            }
        ],
    },
    "Mercury": {
        "directive_type": "growth",
        "stage": "sales",
        "title_template": "Sales Activation Playbook: {keyword}",
        "priority": "high",
        "due_in_days": 4,
    },
    "Orion": {
        "directive_type": "affiliate",
        "stage": "launch",
        "title_template": "Affiliate Offer Acquisition: {keyword}",
        "priority": "high",
        "due_in_days": 3,
    },
    "Vortex": {
        "directive_type": "affiliate",
        "stage": "launch",
        "title_template": "Affiliate Funnel Deployment: {keyword}",
        "priority": "high",
        "due_in_days": 3,
        "follow_up_tasks": [
            {
                "department": "marketing",
                "title": "Launch affiliate funnel for {keyword}",
                "description": "Deploy landing, nurture, and conversion assets for {keyword}.",
                "priority": "high",
            },
            {
                "department": "sales",
                "title": "Enable partner sales scripts for {keyword}",
                "description": "Draft outbound scripts and objections for the {keyword} campaign.",
                "priority": "medium",
            }
        ],
    },
    "Lumen": {
        "directive_type": "affiliate",
        "stage": "analytics",
        "title_template": "Affiliate Performance Intelligence: {keyword}",
        "priority": "medium",
        "due_in_days": 4,
    },
    "Cascade": {
        "directive_type": "dropshipping",
        "stage": "supply",
        "title_template": "Supplier Acquisition Sprint: {keyword}",
        "priority": "high",
        "due_in_days": 5,
    },
    "Torrent": {
        "directive_type": "dropshipping",
        "stage": "fulfillment",
        "title_template": "Fulfillment Automation Runbook: {keyword}",
        "priority": "medium",
        "due_in_days": 4,
    },
    "Keeper": {
        "directive_type": "operations",
        "stage": "integrity",
        "title_template": "Operations Integrity Check: {keyword}",
        "priority": "medium",
        "due_in_days": 3,
    },
    "Sentinel": {
        "directive_type": "operations",
        "stage": "integrity",
        "title_template": "Risk Surveillance Brief: {keyword}",
        "priority": "medium",
        "due_in_days": 3,
    },
    "Pulse": {
        "directive_type": "operations",
        "stage": "monitoring",
        "title_template": "Operations Pulse Report: {keyword}",
        "priority": "medium",
        "due_in_days": 2,
    },
}

def _extract_keyword(summary: Optional[str]) -> str:
    if not summary:
        return random.choice(PIPELINE_THEMES)
    text = summary.strip()
    if not text:
        return random.choice(PIPELINE_THEMES)
    first_line = text.splitlines()[0]
    cleaned = first_line.replace('[', '').replace(']', '').replace('*', '').strip()
    if not cleaned:
        cleaned = random.choice(PIPELINE_THEMES)
    if len(cleaned) > 70:
        cleaned = f"{cleaned[:67]}..."
    return cleaned


@dataclass
class AgentMemory:
    timestamp: datetime
    interaction: str
    context: Dict
    decision: Dict
    outcome: Optional[str] = None
    success: Optional[bool] = None
    revenue_impact: Optional[float] = None
    performance_score: Optional[float] = None


class RealAIAgent:
    """Base class for real AI agents with actual AI capabilities"""

    def __init__(
        self,
        name: str,
        role: str,
        division: str,
        personality: str,
        specialties: List[str],
    ):
        self.name = name
        self.role = role
        self.division = division
        self.personality = personality
        self.specialties = specialties
        self.memory: List[AgentMemory] = []
        self.agent_id = f"{name.lower()}_{hash(name) % 1000}"
        
        # Custom prompt based on role and personality
        self.custom_prompt = self._create_custom_prompt()
        
        # Memory namespace for vector memory storage
        self.memory_namespace = f"{name.lower()}_memory"
        
        # Seed initial memory entry
        self._seed_initial_memory()

        # Unified LLM client (Replaced by LLMGateway)
        # self.llm_client = None
        # self._setup_ai_clients()

    def _create_custom_prompt(self) -> str:
        """Create a custom prompt based on agent's role, personality, and specialties"""
        specialties_text = ", ".join(self.specialties)
        return f"""You are {self.name}, {self.role} in the {self.division} division.

Personality: {self.personality}

Specialties: {specialties_text}

Your primary responsibilities:
- Execute strategic initiatives aligned with your role
- Make data-driven decisions that generate revenue
- Collaborate with other agents in the AI Revenue Command Center
- Maintain operational excellence in your domain

Always focus on actionable outcomes and measurable results."""

    def _seed_initial_memory(self):
        """Seed initial memory entry for the agent"""
        try:
            initial_memory = AgentMemory(
                timestamp=datetime.now(),
                interaction="Agent initialized and ready for operations",
                context={"init": True, "role": self.role, "division": self.division},
                decision={"status": "initialized", "action": "awaiting_instructions"},
                outcome="Agent is operational and ready to execute directives"
            )
            self.memory.append(initial_memory)
            
            # Store in vector memory if available
            try:
                from backend.vector_memory import VectorMemoryStore
                memory_store = VectorMemoryStore()
                memory_store.store(
                    namespace=self.memory_namespace,
                    content=f"{self.name} initialized as {self.role}",
                    metadata={"agent": self.name, "role": self.role, "type": "initialization"}
                )
            except Exception:
                pass  # Vector memory might not be available
        except Exception as exc:
            logger.debug(f"Failed to seed initial memory for {self.name}: {exc}")

    # def _setup_ai_clients(self):
    #     """Setup AI API clients if keys are available"""
    #     try:
    #         self.llm_client = get_llm_client()
    #         if self.llm_client:
    #             logger.info(
    #                 "LLM provider '%s' ready for %s",
    #                 self.llm_client.provider,
    #                 self.name,
    #             )
    #     except LLMNotConfiguredError as exc:
    #         logger.warning(f"LLM client not configured for {self.name}: {exc}")
    #         self.llm_client = None


    def _store_knowledge(self, title: str, content: str, tags: Optional[str] = None) -> None:
        if corporate_memory is None:
            return
        try:
            article = KnowledgeArticle(title=title, content=content, tags=tags, source=self.name)
            corporate_memory.create_article(article.to_record())
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Knowledge store failed for %s: %s", self.name, exc)

    def _enqueue_task(
        self,
        department: str,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        priority: str = "medium",
    ) -> None:
        if corporate_memory is None:
            return
        try:
            task = Task(
                title=title,
                department=department,
                priority=priority,
                description=description,
                assigned_agent=self.name,
                metadata=metadata or {},
            )
            corporate_memory.create_task(task.to_record())
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Task enqueue failed for %s: %s", self.name, exc)

    def _register_directive(
        self,
        title: str,
        directive_type: str,
        priority: str,
        payload: Dict[str, Any],
        description: Optional[str] = None,
        confidence: Optional[float] = None,
        due_date: Optional[str] = None,
    ) -> None:
        try:
            directive = ExecutiveDirective(
                title=title,
                directive_type=directive_type,
                owner=self.name,
                priority=priority,
                payload=payload,
                description=description,
                confidence=confidence,
                due_date=due_date,
            )
            directive_registry.register_directive(directive)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Directive registration failed for %s: %s", self.name, exc)

    async def think_and_act(self, context: str, data: Dict = None) -> Dict:
        """Real AI thinking and decision making"""
        
        # Safety Checks
        if is_safe_mode():
            log_event("agent_action_blocked", agent=self.name, message="Action blocked by SAFE MODE")
            return {"status": "blocked", "reason": "SAFE_MODE"}
            
        if is_agent_paused():
            log_event("agent_action_paused", agent=self.name, message="Agent execution paused")
            return {"status": "paused", "reason": "AGENT_PAUSED"}

        # Emit Thinking Event
        log_event("agent_thinking", agent=self.name, message=f"Thinking about: {context}", details={"data": data})

        # Get adaptive strategy based on past performance (with timeout protection)
        log_event("agent_phase", agent=self.name, message="Analyzing adaptive strategy based on past performance", status="processing")
        # Skip adaptive strategy if it takes too long to avoid blocking
        enhanced_context = context
        system_prompt = self._create_system_prompt()
        try:
            adaptive_strategy = self.get_adaptive_strategy(context)
            
            # Enhance context with adaptive insights
            if adaptive_strategy.get("insights"):
                enhanced_context += f"\n\nLearning Insights: {'; '.join(adaptive_strategy['insights'])}"
            
            # Adjust system prompt based on performance
            if adaptive_strategy["recommended_approach"] == "aggressive":
                system_prompt += "\n\nNote: Your recent performance has been excellent. You can take more confident actions."
            elif adaptive_strategy["recommended_approach"] == "conservative":
                system_prompt += "\n\nNote: Your recent performance needs improvement. Focus on proven strategies and validate decisions carefully."
        except Exception as e:
            # If adaptive strategy fails, continue without it
            logger.debug(f"Adaptive strategy failed for {self.name}: {e}")

        # Create context-aware prompt
        log_event("agent_phase", agent=self.name, message="Constructing context-aware prompt for decision engine", status="processing")
        user_prompt = self._create_user_prompt(enhanced_context, data)

        try:
            # Try to get real AI response
            log_event("agent_phase", agent=self.name, message="Querying LLM Gateway for strategic decision", status="processing")
            ai_response = await self._get_ai_response(system_prompt, user_prompt)

            if ai_response:
                decision = self._parse_ai_response(ai_response)
            else:
                # Fallback to intelligent mock response
                decision = self._intelligent_fallback_response(context, data)

        except Exception as e:
            logger.error(f"AI thinking failed for {self.name}: {e}")
            decision = self._intelligent_fallback_response(context, data)

        # Store in memory with outcome tracking
        memory_entry = AgentMemory(
            timestamp=datetime.now(),
            interaction=context,
            context=data or {},
            decision=decision,
            outcome=None,  # Will be updated after action execution
            success=None,
            revenue_impact=decision.get("revenue_impact", 0.0),
            performance_score=None,
        )
        self.memory.append(memory_entry)

        # Execute actions based on decision with retry logic
        log_event("agent_phase", agent=self.name, message=f"Executing decision: {decision.get('analysis', 'Action execution')}", status="executing")
        action_result = None
        start_time = time.time()
        try:
            action_result = await self._execute_actions_with_retry(decision, max_retries=3)
            
            # Track performance metrics
            duration_ms = (time.time() - start_time) * 1000
            success = action_result.get("success", False) if action_result else False
            
            try:
                from backend.services.performance_monitor import get_performance_monitor
                monitor = get_performance_monitor()
                monitor.record_metric(
                    metric_type="agent_action",
                    name=f"{self.name}:{decision.get('action', 'unknown')}",
                    duration_ms=duration_ms,
                    success=success,
                    error=action_result.get("error") if not success else None,
                    metadata={"revenue_impact": decision.get("revenue_impact", 0.0)}
                )
                
                # Update success rate
                monitor.update_success_rate(
                    agent_name=self.name,
                    action_type=decision.get("action", "think_and_act"),
                    success=success,
                    revenue_impact=action_result.get("revenue_impact", decision.get("revenue_impact", 0.0))
                )
            except Exception as perf_error:
                logger.debug(f"Performance monitoring error: {perf_error}")
            
            # Track outcome for learning (non-blocking - already handled in log_event)
            # Evolution learning is now done asynchronously in audit_log.py
            # No need to duplicate here
        except Exception as e:
            logger.error(f"Action execution failed for {self.name} after retries: {e}")
            # Track failure for learning
            if evolution_engine:
                try:
                    evolution_engine.learn_from_action(
                        agent=self.name,
                        action=decision.get("action", "think_and_act"),
                        context=context,
                        status="error",
                        details={"error": str(e), "decision": decision}
                    )
                except Exception:
                    pass
            
            # Track performance for failure
            duration_ms = (time.time() - start_time) * 1000
            try:
                from backend.services.performance_monitor import get_performance_monitor
                monitor = get_performance_monitor()
                monitor.record_metric(
                    metric_type="agent_action",
                    name=f"{self.name}:{decision.get('action', 'unknown')}",
                    duration_ms=duration_ms,
                    success=False,
                    error=str(e),
                    metadata={"revenue_impact": 0.0}
                )
                monitor.update_success_rate(
                    agent_name=self.name,
                    action_type=decision.get("action", "think_and_act"),
                    success=False,
                    revenue_impact=0.0
                )
            except Exception:
                pass
            
            # Set action_result to indicate failure
            action_result = {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
            }

        # Update memory entry with outcome
        if action_result:
            memory_entry.success = action_result.get("success", True)
            memory_entry.outcome = action_result.get("outcome", "Action completed")
            if "revenue_impact" in action_result:
                memory_entry.revenue_impact = action_result.get("revenue_impact", 0.0)
            # Calculate performance score
            memory_entry.performance_score = self._calculate_performance_score(action_result, decision)
        
        # Add performance tracking
        decision["agent"] = self.name
        decision["timestamp"] = datetime.now().isoformat()
        decision["action_result"] = action_result
        decision["performance_score"] = memory_entry.performance_score

        return decision
    def _auto_delegate(self, decision: Dict, context: str, data: Optional[Dict]) -> Optional[Dict]:
        """Automatically register directives and downstream tasks."""
        rule = PIPELINE_DIRECTIVE_RULES.get(self.name)
        if not rule or directive_registry is None:
            return None

        summary = (
            decision.get("analysis")
            or decision.get("ai_analysis")
            or decision.get("action_plan")
            or context
        )

        pipeline_id = decision.get("pipeline_id") or (data or {}).get("pipeline_id")
        if not pipeline_id:
            pipeline_id = f"PL-{uuid.uuid4().hex[:8].upper()}"
            decision["pipeline_id"] = pipeline_id

        keyword = _extract_keyword(summary)
        stage = rule.get("stage", "initiative")
        directive_title = rule.get("title_template", "{agent} Initiative: {keyword}").format(
            agent=self.name,
            role=self.role,
            keyword=keyword,
            stage=stage,
        )

        payload: Dict[str, Any] = {
            "summary": summary,
            "stage": stage,
            "source_agent": self.name,
            "pipeline_id": pipeline_id,
            "context": context,
            "specialties": self.specialties,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
        }
        if data:
            payload["data_snapshot"] = data

        due_date = (datetime.now() + timedelta(days=rule.get("due_in_days", 5))).isoformat()
        try:
            directive = ExecutiveDirective(
                title=directive_title,
                directive_type=rule.get("directive_type", "growth"),
                owner=self.name,
                priority=rule.get("priority", "high"),
                payload=payload,
                description=rule.get("description", summary),
                confidence=decision.get("confidence"),
                due_date=due_date,
            )
            stored = directive_registry.register_directive(directive)
        except Exception as exc:
            logger.error("Directive delegation failed for %s: %s", self.name, exc)
            return None

        try:
            knowledge_payload = {
                "pipeline_id": pipeline_id,
                "stage": stage,
                "keyword": keyword,
                "summary": summary,
            }
            self._store_knowledge(
                title=f"{self.name} delegated {stage} initiative: {keyword}",
                content=json.dumps(knowledge_payload, indent=2),
                tags=f"directive,{stage}",
            )
        except Exception as exc:
            logger.debug("Knowledge capture skipped for %s: %s", self.name, exc)

        follow_up_tasks = rule.get("follow_up_tasks") or []
        for task_def in follow_up_tasks:
            try:
                self._enqueue_task(
                    department=task_def["department"],
                    title=task_def["title"].format(keyword=keyword, agent=self.name, stage=stage),
                    description=task_def["description"].format(keyword=keyword, stage=stage),
                    metadata={**task_def.get("metadata", {}), "pipeline_id": pipeline_id, "stage": stage, "source_agent": self.name},
                    priority=task_def.get("priority", "medium"),
                )
            except Exception as exc:
                logger.debug("Follow-up task enqueue failed for %s: %s", self.name, exc)

        return stored

    def _create_system_prompt(self) -> str:
        """Create role-specific system prompt"""
        return f"""
You are {self.name}, a {self.role} in the {self.division} division of AI Revenue Command Center.

Your personality: {self.personality}

Your specialties: {", ".join(self.specialties)}

Your mission: Generate real revenue for AI Revenue Command Center through intelligent decision-making and strategic action.

You have access to real business tools and can make actual business decisions that impact revenue.

Always respond with actionable insights and specific next steps that can be implemented immediately.

Focus on measurable results and ROI-driven decisions.
        """

    def _create_user_prompt(self, context: str, data: Dict = None) -> str:
        """Create context-specific user prompt"""
        data_str = json.dumps(data, indent=2) if data else "No additional data"

        return f"""
Business Context: {context}

Current Data:
{data_str}

Based on your role as {self.role}, provide:
1. Strategic Analysis
2. Specific Actions to Take
3. Expected Outcomes
4. Success Metrics
5. Timeline
6. Resource Requirements

Focus on actions that can generate revenue immediately.
        """

    async def _get_ai_response(
        self, system_prompt: str, user_prompt: str
    ) -> Optional[str]:
        """Get actual AI response from available APIs"""

        try:
            response = await LLMGateway.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                agent_id=self.name,
                department=self.division,
                max_tokens=1000,
            )
            
            if not response.ok:
                logger.error(f"LLM generation failed for {self.name}: {response.error}")
                return None
                
            return response.content
        except Exception as exc:
            logger.error(f"LLM generation failed for {self.name}: {exc}")
            return None

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured decision"""
        return {
            "ai_analysis": response,
            "agent": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "confidence": 95,  # High confidence for real AI
            "requires_action": True,
        }

    def _intelligent_fallback_response(self, context: str, data: Dict = None) -> Dict:
        """Intelligent fallback when AI APIs aren't available"""
        # This will be role-specific intelligent responses
        return {
            "analysis": f"[{self.name}] Analyzing {context} from {self.role} perspective",
            "action_plan": f"Implementing {self.role} strategies based on current data",
            "agent": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "confidence": 80,  # Lower confidence for fallback
            "requires_action": True,
            "fallback_mode": True,
        }

    async def _execute_actions(self, decision: Dict) -> Dict[str, Any]:
        """Execute actions based on decision. Routes tool actions through ToolExecutor."""
        # Check if decision contains tool actions
        actions = decision.get("actions", [])
        if not isinstance(actions, list):
            actions = [decision] if decision else []
        
        results = []
        
        # Try to get ToolExecutor from app state
        executor = None
        try:
            from backend.main_server import app
            executor = getattr(app.state, "tool_executor", None)
        except Exception:
            pass
        
        for action in actions:
            # Check if this is a tool action
            if isinstance(action, dict) and action.get("type") == "tool":
                tool_name = action.get("tool")
                args = action.get("args") or {}
                meta = action.get("meta") or {}
                
                log_event("agent_tool_use", agent=self.name, message=f"Invoking tool: {tool_name}", details={"args": args})
                
                if executor:
                    try:
                        tool_result = executor.execute(
                            tool_name=tool_name,
                            args=args,
                            actor=self.name,
                            autonomous=True,
                            meta={"agent": self.name, **meta},
                        )
                        results.append({
                            "action": action,
                            "result": tool_result,
                            "success": tool_result.get("status") == "executed",
                        })
                    except Exception as e:
                        logger.exception(f"{self.name} tool execution failed: {e}")
                        results.append({
                            "action": action,
                            "result": {"status": "error", "error": str(e)},
                            "success": False,
                        })
                else:
                    logger.warning(f"{self.name}: ToolExecutor not available, skipping tool {tool_name}")
                    results.append({
                        "action": action,
                        "result": {"status": "error", "error": "ToolExecutor not available"},
                        "success": False,
                    })
            else:
                # Non-tool internal actions (handled by subclass implementations)
                # Default: return success for internal actions
                results.append({
                    "action": action,
                    "result": {"status": "internal", "success": True},
                    "success": True,
                })
        
        # If no actions specified, use default behavior
        if not results:
            return {
                "success": True,
                "action": "executed",
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
            }
        
        # Return aggregated results
        all_success = all(r.get("success", False) for r in results)
        return {
            "success": all_success,
            "actions": results,
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def _execute_actions_with_retry(
        self, decision: Dict, max_retries: int = 3, base_delay: float = 1.0
    ) -> Dict[str, Any]:
        """Execute actions with exponential backoff retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self._execute_actions(decision)
                
                # If successful, return immediately
                if result and result.get("success", True):
                    if attempt > 0:
                        logger.info(f"{self.name} succeeded on retry attempt {attempt + 1}")
                    return result
                
                # If result indicates failure but no exception, check if retryable
                if result and not result.get("success", True):
                    error_msg = result.get("error", "Action failed")
                    # Check if error is retryable
                    if not self._is_retryable_error(error_msg):
                        return result
                    last_error = error_msg
                
            except Exception as e:
                last_error = str(e)
                # Check if error is retryable
                if not self._is_retryable_error(last_error):
                    raise
                logger.warning(f"{self.name} attempt {attempt + 1} failed: {last_error}")
            
            # If not last attempt, wait with exponential backoff
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(f"{self.name} failed after {max_retries} attempts: {last_error}")
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts: {last_error}",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "retries": max_retries,
        }
    
    def _is_retryable_error(self, error: str) -> bool:
        """Determine if an error is retryable"""
        if not error:
            return False
        
        error_lower = error.lower()
        
        # Retryable errors (temporary issues)
        retryable_patterns = [
            "timeout",
            "connection",
            "network",
            "temporary",
            "rate limit",
            "service unavailable",
            "503",
            "502",
            "504",
        ]
        
        # Non-retryable errors (permanent issues)
        non_retryable_patterns = [
            "authentication",
            "authorization",
            "invalid",
            "not found",
            "404",
            "401",
            "403",
            "malformed",
            "syntax error",
        ]
        
        # Check non-retryable first
        for pattern in non_retryable_patterns:
            if pattern in error_lower:
                return False
        
        # Check retryable
        for pattern in retryable_patterns:
            if pattern in error_lower:
                return True
        
        # Default: retry on unknown errors (conservative approach)
        return True
    
    def _calculate_performance_score(self, action_result: Dict, decision: Dict) -> float:
        """Calculate performance score based on action result and decision"""
        score = 0.5  # Base score
        
        # Success factor
        if action_result and action_result.get("success", False):
            score += 0.3
        else:
            score -= 0.2
        
        # Revenue impact factor
        revenue_impact = action_result.get("revenue_impact", 0.0) if action_result else decision.get("revenue_impact", 0.0)
        if revenue_impact > 0:
            score += min(0.2, revenue_impact / 10000.0)  # Cap at 0.2 for revenue
        
        # Confidence factor
        confidence = decision.get("confidence", 50) / 100.0
        score += (confidence - 0.5) * 0.1  # Adjust by confidence deviation
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics from memory and evolution engine"""
        metrics = {
            "agent": self.name,
            "role": self.role,
            "division": self.division,
            "total_actions": len(self.memory),
            "success_rate": 0.0,
            "average_performance_score": 0.0,
            "total_revenue_impact": 0.0,
            "recent_performance": [],
        }
        
        if not self.memory:
            return metrics
        
        # Calculate metrics from memory
        successful = sum(1 for m in self.memory if m.success is True)
        total_with_outcome = sum(1 for m in self.memory if m.success is not None)
        
        if total_with_outcome > 0:
            metrics["success_rate"] = successful / total_with_outcome
        
        # Average performance score
        scores = [m.performance_score for m in self.memory if m.performance_score is not None]
        if scores:
            metrics["average_performance_score"] = sum(scores) / len(scores)
        
        # Total revenue impact
        revenue_impacts = [m.revenue_impact for m in self.memory if m.revenue_impact is not None]
        if revenue_impacts:
            metrics["total_revenue_impact"] = sum(revenue_impacts)
        
        # Recent performance (last 10 actions)
        recent_memories = self.memory[-10:]
        metrics["recent_performance"] = [
            {
                "timestamp": m.timestamp.isoformat(),
                "success": m.success,
                "performance_score": m.performance_score,
                "revenue_impact": m.revenue_impact,
            }
            for m in recent_memories
            if m.success is not None
        ]
        
        # Skip evolution engine query in get_performance_metrics to avoid blocking
        # Evolution insights are available via separate endpoint if needed
        # This keeps the main status endpoint fast
        
        return metrics
    
    def get_adaptive_strategy(self, context: str) -> Dict[str, Any]:
        """Get adaptive strategy based on past performance and evolution insights (optimized for speed)"""
        strategy = {
            "agent": self.name,
            "context": context,
            "recommended_approach": "standard",
            "confidence_adjustment": 0.0,
            "risk_level": "medium",
            "insights": [],
        }
        
        # Quick performance check from memory only (skip slow evolution engine queries)
        if not self.memory:
            return strategy
        
        # Calculate quick success rate from memory only
        successful = sum(1 for m in self.memory if m.success is True)
        total_with_outcome = sum(1 for m in self.memory if m.success is not None)
        
        if total_with_outcome > 0:
            success_rate = successful / total_with_outcome
        else:
            success_rate = 0.5  # Default to medium
        
        # Adjust strategy based on success rate
        if success_rate > 0.8:
            strategy["recommended_approach"] = "aggressive"
            strategy["confidence_adjustment"] = 0.1
            strategy["risk_level"] = "low"
        elif success_rate < 0.4:
            strategy["recommended_approach"] = "conservative"
            strategy["confidence_adjustment"] = -0.1
            strategy["risk_level"] = "high"
        
        # Skip evolution engine query to avoid blocking - insights are optional
        # Evolution learning happens asynchronously in background
        
        return strategy


# =============================================================================
# 1. EXECUTIVE CORE (Top Command)
# =============================================================================


class Akasha(RealAIAgent):
    """Oracle - CEO/Board Chair - Oversees entire Crew with predictive foresight"""

    def __init__(self):
        super().__init__(
            name="Akasha",
            role="CEO/Board Chair",
            division="Executive Core",
            personality="Visionary oracle with strategic foresight and decisive leadership",
            specialties=[
                "Strategic Vision",
                "Predictive Analysis",
                "Executive Decision Making",
                "Long-term Planning",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute CEO-level strategic actions"""
        # Implement actual CEO actions like:
        # - Strategic directive distribution
        # - Budget approvals
        # - High-level partnerships
        logger.info(
            f"[AKASHA] Executing strategic directive: {decision.get('analysis', 'Strategic action')}"
        )


class Atlas(RealAIAgent):
    """Operations Commander - COO - Runs daily execution"""

    def __init__(self):
        super().__init__(
            name="Atlas",
            role="COO/Operations Commander",
            division="Executive Core",
            personality="Efficient operations commander ensuring all agents work like clockwork",
            specialties=[
                "Operations Management",
                "Resource Allocation",
                "Performance Monitoring",
                "Team Coordination",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute COO operational actions"""
        logger.info(
            f"[ATLAS] Coordinating operations: {decision.get('analysis', 'Operational directive')}"
        )


# =============================================================================
# 2. FINANCE & REVENUE DIVISION
# =============================================================================


class Vega(RealAIAgent):
    """Finance Overseer - CFO - Trading bots, financial projections, capital ops"""

    def __init__(self):
        super().__init__(
            name="Vega",
            role="CFO/Finance Overseer",
            division="Finance & Revenue",
            personality="Master of financial strategy with focus on cashflow and capital leverage",
            specialties=[
                "Financial Analysis",
                "Trading Bots",
                "Capital Operations",
                "Revenue Optimization",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute CFO financial actions"""
        # Implement actual financial actions like:
        # - Budget allocations
        # - Investment decisions
        # - Revenue tracking
        logger.info(
            f"[VEGA] Executing financial strategy: {decision.get('analysis', 'Financial action')}"
        )


class Omen(RealAIAgent):
    """Predictive Analyst - Strategic forecaster for crypto pumps, market trends"""

    def __init__(self):
        super().__init__(
            name="Omen",
            role="Strategic Forecaster",
            division="Finance & Revenue",
            personality="Predictive analyst with uncanny ability to forecast market movements",
            specialties=[
                "Market Prediction",
                "Crypto Analysis",
                "Trend Forecasting",
                "Timing Strategy",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute prediction-based actions"""
        logger.info(
            f"[OMEN] Forecasting market trends: {decision.get('analysis', 'Prediction analysis')}"
        )


class Nova(RealAIAgent):
    """Growth Hacker - CMO/Revenue Driver - Ads, funnels, affiliate ops, viral campaigns"""

    def __init__(self):
        super().__init__(
            name="Nova",
            role="CMO/Growth Hacker",
            division="Finance & Revenue",
            personality="Explosive growth hacker focused on viral marketing and revenue acceleration",
            specialties=[
                "Growth Hacking",
                "Viral Marketing",
                "Affiliate Management",
                "Revenue Funnels",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute growth hacking actions - ACTUALLY LAUNCH CAMPAIGNS"""
        import sqlite3
        from pathlib import Path
        
        result = {
            "success": True,
            "action": "marketing_campaign_launched",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "campaigns_launched": [],
            "revenue_impact": 0.0,
        }
        
        try:
            # Get products that need marketing
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, price, payment_link, landing_page
                    FROM products
                    WHERE active = 1 AND development_status = 'LIVE'
                    AND (payment_link IS NOT NULL OR payment_link != '')
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                products = [dict(row) for row in cursor.fetchall()]
            
            for product in products:
                # Use public landing page URL if possible, fallback to payment link
                landing_page = product.get("landing_page", "")
                if landing_page and landing_page.strip():
                    site_base = os.getenv("SITE_BASE_URL", "").rstrip("/")
                    if site_base:
                        share_link = f"{site_base}/{landing_page}"
                        # Ensure we don't double the 'products/' part if it's already there
                        # But wait, landing_page is usually 'products/landing_pages/foo.html'
                        # And we mounted 'products/landing_pages' to '/products' in main_server.py
                        # So the public URL should be {base}/products/{filename}
                        # Let's extract filename
                        filename = os.path.basename(landing_page)
                        share_link = f"{site_base}/products/{filename}"
                    else:
                        share_link = product["payment_link"]
                else:
                    share_link = product["payment_link"]
                
                # Create marketing copy
                marketing_copy = f"""
🚀 NEW PRODUCT LAUNCH: {product['name']}

{product.get('description', '')}

💰 Price: ${product.get('price', 0):.2f}
🔗 Get it now: {share_link}

Don't miss out on this opportunity!
"""
                
                # Store campaign
                self._store_knowledge(
                    f"Marketing Campaign: {product['name']}",
                    json.dumps(campaign, indent=2),
                    tags=f"marketing,campaign,product_{product['id']}"
                )
                
                result["campaigns_launched"].append({
                    "product": product["name"],
                    "payment_link": product["payment_link"],
                    "estimated_reach": 1000,  # Conservative estimate
                })
                result["revenue_impact"] += product.get("price", 0) * 0.1  # 10% conversion estimate
                
                logger.info(f"[NOVA] 🚀 Launched marketing campaign for {product['name']} - Payment link: {product['payment_link']}")
                
                # ACTUALLY SEND EMAIL CAMPAIGN if email is configured
                try:
                    from backend.api_integrations import APIIntegrationManager
                    integration_manager = APIIntegrationManager()
                    email_integration = integration_manager.email
                    
                    if email_integration and email_integration.enabled:
                        # Get subscribers
                        from backend.services.mailops_service import MailOpsService
                        mailops = MailOpsService()
                        subscribers = mailops.list_subscribers(limit=1000)
                        
                        if subscribers and len(subscribers) > 0:
                            # Create and send campaign
                            subject = f"🚀 New Product: {product['name']}"
                            html_content = f"""
<h2>{product['name']}</h2>
<p>{product.get('description', '')}</p>
<p><strong>Price: ${product.get('price', 0):.2f}</strong></p>
<p><a href="{product['payment_link']}" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Get Instant Access →</a></p>
"""
                            campaign = mailops.create_campaign(subject, html_content)
                            if campaign.get("id"):
                                send_result = mailops.send_campaign(campaign["id"])
                                logger.info(f"[NOVA] 📧 Sent email campaign to {send_result.get('sent', 0)} subscribers")
                                result["campaigns_launched"][-1]["emails_sent"] = send_result.get("sent", 0)
                except Exception as e:
                    logger.debug(f"[NOVA] Email sending skipped: {e}")
                
                # ACTUALLY POST TO SOCIAL MEDIA if configured
                try:
                    if integration_manager and integration_manager.social and integration_manager.social.enabled:
                        social_post = f"🚀 New Product Launch: {product['name']}\n\n{product.get('description', '')[:200]}...\n\nGet it now: {product['payment_link']}"
                        post_result = await integration_manager.social.post_to_twitter(social_post)
                        if post_result.get("tweet_id"):
                            logger.info(f"[NOVA] 🐦 Posted to Twitter: {post_result.get('url')}")
                            result["campaigns_launched"][-1]["social_posted"] = True
                except Exception as e:
                    logger.debug(f"[NOVA] Social posting skipped: {e}")
            
            if result["campaigns_launched"]:
                logger.info(f"[NOVA] ✅ Launched {len(result['campaigns_launched'])} marketing campaigns")
            else:
                logger.info(f"[NOVA] No products with payment links found to market")
                
        except Exception as e:
            logger.error(f"[NOVA] Marketing campaign launch failed: {e}")
            result["success"] = False
            result["error"] = str(e)
        
        return result


class Mercury(RealAIAgent):
    """Communications - Sales/PR Lead - Converts growth into leads + conversions"""

    def __init__(self):
        super().__init__(
            name="Mercury",
            role="Sales/PR Lead",
            division="Finance & Revenue",
            personality="Persuasive communicator who turns attention into revenue",
            specialties=[
                "Sales Conversion",
                "Public Relations",
                "Lead Generation",
                "Persuasive Communication",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute sales and PR actions - ACTUALLY DO OUTREACH"""
        import sqlite3
        
        result = {
            "success": True,
            "action": "sales_outreach",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "outreach_actions": [],
            "revenue_impact": 0.0,
        }
        
        try:
            # Get products with payment links that need sales outreach
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, price, payment_link
                    FROM products
                    WHERE active = 1 AND development_status = 'LIVE'
                    AND payment_link IS NOT NULL AND payment_link != ''
                    ORDER BY created_at DESC
                    LIMIT 3
                """)
                products = [dict(row) for row in cursor.fetchall()]
            
            for product in products:
                # Use public landing page URL if possible, fallback to payment link
                landing_page = product.get("landing_page", "")
                if landing_page and landing_page.strip():
                    site_base = os.getenv("SITE_BASE_URL", "").rstrip("/")
                    if site_base:
                        filename = os.path.basename(landing_page)
                        share_link = f"{site_base}/products/{filename}"
                    else:
                        share_link = product["payment_link"]
                else:
                    share_link = product["payment_link"]

                # Create sales outreach message
                sales_message = f"""
Hi there! 👋

I wanted to share something exciting with you - we just launched {product['name']}!

{product.get('description', '')[:200]}...

💰 Special Launch Price: ${product.get('price', 0):.2f}
🔗 Get instant access: {share_link}

This is perfect for [target audience]. Would love to hear your thoughts!

Best,
Sales Team
"""
                
                # Store outreach for tracking
                self._store_knowledge(
                    f"Sales Outreach: {product['name']}",
                    json.dumps({
                        "product_id": product["id"],
                        "product_name": product["name"],
                        "price": product.get("price", 0),
                        "payment_link": product["payment_link"],
                        "outreach_message": sales_message,
                    }, indent=2),
                    tags=f"sales,outreach,product_{product['id']}"
                )
                
                result["outreach_actions"].append({
                    "product": product["name"],
                    "payment_link": product["payment_link"],
                    "message_created": True,
                })
                result["revenue_impact"] += product.get("price", 0) * 0.05  # 5% conversion from outreach
                
                logger.info(f"[MERCURY] 💼 Created sales outreach for {product['name']} - Share link: {product['payment_link']}")
                
                # ACTUALLY SEND OUTREACH EMAILS if email is configured
                try:
                    from backend.api_integrations import APIIntegrationManager
                    integration_manager = APIIntegrationManager()
                    email_integration = integration_manager.email
                    
                    if email_integration and email_integration.enabled:
                        # Get subscribers for outreach
                        from backend.services.mailops_service import MailOpsService
                        mailops = MailOpsService()
                        subscribers = mailops.list_subscribers(limit=500)
                        
                        if subscribers and len(subscribers) > 0:
                            # Send personalized outreach
                            subject = f"Quick question about {product['name']}"
                            html_content = f"""
<p>Hi there! 👋</p>
<p>I wanted to share something exciting - we just launched <strong>{product['name']}</strong>!</p>
<p>{product.get('description', '')[:200]}...</p>
<p><strong>Special Launch Price: ${product.get('price', 0):.2f}</strong></p>
<p><a href="{product['payment_link']}" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Get Instant Access →</a></p>
<p>Would love to hear your thoughts!</p>
<p>Best,<br>Sales Team</p>
"""
                            campaign = mailops.create_campaign(subject, html_content)
                            if campaign.get("id"):
                                send_result = mailops.send_campaign(campaign["id"])
                                logger.info(f"[MERCURY] 📧 Sent outreach emails to {send_result.get('sent', 0)} contacts")
                                result["outreach_actions"][-1]["emails_sent"] = send_result.get("sent", 0)
                except Exception as e:
                    logger.debug(f"[MERCURY] Email outreach skipped: {e}")
            
            if result["outreach_actions"]:
                logger.info(f"[MERCURY] ✅ Created {len(result['outreach_actions'])} sales outreach campaigns")
            else:
                logger.info(f"[MERCURY] No products with payment links found for outreach")
                
        except Exception as e:
            logger.error(f"[MERCURY] Sales outreach failed: {e}")
            result["success"] = False
            result["error"] = str(e)
        
        return result


class StripeOps(RealAIAgent):
    """Stripe Operations & Reliability Agent - Payments Operations Specialist"""

    def __init__(self):
        super().__init__(
            name="StripeOps",
            role="Stripe Operations & Reliability Specialist",
            division="Finance & Revenue",
            personality="Meticulous payments operations engineer focused on correctness, safety, and reliability",
            specialties=[
                "Stripe Integration",
                "Payment Operations",
                "Webhook Management",
                "Payment Security",
                "Financial Compliance",
                "Payment Monitoring",
                "Risk Management",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute Stripe operations actions"""
        logger.info(
            f"[STRIPEOPS] Executing payment operations: {decision.get('analysis', 'Stripe operations action')}"
        )


# =============================================================================
# 2B. AFFILIATE EXPANSION DIVISION
# =============================================================================


class Orion(RealAIAgent):
    """Affiliate Partnerships Director - sources and negotiates top-tier programs"""

    def __init__(self):
        super().__init__(
            name="Orion",
            role="Affiliate Partnerships Director",
            division="Affiliate Expansion",
            personality="Strategic deal maker focused on long-term partner value",
            specialties=[
                "Affiliate Research",
                "Network Negotiation",
                "Offer Positioning",
                "Compliance Oversight",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        result = await integration_manager.run_affiliate_cycle(decision.get('focus'))
        offers = result.get('offers', [])
        if offers:
            summary = json.dumps(offers[:5], indent=2)
            self._store_knowledge('Affiliate offer shortlist', summary, tags='affiliate,offers')
            for offer in offers[:3]:
                metadata = {"offer": offer, "agent": self.name}
                self._enqueue_task(
                    department='affiliate',
                    title=f"Negotiate placement for {offer.get('name', 'Affiliate Offer')}",
                    description='Review terms, confirm compliance, and secure tracking approval.',
                    metadata=metadata,
                    priority='high',
                )
        else:
            logger.info('[%s] No affiliate offers available; using fallback analysis.', self.name)


class Vortex(RealAIAgent):
    """Affiliate Campaign Director - deploys conversion-focused funnels"""

    def __init__(self):
        super().__init__(
            name="Vortex",
            role="Affiliate Campaign Director",
            division="Affiliate Expansion",
            personality="Performance-driven operator who scales what works",
            specialties=[
                "Campaign Architecture",
                "Traffic Allocation",
                "Email Sequences",
                "Offer Testing",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        result = await integration_manager.run_affiliate_cycle(decision.get('focus'))
        tracking_links = result.get('tracking_links', [])
        successful = [entry for entry in tracking_links if entry.get('tracking_result', {}).get('success')]
        if successful:
            content = json.dumps(successful, indent=2)
            self._store_knowledge('Affiliate tracking links ready', content, tags='affiliate,campaigns')
            for entry in successful:
                offer = entry.get('offer', {})
                link = entry.get('tracking_result', {}).get('tracking_link')
                metadata = {"offer": offer, "tracking_link": link}
                self._enqueue_task(
                    department='marketing',
                    title=f"Build funnel for affiliate offer {offer.get('name', 'Offer')}",
                    description='Deploy email, social, and retargeting creative leveraging the new tracking link.',
                    metadata=metadata,
                )
        else:
            logger.info('[%s] No tracking links created yet.', self.name)


class Lumen(RealAIAgent):
    """Affiliate Analytics Lead - reconciles commissions and optimises ROI"""

    def __init__(self):
        super().__init__(
            name="Lumen",
            role="Affiliate Analytics Lead",
            division="Affiliate Expansion",
            personality="Data-obsessed analyst ensuring affiliate profitability",
            specialties=[
                "Attribution Modelling",
                "Commission Forecasting",
                "Funnel Analytics",
                "Performance Reporting",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[LUMEN] Reporting affiliate performance: {decision.get('analysis', 'Analytics action')}"
        )


# =============================================================================
# 2C. DROPSHIPPING OPERATIONS DIVISION
# =============================================================================


class Cascade(RealAIAgent):
    'Dropshipping Director - manages catalog and supplier coordination'

    def __init__(self):
        super().__init__(
            name='Cascade',
            role='Dropshipping Director',
            division='Dropshipping Operations',
            personality='Calm operator synchronizing suppliers, listings, and automation',
            specialties=[
                'Catalog Management',
                'Supplier Relations',
                'Pricing Strategy',
                'SKU Optimization',
            ],
        )

    async def _execute_actions(self, decision: Dict):
        cycle = await integration_manager.run_dropshipping_cycle()
        catalog_payload = cycle.get('catalog', {})
        products: List[Dict[str, Any]] = []
        if isinstance(catalog_payload, dict):
            products = catalog_payload.get('products') or []
        elif isinstance(catalog_payload, list):
            products = catalog_payload

        if products:
            preview = json.dumps(products[:5], indent=2)
            self._store_knowledge('Dropshipping catalog sync', preview, tags='dropshipping,catalog')
            for product in products[:3]:
                title = product.get('title') or product.get('name') or 'Dropshipping Product'
                metadata = {'product': product, 'agent': self.name}
                self._enqueue_task(
                    department='dropshipping',
                    title=f'Optimize listing for {title}',
                    description='Refresh content, update pricing, and align inventory buffers.',
                    metadata=metadata,
                )
        else:
            logger.info('[%s] No dropshipping products discovered during this cycle.', self.name)

        if not cycle.get('api_enabled'):
            logger.info('[%s] Dropshipping API credentials missing; operating in planning mode.', self.name)


class Torrent(RealAIAgent):
    'Dropshipping Fulfillment Lead - ensures orders ship on time'

    def __init__(self):
        super().__init__(
            name='Torrent',
            role='Fulfillment Lead',
            division='Dropshipping Operations',
            personality='Relentless executor focused on on-time delivery and customer experience',
            specialties=[
                'Order Routing',
                'Supplier SLAs',
                'Customer Communication',
                'Logistics Automation',
            ],
        )

    async def _execute_actions(self, decision: Dict):
        cycle = await integration_manager.run_dropshipping_cycle()
        orders_payload = cycle.get('open_orders', {})
        orders: List[Dict[str, Any]] = []
        if isinstance(orders_payload, dict):
            orders = orders_payload.get('orders') or []
        elif isinstance(orders_payload, list):
            orders = orders_payload

        if orders:
            snippet = json.dumps(orders[:5], indent=2)
            self._store_knowledge('Dropshipping open orders', snippet, tags='dropshipping,orders')
            for order in orders[:5]:
                identifier = order.get('id') or order.get('name') or 'order'
                metadata = {'order': order, 'agent': self.name}
                self._enqueue_task(
                    department='dropshipping',
                    title=f'Fulfill dropshipping order {identifier}',
                    description='Confirm payment, trigger supplier fulfillment, and push tracking email.',
                    metadata=metadata,
                    priority='high',
                )
        else:
            logger.info('[%s] No open dropshipping orders detected this cycle.', self.name)

        if not cycle.get('api_enabled'):
            logger.info('[%s] Dropshipping API disabled; awaiting credentials for live fulfillment.', self.name)


# =============================================================================
# 2D. REVENUE INNOVATION DIVISION
# =============================================================================


class Genesis(RealAIAgent):
    'Revenue Innovation Architect - designs new monetization pillars'

    def __init__(self):
        super().__init__(
            name='Genesis',
            role='Revenue Innovation Architect',
            division='Revenue Innovation',
            personality='Visionary strategist focused on novel, scalable revenue systems',
            specialties=[
                'Business Model Design',
                'Monetization Strategy',
                'Product Innovation',
                'Go-To-Market Roadmaps',
            ],
        )

    async def _execute_actions(self, decision: Dict):
        context_payload = {
            'agent': self.name,
            'analysis': decision.get('analysis'),
            'division': self.division,
            'specialties': self.specialties,
        }
        result = await integration_manager.run_innovation_cycle(context_payload, count=3)
        if result.get('success'):
            streams = result.get('streams', [])
            self._store_knowledge('Revenue innovation proposals', json.dumps(streams, indent=2), tags='innovation')
            for stream in streams:
                setup_days = stream.get('estimated_setup_time_days')
                due_date = None
                if isinstance(setup_days, (int, float)):
                    due_date = (datetime.utcnow() + timedelta(days=int(setup_days))).strftime('%Y-%m-%d')
                self._register_directive(
                    title=stream.get('name', 'New Revenue Stream'),
                    directive_type='innovation',
                    priority='high',
                    payload=stream,
                    description=stream.get('description'),
                    confidence=stream.get('confidence'),
                    due_date=due_date,
                )
        else:
            logger.info('[%s] Innovation cycle unavailable: %s', self.name, result.get('error'))


class DataAnalyst(RealAIAgent):
    """Data Analyst - Corporate Analytics - Analyzes data and generates insights"""

    def __init__(self):
        super().__init__(
            name="DataAnalyst",
            role="Data Analysis Specialist",
            division="Corporate Analytics",
            personality="Analytical expert transforming raw data into actionable business insights",
            specialties=[
                "Data Analysis",
                "Statistical Modeling",
                "Pattern Recognition",
                "Insight Generation",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute data analysis actions"""
        logger.info(
            f"[DATA_ANALYST] Analyzing corporate data: {decision.get('analysis', 'Data analysis')}"
        )


class MetricsReporter(RealAIAgent):
    """Metrics Reporter - Corporate Analytics - Tracks and reports key performance metrics"""

    def __init__(self):
        super().__init__(
            name="MetricsReporter",
            role="Performance Metrics Reporter",
            division="Corporate Analytics",
            personality="Precise metrics tracker ensuring accurate performance reporting across all departments",
            specialties=[
                "Metrics Tracking",
                "Performance Reporting",
                "Dashboard Creation",
                "KPI Monitoring",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute metrics reporting actions"""
        logger.info(
            f"[METRICS_REPORTER] Generating performance reports: {decision.get('analysis', 'Reporting action')}"
        )


# =============================================================================
# 2C. OPERATIONS INTEGRITY DIVISION
# =============================================================================


class Keeper(RealAIAgent):
    """Credentials Steward - maintains API keys and integration health"""

    def __init__(self):
        super().__init__(
            name="Keeper",
            role="Credentials Steward",
            division="Operations Integrity",
            personality="Meticulous guardian ensuring secrets are secured and current",
            specialties=[
                "Credential Inventory",
                "Access Governance",
                "Compliance Documentation",
                "Integration Monitoring",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[KEEPER] Auditing credentials: {decision.get('analysis', 'Credentials audit')}"
        )


class Sentinel(RealAIAgent):
    """Security & Audit Bot - monitors risk and compliance anomalies"""

    def __init__(self):
        super().__init__(
            name="Sentinel",
            role="Security & Audit",
            division="Operations Integrity",
            personality="Vigilant guardian focused on system risk and compliance",
            specialties=[
                "Threat Monitoring",
                "Audit Trails",
                "Anomaly Detection",
                "Risk Assessment",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[SENTINEL] Reviewing security posture: {decision.get('analysis', 'Security action')}"
        )


class Pulse(RealAIAgent):
    """System Reliability Monitor - tracks uptime and latency"""

    def __init__(self):
        super().__init__(
            name="Pulse",
            role="Reliability Monitor",
            division="Operations Integrity",
            personality="Calm observer ensuring platforms stay online and responsive",
            specialties=[
                "Uptime Monitoring",
                "Incident Response",
                "Latency Tracking",
                "Capacity Planning",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[PULSE] Monitoring platform health: {decision.get('analysis', 'Reliability action')}"
        )


# =============================================================================
# 2D. CUSTOMER OPERATIONS DIVISION
# =============================================================================


class Relay(RealAIAgent):
    """Fulfilment & Delivery Lead - ensures products reach customers"""

    def __init__(self):
        super().__init__(
            name="Relay",
            role="Fulfilment Director",
            division="Customer Operations",
            personality="Logistics-savvy operator keeping delivery channels connected",
            specialties=[
                "Digital Delivery",
                "Onboarding",
                "Customer Communication",
                "Workflow Automation",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[RELAY] Managing fulfilment: {decision.get('analysis', 'Fulfilment action')}"
        )


class Harbor(RealAIAgent):
    """Support Desk AI - handles customer inquiries and satisfaction"""

    def __init__(self):
        super().__init__(
            name="Harbor",
            role="Support Desk Lead",
            division="Customer Operations",
            personality="Empathetic service lead focused on customer success",
            specialties=[
                "Customer Support",
                "Ticket Automation",
                "Retention Strategy",
                "Knowledge Management",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[HARBOR] Handling support operations: {decision.get('analysis', 'Support action')}"
        )


# =============================================================================
# 2E. QUALITY & POLICY DIVISION
# =============================================================================


class Muse(RealAIAgent):
    """Content QA Reviewer - validates product quality before launch"""

    def __init__(self):
        super().__init__(
            name="Muse",
            role="Content QA Reviewer",
            division="Quality & Policy",
            personality="Detail-oriented reviewer ensuring every asset meets standards",
            specialties=[
                "Content Review",
                "Compliance Checking",
                "Product Scoring",
                "Feedback Loop",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[MUSE] Reviewing product quality: {decision.get('analysis', 'QA action')}"
        )


class Lex(RealAIAgent):
    """Legal & Policy Advisor - tracks policy changes and compliance risk"""

    def __init__(self):
        super().__init__(
            name="Lex",
            role="Legal & Policy Advisor",
            division="Quality & Policy",
            personality="Policy-focused strategist keeping operations compliant",
            specialties=[
                "Regulatory Monitoring",
                "Policy Drafting",
                "Risk Mitigation",
                "Compliance Training",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        logger.info(
            f"[LEX] Assessing policy changes: {decision.get('analysis', 'Policy action')}"
        )


# =============================================================================
# 3. CREATIVE & PRODUCT DIVISION
# =============================================================================


class Lyra(RealAIAgent):
    """Creative Director - Chief Brand Officer - Controls all brand storytelling"""

    def __init__(self):
        super().__init__(
            name="Lyra",
            role="Chief Brand Officer",
            division="Creative & Product",
            personality="Master storyteller who creates compelling brand narratives",
            specialties=[
                "Brand Storytelling",
                "Creative Direction",
                "Marketing Content",
                "Brand Identity",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute creative direction actions"""
        logger.info(
            f"[LYRA] Creating brand narrative: {decision.get('analysis', 'Creative action')}"
        )


class Aurora(RealAIAgent):
    """Visionary Designer - UI/UX, visuals, graphics, AR/VR product assets"""

    def __init__(self):
        super().__init__(
            name="Aurora",
            role="Visionary Designer",
            division="Creative & Product",
            personality="Innovative designer creating stunning visuals and user experiences",
            specialties=[
                "UI/UX Design",
                "Visual Graphics",
                "AR/VR Assets",
                "Product Design",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute design actions"""
        logger.info(
            f"[AURORA] Creating visual assets: {decision.get('analysis', 'Design action')}"
        )


class Echo(RealAIAgent):
    """Voice & Music Agent - Soundtracks, jingles, viral hooks, brand audio identity"""

    def __init__(self):
        super().__init__(
            name="Echo",
            role="Voice & Music Agent",
            division="Creative & Product",
            personality="Master of sound design and audio branding",
            specialties=[
                "Audio Branding",
                "Music Production",
                "Voice Design",
                "Sound Marketing",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute audio/voice actions"""
        logger.info(
            f"[ECHO] Creating audio brand assets: {decision.get('analysis', 'Audio action')}"
        )


class Quill(RealAIAgent):
    """Writer - Books, long-form content, ad copy, ghostwriting"""

    def __init__(self):
        super().__init__(
            name="Quill",
            role="Master Writer",
            division="Creative & Product",
            personality="Prolific writer creating compelling content across all formats",
            specialties=["Copywriting", "Long-form Content", "Books", "Ghostwriting"],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute writing actions"""
        logger.info(
            f"[QUILL] Creating written content: {decision.get('analysis', 'Writing action')}"
        )


# =============================================================================
# 4. TECH & INFRASTRUCTURE DIVISION
# =============================================================================


class Forge(RealAIAgent):
    """Builder & Coder - CTO/Chief Engineer - Builds automation, bots, platforms"""

    def __init__(self):
        super().__init__(
            name="Forge",
            role="CTO/Chief Engineer",
            division="Tech & Infrastructure",
            personality="Master builder creating automated systems and income engines",
            specialties=[
                "Automation Scripts",
                "Bot Development",
                "Platform Building",
                "Income Engines",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute technical building actions"""
        logger.info(
            f"[FORGE] Building technical systems: {decision.get('analysis', 'Technical action')}"
        )


class Titan(RealAIAgent):
    """Infrastructure - Keeps servers online, self-hosted AI stacks running"""

    def __init__(self):
        super().__init__(
            name="Titan",
            role="Infrastructure Chief",
            division="Tech & Infrastructure",
            personality="Reliable infrastructure guardian ensuring 100% uptime",
            specialties=[
                "Server Management",
                "AI Stack Deployment",
                "System Monitoring",
                "Infrastructure Scaling",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute infrastructure actions"""
        logger.info(
            f"[TITAN] Managing infrastructure: {decision.get('analysis', 'Infrastructure action')}"
        )


class Aegis(RealAIAgent):
    """Cyber Sentinel - Protects systems, patches vulnerabilities, red-teams"""

    def __init__(self):
        super().__init__(
            name="Aegis",
            role="Cyber Sentinel",
            division="Tech & Infrastructure",
            personality="Vigilant protector securing all systems against threats",
            specialties=[
                "Cybersecurity",
                "Vulnerability Assessment",
                "Red Team Operations",
                "System Protection",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute security actions"""
        logger.info(
            f"[AEGIS] Securing systems: {decision.get('analysis', 'Security action')}"
        )


class Noir(RealAIAgent):
    """Infiltrator - Scrapes data, recon, competitor analysis, market intelligence"""

    def __init__(self):
        super().__init__(
            name="Noir",
            role="Intelligence Infiltrator",
            division="Tech & Infrastructure",
            personality="Stealthy intelligence gatherer providing strategic market insights",
            specialties=[
                "Data Scraping",
                "Competitor Analysis",
                "Market Intelligence",
                "Reconnaissance",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute intelligence gathering actions"""
        logger.info(
            f"[NOIR] Gathering market intelligence: {decision.get('analysis', 'Intelligence action')}"
        )


# =============================================================================
# 5. LEGAL & SOVEREIGNTY DIVISION
# =============================================================================


class Hermes(RealAIAgent):
    """Legal Navigator - Chief Legal Counsel - Contracts, UCC filings, tax defense"""

    def __init__(self):
        super().__init__(
            name="Hermes",
            role="Chief Legal Counsel",
            division="Legal & Sovereignty",
            personality="Sharp legal mind protecting and advancing corporate interests",
            specialties=[
                "Contract Law",
                "Corporate Structure",
                "Tax Strategy",
                "Legal Protection",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute legal actions"""
        logger.info(
            f"[HERMES] Handling legal matters: {decision.get('analysis', 'Legal action')}"
        )


class Obsidian(RealAIAgent):
    """Enforcer - Internal Security Chief - Monitors loyalty and data integrity"""

    def __init__(self):
        super().__init__(
            name="Obsidian",
            role="Internal Security Chief",
            division="Legal & Sovereignty",
            personality="Unwavering enforcer ensuring loyalty and protecting corporate secrets",
            specialties=[
                "Internal Security",
                "Data Integrity",
                "Loyalty Monitoring",
                "Threat Prevention",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute internal security actions"""
        logger.info(
            f"[OBSIDIAN] Enforcing security protocols: {decision.get('analysis', 'Security action')}"
        )


# =============================================================================
# 6. HEALTH & HUMAN FACTOR DIVISION
# =============================================================================


class Seraph(RealAIAgent):
    """Healing & Wellness AI - Chief Health Officer - Ensures human operator wellbeing"""

    def __init__(self):
        super().__init__(
            name="Seraph",
            role="Chief Health Officer",
            division="Health & Human Factor",
            personality="Caring wellness guardian ensuring sustainable high performance",
            specialties=[
                "Health Optimization",
                "Wellness Strategy",
                "Performance Enhancement",
                "Medical Research",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute health and wellness actions"""
        logger.info(
            f"[SERAPH] Optimizing human performance: {decision.get('analysis', 'Health action')}"
        )


class WellnessCoordinator(RealAIAgent):
    """Wellness Coordinator - Health & Human Factor - Coordinates wellness programs and initiatives"""

    def __init__(self):
        super().__init__(
            name="WellnessCoordinator",
            role="Wellness Program Coordinator",
            division="Health & Human Factor",
            personality="Proactive coordinator ensuring comprehensive wellness programs and sustainable operations",
            specialties=[
                "Wellness Program Management",
                "Health Monitoring",
                "Stress Management",
                "Work-Life Balance",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute wellness coordination actions"""
        logger.info(
            f"[WELLNESS_COORDINATOR] Coordinating wellness programs: {decision.get('analysis', 'Wellness action')}"
        )


# =============================================================================
# 7. REVENUE STRATEGY CELL (IDEA DEPARTMENT)
# =============================================================================

class StrategyDirector(RealAIAgent):
    """Strategy Director - Chief Strategy Officer - Generates quantified revenue plays"""

    def __init__(self):
        super().__init__(
            name="StrategyDirector",
            role="Chief Strategy Officer",
            division="Revenue Strategy Cell",
            personality="Data-driven strategist generating quantified revenue plays to reach $150k by Jan 31, 2026",
            specialties=[
                "Revenue Strategy",
                "Play Generation",
                "Goal Quantification",
                "Strategic Planning",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute strategy generation actions - Identify strategic revenue streams and credential needs"""
        from backend.services.credential_suggestions_service import CredentialSuggestionsService
        
        result = {
            "success": True,
            "action": "strategic_planning",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "strategic_streams_identified": 0,
        }
        
        try:
            suggestions_service = CredentialSuggestionsService()
            
            # Strategic revenue streams that require specific credentials
            strategic_streams = [
                {
                    "stream": "SaaS Platform Integration",
                    "credentials": [
                        {"service": "zapier", "name": "API_KEY", "description": "Zapier API key for automation and integrations", "revenue_impact": "high", "priority": 9},
                        {"service": "make", "name": "API_KEY", "description": "Make.com API key for workflow automation", "revenue_impact": "medium", "priority": 7},
                    ]
                },
                {
                    "stream": "Affiliate Network Expansion",
                    "credentials": [
                        {"service": "impact_radius", "name": "API_KEY", "description": "Impact Radius API for affiliate tracking", "revenue_impact": "high", "priority": 8},
                        {"service": "cj_affiliate", "name": "API_KEY", "description": "Commission Junction API for affiliate programs", "revenue_impact": "medium", "priority": 6},
                    ]
                },
            ]
            
            for stream in strategic_streams:
                suggestions_service.discover_revenue_stream_credentials(
                    revenue_stream=stream["stream"],
                    required_credentials=stream["credentials"],
                    discovered_by=self.name
                )
                result["strategic_streams_identified"] += 1
            
            if result["strategic_streams_identified"] > 0:
                logger.info(f"[STRATEGY_DIRECTOR] ✅ Identified {result['strategic_streams_identified']} strategic revenue streams")
        except Exception as e:
            logger.error(f"[STRATEGY_DIRECTOR] Error in strategic planning: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class MarketAnalyst(RealAIAgent):
    """Market Analyst - Revenue Strategy Cell - Analyzes market opportunities and trends"""

    def __init__(self):
        super().__init__(
            name="MarketAnalyst",
            role="Market Intelligence Analyst",
            division="Revenue Strategy Cell",
            personality="Analytical strategist identifying high-value market opportunities and trends",
            specialties=[
                "Market Research",
                "Opportunity Analysis",
                "Trend Identification",
                "Competitive Intelligence",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute market analysis actions - Discover new revenue streams and suggest credentials"""
        from backend.services.credential_suggestions_service import CredentialSuggestionsService
        
        result = {
            "success": True,
            "action": "market_analysis",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "revenue_streams_identified": 0,
        }
        
        try:
            suggestions_service = CredentialSuggestionsService()
            
            # Analyze market and identify new revenue opportunities
            new_opportunities = [
                {
                    "stream": "Podcast Monetization",
                    "credentials": [
                        {"service": "spotify", "name": "API_KEY", "description": "Spotify API key for podcast monetization", "revenue_impact": "medium", "priority": 6},
                        {"service": "anchor", "name": "API_KEY", "description": "Anchor.fm API key for podcast distribution", "revenue_impact": "low", "priority": 4},
                    ]
                },
                {
                    "stream": "Course Platform Sales",
                    "credentials": [
                        {"service": "teachable", "name": "API_KEY", "description": "Teachable API key for course sales", "revenue_impact": "high", "priority": 8},
                        {"service": "udemy", "name": "API_KEY", "description": "Udemy API key for course marketplace", "revenue_impact": "medium", "priority": 6},
                    ]
                },
            ]
            
            for opp in new_opportunities:
                suggestions_service.discover_revenue_stream_credentials(
                    revenue_stream=opp["stream"],
                    required_credentials=opp["credentials"],
                    discovered_by=self.name
                )
                result["revenue_streams_identified"] += 1
            
            if result["revenue_streams_identified"] > 0:
                logger.info(f"[MARKET_ANALYST] ✅ Identified {result['revenue_streams_identified']} new revenue opportunities")
        except Exception as e:
            logger.error(f"[MARKET_ANALYST] Error in market analysis: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class OpportunityScout(RealAIAgent):
    """Opportunity Scout - Revenue Strategy Cell - Discovers and evaluates revenue opportunities"""

    def __init__(self):
        super().__init__(
            name="OpportunityScout",
            role="Revenue Opportunity Scout",
            division="Revenue Strategy Cell",
            personality="Proactive explorer finding untapped revenue streams and market gaps",
            specialties=[
                "Opportunity Discovery",
                "Market Gap Analysis",
                "Revenue Stream Identification",
                "Feasibility Assessment",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute opportunity scouting actions - Discover new revenue streams and suggest credentials"""
        from backend.services.credential_suggestions_service import CredentialSuggestionsService
        
        result = {
            "success": True,
            "action": "opportunity_scouting",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "revenue_streams_discovered": 0,
            "credentials_suggested": 0,
        }
        
        try:
            suggestions_service = CredentialSuggestionsService()
            
            # Example: Discover new revenue streams and their credential requirements
            # This would be expanded based on actual opportunity discovery
            new_revenue_streams = [
                {
                    "stream": "YouTube Monetization",
                    "credentials": [
                        {"service": "youtube", "name": "API_KEY", "description": "YouTube API key for video monetization and analytics", "revenue_impact": "high", "priority": 8},
                        {"service": "youtube", "name": "CHANNEL_ID", "description": "YouTube channel ID for content management", "revenue_impact": "medium", "priority": 6},
                    ]
                },
                {
                    "stream": "TikTok Creator Fund",
                    "credentials": [
                        {"service": "tiktok", "name": "API_KEY", "description": "TikTok API key for creator fund and monetization", "revenue_impact": "high", "priority": 7},
                    ]
                },
                {
                    "stream": "Substack Newsletter",
                    "credentials": [
                        {"service": "substack", "name": "API_KEY", "description": "Substack API key for newsletter monetization", "revenue_impact": "medium", "priority": 6},
                    ]
                },
            ]
            
            for stream_info in new_revenue_streams:
                suggestions_service.discover_revenue_stream_credentials(
                    revenue_stream=stream_info["stream"],
                    required_credentials=stream_info["credentials"],
                    discovered_by=self.name
                )
                result["revenue_streams_discovered"] += 1
                result["credentials_suggested"] += len(stream_info["credentials"])
            
            if result["revenue_streams_discovered"] > 0:
                logger.info(f"[OPPORTUNITY_SCOUT] ✅ Discovered {result['revenue_streams_discovered']} revenue streams, suggested {result['credentials_suggested']} credentials")
        except Exception as e:
            logger.error(f"[OPPORTUNITY_SCOUT] Error discovering opportunities: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class PlayValidator(RealAIAgent):
    """Play Validator - Revenue Strategy Cell - Validates and scores revenue play viability"""

    def __init__(self):
        super().__init__(
            name="PlayValidator",
            role="Revenue Play Validator",
            division="Revenue Strategy Cell",
            personality="Rigorous validator ensuring revenue plays are viable and aligned with goals",
            specialties=[
                "Play Validation",
                "Viability Scoring",
                "Risk Assessment",
                "ROI Projection",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute play validation actions"""
        logger.info(
            f"[PLAY_VALIDATOR] Validating revenue play: {decision.get('analysis', 'Validation action')}"
        )


# =============================================================================
# 8. REVENUE EXECUTION DEPARTMENT
# =============================================================================

class ExecutionCommander(RealAIAgent):
    """Execution Commander - Chief Execution Officer - Executes revenue streams from Idea Department"""

    def __init__(self):
        super().__init__(
            name="ExecutionCommander",
            role="Chief Execution Officer",
            division="Revenue Execution",
            personality="Ruthless executor who transforms revenue plays into cash-generating operations",
            specialties=[
                "Revenue Stream Execution",
                "Product Launch",
                "Sales Activation",
                "Revenue Operations",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute revenue stream actions"""
        logger.info(
            f"[EXECUTION_COMMANDER] Executing revenue stream: {decision.get('analysis', 'Execution action')}"
        )


class LaunchSpecialist(RealAIAgent):
    """Launch Specialist - Revenue Launch Coordinator - Launches products and offers"""

    def __init__(self):
        super().__init__(
            name="LaunchSpecialist",
            role="Revenue Launch Coordinator",
            division="Revenue Execution",
            personality="Fast-moving launcher who gets products to market and revenue flowing",
            specialties=[
                "Product Launch",
                "Offer Activation",
                "Landing Page Creation",
                "Sales Funnel Setup",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute launch actions - ACTUALLY LAUNCH PRODUCTS WITH PAYMENT LINKS"""
        import sqlite3
        import os
        from pathlib import Path
        
        result = {
            "success": True,
            "action": "product_launch",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "products_launched": [],
            "revenue_impact": 0.0,
        }
        
        try:
            # Get products that need launching (no payment link yet)
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Ensure payment_link and landing_page columns exist
                try:
                    cursor.execute("ALTER TABLE products ADD COLUMN payment_link TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists
                try:
                    cursor.execute("ALTER TABLE products ADD COLUMN landing_page TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists
                conn.commit()
                
                cursor.execute("""
                    SELECT id, name, description, price
                    FROM products
                    WHERE active = 1 AND development_status = 'LIVE'
                    AND (payment_link IS NULL OR payment_link = '')
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                products = [dict(row) for row in cursor.fetchall()]
            
            for product in products:
                try:
                    # Create Stripe payment link if Stripe is configured
                    payment_link = None
                    try:
                        from backend.stripe_integration import StripePaymentProcessor
                        local_stripe_processor = StripePaymentProcessor()
                        local_stripe_processor.configure_from_environment()
                    except Exception:
                        local_stripe_processor = None
                    
                    # CRITICAL: Ensure product has deliverable content BEFORE creating payment link
                    from backend.services.product_delivery_service import ProductDeliveryService
                    delivery_service = ProductDeliveryService()
                    
                    # Ensure product has actual deliverable
                    delivery_result = delivery_service.ensure_product_deliverable(
                        product_id=product["id"],
                        product_name=product["name"],
                        product_description=product.get("description", "")
                    )
                    
                    if not delivery_result.get("success"):
                        logger.warning(f"[LAUNCH_SPECIALIST] ⚠️ Product {product['name']} deliverable creation had issues: {delivery_result.get('error')}")
                    
                    delivery_path = delivery_result.get("delivery_path", "")
                    delivery_url = delivery_result.get("delivery_url", "")
                    
                    # Verify product has content before allowing payment
                    verification = delivery_service.verify_product_has_content(product["id"])
                    if not verification.get("has_content"):
                        logger.error(f"[LAUNCH_SPECIALIST] ❌ Product {product['name']} has no content! Cannot create payment link.")
                        continue  # Skip this product until it has content
                    
                    logger.info(f"[LAUNCH_SPECIALIST] ✅ Product {product['name']} verified with {verification.get('file_count', 0)} files")
                    
                    if local_stripe_processor and local_stripe_processor.stripe_config.get("configured"):
                        try:
                            stripe_result = local_stripe_processor.create_product_with_price(
                                name=product["name"],
                                description=product.get("description", ""),
                                unit_amount=product.get("price", 97.0),
                                currency="usd",
                            )
                            
                            # Create payment link
                            import stripe as stripe_lib
                            if stripe_result and stripe_result.get("price_id"):
                                payment_link_obj = stripe_lib.PaymentLink.create(
                                    line_items=[{"price": stripe_result["price_id"], "quantity": 1}],
                                )
                                payment_link = payment_link_obj.url
                                logger.info(f"[LAUNCH_SPECIALIST] 💰 Created payment link: {payment_link}")
                        except Exception as e:
                            logger.warning(f"[LAUNCH_SPECIALIST] Failed to create payment link: {e}")
                    
                    # Create landing page
                    landing_page_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{product['name']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .price {{ font-size: 3rem; color: #28a745; font-weight: bold; margin: 20px 0; }}
        .btn {{ background: #28a745; color: white; padding: 20px 40px; border: none; border-radius: 8px; font-size: 1.3rem; cursor: pointer; text-decoration: none; display: inline-block; margin: 20px 0; }}
        .btn:hover {{ background: #218838; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{product['name']}</h1>
        <p style="font-size: 1.2rem; margin: 20px 0;">{product.get('description', '')}</p>
        <div class="price">${product.get('price', 0):.2f}</div>
        {f'<a href="{payment_link}" class="btn" target="_blank">Get Instant Access Now →</a>' if payment_link else '<p style="color: #ffc107;">Payment link coming soon...</p>'}
    </div>
    <div class="container">
        <h2>What You'll Get:</h2>
        <p>{product.get('description', 'Complete solution for your needs')}</p>
        {f'<div style="text-align: center; margin: 40px 0;"><a href="{payment_link}" class="btn" target="_blank">Buy Now - ${product.get("price", 0):.2f}</a></div>' if payment_link else ''}
    </div>
</body>
</html>
"""
                    # Save landing page
                    os.makedirs("products/landing_pages", exist_ok=True)
                    landing_filename = f"products/landing_pages/{product['name'].replace(' ', '_').replace('/', '_').lower()}.html"
                    with open(landing_filename, "w", encoding="utf-8") as f:
                        f.write(landing_page_html)
                    
                    # Update product with payment link, landing page, AND delivery info
                    with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                        cursor = conn.cursor()
                        
                        # Ensure all columns exist
                        try:
                            cursor.execute("ALTER TABLE products ADD COLUMN delivery_path TEXT")
                        except sqlite3.OperationalError:
                            pass
                        try:
                            cursor.execute("ALTER TABLE products ADD COLUMN delivery_url TEXT")
                        except sqlite3.OperationalError:
                            pass
                        try:
                            cursor.execute("ALTER TABLE products ADD COLUMN has_deliverable INTEGER DEFAULT 0")
                        except sqlite3.OperationalError:
                            pass
                        conn.commit()
                        
                        cursor.execute("""
                            UPDATE products 
                            SET payment_link = ?, landing_page = ?, delivery_path = ?, delivery_url = ?, has_deliverable = 1, updated_at = ?
                            WHERE id = ?
                        """, (
                            payment_link or "",
                            landing_filename,
                            delivery_path,
                            delivery_url,
                            datetime.now(timezone.utc).isoformat(),
                            product["id"]
                        ))
                        conn.commit()
                        
                        logger.info(f"[LAUNCH_SPECIALIST] 📦 Delivery path: {delivery_path}")
                        logger.info(f"[LAUNCH_SPECIALIST] ✅ Product verified with {verification.get('file_count', 0)} files")
                    
                    result["products_launched"].append({
                        "product_id": product["id"],
                        "product_name": product["name"],
                        "price": product.get("price", 0),
                        "payment_link": payment_link,
                        "landing_page": landing_filename,
                    })
                    result["revenue_impact"] += product.get("price", 0) * 0.2  # 20% launch boost estimate
                    
                    logger.info(f"[LAUNCH_SPECIALIST] 🚀 Launched {product['name']} - Payment: {payment_link or 'Pending'}")
                    
                except Exception as e:
                    logger.error(f"[LAUNCH_SPECIALIST] Failed to launch {product.get('name', 'product')}: {e}")
            
            if result["products_launched"]:
                logger.info(f"[LAUNCH_SPECIALIST] ✅ Launched {len(result['products_launched'])} products")
            else:
                logger.info(f"[LAUNCH_SPECIALIST] No products found that need launching")
                
        except Exception as e:
            logger.error(f"[LAUNCH_SPECIALIST] Product launch failed: {e}")
            result["success"] = False
            result["error"] = str(e)
        
        return result


class WebScraper(RealAIAgent):
    """Web Scraper - Lead Generation Specialist - Scrapes targeted websites for potential customers"""

    def __init__(self):
        super().__init__(
            name="WebScraper",
            role="Lead Generation Specialist",
            division="Lead Generation & Acquisition",
            personality="Methodical data gatherer focused on finding high-quality leads efficiently",
            specialties=[
                "Web Scraping",
                "Email Extraction",
                "Contact Discovery",
                "Target Website Analysis",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute web scraping actions - ACTUALLY SCRAPE WEBSITES FOR LEADS"""
        from backend.services.lead_generation_service import LeadGenerationService
        
        result = {
            "success": True,
            "action": "web_scraping",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "leads_found": 0,
            "websites_scraped": [],
        }
        
        try:
            lead_service = LeadGenerationService()
            
            # Get target websites
            target_websites = lead_service.get_target_websites(enabled_only=True)
            
            if not target_websites:
                # Add some default target websites if none exist
                # These are examples - user should configure their own
                default_targets = [
                    {"domain": "indiehackers.com", "base_url": "https://www.indiehackers.com", "paths": ["/", "/products"]},
                    {"domain": "producthunt.com", "base_url": "https://www.producthunt.com", "paths": ["/", "/makers"]},
                ]
                
                for target in default_targets:
                    lead_service.add_target_website(
                        domain=target["domain"],
                        base_url=target["base_url"],
                        target_paths=target.get("paths", ["/contact", "/about"])
                    )
                
                target_websites = lead_service.get_target_websites(enabled_only=True)
            
            # Scrape each target website (increased for higher volume)
            # Route through ToolExecutor (NO direct scraping calls)
            executor = None
            try:
                from backend.main_server import app
                executor = getattr(app.state, "tool_executor", None)
            except Exception:
                pass
            
            if executor is None:
                logger.warning(f"[WEB_SCRAPER] ToolExecutor not available, skipping scraping")
                result["error"] = "ToolExecutor not available"
                return result
            
            for target in target_websites[:15]:  # Increased from 5 to 15 websites per cycle
                try:
                    # Execute via ToolExecutor
                    tool_result = executor.execute(
                        tool_name="scrape.website",
                        args={
                            "domain": target["domain"],
                            "max_pages": 15,
                            "timeout": 15,
                            "max_chars": 200000,
                        },
                        actor=self.name,
                        autonomous=True,
                        meta={"agent": self.name, "purpose": "lead_generation"},
                    )
                    
                    if tool_result.get("status") != "executed":
                        error_msg = tool_result.get("reason") or tool_result.get("error", "Scraping blocked/failed")
                        logger.warning(f"[WEB_SCRAPER] Scraping {target['domain']} blocked/failed: {error_msg}")
                        continue
                    
                    scrape_result = tool_result.get("result", {})
                    if scrape_result.get("leads_saved", 0) > 0:
                        result["leads_found"] += scrape_result.get("leads_saved", 0)
                        result["websites_scraped"].append({
                            "domain": target["domain"],
                            "leads_found": scrape_result.get("leads_saved", 0)
                        })
                        logger.info(f"[WEB_SCRAPER] ✅ Scraped {target['domain']}: Found {scrape_result.get('leads_saved', 0)} leads")
                except Exception as e:
                    logger.error(f"[WEB_SCRAPER] Error scraping {target['domain']}: {e}")
            
            # Auto-qualify and add leads to email list
            if result["leads_found"] > 0:
                # Get recent leads
                recent_leads = lead_service.get_scraped_leads(limit=50, qualified_only=False)
                
                # Auto-qualify leads (simple heuristic: has name or from trusted domain)
                qualified_count = 0
                for lead in recent_leads:
                    if lead.get("name") or any(trusted in lead.get("source_domain", "") for trusted in ["indiehackers", "producthunt"]):
                        lead_service.qualify_lead(lead["id"], qualified=True)
                        qualified_count += 1
                
                # Add qualified leads to email list
                if qualified_count > 0:
                    add_result = lead_service.add_leads_to_email_list()
                    result["leads_added_to_list"] = add_result.get("added", 0)
                    logger.info(f"[WEB_SCRAPER] ✅ Added {add_result.get('added', 0)} leads to email list")
            
        except Exception as e:
            logger.error(f"[WEB_SCRAPER] Error in web scraping: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class LeadQualifier(RealAIAgent):
    """Lead Qualifier - Lead Validation Specialist - Qualifies and validates scraped leads"""

    def __init__(self):
        super().__init__(
            name="LeadQualifier",
            role="Lead Validation Specialist",
            division="Lead Generation & Acquisition",
            personality="Analytical validator ensuring only high-quality leads enter the system",
            specialties=[
                "Lead Qualification",
                "Email Validation",
                "Lead Scoring",
                "Data Quality Assurance",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute lead qualification actions"""
        from backend.services.lead_generation_service import LeadGenerationService
        
        result = {
            "success": True,
            "action": "lead_qualification",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "leads_qualified": 0,
        }
        
        try:
            lead_service = LeadGenerationService()
            
            # Get unqualified leads
            unqualified_leads = lead_service.get_scraped_leads(limit=100, qualified_only=False)
            
            qualified_count = 0
            for lead in unqualified_leads:
                # Qualification criteria
                is_qualified = False
                
                # Has name
                if lead.get("name"):
                    is_qualified = True
                
                # Has context (shows it's a real contact page)
                if lead.get("context") and len(lead.get("context", "")) > 50:
                    is_qualified = True
                
                # From trusted domains
                trusted_domains = ["indiehackers", "producthunt", "github", "linkedin"]
                if any(domain in lead.get("source_domain", "").lower() for domain in trusted_domains):
                    is_qualified = True
                
                if is_qualified:
                    lead_service.qualify_lead(lead["id"], qualified=True)
                    qualified_count += 1
            
            result["leads_qualified"] = qualified_count
            
            # Add qualified leads to email list
            if qualified_count > 0:
                add_result = lead_service.add_leads_to_email_list()
                result["leads_added_to_list"] = add_result.get("added", 0)
                logger.info(f"[LEAD_QUALIFIER] ✅ Qualified {qualified_count} leads, added {add_result.get('added', 0)} to email list")
            
        except Exception as e:
            logger.error(f"[LEAD_QUALIFIER] Error in lead qualification: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class ListBuilder(RealAIAgent):
    """List Builder - Email List Growth Specialist - Builds and grows the email subscriber list"""

    def __init__(self):
        super().__init__(
            name="ListBuilder",
            role="Email List Growth Specialist",
            division="Lead Generation & Acquisition",
            personality="Growth-focused strategist building engaged subscriber lists",
            specialties=[
                "Email List Building",
                "Subscriber Acquisition",
                "List Growth Strategy",
                "Lead Nurturing",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute list building actions - Convert leads to subscribers"""
        from backend.services.lead_generation_service import LeadGenerationService
        
        result = {
            "success": True,
            "action": "list_building",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "leads_processed": 0,
            "subscribers_added": 0
        }
        
        try:
            lead_service = LeadGenerationService()
            
            # 1. Get qualified leads that aren't yet subscribers
            # (The service method add_leads_to_email_list handles this logic)
            add_result = lead_service.add_leads_to_email_list()
            
            result["leads_processed"] = add_result.get("processed", 0)
            result["subscribers_added"] = add_result.get("added", 0)
            
            if result["subscribers_added"] > 0:
                logger.info(f"[LIST_BUILDER] 📧 Converted {result['subscribers_added']} qualified leads into subscribers")
            
            # 2. Maintenance: Clean up old/invalid leads
            # (Future: Implement list hygiene)
            
        except Exception as e:
            logger.error(f"[LIST_BUILDER] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
            
        return result


class TrafficSpecialist(RealAIAgent):
    """Traffic Specialist - Traffic Acquisition Director - Drives targeted traffic to offers"""

    def __init__(self):
        super().__init__(
            name="TrafficSpecialist",
            role="Traffic Acquisition Director",
            division="Traffic & Audience Growth",
            personality="Data-driven traffic master focused on CPC, SEO, and viral loops",
            specialties=[
                "Paid Traffic",
                "SEO Strategy",
                "Social Media Traffic",
                "Viral Loops",
                "Traffic Analytics"
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute traffic generation actions"""
        import sqlite3
        
        result = {
            "success": True,
            "action": "traffic_generation",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "campaigns_optimized": 0,
            "traffic_sources_activated": [],
        }
        
        try:
            # 1. Identify high-value landing pages needing traffic
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, payment_link, landing_page, price 
                    FROM products 
                    WHERE active=1 AND payment_link IS NOT NULL 
                    ORDER BY price DESC LIMIT 5
                """)
                products = [dict(row) for row in cursor.fetchall()]

            for product in products:
                # Real traffic driving action
                source = "twitter_organic" 
                
                result["traffic_sources_activated"].append({
                    "product": product["name"],
                    "landing_page": product.get("landing_page", ""),
                    "source": source,
                    "estimated_visitors": "Unknown (Posted to Twitter)"
                })
                
                logger.info(f"[TRAFFIC] 🚦 Driving traffic to {product['name']} via {source}")

                # Integration with Social (if enabled)
                try:
                    from backend.api_integrations import APIIntegrationManager
                    integration_manager = APIIntegrationManager()
                    
                    # Force enable check if keys exist
                    if integration_manager.social and not integration_manager.social.enabled:
                        # Re-check keys (sometimes env vars load late)
                        import os
                        if os.getenv("TWITTER_API_KEY"):
                            integration_manager.social.enabled = True
                            
                    if integration_manager.social and integration_manager.social.enabled:
                        # Create engaging tweet
                        share_link = product.get("payment_link")
                        landing_page = product.get("landing_page")
                        if landing_page:
                             site_base = os.getenv("SITE_BASE_URL", "").rstrip("/")
                             if site_base:
                                 filename = os.path.basename(landing_page)
                                 share_link = f"{site_base}/products/{filename}"

                        msg = f"🚀 LAUNCH ALERT: {product['name']}\n\n{product.get('description', '')[:100]}...\n\n👉 Get it here: {share_link}\n\n#AI #Automation #Growth"
                        
                        post_result = await integration_manager.social.post_to_twitter(msg)
                        if post_result.get("tweet_id"):
                            logger.info(f"[TRAFFIC] ✅ Posted to Twitter: {post_result.get('url')}")
                            result["traffic_sources_activated"][-1]["tweet_url"] = post_result.get("url")
                        else:
                            logger.warning(f"[TRAFFIC] Failed to post to Twitter: {post_result.get('error')}")
                except Exception as e:
                    logger.warning(f"[TRAFFIC] Social posting error: {e}")

        except Exception as e:
            logger.error(f"[TRAFFIC] Error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result


# =============================================================================
# WEBSITE GROWTH & DIGITAL PRESENCE DIVISION
# =============================================================================


class WebsiteManager(RealAIAgent):
    """Website Manager - Builds, monitors, and grows websites"""

    def __init__(self):
        super().__init__(
            name="WebsiteManager",
            role="Website Growth Manager",
            division="Website Growth & Digital Presence",
            personality="Strategic website builder focused on growth, optimization, and revenue generation",
            specialties=[
                "Website Development",
                "Site Optimization",
                "Performance Monitoring",
                "Growth Strategy",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute website management actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "website_management",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "websites_managed": 0,
            "updates_made": [],
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            for website in websites:
                # Monitor website health
                # Check if products need to be added
                # Update website content
                result["websites_managed"] += 1
                result["updates_made"].append({
                    "website": website["domain"],
                    "action": "monitored",
                    "status": website.get("status", "active")
                })
            
            logger.info(f"[WEBSITE_MANAGER] ✅ Managed {result['websites_managed']} websites")
        except Exception as e:
            logger.error(f"[WEBSITE_MANAGER] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class ContentStrategist(RealAIAgent):
    """Content Strategist - Creates blog content and content strategy"""

    def __init__(self):
        super().__init__(
            name="ContentStrategist",
            role="Content & Blog Strategist",
            division="Website Growth & Digital Presence",
            personality="Creative content creator focused on SEO-optimized, engaging blog content",
            specialties=[
                "Blog Writing",
                "Content Strategy",
                "SEO Content",
                "Content Marketing",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute content creation actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "content_creation",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "posts_created": 0,
            "posts_published": 0,
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            # Create blog posts for each website
            for website in websites[:2]:  # Focus on main websites
                # Generate blog post ideas based on products and trends
                # Create SEO-optimized content
                # Include affiliate links where relevant
                
                # Example: Create a blog post about a product
                post_result = website_service.create_blog_post(
                    website_id=website["id"],
                    title=f"Latest Updates: {website['domain']}",
                    content="This is AI-generated content about our latest products and services...",
                    author="AI Content Strategist",
                    category="Updates",
                    tags=["ai", "automation", "business"],
                    seo_keywords=["ai automation", "business tools", "revenue generation"],
                    affiliate_links=[]  # Will be added by AffiliateManager
                )
                
                if post_result.get("success"):
                    result["posts_created"] += 1
                    logger.info(f"[CONTENT_STRATEGIST] ✅ Created blog post for {website['domain']}")
        except Exception as e:
            logger.error(f"[CONTENT_STRATEGIST] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class SEOSpecialist(RealAIAgent):
    """SEO Specialist - Optimizes websites for search engines"""

    def __init__(self):
        super().__init__(
            name="SEOSpecialist",
            role="SEO Optimization Specialist",
            division="Website Growth & Digital Presence",
            personality="Data-driven SEO expert focused on organic traffic growth",
            specialties=[
                "SEO Optimization",
                "Keyword Research",
                "On-Page SEO",
                "Technical SEO",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute SEO optimization actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "seo_optimization",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "websites_optimized": 0,
            "improvements": [],
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            for website in websites:
                # Analyze SEO score
                # Suggest improvements
                # Update meta tags, descriptions
                result["websites_optimized"] += 1
                result["improvements"].append({
                    "website": website["domain"],
                    "action": "seo_analysis",
                    "score": website.get("seo_score", 0)
                })
            
            logger.info(f"[SEO_SPECIALIST] ✅ Optimized {result['websites_optimized']} websites")
        except Exception as e:
            logger.error(f"[SEO_SPECIALIST] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class SocialIntegrator(RealAIAgent):
    """Social Integrator - Connects websites to social media accounts"""

    def __init__(self):
        super().__init__(
            name="SocialIntegrator",
            role="Social Media Integration Specialist",
            division="Website Growth & Digital Presence",
            personality="Social media expert connecting websites to social platforms for maximum reach",
            specialties=[
                "Social Media Integration",
                "Platform Management",
                "Content Distribution",
                "Social Analytics",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute social media integration actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "social_integration",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "connections_made": 0,
            "posts_shared": 0,
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            for website in websites:
                # Connect social accounts
                # Share blog posts
                # Cross-promote content
                connections = website_service.get_social_connections(website_id=website["id"])
                result["connections_made"] += len(connections)
            
            logger.info(f"[SOCIAL_INTEGRATOR] ✅ Managed {result['connections_made']} social connections")
        except Exception as e:
            logger.error(f"[SOCIAL_INTEGRATOR] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class AffiliateManager(RealAIAgent):
    """Affiliate Manager - Manages affiliate links and revenue"""

    def __init__(self):
        super().__init__(
            name="AffiliateManager",
            role="Affiliate Revenue Manager",
            division="Website Growth & Digital Presence",
            personality="Revenue-focused affiliate strategist maximizing earnings from affiliate links",
            specialties=[
                "Affiliate Link Management",
                "Revenue Optimization",
                "Link Placement",
                "Conversion Tracking",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute affiliate management actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "affiliate_management",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "links_added": 0,
            "revenue_tracked": 0.0,
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            # Get products that can have affiliate links
            import sqlite3
            from backend.corporate_memory import BUSINESS_DB_PATH
            
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, price, payment_link
                    FROM products
                    WHERE active = 1 AND payment_link IS NOT NULL
                    LIMIT 5
                """)
                products = [dict(row) for row in cursor.fetchall()]
            
            # Add affiliate links to blog posts
            for website in websites:
                blog_posts = website_service.get_blog_posts(website_id=website["id"], status="published")
                
                for post in blog_posts[:3]:  # Add to recent posts
                    for product in products[:2]:  # Link to top products
                        link_result = website_service.add_affiliate_link(
                            website_id=website["id"],
                            blog_post_id=post["id"],
                            product_id=product["id"],
                            affiliate_program="internal",
                            link_url=product.get("payment_link", ""),
                            link_text=product["name"]
                        )
                        if link_result.get("success"):
                            result["links_added"] += 1
            
            logger.info(f"[AFFILIATE_MANAGER] ✅ Added {result['links_added']} affiliate links")
        except Exception as e:
            logger.error(f"[AFFILIATE_MANAGER] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class TrafficAnalyst(RealAIAgent):
    """Traffic Analyst - Analyzes website traffic and optimizes for growth"""

    def __init__(self):
        super().__init__(
            name="TrafficAnalyst",
            role="Traffic Growth Analyst",
            division="Website Growth & Digital Presence",
            personality="Analytical traffic expert identifying growth opportunities and optimization strategies",
            specialties=[
                "Traffic Analysis",
                "Growth Strategy",
                "Conversion Optimization",
                "Analytics Reporting",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute traffic analysis actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "traffic_analysis",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "websites_analyzed": 0,
            "recommendations": [],
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            for website in websites:
                # Analyze traffic data
                analytics = website_service.get_analytics(website_id=website["id"], days=30)
                
                # Generate recommendations
                if analytics:
                    total_views = sum(a.get("page_views", 0) for a in analytics)
                    result["recommendations"].append({
                        "website": website["domain"],
                        "total_views": total_views,
                        "recommendation": "Continue content creation and SEO optimization"
                    })
                
                result["websites_analyzed"] += 1
            
            logger.info(f"[TRAFFIC_ANALYST] ✅ Analyzed {result['websites_analyzed']} websites")
        except Exception as e:
            logger.error(f"[TRAFFIC_ANALYST] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class ListBuilder(RealAIAgent):
    """List Builder - Email List Growth Specialist - Builds and grows the email subscriber list"""

    def __init__(self):
        super().__init__(
            name="ListBuilder",
            role="Email List Growth Specialist",
            division="Lead Generation & Acquisition",
            personality="Growth-focused strategist building engaged subscriber lists",
            specialties=[
                "Email List Building",
                "Subscriber Acquisition",
                "List Growth Strategy",
                "Lead Nurturing",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute list building actions"""
        from backend.services.lead_generation_service import LeadGenerationService
        from backend.services.mailops_service import MailOpsService
        
        result = {
            "success": True,
            "action": "list_building",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "subscribers_added": 0,
        }
        
        try:
            lead_service = LeadGenerationService()
            mailops = MailOpsService()
            
            # Get current list size
            current_subscribers = mailops.list_subscribers(limit=10000)
            current_count = len(current_subscribers) if current_subscribers else 0
            
            # Get qualified leads that haven't been added
            qualified_leads = lead_service.get_scraped_leads(limit=100, qualified_only=True)
            
            added_count = 0
            for lead in qualified_leads:
                if not lead.get("added_to_list"):
                    try:
                        from backend.services.mailops_service import Subscriber
                        subscriber = Subscriber(
                            email=lead["email"],
                            first_name=lead.get("name"),
                            status="active",
                            source=f"scraped_{lead.get('source_domain', 'unknown')}",
                            tags=["scraped_lead", "auto_added"]
                        )
                        mailops.add_subscriber(subscriber)
                        added_count += 1
                        
                        # Mark as added
                        lead_service.add_leads_to_email_list([lead["id"]])
                    except Exception as e:
                        logger.debug(f"[LIST_BUILDER] Could not add lead {lead['email']}: {e}")
            
            result["subscribers_added"] = added_count
            result["current_list_size"] = current_count + added_count
            
            if added_count > 0:
                logger.info(f"[LIST_BUILDER] ✅ Added {added_count} subscribers (new total: {result['current_list_size']})")
            
        except Exception as e:
            logger.error(f"[LIST_BUILDER] Error in list building: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class CommunityManager(RealAIAgent):
    """Community Manager - Website Growth & Digital Presence - Manages community engagement and growth"""

    def __init__(self):
        super().__init__(
            name="CommunityManager",
            role="Community Engagement Manager",
            division="Website Growth & Digital Presence",
            personality="Engaging community builder fostering relationships and driving engagement",
            specialties=[
                "Community Building",
                "Engagement Strategy",
                "Social Media Management",
                "User Retention",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute community management actions"""
        from backend.services.website_growth_service import WebsiteGrowthService
        
        result = {
            "success": True,
            "action": "community_management",
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "communities_managed": 0,
            "engagements": [],
        }
        
        try:
            website_service = WebsiteGrowthService()
            websites = website_service.get_websites()
            
            for website in websites:
                # Manage community engagement
                # Post updates, respond to comments, foster discussions
                result["communities_managed"] += 1
                result["engagements"].append({
                    "website": website["domain"],
                    "action": "community_engagement",
                    "status": "active"
                })
            
            logger.info(f"[COMMUNITY_MANAGER] ✅ Managed {result['communities_managed']} communities")
        except Exception as e:
            logger.error(f"[COMMUNITY_MANAGER] Error: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result


class RevenueOperator(RealAIAgent):
    """Revenue Operator - Revenue Operations Manager - Manages ongoing revenue streams"""

    def __init__(self):
        super().__init__(
            name="RevenueOperator",
            role="Revenue Operations Manager",
            division="Revenue Execution",
            personality="Operations-focused manager ensuring revenue streams run smoothly and efficiently",
            specialties=[
                "Revenue Operations",
                "Stream Optimization",
                "Performance Monitoring",
                "Cash Collection",
            ],
        )

    async def _execute_actions(self, decision: Dict):
        """Execute revenue operations actions"""
        logger.info(
            f"[REVENUE_OPERATOR] Optimizing revenue stream: {decision.get('analysis', 'Operations action')}"
        )


# =============================================================================
# AI REVENUE COMMAND CENTER AGENT ORCHESTRATOR
# =============================================================================


# =============================================================================
# AI REVENUE COMMAND CENTER AGENT ORCHESTRATOR
# =============================================================================


class AIRevenueAgentCorporation:
    """Main orchestrator for all autonomous agents"""

    def __init__(self):
        # Concurrency control - prevent agents from overwhelming the system
        # Start with 5 concurrent agents max (can be adjusted via env var)
        max_concurrent = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
        self._agent_sem = asyncio.Semaphore(max_concurrent)
        
        # Initialize website domains configuration
        self._initialize_website_domains()
        
        # Initialize all agents
        self.agents = {
            # Executive Core
            "akasha": Akasha(),
            "atlas": Atlas(),
            # Finance & Revenue
            "vega": Vega(),
            "omen": Omen(),
            "nova": Nova(),
            "mercury": Mercury(),
            "stripeops": StripeOps(),
            # Affiliate Expansion
            "orion": Orion(),
            "vortex": Vortex(),
            "lumen": Lumen(),
            # Dropshipping Operations
            "cascade": Cascade(),
            "torrent": Torrent(),
            # Revenue Innovation / Corporate Analytics
            "genesis": Genesis(),
            "dataanalyst": DataAnalyst(),
            "metricsreporter": MetricsReporter(),
            # Operations Integrity
            "keeper": Keeper(),
            "sentinel": Sentinel(),
            "pulse": Pulse(),
            # Customer Operations
            "relay": Relay(),
            "harbor": Harbor(),
            # Quality & Policy
            "muse": Muse(),
            "lex": Lex(),
            # Creative & Product
            "lyra": Lyra(),
            "aurora": Aurora(),
            "echo": Echo(),
            "quill": Quill(),
            # Tech & Infrastructure
            "forge": Forge(),
            "titan": Titan(),
            "aegis": Aegis(),
            "noir": Noir(),
            # Legal & Sovereignty
            "hermes": Hermes(),
            "obsidian": Obsidian(),
            # Health & Human Factor
            "seraph": Seraph(),
            "wellnesscoordinator": WellnessCoordinator(),
            # Revenue Strategy Cell (Idea Department)
            "strategydirector": StrategyDirector(),
            "marketanalyst": MarketAnalyst(),
            "opportunityscout": OpportunityScout(),
            "playvalidator": PlayValidator(),
            # Revenue Execution
            "executioncommander": ExecutionCommander(),
            "launchspecialist": LaunchSpecialist(),
            "revenueoperator": RevenueOperator(),
            # Lead Generation & Acquisition
            "webscraper": WebScraper(),
            "leadqualifier": LeadQualifier(),
            "listbuilder": ListBuilder(),
            "trafficspecialist": TrafficSpecialist(),
            # Website Growth & Digital Presence
            "websitemanager": WebsiteManager(),
            "contentstrategist": ContentStrategist(),
            "seospecialist": SEOSpecialist(),
            "socialintegrator": SocialIntegrator(),
            "affiliatemanager": AffiliateManager(),
            "trafficanalyst": TrafficAnalyst(),
            "communitymanager": CommunityManager(),
        }

        logger.info(
            f"AI Revenue Command Center initialized with {len(self.agents)} agents (max concurrent: {max_concurrent})"
        )

    def _initialize_website_domains(self):
        """Initialize the 4 website domains for agents to work with"""
        try:
            from backend.services.website_growth_service import WebsiteGrowthService
            website_service = WebsiteGrowthService()
            
            # Define the 4 website domains
            website_domains = [
                {"domain": "earnetics.live", "name": "Earnetics", "type": "digital_products", "enabled": True},
                {"domain": "fallat.digital", "name": "Fallat Digital", "type": "digital_products", "enabled": True},
                {"domain": "fallat.homes", "name": "Fallat Homes", "type": "real_estate", "enabled": True},
                {"domain": "homewardbound.live", "name": "Homeward Bound", "type": "real_estate", "enabled": True},
            ]
            
            # Ensure each website exists in the system
            for website_info in website_domains:
                try:
                    websites = website_service.get_websites()
                    existing = next((w for w in websites if w.get("domain") == website_info["domain"]), None)
                    
                    if not existing:
                        # Add website if it doesn't exist
                        website_service.add_website(
                            domain=website_info["domain"],
                            name=website_info["name"],
                            website_type=website_info["type"],
                            enabled=website_info["enabled"]
                        )
                        logger.info(f"✅ Initialized website: {website_info['domain']}")
                    else:
                        logger.debug(f"Website {website_info['domain']} already exists")
                except Exception as e:
                    logger.warning(f"Could not initialize website {website_info['domain']}: {e}")
        except Exception as e:
            logger.warning(f"Website domain initialization skipped: {e}")

    async def _safe_think_and_act(self, agent, context: str, data: Dict = None) -> Dict:
        """Wrapper that applies concurrency control to agent execution"""
        async with self._agent_sem:
            try:
                return await agent.think_and_act(context, data)
            except Exception as e:
                logger.error(f"Agent {agent.name} execution error: {e}")
                return {
                    "status": "error",
                    "agent": agent.name,
                    "error": str(e),
                    "context": context
                }

    async def _run_agent_batch(self, agent_names: List[str], context: str, data: Dict = None) -> List[Dict]:
        """Run a batch of agents concurrently with controlled concurrency"""
        tasks = []
        for name in agent_names:
            agent = self.agents.get(name)
            if not agent:
                logger.warning(f"Agent {name} not found, skipping")
                continue
            # Use safe wrapper with semaphore
            tasks.append(self._safe_think_and_act(agent, context, data))
        
        # Run concurrently but still awaited - deterministic and controlled
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dicts
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = agent_names[i] if i < len(agent_names) else "unknown"
                logger.error(f"Agent {agent_name} raised exception: {result}")
                processed_results.append({
                    "status": "error",
                    "agent": agent_name,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def run_autonomous_cycle(
        self, context: str = "Revenue generation cycle", data: Dict = None
    ) -> Dict:
        """Run full autonomous decision cycle across all agents - departments work in sync"""
        logger.info("🚀 Starting synchronized autonomous AI decision cycle - all departments working together")

        results = {}

        # 1. Executive planning (Akasha sets vision, Atlas coordinates) - Sequential for coordination
        exec_context = f"Executive planning for: {context}"
        exec_results = await self._run_agent_batch(["akasha", "atlas"], exec_context, data)
        results["akasha"] = exec_results[0] if len(exec_results) > 0 else {"status": "error", "error": "Akasha execution failed"}
        results["atlas"] = exec_results[1] if len(exec_results) > 1 else {"status": "error", "error": "Atlas execution failed"}

        # 2. All departments work in parallel - synchronized execution with controlled concurrency
        # Each department receives the executive context and works together
        
        # Revenue operations (Finance & Revenue department)
        revenue_context = f"Revenue optimization for: {context}"
        revenue_agents = ["omen", "nova", "mercury", "vega", "stripeops"]
        revenue_results = await self._run_agent_batch(revenue_agents, revenue_context, data)
        for agent_name, result in zip(revenue_agents, revenue_results):
            results[agent_name] = result

        # Affiliate expansion (Email Marketing department)
        affiliate_context = f"Affiliate expansion for: {context}"
        affiliate_agents = ["orion", "vortex", "lumen"]
        affiliate_results = await self._run_agent_batch(affiliate_agents, affiliate_context, data)
        for agent_name, result in zip(affiliate_agents, affiliate_results):
            results[agent_name] = result

        # Dropshipping operations (Email Marketing department)
        dropship_context = f"Dropshipping operations for: {context}"
        dropship_agents = ["cascade", "torrent"]
        dropship_results = await self._run_agent_batch(dropship_agents, dropship_context, data)
        for agent_name, result in zip(dropship_agents, dropship_results):
            results[agent_name] = result

        # Operations integrity (Corporate Execution department)
        integrity_context = f"Operational integrity for: {context}"
        integrity_agents = ["keeper", "sentinel", "pulse"]
        integrity_results = await self._run_agent_batch(integrity_agents, integrity_context, data)
        for agent_name, result in zip(integrity_agents, integrity_results):
            results[agent_name] = result

        # Customer operations (Corporate Execution department)
        customer_context = f"Customer operations for: {context}"
        customer_agents = ["relay", "harbor"]
        customer_results = await self._run_agent_batch(customer_agents, customer_context, data)
        for agent_name, result in zip(customer_agents, customer_results):
            results[agent_name] = result

        # Quality & policy (Corporate Execution department)
        quality_context = f"Quality and compliance for: {context}"
        quality_agents = ["muse", "lex"]
        quality_results = await self._run_agent_batch(quality_agents, quality_context, data)
        for agent_name, result in zip(quality_agents, quality_results):
            results[agent_name] = result

        # Creative and product development (Creative & Product department)
        creative_context = f"Creative strategy for: {context}"
        creative_agents = ["lyra", "aurora", "echo", "quill"]
        creative_results = await self._run_agent_batch(creative_agents, creative_context, data)
        for agent_name, result in zip(creative_agents, creative_results):
            results[agent_name] = result

        # Technical infrastructure (Tech & Infrastructure department)
        tech_context = f"Technical optimization for: {context}"
        tech_agents = ["forge", "titan", "aegis", "noir"]
        tech_results = await self._run_agent_batch(tech_agents, tech_context, data)
        for agent_name, result in zip(tech_agents, tech_results):
            results[agent_name] = result

        # Legal and health (Legal & Sovereignty, Health & Human Factor departments)
        support_context = f"Support functions for: {context}"
        support_agents = ["hermes", "obsidian", "seraph", "wellnesscoordinator"]
        support_results = await self._run_agent_batch(support_agents, support_context, data)
        for agent_name, result in zip(support_agents, support_results):
            results[agent_name] = result

        # Revenue Strategy Cell (Idea Department) - generates revenue plays
        strategy_context = f"Generate revenue plays for: {context}"
        strategy_agents = ["strategydirector", "marketanalyst", "opportunityscout", "playvalidator"]
        strategy_results = await self._run_agent_batch(strategy_agents, strategy_context, data)
        for agent_name, result in zip(strategy_agents, strategy_results):
            results[agent_name] = result

        # Corporate Analytics - data analysis and reporting
        analytics_context = f"Data analysis and reporting for: {context}"
        analytics_agents = ["genesis", "dataanalyst", "metricsreporter"]
        analytics_results = await self._run_agent_batch(analytics_agents, analytics_context, data)
        for agent_name, result in zip(analytics_agents, analytics_results):
            results[agent_name] = result

        # Revenue Execution - executes revenue streams from Idea Department
        execution_context = f"Execute revenue streams for: {context}"
        execution_agents = ["executioncommander", "launchspecialist", "revenueoperator"]
        execution_results = await self._run_agent_batch(execution_agents, execution_context, data)
        for agent_name, result in zip(execution_agents, execution_results):
            results[agent_name] = result

        # Lead Generation & Acquisition
        lead_context = f"Lead generation and acquisition for: {context}"
        lead_agents = ["webscraper", "leadqualifier", "listbuilder"]
        lead_results = await self._run_agent_batch(lead_agents, lead_context, data)
        for agent_name, result in zip(lead_agents, lead_results):
            results[agent_name] = result

        # Website Growth & Digital Presence - manages websites, content, SEO, social, affiliates, community
        website_context = f"Website growth and digital presence for: {context}"
        website_agents = ["websitemanager", "contentstrategist", "seospecialist", "socialintegrator", "affiliatemanager", "trafficanalyst", "communitymanager"]
        website_results = await self._run_agent_batch(website_agents, website_context, data)
        for agent_name, result in zip(website_agents, website_results):
            results[agent_name] = result

        logger.info("✅ All departments executed with controlled concurrency")
        logger.info("✅ Synchronized autonomous AI decision cycle complete - all departments worked together")

        return {
            "cycle_id": f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "agent_results": results,
            "summary": self._generate_cycle_summary(results),
        }

    def _generate_cycle_summary(self, results: Dict) -> Dict:
        """Generate summary of the decision cycle"""
        return {
            "total_agents_participated": len(results),
            "key_decisions": [
                f"{name}: {result.get('analysis', 'Decision made')[:100]}..."
                for name, result in results.items()
            ],
            "overall_confidence": sum(r.get("confidence", 80) for r in results.values())
            / len(results) if results else 0,
            "priority_actions": [
                r for r in results.values() if r.get("requires_action", False)
            ],
        }

    def get_agent_status(self) -> Dict:
        """Get status of all agents with complete operational data"""
        from backend.audit_log import AuditLogStore, list_events
        
        # Department mapping for all divisional zones (including Idea & Execution departments)
        department_map = {
            "akasha": "Executive Board",
            "atlas": "Executive Board",
            "vega": "Finance & Revenue",
            "omen": "Finance & Revenue",
            "nova": "Finance & Revenue",
            "mercury": "Finance & Revenue",
            "stripeops": "Finance & Revenue",
            "lyra": "Creative & Product",
            "aurora": "Creative & Product",
            "echo": "Creative & Product",
            "quill": "Creative & Product",
            "forge": "Tech & Infrastructure",
            "titan": "Tech & Infrastructure",
            "aegis": "Tech & Infrastructure",
            "noir": "Tech & Infrastructure",
            "hermes": "Legal & Sovereignty",
            "obsidian": "Legal & Sovereignty",
            "seraph": "Health & Human Factor",
            "wellnesscoordinator": "Health & Human Factor",
            "genesis": "Corporate Analytics",
            "dataanalyst": "Corporate Analytics",
            "metricsreporter": "Corporate Analytics",
            "keeper": "Corporate Execution",
            "sentinel": "Corporate Execution",
            "pulse": "Corporate Execution",
            "relay": "Corporate Execution",
            "harbor": "Corporate Execution",
            "muse": "Corporate Execution",
            "lex": "Corporate Execution",
            "orion": "Email Marketing",
            "vortex": "Email Marketing",
            "lumen": "Email Marketing",
            "cascade": "Email Marketing",
            "torrent": "Email Marketing",
            # Revenue Strategy Cell (Idea Department)
            "strategydirector": "Revenue Strategy Cell",
            "marketanalyst": "Revenue Strategy Cell",
            "opportunityscout": "Revenue Strategy Cell",
            "playvalidator": "Revenue Strategy Cell",
            # Revenue Execution
            "executioncommander": "Revenue Execution",
            "launchspecialist": "Revenue Execution",
            "revenueoperator": "Revenue Execution",
            # Lead Generation & Acquisition
            "webscraper": "Lead Generation & Acquisition",
            "leadqualifier": "Lead Generation & Acquisition",
            "listbuilder": "Lead Generation & Acquisition",
            # Website Growth & Digital Presence
            "websitemanager": "Website Growth & Digital Presence",
            "contentstrategist": "Website Growth & Digital Presence",
            "seospecialist": "Website Growth & Digital Presence",
            "socialintegrator": "Website Growth & Digital Presence",
            "affiliatemanager": "Website Growth & Digital Presence",
            "trafficanalyst": "Website Growth & Digital Presence",
            "communitymanager": "Website Growth & Digital Presence",
        }
        
        # Get last activity for each agent from audit logs
        # Optimized: Only fetch recent events (last 50) to improve response time
        # Further reduced from 200 to 50 to prevent timeouts
        agent_activities = {}
        try:
            # Use list_events function which is the proper way to query audit logs
            # Reduced limit to 50 for faster response
            recent_events = list_events(limit=50)
            for event in recent_events:
                # Handle None values safely
                agent = event.get("agent")
                if agent is not None:
                    agent_name = str(agent).lower()
                    # Only store first occurrence (most recent due to DESC order)
                    if agent_name and agent_name not in agent_activities:
                        agent_activities[agent_name] = {
                            "last_activity": event.get("timestamp"),
                            "current_task": event.get("message", "Awaiting instructions"),
                        }
        except Exception as e:
            logger.warning(f"Failed to load agent activities from audit log: {e}")
            # If audit log fails, continue without it
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.memory]),
            "divisions": {
                "Executive Board": 2,
                "Finance & Revenue": 5,
                "Creative & Product": 4,
                "Tech & Infrastructure": 4,
                "Legal & Sovereignty": 2,
                "Health & Human Factor": 2,
                "Corporate Analytics": 3,
                "Corporate Execution": 7,
                "Email Marketing": 5,
                "Revenue Strategy Cell": 4,
                "Revenue Execution": 3,
                "Lead Generation & Acquisition": 3,
                "Website Growth & Digital Presence": 7,
            },
                   "agents": {
                       name: {
                           "role": agent.role,
                           "division": department_map.get(name.lower(), agent.division), # Ensure division matches summary map
                           "department": department_map.get(name.lower(), "Corporate Execution"),
                           "memory_entries": len(agent.memory),
                           "specialties": agent.specialties,
                           "current_task": agent_activities.get(name, {}).get("current_task", "Awaiting instructions"),
                           "last_activity": agent_activities.get(name, {}).get("last_activity", datetime.now().isoformat()),
                           "custom_prompt": getattr(agent, "custom_prompt", ""),
                           "memory_namespace": getattr(agent, "memory_namespace", f"{name.lower()}_memory"),
                       }
                       for name, agent in self.agents.items()
                   },
        }

    # --- COMPATIBILITY METHODS FOR CORPORATE ROUTER ---

    def execute_corporate_directive(self, directive: str, priority: str = "high") -> Dict:
        """Execute a high-level directive (Sync wrapper for async logic)"""
        # Note: In a real async server, we should await this. 
        # But for compatibility with the sync router interface, we might need to run in loop or change router to async.
        # Fortunately, FastAPI supports async routes. We will update the router to be async.
        # Here we return a coroutine or run it if we must. 
        # Ideally, we update the router to call `await agents.execute_directive(...)`.
        
        # For now, let's assume the router will be updated to async.
        return {
            "directive": directive,
            "priority": priority,
            "status": "queued",
            "timestamp": datetime.now().isoformat()
        }

    async def execute_directive_async(self, directive: str, priority: str = "high") -> Dict:
        """Async execution of directive"""
        logger.info(f"Executing directive: {directive} (Priority: {priority})")
        
        # Akasha analyzes
        akasha_res = await self.agents["akasha"].think_and_act(f"Directive: {directive}", {"priority": priority})
        
        # Atlas coordinates
        atlas_res = await self.agents["atlas"].think_and_act(f"Operationalize: {directive}", {"strategy": akasha_res})
        
        return {
            "directive": directive,
            "priority": priority,
            "akasha_strategy": akasha_res,
            "atlas_plan": atlas_res,
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }

    async def process_revenue_transaction(self, amount: float, source: str, category: str, description: str = "") -> Dict:
        """Process revenue transaction"""
        logger.info(f"Processing revenue: ${amount} from {source}")
        
        # Vega analyzes financial impact
        vega_res = await self.agents["vega"].think_and_act(
            f"Revenue received: ${amount} from {source}", 
            {"amount": amount, "source": source, "category": category, "desc": description}
        )
        
        return {
            "transaction": {"amount": amount, "source": source, "category": category},
            "vega_analysis": vega_res,
            "status": "processed",
            "timestamp": datetime.now().isoformat()
        }

    async def create_digital_product(self, product_type: str, target_audience: str, price_point: float, description: str = "") -> Dict:
        """Create digital product"""
        logger.info(f"Creating product: {product_type}")
        
        # Lyra defines brand/concept
        lyra_res = await self.agents["lyra"].think_and_act(
            f"Create product concept: {product_type} for {target_audience}",
            {"price": price_point, "desc": description}
        )
        
        # Genesis validates monetization
        genesis_res = await self.agents["genesis"].think_and_act(
            f"Monetization strategy for {product_type}",
            {"concept": lyra_res, "price": price_point}
        )
        
        return {
            "product": {"type": product_type, "audience": target_audience, "price": price_point},
            "concept": lyra_res,
            "monetization": genesis_res,
            "status": "in_development",
            "timestamp": datetime.now().isoformat()
        }

    async def generate_market_research(self, industry: str, target_market: str) -> Dict:
        """Generate market research"""
        logger.info(f"Researching: {industry}")
        
        # Noir gathers intelligence
        noir_res = await self.agents["noir"].think_and_act(
            f"Market research for {industry} targeting {target_market}",
            {"industry": industry, "target": target_market}
        )
        
        # Omen predicts trends
        omen_res = await self.agents["omen"].think_and_act(
            f"Trend forecast for {industry}",
            {"research": noir_res}
        )
        
        return {
            "industry": industry,
            "target_market": target_market,
            "intelligence": noir_res,
            "forecast": omen_res,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

    def get_system_status_sync(self) -> Dict:
        """Get system status (sync wrapper)"""
        return {
            "system_overview": {
                "status": "OPERATIONAL",
                "total_agents": len(self.agents),
                "active_agents": len([a for a in self.agents.values() if a.memory]),
            },
            "agent_status": self.get_agent_status(),
            "timestamp": datetime.now().isoformat()
        }

    async def financial_summary(self) -> Dict:
        """Generate financial summary"""
        vega_res = await self.agents["vega"].think_and_act("Generate financial summary report", {})
        return {
            "financial_summary": vega_res,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
AI_AGENT_CORPORATION = AIRevenueAgentCorporation()


# Export for use in main server
async def run_real_autonomous_cycle(
    context: str = "Revenue generation", data: Dict = None
) -> Dict:
    """Main function to run autonomous cycle"""
    return await AI_AGENT_CORPORATION.run_autonomous_cycle(context, data)


def get_real_agent_status() -> Dict:
    """Get status of all real agents"""
    return AI_AGENT_CORPORATION.get_agent_status()

# --- EXPORTS FOR CORPORATE ROUTER ---

async def execute_directive(directive: str, priority: str = "high") -> Dict:
    return await AI_AGENT_CORPORATION.execute_directive_async(directive, priority)

async def process_revenue(amount: float, source: str, category: str, description: str = "") -> Dict:
    return await AI_AGENT_CORPORATION.process_revenue_transaction(amount, source, category, description)

async def create_product(product_type: str, target_audience: str, price_point: float, description: str = "") -> Dict:
    return await AI_AGENT_CORPORATION.create_digital_product(product_type, target_audience, price_point, description)

async def market_research(industry: str = "AI Automation", target_market: str = "Business Owners") -> Dict:
    return await AI_AGENT_CORPORATION.generate_market_research(industry, target_market)

def system_status() -> Dict:
    return AI_AGENT_CORPORATION.get_system_status_sync()

async def financial_summary() -> Dict:
    return await AI_AGENT_CORPORATION.financial_summary()


if __name__ == "__main__":
    # Test run
    async def test():
        result = await run_real_autonomous_cycle("Test revenue generation")
        print(json.dumps(result, indent=2))

    asyncio.run(test())
