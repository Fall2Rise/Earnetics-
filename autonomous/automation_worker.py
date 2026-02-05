"""Autonomous automation worker that executes department task queues."""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional

from autonomous.workflow_queue import WorkflowQueueRepository

try:
    from backend.api_integrations import APIIntegrationManager
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    try:
        from api_integrations import APIIntegrationManager  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        APIIntegrationManager = None  # type: ignore

try:
    from backend.corporate_memory import CorporateMemory, CorporateMemoryError
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    from corporate_memory import CorporateMemory, CorporateMemoryError  # type: ignore


logger = logging.getLogger("AutonomyWorker")

TaskHandler = Callable[["TaskExecutionContext"], Awaitable["TaskExecutionResult"]]


@dataclass
class TaskExecutionContext:
    """Execution context passed to department handlers."""

    task: Dict[str, Any]
    queue_item: Dict[str, Any]
    started_at: datetime


@dataclass
class TaskExecutionResult:
    """Outcome returned by task handlers."""

    success: bool
    message: str
    output: Dict[str, Any]
    retry_delay_minutes: Optional[int] = None


class AutomationWorker:
    """Continuously claims and executes ready department tasks."""

    def __init__(
        self,
        corporate_memory: CorporateMemory,
        queue_repository: WorkflowQueueRepository,
        *,
        departments: Optional[Iterable[str]] = None,
        handlers: Optional[Dict[str, TaskHandler]] = None,
        integration_manager: Optional["APIIntegrationManager"] = None,
        email_agents: Optional[Dict[str, Any]] = None,
        poll_interval_seconds: float = 15.0,
        retry_backoff_minutes: int = 5,
        worker_id: str = "autonomy-worker",
    ) -> None:
        self.corporate_memory = corporate_memory
        self.queue_repository = queue_repository
        self.poll_interval = max(0.5, float(poll_interval_seconds))
        self.retry_backoff_minutes = max(1, int(retry_backoff_minutes))
        self.worker_id = worker_id
        self._handlers = {
            self._normalize_department(key): value
            for key, value in (handlers or {}).items()
        }
        self.departments = self._derive_departments(departments)
        self._running = False
        self._loop: Optional[asyncio.Task] = None
        self._department_briefs = self._build_brief_factories()
        self.integration_manager = (
            integration_manager
            if integration_manager is not None
            else self._init_integration_manager()
        )
        self.email_agents = email_agents if email_agents is not None else self._load_email_agents()
        self._stripe_warned = False
        self._email_warned = False
        self._register_default_handlers()

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._loop = asyncio.create_task(self._run_loop(), name=f"{self.worker_id}-loop")
        logger.info(
            "Autonomy worker %s started (departments=%s, interval=%ss)",
            self.worker_id,
            ",".join(self.departments) or "none",
            self.poll_interval,
        )

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._loop:
            self._loop.cancel()
            try:
                await self._loop
            except asyncio.CancelledError:
                pass
            finally:
                self._loop = None
        logger.info("Autonomy worker %s stopped", self.worker_id)

    def is_running(self) -> bool:
        return self._running

    async def process_once(self) -> bool:
        """Process available tasks once, returning True if any were executed."""

        processed = False
        while True:
            queue_item = await self._claim_next_item()
            if not queue_item:
                break
            processed = True
            await self._execute_queue_item(queue_item)
        return processed

    async def _run_loop(self) -> None:
        try:
            while self._running:
                worked = await self.process_once()
                if not worked:
                    await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Automation worker loop crashed: %s", exc)
            self._running = False

    def _init_integration_manager(self) -> Optional["APIIntegrationManager"]:
        if APIIntegrationManager is None:
            return None
        try:
            return APIIntegrationManager()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize API integrations: %s", exc)
            return None

    def _register_default_handlers(self) -> None:
        stripe = self._stripe_integration()
        if stripe:
            self._handlers.setdefault("finance", self._finance_handler)
            self._handlers.setdefault("payments", self._payments_handler)
        email = self._email_integration()
        if email:
            self._handlers.setdefault("marketing", self._marketing_handler)
            self._handlers.setdefault("customer_success", self._marketing_handler)
        if self.email_agents:
            self._handlers.setdefault("email_marketing", self._email_marketing_handler)

    def _integration_attr(self, name: str) -> Optional[Any]:
        if self.integration_manager is None:
            return None
        return getattr(self.integration_manager, name, None)

    def _load_email_agents(self) -> Dict[str, Any]:
        try:
            from backend.ai_corporate_hierarchy import AI_CORPORATION

            division = AI_CORPORATION.get("email_marketing_division", {})
            return {
                "list_engineering": division.get("beacon"),
                "campaign_creative": division.get("quill"),
            }
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Email marketing agents unavailable: %s", exc)
            return {}

    async def _email_marketing_handler(self, context: TaskExecutionContext) -> TaskExecutionResult:
        metadata = self._task_metadata(context.task)
        task_type = str(
            metadata.get("task_type")
            or metadata.get("action_type")
            or metadata.get("action")
            or ""
        ).lower()
        if task_type in {"list", "list_engineering", "list_steward"}:
            agent = self.email_agents.get("list_engineering")
        else:
            agent = self.email_agents.get("campaign_creative")
        if not agent:
            task_id = context.task.get("id")
            logger.warning("Email campaign handler missing specialist; falling back to marketing (task_id=%s)", task_id)
            return await self._marketing_handler(context)

        campaign_name = (
            metadata.get("campaign_name")
            or metadata.get("campaign")
            or context.task.get("title")
            or "campaign"
        )
        try:
            result = await agent.execute_business_function(
                context=f"Automation worker email run for {campaign_name}",
                data=metadata,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Email marketing agent execution failed: %s", exc)
            return TaskExecutionResult(
                success=False,
                message=f"Email marketing handler failed: {exc}",
                output={"error": str(exc), "campaign": campaign_name},
                retry_delay_minutes=self.retry_backoff_minutes,
            )

        return TaskExecutionResult(
            success=True,
            message=f"Email marketing outputs ready for {campaign_name}",
            output={
                "campaign": campaign_name,
                "agent_result": result,
            },
        )

    def _stripe_integration(self):
        stripe = self._integration_attr("stripe")
        if stripe and getattr(stripe, "enabled", False):
            return stripe
        if not self._stripe_warned:
            logger.warning("Stripe integration disabled – finance handlers will use fallback outputs")
            self._stripe_warned = True
        return None

    def _email_integration(self):
        email = self._integration_attr("email")
        if email and getattr(email, "enabled", False):
            return email
        if not self._email_warned:
            logger.warning("Email SMTP integration disabled – marketing handlers will queue plans only")
            self._email_warned = True
        return None

    @staticmethod
    def _task_metadata(task: Dict[str, Any]) -> Dict[str, Any]:
        metadata = task.get("metadata") or {}
        return metadata if isinstance(metadata, dict) else {}

    @staticmethod
    def _normalize_recipients(metadata: Dict[str, Any]) -> List[str]:
        recipients = metadata.get("recipients") or metadata.get("emails")
        if not recipients:
            return []
        if isinstance(recipients, str):
            values = [item.strip() for item in recipients.split(",") if item.strip()]
        elif isinstance(recipients, (list, tuple, set)):
            values = [str(item).strip() for item in recipients if str(item).strip()]
        else:
            values = [str(recipients).strip()]
        return [addr for addr in values if addr]

    async def _run_stripe_activity(
        self,
        context: TaskExecutionContext,
        *,
        allow_product: bool,
    ) -> TaskExecutionResult:
        stripe = self._stripe_integration()
        if not stripe:
            return await self._default_handler(context)

        metadata = self._task_metadata(context.task)
        limit_raw = metadata.get("stripe_limit") or metadata.get("payment_limit") or 10
        try:
            limit = max(1, int(limit_raw))
        except (TypeError, ValueError):
            limit = 10

        # Route through ToolExecutor (NO direct Stripe calls)
        executor = None
        try:
            from backend.main_server import app
            executor = getattr(app.state, "tool_executor", None)
        except Exception:
            pass
        
        if executor is None:
            logger.warning("ToolExecutor not available, falling back to default handler")
            return await self._default_handler(context)

        # Execute via ToolExecutor
        try:
            tool_result = executor.execute(
                tool_name="stripe.get_recent_payments",
                args={"limit": limit},
                actor="AutomationWorker",
                autonomous=True,
                meta={"department": context.task.get("department"), "task_id": context.task.get("id")},
            )
            
            if tool_result.get("status") != "executed":
                error_msg = tool_result.get("reason") or tool_result.get("error", "Tool execution failed")
                return TaskExecutionResult(
                    success=False,
                    message=f"Stripe payments fetch blocked/failed: {error_msg}",
                    output=tool_result,
                    retry_delay_minutes=self.retry_backoff_minutes,
                )
            
            payments_data = tool_result.get("result", {})
            payments = payments_data.get("payments", [])
            
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("ToolExecutor Stripe payments fetch failed: %s", exc)
            return TaskExecutionResult(
                success=False,
                message=f"Stripe payments fetch failed: {exc}",
                output={"error": str(exc), "limit": limit},
                retry_delay_minutes=self.retry_backoff_minutes,
            )

        total_amount = round(
            sum(float(payment.get("amount") or 0.0) for payment in payments), 2
        )
        currency = payments[0].get("currency") if payments else "usd"
        output: Dict[str, Any] = {
            "payments_reviewed": payments,
            "payment_count": len(payments),
            "total_amount": total_amount,
            "currency": currency,
            "limit": limit,
        }

        if allow_product and metadata.get("create_product"):
            product_name = metadata.get("product_name") or context.task.get("title") or "Stripe Product"
            description = metadata.get("product_description") or context.task.get("description") or product_name
            price_raw = metadata.get("price") or metadata.get("unit_amount") or 97.0
            try:
                price = float(price_raw)
            except (TypeError, ValueError):
                price = 97.0
            # Route through ToolExecutor (NO direct Stripe calls)
            try:
                tool_result = executor.execute(
                    tool_name="stripe.create_product",
                    args={
                        "name": product_name,
                        "description": description,
                        "price": price,
                        "currency": metadata.get("currency", "usd"),
                    },
                    actor="AutomationWorker",
                    autonomous=True,
                    meta={"department": context.task.get("department"), "task_id": context.task.get("id")},
                )
                
                if tool_result.get("status") != "executed":
                    error_msg = tool_result.get("reason") or tool_result.get("error", "Tool execution failed")
                    output["product_setup"] = {"error": error_msg, "tool_result": tool_result}
                    return TaskExecutionResult(
                        success=False,
                        message=f"Stripe product creation blocked/failed: {error_msg}",
                        output=output,
                        retry_delay_minutes=self.retry_backoff_minutes,
                    )
                
                product_result = tool_result.get("result", {})
                
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("ToolExecutor Stripe product creation failed: %s", exc)
                output["product_setup"] = {"error": str(exc)}
                return TaskExecutionResult(
                    success=False,
                    message=f"Stripe product creation failed: {exc}",
                    output=output,
                    retry_delay_minutes=self.retry_backoff_minutes,
                )
            output["product_setup"] = product_result
            if isinstance(product_result, dict) and product_result.get("error"):
                return TaskExecutionResult(
                    success=False,
                    message=f"Stripe product creation failed: {product_result['error']}",
                    output=output,
                    retry_delay_minutes=self.retry_backoff_minutes,
                )

        message = (
            f"Processed {len(payments)} Stripe payments totaling ${total_amount:,.2f}"
            if payments
            else "Checked Stripe payments (no recent charges)"
        )
        return TaskExecutionResult(success=True, message=message, output=output)

    async def _finance_handler(self, context: TaskExecutionContext) -> TaskExecutionResult:
        return await self._run_stripe_activity(context, allow_product=True)

    async def _payments_handler(self, context: TaskExecutionContext) -> TaskExecutionResult:
        return await self._run_stripe_activity(context, allow_product=False)

    async def _marketing_handler(self, context: TaskExecutionContext) -> TaskExecutionResult:
        email = self._email_integration()
        if not email:
            return await self._default_handler(context)

        metadata = self._task_metadata(context.task)
        campaign_name = metadata.get("campaign") or metadata.get("product_name") or context.task.get("title") or "Marketing Campaign"

        try:
            sequence = await email.create_email_sequence(campaign_name)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Email sequence generation failed: %s", exc)
            return TaskExecutionResult(
                success=False,
                message=f"Email sequence generation failed: {exc}",
                output={"campaign": campaign_name, "error": str(exc)},
                retry_delay_minutes=self.retry_backoff_minutes,
            )

        recipients = self._normalize_recipients(metadata)
        send_result: Optional[Dict[str, Any]] = None
        if recipients:
            subject = metadata.get("subject") or f"{campaign_name} launch"
            content = metadata.get("html_content") or metadata.get("content") or context.task.get("description") or f"Introducing {campaign_name}"
            if "<" not in content:
                content = f"<p>{content}</p>"
            try:
                send_result = await email.send_promotional_email(recipients, subject, content)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Email delivery failed: %s", exc)
                return TaskExecutionResult(
                    success=False,
                    message=f"Email delivery failed: {exc}",
                    output={
                        "campaign": campaign_name,
                        "sequence": sequence,
                        "recipients": recipients,
                        "error": str(exc),
                    },
                    retry_delay_minutes=self.retry_backoff_minutes,
                )
            if isinstance(send_result, dict) and send_result.get("error"):
                return TaskExecutionResult(
                    success=False,
                    message=f"Email delivery failed: {send_result['error']}",
                    output={
                        "campaign": campaign_name,
                        "sequence": sequence,
                        "recipients": recipients,
                        "send_result": send_result,
                    },
                    retry_delay_minutes=self.retry_backoff_minutes,
                )

        output = {
            "campaign": campaign_name,
            "sequence": sequence,
            "recipients": recipients,
            "send_result": send_result,
        }
        if recipients:
            message = f"Sent campaign to {len(recipients)} recipients"
        else:
            message = f"Prepared email automation for {campaign_name}"
        return TaskExecutionResult(success=True, message=message, output=output)

    async def _claim_next_item(self) -> Optional[Dict[str, Any]]:
        for department in self.departments:
            item = await asyncio.to_thread(
                self.queue_repository.claim_next,
                department,
                self.worker_id,
            )
            if item:
                return item
        return None

    async def _execute_queue_item(self, queue_item: Dict[str, Any]) -> None:
        task_id = int(queue_item["task_id"])
        task = await asyncio.to_thread(self.corporate_memory.get_task, task_id)
        if not task:
            logger.warning(
                "Queue item %s references missing task %s; marking failed",
                queue_item.get("id"),
                task_id,
            )
            await asyncio.to_thread(
                self.queue_repository.mark_failed,
                int(queue_item.get("id")),
                error="missing_task",
            )
            return

        try:
            task = await asyncio.to_thread(
                self.corporate_memory.mark_task_in_progress,
                task_id,
                claimed_by=self.worker_id,
            )
        except CorporateMemoryError as exc:
            logger.exception("Unable to mark task %s in progress: %s", task_id, exc)
            await asyncio.to_thread(
                self.queue_repository.mark_failed,
                int(queue_item.get("id")),
                error=str(exc),
            )
            return

        # Check if this is a tool-based execution (new format)
        tool_name = task.get("tool") or queue_item.get("tool")
        if tool_name:
            # Route through ToolExecutor
            try:
                # Get ToolExecutor from app state (injected or from global)
                executor = getattr(self, "_tool_executor", None)
                if executor is None:
                    # Try to get from app state if we have access
                    try:
                        from backend.main_server import app
                        executor = getattr(app.state, "tool_executor", None)
                    except Exception:
                        pass
                
                if executor is None:
                    raise RuntimeError("ToolExecutor not wired on app.state")
                
                args = task.get("args") or task.get("payload") or {}
                meta = task.get("meta") or {}
                meta.update({
                    "department": task.get("department"),
                    "job_id": str(queue_item.get("id")),
                    "task_id": task_id,
                })
                
                # Execute via ToolExecutor (autonomous=True for automation worker)
                tool_result = executor.execute(
                    tool_name=tool_name,
                    args=args,
                    actor="AutomationWorker",
                    autonomous=True,
                    meta=meta,
                )
                
                # Convert ToolExecutor result to TaskExecutionResult
                if tool_result.get("status") == "executed":
                    result = TaskExecutionResult(
                        success=True,
                        message=f"Tool {tool_name} executed successfully",
                        output=tool_result.get("result", {}),
                    )
                elif tool_result.get("status") == "needs_approval":
                    result = TaskExecutionResult(
                        success=False,
                        message=f"Tool {tool_name} requires approval (request_id: {tool_result.get('request_id')})",
                        output=tool_result,
                        retry_delay_minutes=60,  # Wait for approval
                    )
                elif tool_result.get("status") == "blocked":
                    result = TaskExecutionResult(
                        success=False,
                        message=f"Tool {tool_name} blocked: {tool_result.get('reason')}",
                        output=tool_result,
                    )
                else:
                    result = TaskExecutionResult(
                        success=False,
                        message=f"Tool {tool_name} failed: {tool_result.get('error', 'Unknown error')}",
                        output=tool_result,
                    )
            except Exception as exc:
                logger.exception("ToolExecutor execution failed for task %s: %s", task_id, exc)
                result = TaskExecutionResult(
                    success=False,
                    message=f"ToolExecutor error: {exc}",
                    output={"error": str(exc)},
                )
        else:
            # Legacy handler-based execution
            context = TaskExecutionContext(
                task=task,
                queue_item=queue_item,
                started_at=datetime.utcnow(),
            )
            handler = self._select_handler(task)
            try:
                result = await self._call_handler(handler, context)
            except Exception as exc:  # pragma: no cover - robust handler boundary
                logger.exception("Automation handler crashed for task %s: %s", task_id, exc)
                result = TaskExecutionResult(
                    success=False,
                    message=str(exc),
                    output={"error": str(exc)},
                )

        duration_ms = int((datetime.utcnow() - context.started_at).total_seconds() * 1000)
        log_entry = {
            "event": "automated_execution",
            "worker": self.worker_id,
            "status": "success" if result.success else "failed",
            "message": result.message,
            "department": task.get("department"),
            "duration_ms": duration_ms,
            "queue_attempt": int(queue_item.get("attempts") or 1),
            "outputs": result.output,
        }
        await asyncio.to_thread(self.corporate_memory.append_task_log, task_id, log_entry)

        if result.success:
            await asyncio.to_thread(self.corporate_memory.mark_task_complete, task_id)
            await asyncio.to_thread(
                self.queue_repository.mark_completed,
                int(queue_item.get("id")),
            )
            return

        attempts = int(queue_item.get("attempts") or 1)
        max_attempts = int(queue_item.get("max_attempts") or 3)
        retry_delay = result.retry_delay_minutes or self.retry_backoff_minutes

        if attempts >= max_attempts:
            await asyncio.to_thread(
                self.corporate_memory.mark_task_blocked,
                task_id,
                reason=result.message,
                details={"attempts": attempts},
            )
            await asyncio.to_thread(
                self.queue_repository.mark_failed,
                int(queue_item.get("id")),
                error=result.message,
            )
        else:
            await asyncio.to_thread(self.corporate_memory.release_task, task_id)
            await asyncio.to_thread(
                self.queue_repository.release,
                int(queue_item.get("id")),
                reason=result.message,
                delay_minutes=retry_delay,
            )

    async def _call_handler(
        self,
        handler: TaskHandler,
        context: TaskExecutionContext,
    ) -> TaskExecutionResult:
        result = handler(context)
        if inspect.isawaitable(result):
            result = await result
        if not isinstance(result, TaskExecutionResult):
            raise TypeError("Task handlers must return TaskExecutionResult instances")
        return result

    def _select_handler(self, task: Dict[str, Any]) -> TaskHandler:
        department_key = self._normalize_department(task.get("department"))
        return self._handlers.get(department_key, self._default_handler)

    def _derive_departments(self, departments: Optional[Iterable[str]]) -> List[str]:
        defaults = [
            "finance",
            "payments",
            "marketing",
            "sales",
            "operations",
            "product",
            "engineering",
            "design",
            "dropshipping",
            "affiliate",
            "innovation",
            "analytics",
            "system",
            "customer_success",
            "reinvestment",
        ]
        source = departments or defaults
        result: List[str] = []
        seen: set[str] = set()
        for item in source:
            key = self._normalize_department(item)
            if key and key not in seen:
                result.append(key)
                seen.add(key)
        return result

    def _build_brief_factories(self) -> Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]:
        return {
            "finance": self._finance_brief,
            "payments": self._payments_brief,
            "marketing": self._marketing_brief,
            "sales": self._sales_brief,
            "operations": self._operations_brief,
            "product": self._product_brief,
            "engineering": self._engineering_brief,
            "design": self._design_brief,
            "dropshipping": self._dropshipping_brief,
            "affiliate": self._affiliate_brief,
            "innovation": self._innovation_brief,
            "analytics": self._analytics_brief,
            "system": self._system_brief,
            "customer_success": self._customer_success_brief,
            "reinvestment": self._finance_brief,
        }

    async def _default_handler(self, context: TaskExecutionContext) -> TaskExecutionResult:
        brief = self._build_brief(context.task)
        message = brief.get("summary") or f"Automated execution completed for {context.task.get('title')}"
        return TaskExecutionResult(success=True, message=message, output=brief)

    def _build_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        department_key = self._normalize_department(task.get("department"))
        builder = self._department_briefs.get(department_key, self._generic_brief)
        return builder(task)

    @staticmethod
    def _normalize_department(value: Optional[str]) -> str:
        return (value or "").strip().lower().replace(" ", "_")

    @staticmethod
    def _priority_multiplier(task: Dict[str, Any]) -> float:
        priority = (task.get("priority") or "medium").lower()
        return {
            "critical": 1.6,
            "high": 1.3,
            "medium": 1.0,
            "low": 0.7,
        }.get(priority, 1.0)

    def _baseline_value(self, task: Dict[str, Any], base: float) -> float:
        title = task.get("title") or ""
        length_factor = max(len(title), 1) / 12
        return round(base * self._priority_multiplier(task) * (1 + length_factor * 0.05), 2)

    def _finance_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        projected = self._baseline_value(task, 12000)
        reserve = round(projected * 0.22, 2)
        reinvest = round(projected * 0.35, 2)
        return {
            "summary": f"Modeled cashflow impact for {task.get('title')}.",
            "ledger": {
                "projected_gross": projected,
                "recommended_reserve": reserve,
                "recommended_reinvestment": reinvest,
                "confidence": round(0.68 + self._priority_multiplier(task) * 0.12, 2),
            },
            "next_actions": [
                "Sync projection to Stripe revenue ledger",
                "Notify CFO review channel",
                "Prepare reinvestment brief for operations",
            ],
        }

    def _payments_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        throughput = int(self._baseline_value(task, 18))
        return {
            "summary": f"Validated payment automation for {task.get('title')}.",
            "payment_summary": {
                "transactions_reviewed": throughput,
                "pending_disputes": max(0, throughput // 9 - 1),
                "automations_enabled": ["payout_reconciliation", "fee_audit"],
            },
            "next_actions": [
                "Confirm webhook status",
                "Update finance dashboard",
            ],
        }

    def _marketing_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        reach = int(self._baseline_value(task, 2200))
        return {
            "summary": f"Generated multi-channel plan for {task.get('title')}.",
            "campaign_plan": {
                "expected_reach": reach,
                "channels": ["email", "social", "retargeting"],
                "cta": "Book strategy session",
            },
            "assets": [
                "launch_brief.md",
                "audience_segments.json",
            ],
        }

    def _sales_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pipeline = int(self._baseline_value(task, 18000))
        return {
            "summary": f"Activated sales playbook for {task.get('title')}.",
            "pipeline_projection": {
                "pipeline_value": pipeline,
                "target_accounts": max(5, pipeline // 1500),
                "touch_pattern": ["email", "linkedin", "call"],
            },
            "next_actions": ["Distribute playbook", "Launch outreach sprint"],
        }

    def _operations_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        cycle_time = max(2.0, 6.0 / self._priority_multiplier(task))
        return {
            "summary": f"Structured execution workflow for {task.get('title')}.",
            "sop": {
                "cycle_time_days": round(cycle_time, 2),
                "risk_controls": ["sla_monitoring", "dependency_checks"],
                "owners": [task.get("claimed_by") or "atlas"],
            },
            "next_actions": ["Document SOP", "Sync with innovation desk"],
        }

    def _product_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        story_points = int(self._baseline_value(task, 34))
        return {
            "summary": f"Drafted product delivery outline for {task.get('title')}.",
            "backlog": {
                "story_points": story_points,
                "mvp_scope": ["core_workflow", "analytics_snapshot"],
                "qa_gate": "compliance_review",
            },
            "next_actions": ["Review with engineering", "Prepare QA checklist"],
        }

    def _engineering_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        hours = round(self._baseline_value(task, 22) / 3, 1)
        return {
            "summary": f"Scoped technical implementation for {task.get('title')}.",
            "architecture": {
                "estimated_engineering_hours": hours,
                "stack": ["FastAPI", "SQLite", "Redis (planned)"],
                "automation_hooks": ["autonomy_worker", "telemetry_collector"],
            },
            "next_actions": ["Create task tickets", "Schedule pairing session"],
        }

    def _design_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        screens = max(3, int(self._baseline_value(task, 5) // 2))
        return {
            "summary": f"Prepared design exploration for {task.get('title')}.",
            "deliverables": {
                "wireframes": screens,
                "brand_elements": ["palette", "typography"],
                "accessibility": "AA",
            },
            "next_actions": ["Handoff to product", "Collect stakeholder feedback"],
        }

    def _dropshipping_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        suppliers = max(2, int(self._baseline_value(task, 4) // 2))
        return {
            "summary": f"Lined up fulfillment workflow for {task.get('title')}.",
            "supply_chain": {
                "qualified_suppliers": suppliers,
                "catalog_synced": True,
                "avg_margin": round(0.32 * self._priority_multiplier(task), 2),
            },
            "next_actions": ["Push catalog update", "Notify customer success"],
        }

    def _affiliate_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        partners = max(3, int(self._baseline_value(task, 6)))
        return {
            "summary": f"Optimized affiliate initiative for {task.get('title')}.",
            "partnerships": {
                "partners_contacted": partners,
                "offers_live": max(1, partners // 3),
                "tracking_setup": True,
            },
            "next_actions": ["Distribute creative kit", "Schedule performance sync"],
        }

    def _innovation_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        trials = max(1, int(self._baseline_value(task, 3)))
        return {
            "summary": f"Defined pilot roadmap for {task.get('title')}.",
            "experiment_plan": {
                "pilot_trials": trials,
                "validation_metrics": ["activation", "retention"],
                "go_no_go": "board_review",
            },
            "next_actions": ["Assemble pilot cohort", "Allocate R&D budget"],
        }

    def _analytics_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        dashboards = max(1, int(self._baseline_value(task, 2)))
        return {
            "summary": f"Published analytics snapshot for {task.get('title')}.",
            "insights": {
                "dashboards_updated": dashboards,
                "anomaly_score": round(0.1 * self._priority_multiplier(task), 3),
                "data_sources": ["stripe", "marketing_crm"],
            },
            "next_actions": ["Share insights digest", "Trigger telemetry snapshot"],
        }

    def _system_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        checks = max(3, int(self._baseline_value(task, 8)))
        return {
            "summary": f"Completed system readiness checks for {task.get('title')}.",
            "systems": {
                "checks_passed": checks,
                "incident_count": 0,
                "maintenance_window": "scheduled",
            },
            "next_actions": ["Update ops log", "Inform engineering"],
        }

    def _customer_success_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        onboarding = int(self._baseline_value(task, 4))
        return {
            "summary": f"Delivered customer success play for {task.get('title')}.",
            "customer_plan": {
                "active_onboardings": onboarding,
                "retention_play": "value_review",
                "nps_target": 64 + int(6 * self._priority_multiplier(task)),
            },
            "next_actions": ["Send customer briefing", "Log CRM updates"],
        }

    def _generic_brief(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "summary": f"Completed automation run for {task.get('title')}.",
            "notes": {
                "department": task.get("department"),
                "priority": task.get("priority"),
                "objective_id": task.get("objective_id"),
            },
            "next_actions": ["Review output", "Schedule follow-up"],
        }


__all__ = [
    "AutomationWorker",
    "TaskExecutionContext",
    "TaskExecutionResult",
]
