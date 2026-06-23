from backend.asset_compounding_engine import (
    AssetClass,
    OpportunityInput,
    build_default_playbook,
    rank_opportunities,
    score_opportunity,
)


def test_score_opportunity_prioritizes_ownership_scale_and_automation():
    play = score_opportunity(
        OpportunityInput(
            name="Lead Gen Site",
            description="Owned lead generation property",
            asset_class=AssetClass.LEAD_GEN,
            startup_cost=500,
            estimated_monthly_cashflow=1000,
            time_to_first_cash_days=30,
            owner_required_hours_per_week=4,
            ownership_score=9,
            scalability_score=9,
            automation_score=8,
            recurring_revenue_score=7,
            margin_score=9,
            defensibility_score=6,
            reinvestment_score=8,
        )
    )

    assert play.wealth_score >= 7
    assert play.leverage_score >= 8
    assert play.payback_months == 0.5
    assert play.allocation_priority in {"deploy_capital_and_agents", "test_fast"}


def test_rank_opportunities_places_asset_play_above_low_leverage_labor():
    asset_play = OpportunityInput(
        name="Digital Product Funnel",
        description="Owned digital product with automated delivery",
        asset_class=AssetClass.INTELLECTUAL_PROPERTY,
        startup_cost=300,
        estimated_monthly_cashflow=1200,
        time_to_first_cash_days=21,
        owner_required_hours_per_week=5,
        ownership_score=9,
        scalability_score=9,
        automation_score=9,
        recurring_revenue_score=6,
        margin_score=10,
        defensibility_score=5,
        reinvestment_score=8,
    )
    labor_play = OpportunityInput(
        name="Hourly Labor Contract",
        description="Owner-operated labor contract",
        asset_class=AssetClass.BUSINESS,
        startup_cost=100,
        estimated_monthly_cashflow=4000,
        time_to_first_cash_days=7,
        owner_required_hours_per_week=60,
        ownership_score=2,
        scalability_score=2,
        automation_score=1,
        recurring_revenue_score=2,
        margin_score=4,
        defensibility_score=1,
        reinvestment_score=3,
    )

    ranked = rank_opportunities([labor_play, asset_play])

    assert ranked[0].name == "Digital Product Funnel"
    assert ranked[-1].name == "Hourly Labor Contract"


def test_default_playbook_is_ranked_and_serializable():
    ranked = rank_opportunities(build_default_playbook())

    assert ranked
    assert ranked[0].wealth_score >= ranked[-1].wealth_score
    assert isinstance(ranked[0].to_dict(), dict)
