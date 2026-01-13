"""Seed initial revenue-generating products on system startup."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

# Initial products that can start generating revenue immediately
INITIAL_PRODUCTS: List[Dict[str, any]] = [
    {
        "name": "AI Automation Audit",
        "description": "Comprehensive audit of your business automation opportunities. Includes detailed analysis, recommendations, and implementation roadmap.",
        "price": 197.0,
        "category": "consulting",
        "type": "one-time",
    },
    {
        "name": "Growth Playbook",
        "description": "Step-by-step marketing and revenue blueprint tailored to your business. Includes traffic strategies, conversion optimization, and scaling tactics.",
        "price": 97.0,
        "category": "digital_product",
        "type": "one-time",
    },
    {
        "name": "DFY Affiliate Engine Setup",
        "description": "Done-for-you affiliate program installation. We set up your complete affiliate infrastructure, tracking, and onboarding system.",
        "price": 497.0,
        "category": "service",
        "type": "one-time",
    },
    {
        "name": "Monthly AI Operations Retainer",
        "description": "Ongoing AI agent operations and optimization. Includes monthly strategy sessions, performance reviews, and continuous optimization.",
        "price": 997.0,
        "category": "service",
        "type": "recurring",
        "interval": "month",
    },
    {
        "name": "Revenue Loop Implementation",
        "description": "Full implementation of autonomous revenue generation system. Includes product creation, marketing automation, and payment processing setup.",
        "price": 1997.0,
        "category": "service",
        "type": "one-time",
    },
    {
        "name": "Lead Generation System",
        "description": "Complete lead generation funnel setup with email sequences, landing pages, and traffic strategies. Ready to start generating leads immediately.",
        "price": 697.0,
        "category": "service",
        "type": "one-time",
    },
]


def seed_initial_products(db_path: Path) -> int:
    """Seed initial products into the database if none exist."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if products table exists, create if not
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT,
                    type TEXT DEFAULT 'one-time',
                    interval TEXT,
                    active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Check if we already have products
            cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.info(f"Products already exist ({existing_count}). Skipping seed.")
                return existing_count
            
            # Insert initial products
            now = datetime.utcnow().isoformat()
            created = 0
            
            for product in INITIAL_PRODUCTS:
                try:
                    cursor.execute("""
                        INSERT INTO products 
                        (name, description, price, category, type, interval, active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """, (
                        product["name"],
                        product["description"],
                        product["price"],
                        product.get("category", "digital_product"),
                        product.get("type", "one-time"),
                        product.get("interval"),
                        now,
                        now,
                    ))
                    created += 1
                    logger.info(f"✅ Seeded product: {product['name']} (${product['price']})")
                except sqlite3.IntegrityError:
                    # Product already exists, skip
                    logger.debug(f"Product {product['name']} already exists, skipping")
                    continue
            
            conn.commit()
            logger.info(f"🎯 Seeded {created} initial revenue-generating products")
            return created
            
    except Exception as e:
        logger.error(f"Error seeding initial products: {e}")
        return 0


def sync_products_to_stripe(db_path: Path, stripe_processor) -> int:
    """Sync seeded products to Stripe so they're ready to sell."""
    if not stripe_processor or not stripe_processor.stripe_config.get("configured"):
        logger.warning("Stripe not configured, skipping product sync")
        return 0
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all active products that aren't synced to Stripe yet
            cursor.execute("""
                SELECT p.* 
                FROM products p
                LEFT JOIN stripe_product_mappings spm ON p.id = spm.product_id
                WHERE p.active = 1 AND spm.product_id IS NULL
            """)
            unsynced = cursor.fetchall()
            
            synced = 0
            for product_row in unsynced:
                try:
                    product_id = product_row["id"]
                    name = product_row["name"]
                    description = product_row["description"] or name
                    price = float(product_row["price"])
                    product_type = product_row["type"] if "type" in product_row.keys() else "one-time"
                    interval = product_row["interval"] if "interval" in product_row.keys() and product_row["interval"] else "month"
                    
                    # Create in Stripe
                    result = stripe_processor.create_product_with_price(
                        name=name,
                        description=description,
                        unit_amount=price,
                        currency="usd",
                        interval=interval if product_type == "recurring" else None,
                    )
                    
                    # Map to local product
                    stripe_processor._upsert_mapping({
                        "product_id": product_id,
                        "stripe_product_id": result["product_id"],
                        "stripe_price_id": result["price_id"],
                        "currency": "usd",
                        "unit_amount": int(price * 100),
                        "active": 1,
                        "synced_at": datetime.utcnow().isoformat(),
                    })
                    
                    synced += 1
                    logger.info(f"✅ Synced product to Stripe: {name}")
                except Exception as e:
                    logger.error(f"Error syncing product {product_row['name']} to Stripe: {e}")
                    continue
            
            if synced > 0:
                logger.info(f"🎯 Synced {synced} products to Stripe - ready to accept payments!")
            
            return synced
            
    except Exception as e:
        logger.error(f"Error syncing products to Stripe: {e}")
        return 0

