from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from backend.agents.atom_agent import AtomAgent
from backend.agents.base_agent import OrganizationAgent
from backend.agents.engineering_agents import (
    BackendDevAgent,
    CodeReviewerAgent,
    DBEngineerAgent,
    DevOpsEngineerAgent,
    EngLeadAgent,
    FrontendDevAgent,
    SecurityAuditorAgent,
)
from backend.agents.executive_agents import CCOAgent, CPOAgent, CTOAgent
from backend.agents.growth_agents import (
    AdDesignerAgent,
    AnalyticsOfficerAgent,
    CopywriterAgent,
    GrowthHeadAgent,
    PivotMasterAgent,
    SEOSpecialistAgent,
    SocialManagerAgent,
    SupportBotAgent,
)
from backend.agents.qa_agents import (
    EdgeCaseMonkeyAgent,
    PerformanceAnalystAgent,
    QALeadAgent,
    UITesterAgent,
    UnitTesterAgent,
)
from backend.agents.research_agents import (
    CompetitorSpyAgent,
    KeywordAnalystAgent,
    NicheValidatorAgent,
    PersonaBotAgent,
    ResearchHeadAgent,
    TrendHunterAgent,
)

logger = logging.getLogger(__name__)

# Resolve paths relative to the repository root so imports work no matter the CWD.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "organization.yaml"
METRICS_PATH = BASE_DIR / "financial" / "performance_metrics.json"

AGENT_CLASS_MAP: Dict[str, Any] = {
    "ceo": AtomAgent,
    "cpo": CPOAgent,
    "cto": CTOAgent,
    "cco": CCOAgent,
    "research_head": ResearchHeadAgent,
    "trend_hunter": TrendHunterAgent,
    "keyword_analyst": KeywordAnalystAgent,
    "competitor_spy": CompetitorSpyAgent,
    "persona_bot": PersonaBotAgent,
    "niche_validator": NicheValidatorAgent,
    "eng_lead": EngLeadAgent,
    "backend_dev": BackendDevAgent,
    "frontend_dev": FrontendDevAgent,
    "db_engineer": DBEngineerAgent,
    "devops_engineer": DevOpsEngineerAgent,
    "security_auditor": SecurityAuditorAgent,
    "code_reviewer": CodeReviewerAgent,
    "qa_lead": QALeadAgent,
    "unit_tester": UnitTesterAgent,
    "ui_tester": UITesterAgent,
    "edge_case_monkey": EdgeCaseMonkeyAgent,
    "performance_analyst": PerformanceAnalystAgent,
    "growth_head": GrowthHeadAgent,
    "copywriter": CopywriterAgent,
    "ad_designer": AdDesignerAgent,
    "social_manager": SocialManagerAgent,
    "seo_specialist": SEOSpecialistAgent,
    "support_bot": SupportBotAgent,
    "analytics_officer": AnalyticsOfficerAgent,
    "pivot_master": PivotMasterAgent,
}

ROUTING_RULES: List[Dict[str, Any]] = [
    {
        "keywords": ("revenue", "sales", "pipeline"),
        "agents": ["growth_head", "analytics_officer", "pivot_master"],
    },
    {
        "keywords": ("product", "feature", "launch"),
        "agents": ["cpo", "eng_lead", "qa_lead", "cco"],
    },
    {
        "keywords": ("research", "market", "persona", "keyword", "niche"),
        "agents": [
            "research_head",
            "trend_hunter",
            "keyword_analyst",
            "competitor_spy",
            "persona_bot",
            "niche_validator",
        ],
    },
    {
        "keywords": ("quality", "bug", "regression", "test"),
        "agents": [
            "qa_lead",
            "unit_tester",
            "ui_tester",
            "edge_case_monkey",
            "performance_analyst",
        ],
    },
    {
        "keywords": ("tech", "architecture", "deploy", "security"),
        "agents": ["cto", "eng_lead", "devops_engineer", "security_auditor", "code_reviewer"],
    },
]


def _load_yaml_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing organization config at {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if "organization" not in data:
        raise ValueError("organization.yaml must define an 'organization' block")
    return data


def _normalize_relation(value: Optional[Any]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _build_generic_agent(config: Dict[str, Any]) -> OrganizationAgent:
    return OrganizationAgent(
        org_id=config["id"],
        name=config["name"],
        pod=config["pod"],
        role_summary=config.get("role", ""),
        responsibilities=config.get("responsibilities", []),
        reports_to=_normalize_relation(config.get("reports_to")),
        manages=_normalize_relation(config.get("manages")),
    )


class EarneticsCorporation:
    def __init__(self, config_path: Path = CONFIG_PATH, metrics_path: Path = METRICS_PATH) -> None:
        self.config_path = config_path
        self.metrics_path = metrics_path
        self.organization_config = _load_yaml_config(config_path)
        self.agents = self._instantiate_agents()
        self.pod_index = self._build_pod_index()
        self.performance_metrics = self._load_or_initialize_metrics()

    def _instantiate_agents(self) -> Dict[str, Any]:
        agents: Dict[str, Any] = {}
        org_section = self.organization_config.get("organization", {})
        ceo_class = AGENT_CLASS_MAP.get("ceo")
        if ceo_class is None:
            raise ValueError("Missing CEO class mapping")
        agents["ceo"] = ceo_class()
        for agent_cfg in org_section.get("agents", []):
            agent_id = agent_cfg["id"]
            agent_class = AGENT_CLASS_MAP.get(agent_id)
            if agent_class is not None:
                agents[agent_id] = agent_class()
            else:
                agents[agent_id] = _build_generic_agent(agent_cfg)
        return agents

    def _build_pod_index(self) -> Dict[str, Dict[str, Any]]:
        pods: Dict[str, Dict[str, Any]] = {}
        org_section = self.organization_config.get("organization", {})
        for pod in org_section.get("pods", []):
            pods[pod["id"]] = {
                "name": pod["name"],
                "description": pod.get("description", ""),
                "agents": [],
            }
        for agent_id, agent in self.agents.items():
            pod_id = getattr(agent, "pod", None)
            if pod_id and pod_id in pods:
                pods[pod_id]["agents"].append(agent_id)
        if "executive" in pods and "ceo" not in pods["executive"]["agents"]:
            pods["executive"]["agents"].insert(0, "ceo")
        return pods

    def _load_or_initialize_metrics(self) -> Dict[str, Any]:
        if self.metrics_path.exists():
            try:
                with self.metrics_path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception as exc:
                logger.warning("Unable to read metrics file: %s", exc)
        metrics = {
            "total_revenue": 0.0,
            "monthly_target": 150000.0,
            "active_customers": 0,
            "products_created": 0,
            "directives_executed": 0,
            "last_updated": datetime.utcnow().isoformat(),
        }
        self._save_metrics(metrics)
        return metrics

    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with self.metrics_path.open("w", encoding="utf-8") as handle:
            json.dump(metrics, handle, indent=2)

    def _context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = {
            "total_revenue": self.performance_metrics["total_revenue"],
            "monthly_target": self.performance_metrics["monthly_target"],
            "active_customers": self.performance_metrics["active_customers"],
            "products_created": self.performance_metrics["products_created"],
        }
        if extra:
            context.update(extra)
        return context

    def _plan_for_agent(self, agent_id: str, context: Dict[str, Any], signal: Optional[str] = None) -> Optional[Dict[str, Any]]:
        agent = self.agents.get(agent_id)
        if agent is None:
            return None
        if hasattr(agent, "plan_focus"):
            return agent.plan_focus(context)
        if hasattr(agent, "strategic_brief"):
            signal_value = signal or context.get("directive", "directive")
            return agent.strategic_brief(signal_value, context)
        if hasattr(agent, "profile"):
            return agent.profile()
        return None

    def _plan_for_agents(self, agent_ids: List[str], context: Dict[str, Any], signal: Optional[str] = None) -> Dict[str, Any]:
        plans: Dict[str, Any] = {}
        for agent_id in agent_ids:
            plan = self._plan_for_agent(agent_id, context, signal)
            if plan is not None:
                plans[agent_id] = plan
        return plans

    def _route_directive(self, directive: str) -> List[str]:
        directive_lower = directive.lower()
        routed: List[str] = []
        for rule in ROUTING_RULES:
            if any(keyword in directive_lower for keyword in rule["keywords"]):
                for agent_id in rule["agents"]:
                    if agent_id in self.agents and agent_id not in routed:
                        routed.append(agent_id)
        if not routed:
            for fallback in ["cpo", "eng_lead", "growth_head"]:
                if fallback in self.agents and fallback not in routed:
                    routed.append(fallback)
        return routed

    def execute_corporate_directive(self, directive: str, priority: str = "high") -> Dict[str, Any]:
        context = self._context({"directive": directive, "priority": priority})
        ceo_brief = self._plan_for_agent("ceo", context, directive)
        routed_agents = self._route_directive(directive)
        departmental_focus = self._plan_for_agents(routed_agents, context, directive)
        self.performance_metrics["directives_executed"] += 1
        self.performance_metrics["last_updated"] = datetime.utcnow().isoformat()
        self._save_metrics(self.performance_metrics)
        return {
            "directive": directive,
            "priority": priority,
            "status": "executed",
            "ceo_brief": ceo_brief,
            "departmental_focus": departmental_focus,
            "coordination_scope": routed_agents,
            "success_probability": min(99, 84 + len(departmental_focus) * 2),
            "execution_window": "2-4 weeks",
            "metrics": self.performance_metrics.copy(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def process_revenue_transaction(self, amount: float, source: str, category: str) -> Dict[str, Any]:
        context = self._context({"amount": amount, "source": source, "category": category})
        growth_plan = self._plan_for_agent("growth_head", context, source)
        analytics_plan = self._plan_for_agent("analytics_officer", context, source)
        pivot_plan = self._plan_for_agent("pivot_master", context, source)
        self.performance_metrics["total_revenue"] += amount
        if category == "digital_sales":
            self.performance_metrics["active_customers"] += 1
        self.performance_metrics["last_updated"] = datetime.utcnow().isoformat()
        self._save_metrics(self.performance_metrics)
        return {
            "transaction": {
                "amount": amount,
                "source": source,
                "category": category,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "growth_analysis": growth_plan,
            "analytics_review": analytics_plan,
            "pivot_readiness": pivot_plan,
            "updated_metrics": self.performance_metrics.copy(),
            "status": "processed",
        }

    def create_digital_product(self, product_type: str, target_audience: str, price_point: float) -> Dict[str, Any]:
        context = self._context(
            {
                "product_type": product_type,
                "target_audience": target_audience,
                "price_point": price_point,
            }
        )
        leadership_agents = ["cpo", "eng_lead", "qa_lead", "cco"]
        launch_agents = ["copywriter", "ad_designer", "growth_head", "seo_specialist"]
        leadership_plan = self._plan_for_agents(leadership_agents, context, product_type)
        launch_plan = self._plan_for_agents(launch_agents, context, product_type)
        product_id = f"PROD_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.performance_metrics["products_created"] += 1
        self.performance_metrics["last_updated"] = datetime.utcnow().isoformat()
        self._save_metrics(self.performance_metrics)
        return {
            "product": {
                "id": product_id,
                "type": product_type,
                "target_audience": target_audience,
                "price_point": price_point,
                "status": "in_development",
            },
            "product_leadership": leadership_plan,
            "launch_support": launch_plan,
            "go_to_market_agents": launch_agents,
            "estimated_launch_window": "4-6 weeks",
            "status": "coordinating",
            "metrics": self.performance_metrics.copy(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def generate_market_research(self, industry: str, target_market: str) -> Dict[str, Any]:
        context = self._context({"industry": industry, "target_market": target_market})
        research_agents = [
            "research_head",
            "trend_hunter",
            "keyword_analyst",
            "competitor_spy",
            "persona_bot",
            "niche_validator",
        ]
        research_outputs = self._plan_for_agents(research_agents, context, industry)
        return {
            "industry": industry,
            "target_market": target_market,
            "status": "completed",
            "research_outputs": research_outputs,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_system_status(self) -> Dict[str, Any]:
        context = self._context({"signal": "system_status"})
        ceo_view = self._plan_for_agent("ceo", context, "system_status")
        pivot_view = self._plan_for_agent("pivot_master", context, "system_status")
        qa_view = self._plan_for_agent("qa_lead", context, "system_status")
        pod_snapshot = {
            pod_id: {
                "name": details["name"],
                "agents": details["agents"],
                "description": details["description"],
            }
            for pod_id, details in self.pod_index.items()
        }
        return {
            "system_overview": {
                "status": "OPERATIONAL",
                "total_agents": len(self.agents),
                "pods": pod_snapshot,
                "performance_metrics": self.performance_metrics.copy(),
            },
            "executive_assessment": ceo_view,
            "pivot_readiness": pivot_view,
            "quality_status": qa_view,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def financial_summary(self) -> Dict[str, Any]:
        context = self._context({"signal": "financial_summary"})
        analytics_plan = self._plan_for_agent("analytics_officer", context, "financial_summary")
        growth_plan = self._plan_for_agent("growth_head", context, "financial_summary")
        pivot_plan = self._plan_for_agent("pivot_master", context, "financial_summary")
        return {
            "financial_summary": {
                "analytics_officer": analytics_plan,
                "growth_head": growth_plan,
                "pivot_master": pivot_plan,
            },
            "performance_metrics": self.performance_metrics.copy(),
            "timestamp": datetime.utcnow().isoformat(),
        }


aio_corporation = EarneticsCorporation()


def execute_directive(directive: str, priority: str = "high") -> Dict[str, Any]:
    return ai_corporation.execute_corporate_directive(directive, priority)


def process_revenue(amount: float, source: str, category: str, description: str = "") -> Dict[str, Any]:
    return ai_corporation.process_revenue_transaction(amount, source, category)


def create_product(
    product_type: str, target_audience: str, price_point: float, description: str = ""
) -> Dict[str, Any]:
    return ai_corporation.create_digital_product(product_type, target_audience, price_point)


def market_research(industry: str = "AI Automation", target_market: str = "Business Owners") -> Dict[str, Any]:
    return ai_corporation.generate_market_research(industry, target_market)


def system_status() -> Dict[str, Any]:
    return ai_corporation.get_system_status()


def financial_summary() -> Dict[str, Any]:
    return ai_corporation.financial_summary()
