from __future__ import annotations

from backend.agents.base_agent import OrganizationAgent


class QALeadAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="qa_lead",
            name="QA Lead",
            pod="qa",
            role_summary="Owns the release quality bar and go/no-go decisions.",
            responsibilities=[
                "maintain_test_strategy",
                "approve_or_reject_releases",
                "coordinate_with_eng_and_growth",
            ],
            reports_to=["ceo"],
            manages=[
                "unit_tester",
                "ui_tester",
                "edge_case_monkey",
                "performance_analyst",
            ],
        )


class UnitTesterAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="unit_tester",
            name="Unit Tester",
            pod="qa",
            role_summary="Writes and maintains automated unit tests for backend and logic.",
            responsibilities=[
                "write_pytest_suites",
                "generate_coverage_reports",
                "report_failing_tests",
            ],
            reports_to=["qa_lead"],
            manages=[],
        )


class UITesterAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="ui_tester",
            name="UI Tester",
            pod="qa",
            role_summary="Simulates user flows, clicks, and visual regressions.",
            responsibilities=[
                "build_end_to_end_tests",
                "verify_ui_against_design_specs",
                "log_bugs_with_repro_steps",
            ],
            reports_to=["qa_lead"],
            manages=[],
        )


class EdgeCaseMonkeyAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="edge_case_monkey",
            name="Edge Case Monkey",
            pod="qa",
            role_summary="Tries to break the system with weird inputs and edge conditions.",
            responsibilities=[
                "fuzz_test_forms_and_apis",
                "test_unexpected_user_behaviors",
                "document_crashes",
            ],
            reports_to=["qa_lead"],
            manages=[],
        )


class PerformanceAnalystAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="performance_analyst",
            name="Performance Analyst",
            pod="qa",
            role_summary="Benchmarks load time, throughput, and latency for core flows.",
            responsibilities=[
                "run_load_tests",
                "profile_slow_endpoints",
                "suggest_optimizations",
            ],
            reports_to=["qa_lead"],
            manages=[],
        )
