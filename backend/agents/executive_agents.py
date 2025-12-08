from __future__ import annotations

from backend.agents.base_agent import OrganizationAgent


class CPOAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="cpo",
            name="Chief Product Officer",
            pod="executive",
            role_summary="Translates revenue targets into product roadmaps, funnels, and offers.",
            responsibilities=[
                "maintain_product_roadmap",
                "select_core_plays_for_execution",
                "define_feature_sets_for_each_play",
                "coordinate_with_research_and_engineering",
            ],
            reports_to=["ceo"],
            manages=[],
        )


class CTOAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="cto",
            name="Chief Technology Officer",
            pod="executive",
            role_summary="Decides tech stacks, architecture patterns, and core services for Earnetics.",
            responsibilities=[
                "select_core_tech_stack",
                "define_service_boundaries_and_apis",
                "approve_long_term_technical_direction",
                "coordinate_with_eng_lead_and_security_auditor",
            ],
            reports_to=["ceo"],
            manages=[],
        )


class CCOAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="cco",
            name="Chief Creative Officer",
            pod="executive",
            role_summary="Owns brand voice, visuals, and emotional tone of all public-facing assets.",
            responsibilities=[
                "define_brand_guidelines",
                "approve_landing_page_and_ad_creatives",
                "coordinate_with_copywriter_and_ad_designer",
            ],
            reports_to=["ceo"],
            manages=[],
        )
