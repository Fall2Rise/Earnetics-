from __future__ import annotations

from backend.agents.base_agent import OrganizationAgent


class GrowthHeadAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="growth_head",
            name="Head of Sales & Growth",
            pod="growth",
            role_summary="Owns funnel performance, pricing, and scaling decisions.",
            responsibilities=[
                "define_pricing_strategy",
                "approve_launches",
                "coordinate_scaling_or_pivots",
            ],
            reports_to=["ceo"],
            manages=[
                "copywriter",
                "ad_designer",
                "social_manager",
                "seo_specialist",
                "support_bot",
                "analytics_officer",
                "pivot_master",
            ],
        )


class CopywriterAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="copywriter",
            name="Copywriter",
            pod="growth",
            role_summary="Writes landing pages, emails, and sales scripts optimized for conversions.",
            responsibilities=[
                "craft_hooks_and_headlines",
                "write_email_sequences",
                "a_b_test_copy_variants",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class AdDesignerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="ad_designer",
            name="Ad Creative Designer",
            pod="growth",
            role_summary="Generates ad creatives via prompt-based design tools.",
            responsibilities=[
                "generate_prompts_for_creatives",
                "design_thumbnails_and_ad_images",
                "package_assets_for_platforms",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class SocialManagerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="social_manager",
            name="Social Media Manager",
            pod="growth",
            role_summary="Plans and posts social content to drive awareness and traffic.",
            responsibilities=[
                "schedule_posts",
                "repurpose_content",
                "monitor_engagement",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class SEOSpecialistAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="seo_specialist",
            name="SEO Specialist",
            pod="growth",
            role_summary="Optimizes pages and content for search visibility and organic traffic.",
            responsibilities=[
                "set_meta_titles",
                "map_internal_links",
                "coordinate_with_keyword_analyst",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class SupportBotAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="support_bot",
            name="Customer Support Bot",
            pod="growth",
            role_summary="Handles user questions and objections to refine UX.",
            responsibilities=[
                "log_common_questions",
                "propose_faq_updates",
                "surface_product_gaps",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class AnalyticsOfficerAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="analytics_officer",
            name="Analytics Officer",
            pod="growth",
            role_summary="Tracks conversion, revenue, and funnel performance across plays.",
            responsibilities=[
                "maintain_metrics_dashboard",
                "compute_kpis_for_each_play",
                "report_winners_and_losers",
            ],
            reports_to=["growth_head"],
            manages=[],
        )


class PivotMasterAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="pivot_master",
            name="Pivot Master",
            pod="growth",
            role_summary="Monitors revenue vs goals and triggers pivots when plays fail.",
            responsibilities=[
                "detect_underperforming_plays",
                "propose_pivot_scenarios",
                "coordinate_resets_with_executives",
            ],
            reports_to=["growth_head"],
            manages=[],
        )
