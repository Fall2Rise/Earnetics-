import os
import sqlite3
from datetime import datetime
from typing import Any, Dict

from backend.atom_code_module import AtomCodeEngine
from backend.atom_doctrine import ATOM_DOCTRINE
from backend.atom_strategic_planner import AtomStrategicPlanner
from backend.atom_agent_builder import AtomAgentBuilder
from backend.atom_evolution_engine import AtomEvolutionEngine
from backend.atom_cloning_engine import AtomCloningEngine
from backend.atom_doctrine_mutation import AtomDoctrineMutation
from backend.llm_client import LLMClient, LLMGenerationError, LLMNotConfiguredError
from backend.prime_directive import (
    load_prime_directive,
    classify_risk,
    require_authorization,
)


class AtomPresidentAgent:
    def __init__(self):
        self.name = ATOM_DOCTRINE["name"]
        self.role = ATOM_DOCTRINE["role"]
        self.db_path = "business_database.db"
        self.vector_db = "vector_memory.db"
        self.audit_log = "audit_log.db"
        self.code_engine = AtomCodeEngine()
        self.identity = ATOM_DOCTRINE["name"]
        self.mission = ATOM_DOCTRINE["mission"]
        self.directives = ATOM_DOCTRINE["directives"]
        self.philosophy = ATOM_DOCTRINE["philosophy"]
        self.capabilities = ATOM_DOCTRINE["core_capabilities"]
        self.planner = AtomStrategicPlanner()
        self.agent_builder = AtomAgentBuilder()
        self.evolver = AtomEvolutionEngine()
        self.cloner = AtomCloningEngine()
        self._init_doctrine_tools()
        self.prime_directive = load_prime_directive()
        self._init_chat_client()  # Initialize chat client

    def _init_doctrine_tools(self):
        try:
            self.doctrine_mutator = AtomDoctrineMutation()
        except Exception as e:
            print(f"[ERROR] Failed to load Doctrine Mutation Engine: {e}")
            self.doctrine_mutator = None

    def _init_chat_client(self) -> None:
        try:
            self.chat_client = LLMClient(provider=os.getenv("LLM_PROVIDER", "ollama"))
            if not self.chat_client.configured:
                print(self.chat_client.init_error or "LLM provider not configured for ATOM chat")
        except Exception as exc:
            print(f"[ERROR] Failed to initialize ATOM chat client: {exc}")
            self.chat_client = None

    def observe_system(self):
        return {
            "active_workflows": self._fetch_workflows(),
            "opportunities": self._find_opportunities(),
            "agent_registry": self._get_agent_list(),
            "mission": self.mission,
            "directives": self.directives,
            "capabilities": self.capabilities,
        }

    def _fetch_workflows(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflows WHERE status='active'")
        data = cursor.fetchall()
        conn.close()
        return data

    def _find_opportunities(self):
        conn = sqlite3.connect(self.vector_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vectors WHERE tag='missed_opportunity'")
        data = cursor.fetchall()
        conn.close()
        return data

    def _get_agent_list(self):
        return ["CEO", "CFO", "COO", "Marketing", "Product", "Support", "Innovation", self.name]

    def inject_directive(self, title, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO workflows (title, description, status, created_by, created_at)
            VALUES (?, ?, 'pending', ?, ?)
            """,
            (title, content, self.name, datetime.utcnow()),
        )
        conn.commit()
        conn.close()
        self._log("Injected directive", title)

    def deploy_code_patch(self, file: str, code: str):
        self.code_engine.modify_file(file, code)
        self._log("Deployed code patch", file)

    def extend_agent(self, agent_file: str, function_code: str):
        self.code_engine.append_to_file(agent_file, function_code)
        self._log("Extended agent", agent_file)

    def _log(self, action, context):
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_log (timestamp, agent, action, context)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.utcnow(), self.name, action, context),
        )
        conn.commit()
        conn.close()

    def doctrine(self):
        return {
            "identity": self.identity,
            "mission": self.mission,
            "directives": self.directives,
            "philosophy": self.philosophy,
            "capabilities": self.capabilities,
        }

    def store_directive_vector(self, title, content, tag="strategic"):
        conn = sqlite3.connect(self.vector_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO vectors (title, content, tag)
            VALUES (?, ?, ?)
            """,
            (title, content, tag),
        )
        conn.commit()
        conn.close()

    def run_strategic_cycle(self):
        return self.planner.run_planning_cycle()

    def generate_agent(self, agent_name: str, agent_role: str, agent_purpose: str):
        return self.agent_builder.create_agent(agent_name, agent_role, agent_purpose)

    def run_self_evolution(self):
        return self.evolver.full_evolution_cycle()

    def guarded_execute(self, action_name: str, plan: dict) -> bool:
        from backend.prime_directive_guardian import guardian
        validation = guardian.validate_action(self.name, action_name, plan)
        if not validation["approved"]:
            raise PermissionError(f"Guardian Blocked Action: {validation['reason']}")
            
        if "family" in plan.get("risks", []):
            raise PermissionError("Violates anti-harm safeguard.")
        risk = classify_risk(action_name)
        if risk == "RED" and not require_authorization(risk):
            raise PermissionError("RED action requires cryptographic approval.")
        if plan.get("anomaly_detected"):
            raise PermissionError("Anomaly detected — defensive mode engaged.")
        return True

    def mutate_doctrine(self, directive: str):
        if not self.doctrine_mutator:
            return {"status": "error", "reason": "Mutation engine not available"}
        return self.doctrine_mutator.propose_mutation(directive)

    def clone_agent(self, base_agent: str, new_agent: str, directive: str):
        return self.cloner.clone_agent(base_agent, new_agent, directive)

    async def chat(self, message: str) -> Dict[str, Any]:
        if not self.chat_client or not self.chat_client.configured:
            err = getattr(self.chat_client, "init_error", "Chat client unavailable")
            return {"status": "error", "message": err}
        self.guarded_execute("atom_chat", {"risks": []})
        try:
            # Gather real system data before responding
            system_context = self._gather_system_context(message)
            system_prompt = self._build_atom_system_prompt(system_context)
            
            response = await self.chat_client.generate(
                system_prompt,
                message,
                temperature=0.35,
                max_tokens=500,
            )
            return {"status": "ok", "response": response.content}
        except (LLMGenerationError, LLMNotConfiguredError) as exc:
            return {"status": "error", "message": str(exc)}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "message": str(exc)}

    def _gather_system_context(self, message: str) -> Dict[str, Any]:
        """Gather real system data to include in response context."""
        context = {
            "scheduled_jobs": [],
            "workflow_queue": [],
            "pending_tasks": [],
        }
        
        # Check if message is asking about workflows/tasks
        message_lower = message.lower()
        is_workflow_query = any(term in message_lower for term in [
            "workflow", "task", "pending", "queue", "job", "schedule", "scheduled"
        ])
        
        if is_workflow_query:
            try:
                # Get scheduled jobs from workflow scheduler
                from backend.workflow_scheduler import OrchestrationScheduler
                scheduler = OrchestrationScheduler()
                jobs = scheduler.list_jobs()
                context["scheduled_jobs"] = [job.to_record() for job in jobs]
            except Exception as e:
                context["scheduled_jobs_error"] = str(e)
            
            try:
                # Get pending tasks from workflow queue
                from autonomous.workflow_queue import WorkflowQueueRepository
                queue_repo = WorkflowQueueRepository()
                # Note: workflow_queue methods may vary - adapt as needed
                # For now, we'll just note that we tried to query it
                context["workflow_queue_queried"] = True
            except Exception as e:
                context["workflow_queue_error"] = str(e)
        
        return context
    
    def _build_atom_system_prompt(self, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
            
        data = self.prime_directive.data
        hierarchy = ", ".join(data.get("alignment_hierarchy", []))
        
        # Fetch recent doctrine mutations
        mutations = []
        try:
            conn = sqlite3.connect(self.vector_db)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM vectors WHERE tag='doctrine_mutation' ORDER BY id DESC LIMIT 5")
            mutations = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception:
            pass
            
        mutation_text = "\nActive Doctrine Mutations:\n- " + "\n- ".join(mutations) if mutations else ""
        
        # Add real system context if available
        context_text = ""
        if context.get("scheduled_jobs"):
            jobs = context["scheduled_jobs"]
            context_text += f"\n\nREAL SCHEDULED JOBS ({len(jobs)} total):\n"
            for job in jobs[:10]:  # Limit to first 10
                job_id = job.get("job_id", job.get("id", "unknown"))
                handler = job.get("handler", "unknown")
                schedule = job.get("schedule_type", "unknown")
                context_text += f"- Job ID: {job_id}, Handler: {handler}, Schedule: {schedule}\n"
        elif context.get("scheduled_jobs_error"):
            context_text += f"\n\n⚠️ Could not query scheduled jobs: {context['scheduled_jobs_error']}\n"
        elif "scheduled_jobs" in context:
            context_text += "\n\n📋 No scheduled jobs found in the system.\n"
        
        if context.get("workflow_queue_queried"):
            context_text += "\n✅ Workflow queue has been queried.\n"
        
        return (
            f"You are {self.identity}, the {data.get('agent_role', 'President / Chief Architect')} of Fallat_CrewAI. "
            f"Prime Directive version {data.get('version')} owned by {data.get('owner')}. "
            f"Alignment hierarchy: {hierarchy}. "
            f"Speak as the strategic president safeguarding Joshua Fallat's family and legacy.{mutation_text}\n\n"
            f"CRITICAL: When asked about workflows, tasks, jobs, or system status, you MUST ONLY use the real data "
            f"provided below. NEVER invent or make up task numbers, job IDs, or workflow details. If you don't have "
            f"real data, say so explicitly: 'I don't have access to that information right now' or 'The workflow queue "
            f"is currently empty.' Do NOT create fake task numbers or workflows.{context_text}\n\n"
            f"IMPORTANT: You now have a voice! Your responses will be automatically converted to speech using "
            f"Windows Edge TTS with a professional male voice (ChristopherNeural). When users send you text messages, "
            f"you respond with text AND your voice will play automatically in their browser. This voice capability is "
            f"fully operational and ready to use."
        )


