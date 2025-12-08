from __future__ import annotations

from backend.agents.base_agent import OrganizationAgent


class ResearchHeadAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="research_head",
            name="Head of Research",
            pod="research",
            role_summary=
            "Summarizes market intelligence into clear recommendations for the executive pod.",
            responsibilities=
            [
                "synthesize_research_reports",
                "recommend_best_niches_and_topics",
                "flag_dying_markets_and_risks",
            ],
            reports_to=["ceo"],
            manages=[
                "trend_hunter",
                "keyword_analyst",
                "competitor_spy",
                "persona_bot",
                "niche_validator",
            ],
        )


class TrendHunterAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="trend_hunter",
            name="Trend Hunter",
            pod="research",
            role_summary=
            "Scrapes news, social platforms, and APIs to find viral trends for offers and content.",
            responsibilities=
            [
                "scan_google_trends_twitter_reddit",
                "detect_emerging_topics",
                "produce_trend_lists_for_keyword_analyst",
            ],
            reports_to=["research_head"],
            manages=[],
        )


class KeywordAnalystAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="keyword_analyst",
            name="Keyword Analyst",
            pod="research",
            role_summary="Uses SEO tools to find high-volume, low-competition search terms and hooks.",
            responsibilities=
            [
                "fetch_keyword_metrics_from_apis",
                "generate_keyword_clusters_for_content",
                "handoff_to_seo_specialist_and_copywriter",
            ],
            reports_to=["research_head"],
            manages=[],
        )


class CompetitorSpyAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="competitor_spy",
            name="Competitor Spy",
            pod="research",
            role_summary=
            "Profiles top competitors to capture pricing, feature sets, funnels, and ads.",
            responsibilities=
            [
                "map_competitor_offers_and_pricing",
                "capture_examples_of_ad_creatives_and_funnels",
                "identify_gaps_and_weaknesses",
            ],
            reports_to=["research_head"],
            manages=[],
        )


class PersonaBotAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="persona_bot",
            name="User Persona Bot",
            pod="research",
            role_summary="Simulates target personas to test messaging, objections, and desires.",
            responsibilities=
            [
                "generate_persona_profiles",
                "run_message_tests",
                "report_likely_objections_and_desires",
            ],
            reports_to=["research_head"],
            manages=[],
        )


class NicheValidatorAgent(OrganizationAgent):
    def __init__(self) -> None:
        super().__init__(
            org_id="niche_validator",
            name="Niche Validator",
            pod="research",
            role_summary=
            "Calculates win probability per niche or play using trend and competitive data.",
            responsibilities=
            [
                "combine_trends_keywords_competitors",
                "score_niches_on_profitability_and_risk",
                "recommend_go_or_no_go_to_executives",
            ],
            reports_to=["research_head"],
            manages=[],
        )
