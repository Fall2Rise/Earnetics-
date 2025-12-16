"""
Revenue Loop Orchestrator
-------------------------
Orchestrates the startup revenue workflow:
R&D -> Strategy -> Product -> Content -> Email -> Launch
"""
import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

from backend.stripe_integration import StripePaymentProcessor
from backend.services.content_engine_service import ContentEngineService
from backend.services.email_service import EmailService
# from backend.services.rnd_affiliate_research import ... # (Using simulated R&D for now)

logger = logging.getLogger("RevenueOrchestrator")

async def run_earnings_workflow_once() -> Dict[str, Any]:
    """
    Executes a single pass of the departmental revenue loop.
    """
    logger.info("🚀 Starting Earnetics Revenue Workflow...")
    
    results = {}

    # 1. R&D Department
    # -----------------
    logger.info("[R&D] Researching opportunities...")
    
    # Load Verified Niches (Safe R&D Protocol)
    import yaml
    import random
    import sqlite3
    import json
    from pathlib import Path
    from backend.corporate_memory import BUSINESS_DB_PATH
    
    # 1. Load Static Niches
    static_niches = []
    verified_niches_path = Path("backend/data/verified_niches.yaml")
    if verified_niches_path.exists():
        with open(verified_niches_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            static_niches = data.get("niches", [])

    # 2. Load Dynamic Library Niches
    library_niches = []
    try:
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # Ensure table exists first to avoid crash on fresh db
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='library_items'")
            if cur.fetchone():
                cur.execute("SELECT * FROM library_items WHERE category='Research'")
                rows = cur.fetchall()
                for row in rows:
                    try:
                        playbook = json.loads(row["detailed_playbook"])
                        # Adapt library format to opportunity format
                        library_niches.append({
                            "niche": playbook.get("niche") or row["title"],
                            "target_audience": playbook.get("target_audience", "General Market"),
                            "pain_point": playbook.get("pain_point", "Inefficiency"),
                            "offer_idea": playbook.get("offer_idea") or row["title"],
                            "suggested_price_cents": playbook.get("suggested_price_cents", 9700),
                            "suggested_interval": playbook.get("suggested_interval", "month"),
                            "positioning_seed": playbook.get("positioning", "")
                        })
                    except Exception:
                        pass
    except Exception as e:
        logger.warning(f"Failed to load library niches: {e}")

    # 3. Combine and Select
    all_niches = static_niches + library_niches
    
    if all_niches:
        selected = random.choice(all_niches)
        opportunity = {
            "niche": selected["niche"],
            "target_audience": selected["target_audience"],
            "pain_point": selected["pain_point"],
            "offer_idea": selected["offer_idea"],
            "suggested_price_cents": selected.get("suggested_price_cents", 9700),
            "suggested_interval": selected.get("suggested_interval", "month"),
            "positioning_seed": selected.get("positioning_seed") or selected.get("positioning", "")
        }
        source = "Library" if selected in library_niches else "Verified Database"
        logger.info(f"[R&D] Dynamic Selection ({source}): {opportunity['niche']}")
    else:
            # Fallback if file is empty
        opportunity = {
            "niche": "AI Automation for Real Estate",
            "target_audience": "Real Estate Agents",
            "pain_point": "Spending too much time on lead follow-up",
            "offer_idea": "DFY AI SMS Bot for Realtors",
            "suggested_price_cents": 9700,
            "suggested_interval": "month"
        }
        logger.warning("[R&D] No niches found. Using fallback.")

    results["rnd"] = opportunity
    logger.info(f"[R&D] Selected niche: {opportunity['niche']}")

    # 2. Strategy Department
    # ----------------------
    logger.info("[STRATEGY] Refining offer strategy...")
    # Transform research into a concrete offer structure
    
    # Use suggested pricing from R&D if available, otherwise default
    price_cents = opportunity.get("suggested_price_cents", 9700)
    interval = opportunity.get("suggested_interval", "month")
    positioning = opportunity.get("positioning_seed") or "Never lose a lead again. 24/7 instant response."

    strategy = {
        "offer_name": opportunity["offer_idea"],
        "positioning": positioning,
        "pricing_model": "recurring",
        "price_cents": price_cents,
        "currency": "usd",
        "interval": interval
    }
    results["strategy"] = strategy
    logger.info(f"[STRATEGY] Defined offer: {strategy['offer_name']} @ ${strategy['price_cents']/100}/mo")

    # 3. Product Department (Stripe)
    # ------------------------------
    logger.info("[PRODUCT] Syncing with Stripe...")
    stripe_processor = StripePaymentProcessor()
    stripe_processor.configure_from_environment()
    
    try:
        product_result = stripe_processor.get_or_create_product_and_price(
            name=strategy["offer_name"],
            description=strategy["positioning"],
            unit_amount=strategy["price_cents"] / 100.0,
            currency=strategy["currency"],
            interval=strategy["interval"]
        )
        results["product"] = product_result
        logger.info(f"[PRODUCT] Stripe Product Ready: {product_result['product_id']} (Price: {product_result['price_id']})")
    except Exception as e:
        logger.error(f"[PRODUCT] Stripe sync failed: {e}")
        results["product"] = {"error": str(e)}

    # 4. Content Department
    # ---------------------
    logger.info("[CONTENT] Generating marketing assets...")
    content_engine = ContentEngineService()
    
    # Generate landing page copy (Master Content)
    master_content = await content_engine.generate_master_content(
        topic=f"{strategy['offer_name']} - {strategy['positioning']}",
        tone="persuasive"
    )
    results["content"] = master_content
    logger.info(f"[CONTENT] Master content generated: {master_content['id']}")

    # 5. Email Department
    # -------------------
    logger.info("[EMAIL] Drafting email sequence...")
    # Simulate email generation (since EmailService is for sending)
    email_sequence = [
        {
            "subject": f"Stop losing leads, {{name}}",
            "body": f"Hi {{name}},\n\nAre you tired of missing calls? Our {strategy['offer_name']} handles it for you..."
        },
        {
            "subject": "Your 24/7 Inside Sales Agent",
            "body": "Imagine having an ISA who never sleeps. That's what our AI bot does..."
        },
        {
            "subject": "Last chance to automate your follow-up",
            "body": "Join hundreds of realtors saving 10+ hours a week..."
        }
    ]
    results["email"] = email_sequence
    logger.info(f"[EMAIL] Generated {len(email_sequence)} email drafts.")

    # 6. Launch/Analytics Department
    # ------------------------------
    logger.info("[LAUNCH] Finalizing campaign setup...")
    campaign_record = {
        "id": f"camp_{int(datetime.now().timestamp())}",
        "name": f"Launch: {strategy['offer_name']}",
        "status": "READY_FOR_TRAFFIC",
        "product_id": results.get("product", {}).get("product_id"),
        "created_at": datetime.now().isoformat()
    }
    results["campaign"] = campaign_record
    logger.info(f"[LAUNCH] Campaign '{campaign_record['name']}' is {campaign_record['status']}")

    logger.info("✅ Revenue Workflow Complete.")
    return results
