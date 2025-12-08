from __future__ import annotations

from backend.agents.base_agent import OrganizationAgent


class EngLeadAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="eng_lead",
            name="Lead Architect",
            pod="engineering",
            role_summary=
            "Converts product requirements into architecture specs and detailed engineering tasks.",
            responsibilities=[
                "produce_architecture_specs",
                "maintain_system_diagrams",
                "break_features_into_tasks",
                "coordinate_with_cto_and_qa_lead",
            ],
            reports_to=["ceo"],
            manages=[
                "backend_dev",
                "frontend_dev",
                "db_engineer",
                "devops_engineer",
                "security_auditor",
                "code_reviewer",
            ],
        )


class BackendDevAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="backend_dev",
            name="Backend Developer",
            pod="engineering",
            role_summary="Implements APIs, core business logic, schedulers, and data pipelines.",
            responsibilities=[
                "implement_business_logic",
                "integrate_third_party_apis",
                "write_unit_tests_for_core_functions",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )


class FrontendDevAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="frontend_dev",
            name="Frontend Developer",
            pod="engineering",
            role_summary="Builds dashboards and interfaces for Earnetics products.",
            responsibilities=[
                "implement_web_ui_and_visualizations",
                "connect_frontend_to_backends",
                "support_data_visualization_for_metrics",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )


class DBEngineerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="db_engineer",
            name="Database Engineer",
            pod="engineering",
            role_summary="Designs and maintains relational and vector databases for plays, metrics, and logs.",
            responsibilities=[
                "design_schemas",
                "optimize_queries_and_indexes",
                "maintain_backup_and_migration_plans",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )


class DevOpsEngineerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="devops_engineer",
            name="DevOps Engineer",
            pod="engineering",
            role_summary=
            "Handles Dockerization, CI/CD pipelines, deployment scripts, and runtime environments.",
            responsibilities=[
                "write_dockerfiles_and_compose_configs",
                "configure_ci_cd_pipelines",
                "manage_environment_configs_and_scaling",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )


class SecurityAuditorAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="security_auditor",
            name="Security Auditor",
            pod="engineering",
            role_summary=
            "Reviews systems for vulnerabilities, secrets exposure, and misconfigurations before release.",
            responsibilities=[
                "run_security_checks",
                "scan_for_leaked_keys",
                "provide_fix_recommendations",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )


class CodeReviewerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="code_reviewer",
            name="Code Reviewer",
            pod="engineering",
            role_summary="Reviews code from all devs to reduce hallucinations and enforce standards.",
            responsibilities=[
                "enforce_code_style",
                "verify_logic_against_requirements",
                "coordinate_with_qa_on_test_coverage",
            ],
            reports_to=["eng_lead"],
            manages=[],
        )
