"""Core play definitions for Earnetics Wealth Core.

These are canonical revenue play blueprints that seed the WealthPortfolio
on first startup when the portfolio is empty.
"""

from typing import Any, Dict, List

CORE_PLAYS_SEED: List[Dict[str, Any]] = [
    # 1) Increase investments in marketing
    {
        "id": "rev-01-increase-investments-marketing",
        "name": "Increase Investments in Marketing",
        "description": "Scale high-performing lead generation channels while protecting CAC and sales capacity.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["marketing", "lead_generation", "budget_allocation", "growth"],
        "budget": {
            "mode": "performance_based",
            "max_monthly_spend_usd": 20000,
            "reinvest_ratio": 0.4,
        },
        "kpis": {
            "target_mqls_per_month": 200,
            "max_target_cac_usd": 150,
            "pipeline_coverage_multiple": 3.0,
            "lead_to_opportunity_rate_target": 0.2,
            "opportunity_to_close_rate_target": 0.25,
        },
        "execution_plan": {
            "owner_roles": ["Marketing_Ops_Agent", "Demand_Gen_Agent"],
            "channels": ["paid_ads", "organic_search", "social", "email"],
            "cadence": {
                "analysis": "weekly",
                "optimization": "weekly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "pull_channel_performance",
                    "title": "Pull Current Channel Performance",
                    "desc": "Collect performance for all existing acquisition channels including spend, CAC, conversion rates and revenue.",
                    "automation": [
                        "pull_crm_opportunity_data",
                        "pull_ads_platform_stats",
                        "merge_channel_kpis_to_dashboard",
                    ],
                },
                {
                    "key": "rank_channels",
                    "title": "Rank Channels By Efficiency",
                    "desc": "Rank channels by CAC, conversion rate, and LTV so budget increases only go to the most efficient sources.",
                    "automation": [
                        "score_channels_by_cac_and_ltv",
                        "tag_channels_as_scale_or_cut",
                    ],
                },
                {
                    "key": "reallocate_budget",
                    "title": "Reallocate Marketing Budget",
                    "desc": "Shift budget from underperforming channels into high-performing ones while respecting monthly caps and CAC limits.",
                    "automation": [
                        "update_ads_budgets_via_api",
                        "notify_marketing_owner_of_changes",
                    ],
                },
                {
                    "key": "capacity_check",
                    "title": "Check Sales Capacity Before Scaling",
                    "desc": "Ensure sales team capacity is not exceeded by projected lead volume to avoid pipeline overload.",
                    "automation": [
                        "calculate_leads_per_rep_projection",
                        "alert_sales_lead_if_capacity_exceeded",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["scaling_smb", "midmarket"],
            "ideal_industries": ["b2b_saas", "services"],
            "dependencies": ["needs_crm", "needs_ads_accounts", "needs_marketing_automation"],
            "notes": "Used when the company has reliable CAC benchmarks and wants to scale demand generation without crushing sales.",
        },
    },

    # 2) Experiment with sales compensation
    {
        "id": "rev-02-sales-compensation-experiments",
        "name": "Optimize Sales Compensation",
        "description": "Run structured experiments on commission plans to increase win rates, deal size and long-term value.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["sales", "compensation", "commission", "incentives"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 5000,
            "reinvest_ratio": 0.2,
        },
        "kpis": {
            "win_rate_uplift_target": 0.05,
            "avg_deal_size_uplift_target": 0.1,
            "clv_improvement_target": 0.1,
            "ramp_time_reduction_days": 15,
        },
        "execution_plan": {
            "owner_roles": ["Sales_Leader_Agent", "RevOps_Agent"],
            "channels": ["crm", "internal_comms"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "quarterly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "baseline_metrics",
                    "title": "Establish Baseline Metrics",
                    "desc": "Capture current win rates, deal sizes and contract terms by rep and segment before any changes.",
                    "automation": [
                        "pull_crm_closed_won_lost_data",
                        "calculate_baseline_sales_metrics",
                    ],
                },
                {
                    "key": "design_plan_variants",
                    "title": "Design Compensation Plan Variants",
                    "desc": "Design 2–3 alternative commission structures that reward higher LTV and lower discounting.",
                    "automation": [
                        "generate_plan_templates",
                        "simulate_commission_costs_from_history",
                    ],
                },
                {
                    "key": "pilot_and_measure",
                    "title": "Pilot Changes With a Subset of Reps",
                    "desc": "Assign plan variants to pilot groups and compare performance against control over a set period.",
                    "automation": [
                        "tag_pilot_reps_in_crm",
                        "track_pilot_kpis_vs_control",
                        "send_monthly_pilot_reports_to_leadership",
                    ],
                },
                {
                    "key": "rollout_or_revert",
                    "title": "Roll Out Best Plan or Revert",
                    "desc": "Promote the winning plan to the full team if it outperforms baseline; otherwise revert and log learnings.",
                    "automation": [
                        "update_compensation_docs",
                        "notify_finance_and_hr",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["scaling_smb", "midmarket"],
            "ideal_industries": ["b2b_saas", "agency", "services"],
            "dependencies": ["needs_crm", "needs_hr_payroll"],
            "notes": "Use when sales performance is flat and reps are not strongly incentivized to close healthy deals.",
        },
    },

    # 3) Focus on brand awareness
    {
        "id": "rev-03-brand-awareness-engine",
        "name": "Brand Awareness Growth Engine",
        "description": "Systematically grow brand visibility and demand through consistent top-of-funnel campaigns and content.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["brand", "awareness", "content", "social"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 8000,
            "reinvest_ratio": 0.3,
        },
        "kpis": {
            "brand_search_volume_lift_target": 0.15,
            "social_reach_growth_target": 0.2,
            "website_sessions_growth_target": 0.15,
            "direct_traffic_growth_target": 0.1,
        },
        "execution_plan": {
            "owner_roles": ["Brand_Marketing_Agent", "Content_Agent"],
            "channels": ["social", "blog", "video", "podcast"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "audience_mapping",
                    "title": "Map Priority Audiences and Channels",
                    "desc": "Define primary personas and identify which channels they use for discovery and research.",
                    "automation": [
                        "analyze_crm_segments",
                        "combine_with_website_analytics_personas",
                    ],
                },
                {
                    "key": "content_calendar",
                    "title": "Build Awareness Content Calendar",
                    "desc": "Generate a rolling calendar of educational and authority-building content mapped to each persona and channel.",
                    "automation": [
                        "generate_topic_backlog_from_keyword_data",
                        "schedule_content_in_social_tool",
                    ],
                },
                {
                    "key": "brand_tracking",
                    "title": "Track Brand Awareness Signals",
                    "desc": "Monitor branded search, social mentions and direct traffic as proxy indicators of brand lift.",
                    "automation": [
                        "pull_brand_keyword_stats",
                        "track_social_mentions_and_tags",
                        "update_brand_kpi_dashboard",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["early_stage_saas", "scaling_smb"],
            "ideal_industries": ["b2b_saas", "consumer_apps"],
            "dependencies": ["needs_analytics", "needs_social_accounts"],
            "notes": "Use when performance channels are plateauing and you need more people to even know you exist.",
        },
    },

    # 4) Adjust brand positioning
    {
        "id": "rev-04-reposition-brand",
        "name": "Brand Positioning Shift",
        "description": "Realign brand messaging and category position to better match what high-value customers care about.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["brand", "positioning", "messaging", "strategy"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 10000,
            "reinvest_ratio": 0.25,
        },
        "kpis": {
            "win_rate_lift_in_target_segment": 0.1,
            "nps_improvement_target": 5,
            "message_resonance_score_target": 0.2,
            "pricing_power_increase_target": 0.05,
        },
        "execution_plan": {
            "owner_roles": ["Product_Marketing_Agent", "Leadership_Agent"],
            "channels": ["website", "sales_assets", "ads"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "voice_of_customer_research",
                    "title": "Run Voice of Customer Research",
                    "desc": "Interview and survey best-fit customers to capture their words for pains, outcomes and alternatives.",
                    "automation": [
                        "pull_recent_win_loss_notes",
                        "cluster_feedback_into_themes",
                    ],
                },
                {
                    "key": "craft_new_positioning",
                    "title": "Craft New Positioning Narrative",
                    "desc": "Draft new value propositions, category framing and proof points based on customer language.",
                    "automation": [
                        "generate_positioning_doc_draft",
                        "compare_new_vs_old_message_performance",
                    ],
                },
                {
                    "key": "rollout_new_messaging",
                    "title": "Roll Out New Messaging Across Assets",
                    "desc": "Update website, sales decks, ad copy and onboarding flows to reflect the new positioning.",
                    "automation": [
                        "create_asset_update_task_list",
                        "track_asset_update_completion",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["scaling_smb", "midmarket"],
            "ideal_industries": ["b2b_saas", "healthtech", "fintech"],
            "dependencies": ["needs_website_cms", "needs_sales_enablement"],
            "notes": "Use when buyers misunderstand your value or lump you with cheap alternatives.",
        },
    },

    # 5) Implement premium pricing
    {
        "id": "rev-05-premium-pricing-strategy",
        "name": "Premium Pricing Uplift",
        "description": "Increase prices and reposition plans to capture more value from high-intent customers.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["pricing", "revenue", "monetization"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 3000,
            "reinvest_ratio": 0.15,
        },
        "kpis": {
            "arpu_increase_target": 0.15,
            "churn_increase_max_tolerated": 0.02,
            "gross_revenue_lift_target": 0.1,
            "enterprise_deal_count_growth": 0.1,
        },
        "execution_plan": {
            "owner_roles": ["Monetization_Agent", "Finance_Agent"],
            "channels": ["billing", "website", "sales"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "price_sensitivity_analysis",
                    "title": "Analyze Price Sensitivity",
                    "desc": "Review discounting behavior, win/loss reasons and competitor pricing to estimate price elasticity.",
                    "automation": [
                        "pull_discounting_data_from_crm",
                        "compare_current_prices_with_competitors",
                    ],
                },
                {
                    "key": "design_new_tiers",
                    "title": "Design New Pricing Tiers",
                    "desc": "Create updated plans with clearer value ladders and higher anchor pricing for advanced tiers.",
                    "automation": [
                        "generate_plan_matrix",
                        "simulate_revenue_impact_using_historical_data",
                    ],
                },
                {
                    "key": "grandfather_and_rollout",
                    "title": "Grandfather Old Customers and Roll Out",
                    "desc": "Grandfather existing customers where needed and roll out new prices for new deals and upgrades.",
                    "automation": [
                        "segment_customers_for_grandfathering",
                        "update_billing_system_plans",
                        "notify_sales_and_support_of_changes",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["scaling_smb", "midmarket"],
            "ideal_industries": ["b2b_saas"],
            "dependencies": ["needs_billing_system", "needs_crm"],
            "notes": "Best used when product value is clearly higher than current price suggests.",
        },
    },

    # 6) Strategic discounted pricing
    {
        "id": "rev-06-strategic-discounting",
        "name": "Strategic Discount & Offer Engine",
        "description": "Use tightly controlled discounts, bundles and loyalty offers to increase conversion and order value.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["pricing", "discounts", "promotions", "conversion"],
        "budget": {
            "mode": "experimental",
            "max_monthly_spend_usd": 5000,
            "reinvest_ratio": 0.2,
        },
        "kpis": {
            "checkout_conversion_lift_target": 0.1,
            "avg_order_value_increase_target": 0.1,
            "discount_usage_rate_max": 0.3,
            "gross_margin_floor": 0.6,
        },
        "execution_plan": {
            "owner_roles": ["Growth_Agent", "Ecommerce_Agent"],
            "channels": ["website", "email", "ads"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "identify_high_intent_segments",
                    "title": "Identify High-Intent Segments",
                    "desc": "Determine which segments abandon at checkout or hesitate despite high intent.",
                    "automation": [
                        "analyze_cart_abandonment",
                        "segment_users_by_behavior",
                    ],
                },
                {
                    "key": "design_promo_rules",
                    "title": "Design Smart Promotion Rules",
                    "desc": "Create rules for limited-time discounts, bundles and loyalty rewards with guardrails on margin.",
                    "automation": [
                        "define_discount_rule_engine_config",
                        "simulate_margin_impact_for_each_rule",
                    ],
                },
                {
                    "key": "test_and_iterate_promos",
                    "title": "Test Promotions and Iterate",
                    "desc": "AB test different offers and keep only those that increase net profit and LTV.",
                    "automation": [
                        "run_ab_tests_on_offer_variants",
                        "auto_pause_underperforming_promos",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["ecommerce", "b2c", "b2b_saas"],
            "ideal_industries": ["ecommerce", "b2b_saas"],
            "dependencies": ["needs_checkout_system"],
            "notes": "Avoid blanket discounting; use rules and profitability checks.",
        },
    },

    # 7) Expand distribution channels
    {
        "id": "rev-07-expand-distribution-channels",
        "name": "Distribution Channel Expansion",
        "description": "Add new sales and delivery channels to reach more buyers without losing control of margins.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["distribution", "channels", "partners", "marketplace"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 15000,
            "reinvest_ratio": 0.3,
        },
        "kpis": {
            "new_channel_revenue_share_target": 0.2,
            "channel_cac_ceiling": 200,
            "active_resellers_target": 10,
            "marketplace_rating_floor": 4.3,
        },
        "execution_plan": {
            "owner_roles": ["Channel_Sales_Agent", "Partnerships_Agent"],
            "channels": ["reseller", "marketplaces", "direct", "distributors"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "map_existing_channels",
                    "title": "Map Existing and Potential Channels",
                    "desc": "Document current channels and identify gaps where buyers expect to find you.",
                    "automation": [
                        "pull_sales_by_channel_report",
                        "generate_channel_gap_analysis",
                    ],
                },
                {
                    "key": "onboard_new_channel",
                    "title": "Onboard a New Channel",
                    "desc": "Select a high-potential channel and build the basic listing, pricing and fulfillment rules.",
                    "automation": [
                        "create_marketplace_or_reseller_listing_templates",
                        "sync_inventory_and_pricing_feeds",
                    ],
                },
                {
                    "key": "monitor_channel_profitability",
                    "title": "Monitor Channel Profitability",
                    "desc": "Track net margin and churn by channel to quickly prune unprofitable ones.",
                    "automation": [
                        "merge_channel_fees_with_cogs",
                        "flag_channels_below_margin_floor",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["product_business", "ecommerce"],
            "ideal_industries": ["retail", "consumer_goods", "software_distribution"],
            "dependencies": ["needs_inventory_or_license_system"],
            "notes": "Use when one channel dominates revenue and you want diversification.",
        },
    },

    # 8) Change / adapt offers
    {
        "id": "rev-08-offer-optimization",
        "name": "Offer Optimization and Bundling",
        "description": "Repackage products and services into more compelling offers that better match buyer needs.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["offers", "bundling", "upsell", "product"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 4000,
            "reinvest_ratio": 0.2,
        },
        "kpis": {
            "avg_order_value_increase_target": 0.15,
            "attach_rate_target": 0.2,
            "conversion_rate_lift_target": 0.05,
        },
        "execution_plan": {
            "owner_roles": ["Product_Marketing_Agent", "Growth_Agent"],
            "channels": ["website", "checkout", "sales"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "analyze_line_item_sales",
                    "title": "Analyze Line-Item Sales",
                    "desc": "Identify products commonly purchased together and those with low attach rates.",
                    "automation": [
                        "pull_order_line_items",
                        "compute_product_pair_frequencies",
                    ],
                },
                {
                    "key": "create_bundles_and_addons",
                    "title": "Create Bundles and Add-ons",
                    "desc": "Design bundles and add-ons that increase perceived value while preserving margin.",
                    "automation": [
                        "generate_bundle_candidates",
                        "simulate_bundle_price_and_margin",
                    ],
                },
                {
                    "key": "deploy_offer_tests",
                    "title": "Deploy Offer Experiments",
                    "desc": "AB test new offers at checkout and via sales scripts and keep only top performers.",
                    "automation": [
                        "configure_checkout_ab_tests",
                        "measure_offer_test_results",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["ecommerce", "b2b_saas", "services"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_checkout_or_crm"],
            "notes": "Fast way to unlock more revenue per customer without building new product.",
        },
    },

    # 9) Reposition existing offerings
    {
        "id": "rev-09-reposition-offerings",
        "name": "Use-Case Repositioning",
        "description": "Reframe existing products around specific use cases and verticals to unlock new segments.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["positioning", "use_cases", "verticals"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 6000,
            "reinvest_ratio": 0.25,
        },
        "kpis": {
            "new_segment_pipeline_share_target": 0.2,
            "win_rate_in_new_segment_target": 0.2,
            "number_of_use_case_pages": 5,
        },
        "execution_plan": {
            "owner_roles": ["Product_Marketing_Agent", "Sales_Leader_Agent"],
            "channels": ["website", "sales_assets", "email"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "identify_use_case_clusters",
                    "title": "Identify Use-Case Clusters",
                    "desc": "Group customers by the primary job they hire your product to do and the vertical they belong to.",
                    "automation": [
                        "cluster_customers_by_usage_patterns",
                        "tag_accounts_with_primary_use_case",
                    ],
                },
                {
                    "key": "create_use_case_assets",
                    "title": "Create Use-Case Specific Assets",
                    "desc": "Generate landing pages, case studies and sales one-pagers per use case.",
                    "automation": [
                        "generate_use_case_page_templates",
                        "pull_relevant_case_study_quotes",
                    ],
                },
                {
                    "key": "target_use_case_campaigns",
                    "title": "Launch Use-Case Campaigns",
                    "desc": "Run campaigns targeting each use case and measure uptake versus generic messaging.",
                    "automation": [
                        "launch_segmented_email_campaigns",
                        "compare_use_case_vs_generic_performance",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["b2b_saas", "services"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_crm", "needs_website_cms"],
            "notes": "Useful when product is broad but messaging is generic and unfocused.",
        },
    },

    # 10) Modernize legacy offerings
    {
        "id": "rev-10-modernize-legacy-offerings",
        "name": "Modernize Legacy Offerings",
        "description": "Refresh outdated products or services to meet current expectations, and re-launch them for new revenue.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["legacy", "product_refresh", "relaunch"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 12000,
            "reinvest_ratio": 0.3,
        },
        "kpis": {
            "legacy_revenue_reactivation_target": 0.2,
            "customer_satisfaction_lift_target": 0.15,
            "upgrade_rate_from_legacy_target": 0.25,
        },
        "execution_plan": {
            "owner_roles": ["Product_Agent", "Customer_Success_Agent"],
            "channels": ["email", "in_app", "sales"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "audit_legacy_portfolio",
                    "title": "Audit Legacy Portfolio",
                    "desc": "Identify legacy products with loyal but shrinking user bases and outdated UX or packaging.",
                    "automation": [
                        "list_legacy_skus_and_plans",
                        "pull_churn_and_usage_for_legacy",
                    ],
                },
                {
                    "key": "define_modernization_scope",
                    "title": "Define Modernization Scope",
                    "desc": "Specify what needs updating—UX, pricing, packaging, compliance—based on customer feedback.",
                    "automation": [
                        "aggregate_legacy_feedback",
                        "prioritize_modernization_backlog",
                    ],
                },
                {
                    "key": "relaunch_to_legacy_segment",
                    "title": "Relaunch Updated Legacy Offering",
                    "desc": "Announce the refreshed offering to existing and lapsed legacy users with special upgrade paths.",
                    "automation": [
                        "build_reactivation_email_sequences",
                        "track_upgrade_and_reactivation_rates",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["established", "midmarket"],
            "ideal_industries": ["software", "telecom", "financial_services"],
            "dependencies": ["needs_product_team", "needs_success_team"],
            "notes": "Helps unlock value from old lines without building from scratch.",
        },
    },

    # 11) Solidify recurring revenue
    {
        "id": "rev-11-solidify-recurring-revenue",
        "name": "Recurring Revenue Solidification",
        "description": "Convert one-off or ad-hoc revenue into predictable subscriptions and renewable contracts.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["subscriptions", "contracts", "recurring_revenue"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 7000,
            "reinvest_ratio": 0.25,
        },
        "kpis": {
            "mrr_growth_target": 0.15,
            "contract_renewal_rate_target": 0.9,
            "share_of_revenue_recurring_target": 0.7,
        },
        "execution_plan": {
            "owner_roles": ["Monetization_Agent", "Customer_Success_Agent"],
            "channels": ["billing", "crm", "email"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "quarterly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "map_non_recurring_revenue",
                    "title": "Map Non-Recurring Revenue",
                    "desc": "Identify services and products that are frequently repurchased but not on subscription.",
                    "automation": [
                        "pull_invoice_history",
                        "tag_repeat_purchases_without_contracts",
                    ],
                },
                {
                    "key": "design_subscription_packages",
                    "title": "Design Subscription and Retainer Packages",
                    "desc": "Bundle recurring value into monthly or annual contracts with clear benefits over ad hoc.",
                    "automation": [
                        "generate_subscription_package_options",
                        "simulate_mrr_and_margin_impact",
                    ],
                },
                {
                    "key": "migrate_customers",
                    "title": "Migrate Customers to Recurring",
                    "desc": "Prioritize high-fit accounts for contract migration and orchestrate outreach.",
                    "automation": [
                        "generate_migration_target_list",
                        "create_success_and_sales_playbooks",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["services", "b2b_saas"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_billing_system", "needs_crm"],
            "notes": "Core play for stabilizing cash flow and valuation.",
        },
    },

    # 12) Target product penetration
    {
        "id": "rev-12-product-penetration",
        "name": "Product Penetration in Existing Accounts",
        "description": "Drive deeper adoption and expansion within current customers via upsell and cross-sell motions.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["upsell", "cross_sell", "expansion", "account_growth"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 6000,
            "reinvest_ratio": 0.25,
        },
        "kpis": {
            "net_revenue_retention_target": 1.1,
            "expansion_revenue_share_target": 0.25,
            "multi_product_account_share_target": 0.5,
        },
        "execution_plan": {
            "owner_roles": ["Account_Management_Agent", "Customer_Success_Agent"],
            "channels": ["crm", "in_app", "email"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "identify_expansion_signals",
                    "title": "Identify Expansion Signals",
                    "desc": "Use usage patterns and account health to flag customers ready for add-ons or higher tiers.",
                    "automation": [
                        "compute_product_usage_scores",
                        "flag_accounts_with_high_usage_and_health",
                    ],
                },
                {
                    "key": "build_expansion_playbooks",
                    "title": "Build Expansion Playbooks",
                    "desc": "Create tailored offers and scripts for upsell and cross-sell by segment.",
                    "automation": [
                        "generate_expansion_sequences",
                        "sync_playbooks_to_crm",
                    ],
                },
                {
                    "key": "run_expansion_campaigns",
                    "title": "Run Expansion Campaigns",
                    "desc": "Coordinate success and sales outreach focused on expansion opportunities.",
                    "automation": [
                        "create_expansion_tasks_for_account_owners",
                        "track_expansion_pipeline_and_closed_won",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["b2b_saas", "services"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_product_usage_data", "needs_crm"],
            "notes": "High ROI play because it targets customers who already trust you.",
        },
    },

    # 13) Focus on customer retention
    {
        "id": "rev-13-customer-retention",
        "name": "Customer Retention & Churn Reduction",
        "description": "Actively monitor and reduce churn using health scores, save plays, and proactive outreach.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["retention", "churn", "customer_success"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 8000,
            "reinvest_ratio": 0.3,
        },
        "kpis": {
            "gross_churn_rate_max": 0.05,
            "net_revenue_retention_floor": 1.0,
            "save_play_success_rate_target": 0.3,
        },
        "execution_plan": {
            "owner_roles": ["Customer_Success_Agent", "Support_Agent"],
            "channels": ["crm", "in_app", "email", "support"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "build_health_scores",
                    "title": "Build Account Health Scores",
                    "desc": "Combine usage, support volume and payment behavior into a single churn-risk score.",
                    "automation": [
                        "pull_usage_and_support_data",
                        "calculate_health_score_per_account",
                    ],
                },
                {
                    "key": "define_save_plays",
                    "title": "Define Churn Save Plays",
                    "desc": "Create outreach templates and offers tailored to specific risk reasons.",
                    "automation": [
                        "generate_save_play_templates",
                        "map_save_plays_to_health_segments",
                    ],
                },
                {
                    "key": "monitor_and_trigger",
                    "title": "Monitor Health and Trigger Plays",
                    "desc": "Continuously watch for drops in health score and automatically trigger tasks.",
                    "automation": [
                        "set_health_score_threshold_alerts",
                        "auto_create_save_tasks_in_crm",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["b2b_saas", "subscription_business"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_product_usage_data", "needs_support_system"],
            "notes": "Retention is usually cheaper than acquisition; this play protects base revenue.",
        },
    },

    # 14) Optimize mobile experience
    {
        "id": "rev-14-optimize-mobile-experience",
        "name": "Mobile Experience Optimization",
        "description": "Improve mobile UX and performance to remove friction and increase conversions from mobile traffic.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["mobile", "ux", "conversion", "website"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 9000,
            "reinvest_ratio": 0.25,
        },
        "kpis": {
            "mobile_conversion_rate_lift_target": 0.2,
            "mobile_bounce_rate_reduction_target": 0.15,
            "mobile_page_load_time_max_seconds": 3,
        },
        "execution_plan": {
            "owner_roles": ["Web_Optimization_Agent", "UX_Agent"],
            "channels": ["mobile_web", "app"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "audit_mobile_funnel",
                    "title": "Audit Mobile Funnel",
                    "desc": "Measure where mobile users drop off across the funnel from landing to checkout.",
                    "automation": [
                        "pull_mobile_analytics",
                        "visualize_mobile_funnel_dropoffs",
                    ],
                },
                {
                    "key": "fix_core_ux_issues",
                    "title": "Fix Core UX and Speed Issues",
                    "desc": "Identify slow pages, layout shifts and tiny tap targets that hurt conversion.",
                    "automation": [
                        "run_lighthouse_mobile_audits",
                        "create_ticket_backlog_for_ux_fixes",
                    ],
                },
                {
                    "key": "ab_test_mobile_changes",
                    "title": "AB Test Mobile Enhancements",
                    "desc": "Roll out improvements behind experiments to confirm revenue impact.",
                    "automation": [
                        "configure_mobile_ab_tests",
                        "compare_variant_performance_over_time",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["ecommerce", "b2c", "b2b_saas"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_analytics", "needs_website_cms"],
            "notes": "Use when mobile traffic is high but conversion lags desktop.",
        },
    },

    # 15) Nurture brand advocates
    {
        "id": "rev-15-brand-advocate-program",
        "name": "Brand Advocate & Referral Program",
        "description": "Turn your happiest customers into active advocates and referrers.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["advocacy", "referrals", "community"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 6000,
            "reinvest_ratio": 0.35,
        },
        "kpis": {
            "referral_lead_share_target": 0.2,
            "advocate_nps_floor": 50,
            "review_volume_growth_target": 0.3,
        },
        "execution_plan": {
            "owner_roles": ["Customer_Marketing_Agent", "Community_Agent"],
            "channels": ["email", "community", "review_sites"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "identify_potential_advocates",
                    "title": "Identify Potential Advocates",
                    "desc": "Use NPS and product usage to find highly satisfied, engaged customers.",
                    "automation": [
                        "pull_nps_scores",
                        "filter_high_health_accounts",
                    ],
                },
                {
                    "key": "launch_advocate_program",
                    "title": "Launch Advocate Program",
                    "desc": "Invite high-fit customers into a structured program with perks for referrals and reviews.",
                    "automation": [
                        "send_advocate_invitation_campaign",
                        "track_program_enrollment",
                    ],
                },
                {
                    "key": "track_referrals_and_reviews",
                    "title": "Track Referrals and Reviews",
                    "desc": "Attribute new pipeline and online reviews to advocate activity.",
                    "automation": [
                        "sync_referral_codes_to_crm",
                        "monitor_review_sites_and_link_to_accounts",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["b2b_saas", "b2c_apps"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_nps_program", "needs_crm"],
            "notes": "Advocates multiply trust in the market; combine with brand awareness play.",
        },
    },

    # 16) Develop new partnerships
    {
        "id": "rev-16-partnership-development",
        "name": "Strategic Partnership Development",
        "description": "Create and grow partnerships that extend reach, add capabilities, or create co-sell opportunities.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["partnerships", "alliances", "cosell"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 10000,
            "reinvest_ratio": 0.3,
        },
        "kpis": {
            "partner_sourced_pipeline_target": 0.25,
            "active_partners_target": 10,
            "partner_sourced_revenue_target": 0.2,
        },
        "execution_plan": {
            "owner_roles": ["Partnerships_Agent", "Sales_Leader_Agent"],
            "channels": ["partner_portal", "co_marketing", "events"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "define_partner_profile",
                    "title": "Define Ideal Partner Profile",
                    "desc": "Specify attributes of ideal technology, reseller or integration partners.",
                    "automation": [
                        "analyze_current_customer_stack",
                        "generate_partner_candidate_list",
                    ],
                },
                {
                    "key": "build_partner_program",
                    "title": "Build Partner Program Structure",
                    "desc": "Define tiers, benefits, requirements and enablement assets for partners.",
                    "automation": [
                        "create_partner_playbooks",
                        "generate_partner_onboarding_materials",
                    ],
                },
                {
                    "key": "launch_cosell_motions",
                    "title": "Launch Co-Sell Motions",
                    "desc": "Coordinate joint campaigns and co-selling with top partners.",
                    "automation": [
                        "track_partner_sourced_opportunities",
                        "share_pipeline_reports_with_partners",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["scaling_smb", "midmarket"],
            "ideal_industries": ["b2b_saas", "infrastructure", "services"],
            "dependencies": ["needs_crm", "needs_partner_management"],
            "notes": "Use when organic and paid channels are tapped and ecosystem leverage is needed.",
        },
    },

    # 17) Engage industry influencers
    {
        "id": "rev-17-industry-influencer-engagement",
        "name": "Industry Influencer Engagement",
        "description": "Collaborate with relevant influencers or creators whose audience matches target buyers.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["influencer", "social", "brand", "collaboration"],
        "budget": {
            "mode": "experimental",
            "max_monthly_spend_usd": 8000,
            "reinvest_ratio": 0.2,
        },
        "kpis": {
            "influencer_campaign_roi_target": 1.5,
            "qualified_leads_from_influencers_target": 50,
            "engagement_rate_on_influencer_content_target": 0.05,
        },
        "execution_plan": {
            "owner_roles": ["Brand_Marketing_Agent", "Social_Agent"],
            "channels": ["social", "video", "podcasts"],
            "cadence": {
                "analysis": "per_campaign",
                "optimization": "per_campaign",
                "reporting": "per_campaign",
            },
            "steps": [
                {
                    "key": "select_fit_influencers",
                    "title": "Select Fit Influencers",
                    "desc": "Identify influencers whose audience matches your ICP and whose content tone fits the brand.",
                    "automation": [
                        "scrape_influencer_audience_demographics",
                        "score_influencers_by_audience_fit",
                    ],
                },
                {
                    "key": "craft_campaign_briefs",
                    "title": "Craft Campaign Briefs",
                    "desc": "Create clear briefs for sponsored content, live sessions or endorsements.",
                    "automation": [
                        "generate_campaign_brief_templates",
                        "track_approvals_and_contracts",
                    ],
                },
                {
                    "key": "measure_influencer_performance",
                    "title": "Measure Influencer Performance",
                    "desc": "Track clicks, leads and revenue associated with each influencer campaign.",
                    "automation": [
                        "assign_unique_tracking_links",
                        "attribute_pipeline_to_influencer_sources",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["consumer_brands", "b2b_niche"],
            "ideal_industries": ["ecommerce", "b2c_apps", "niche_b2b"],
            "dependencies": ["needs_analytics", "needs_tracking_links"],
            "notes": "Avoid influencers whose audience is large but misaligned; quality over reach.",
        },
    },

    # 18) Diversify geographical reach
    {
        "id": "rev-18-geographical-expansion",
        "name": "Geographical Market Expansion",
        "description": "Expand into new regions or countries with localized offerings and compliance.",
        "status": "DRAFT",
        "risk_tier": "high",
        "tags": ["geography", "expansion", "localization"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 25000,
            "reinvest_ratio": 0.35,
        },
        "kpis": {
            "new_region_revenue_share_target": 0.2,
            "payback_period_months_max": 24,
            "localized_conversion_rate_floor": 0.8,
        },
        "execution_plan": {
            "owner_roles": ["Expansion_Agent", "Legal_Agent", "Localization_Agent"],
            "channels": ["website", "local_partners", "ads"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "select_target_region",
                    "title": "Select Target Region",
                    "desc": "Evaluate candidate regions based on demand signals, competition and complexity.",
                    "automation": [
                        "analyze_signups_by_country",
                        "score_regions_by_potential_and_risk",
                    ],
                },
                {
                    "key": "localize_product_and_pricing",
                    "title": "Localize Product and Pricing",
                    "desc": "Translate key assets, adapt pricing and ensure basic legal compliance.",
                    "automation": [
                        "generate_translation_tasks",
                        "map_pricing_to_local_currency",
                    ],
                },
                {
                    "key": "launch_region_campaign",
                    "title": "Launch Region-Specific Campaign",
                    "desc": "Run campaigns and establish local partners where needed.",
                    "automation": [
                        "launch_region_targeted_ads",
                        "track_region_specific_pipeline",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["midmarket", "enterprise"],
            "ideal_industries": ["b2b_saas", "ecommerce"],
            "dependencies": ["needs_legal_review", "needs_localization"],
            "notes": "High complexity; use once home market is strong.",
        },
    },

    # 19) Offer multiple payment options
    {
        "id": "rev-19-multiple-payment-options",
        "name": "Multiple Payment Options Optimization",
        "description": "Add and optimize payment options to reduce checkout friction and abandonment.",
        "status": "DRAFT",
        "risk_tier": "low",
        "tags": ["payments", "checkout", "conversion"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 4000,
            "reinvest_ratio": 0.2,
        },
        "kpis": {
            "checkout_abandonment_reduction_target": 0.1,
            "payment_success_rate_floor": 0.95,
            "share_of_alt_payments_target": 0.3,
        },
        "execution_plan": {
            "owner_roles": ["Payments_Agent", "Growth_Agent"],
            "channels": ["checkout", "billing"],
            "cadence": {
                "analysis": "monthly",
                "optimization": "monthly",
                "reporting": "monthly",
            },
            "steps": [
                {
                    "key": "audit_current_payments",
                    "title": "Audit Current Payment Flow",
                    "desc": "Measure failures, drop-offs and support tickets related to payment.",
                    "automation": [
                        "pull_payment_gateway_logs",
                        "correlate_payment_issues_with_tickets",
                    ],
                },
                {
                    "key": "add_high_demand_methods",
                    "title": "Add High-Demand Payment Methods",
                    "desc": "Integrate additional payment methods favored by target customers.",
                    "automation": [
                        "rank_missing_payment_methods_by_demand",
                        "create_integration_tasks_for_top_methods",
                    ],
                },
                {
                    "key": "monitor_payment_mix",
                    "title": "Monitor Payment Mix and Health",
                    "desc": "Track adoption and reliability of each payment option.",
                    "automation": [
                        "build_payment_method_kpi_dashboard",
                        "alert_on_payment_failure_spikes",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["ecommerce", "subscription_business"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_payment_gateway"],
            "notes": "Low risk, often quick conversion win.",
        },
    },

    # 20) Avoid bad customer relationships
    {
        "id": "rev-20-prune-bad-customers",
        "name": "Prune Unprofitable Customer Relationships",
        "description": "Identify and phase out customers who consistently destroy margin, morale or capacity.",
        "status": "DRAFT",
        "risk_tier": "medium",
        "tags": ["profitability", "customer_selection", "operations"],
        "budget": {
            "mode": "fixed",
            "max_monthly_spend_usd": 2000,
            "reinvest_ratio": 0.1,
        },
        "kpis": {
            "support_hours_reduced_target": 0.2,
            "avg_margin_improvement_target": 0.1,
            "high_maintenance_account_share_max": 0.05,
        },
        "execution_plan": {
            "owner_roles": ["RevOps_Agent", "Leadership_Agent", "Customer_Success_Agent"],
            "channels": ["crm", "billing"],
            "cadence": {
                "analysis": "quarterly",
                "optimization": "quarterly",
                "reporting": "quarterly",
            },
            "steps": [
                {
                    "key": "define_bad_customer_criteria",
                    "title": "Define Bad Customer Criteria",
                    "desc": "Agree on objective thresholds for unprofitability or abuse (over-support, non-payment, constant escalations).",
                    "automation": [
                        "calculate_account_level_profitability",
                        "flag_accounts_exceeding_support_and_escalation_thresholds",
                    ],
                },
                {
                    "key": "segment_and_review_accounts",
                    "title": "Segment and Review High-Risk Accounts",
                    "desc": "Create a review list of customers meeting the criteria for potential pruning or repricing.",
                    "automation": [
                        "generate_high_maintenance_account_report",
                        "route_accounts_to_leadership_for_review",
                    ],
                },
                {
                    "key": "execute_pruning_or_repricing",
                    "title": "Execute Pruning or Repricing Plan",
                    "desc": "Offer new terms, higher pricing, or terminate relationships where necessary.",
                    "automation": [
                        "prepare_communication_templates",
                        "update_contract_status_in_crm_and_billing",
                    ],
                },
            ],
        },
        "metadata": {
            "ideal_company_stage": ["services", "b2b_saas"],
            "ideal_industries": ["any"],
            "dependencies": ["needs_profitability_data", "needs_crm", "needs_billing_system"],
            "notes": "Use carefully; the goal is freeing capacity and protecting profitability, not punishing customers.",
        },
    },
]
