"""
Production Readiness Script
Ensures all revenue-generating operations are properly configured and ready.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone
from backend.corporate_memory import BUSINESS_DB_PATH
from backend.seed_initial_products import seed_initial_products, sync_products_to_stripe
from backend.stripe_integration import StripePaymentProcessor

logger = logging.getLogger(__name__)

def ensure_products_table_schema(db_path: Path) -> None:
    """Ensure products table has the correct unified schema."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create unified products table schema
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
                development_status TEXT DEFAULT 'LIVE',
                launch_date TEXT,
                revenue_generated REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Add missing columns if they don't exist
        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "development_status" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN development_status TEXT DEFAULT 'LIVE'")
        if "launch_date" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN launch_date TEXT")
        if "revenue_generated" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN revenue_generated REAL DEFAULT 0")
        if "category" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
        if "type" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN type TEXT DEFAULT 'one-time'")
        if "interval" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN interval TEXT")
        if "active" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN active INTEGER DEFAULT 1")
        if "created_at" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))")
        if "updated_at" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))")
        
        conn.commit()
        logger.info("✅ Products table schema verified and updated")

def ensure_stripe_mappings_table(db_path: Path) -> None:
    """Ensure Stripe product mappings table exists."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stripe_product_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                stripe_product_id TEXT NOT NULL,
                stripe_price_id TEXT NOT NULL,
                currency TEXT DEFAULT 'usd',
                unit_amount INTEGER NOT NULL,
                active INTEGER DEFAULT 1,
                synced_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        conn.commit()
        logger.info("✅ Stripe mappings table verified")

def ensure_initial_products(db_path: Path, stripe_processor) -> int:
    """Ensure initial revenue products exist and are synced to Stripe."""
    # First ensure schema
    ensure_products_table_schema(db_path)
    ensure_stripe_mappings_table(db_path)
    
    # Seed products
    products_created = seed_initial_products(db_path)
    
    # Sync to Stripe
    if stripe_processor and stripe_processor.stripe_config.get("configured"):
        synced = sync_products_to_stripe(db_path, stripe_processor)
        logger.info(f"✅ Synced {synced} products to Stripe")
    else:
        logger.warning("⚠️ Stripe not configured - products created but not synced")
    
    return products_created

def verify_revenue_operations() -> dict:
    """Verify all revenue operations are properly configured."""
    results = {
        "products_table": False,
        "stripe_mappings": False,
        "initial_products": 0,
        "stripe_synced": False,
        "stripe_configured": False,
    }
    
    try:
        # Check products table
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            results["products_table"] = cursor.fetchone() is not None
            
            if results["products_table"]:
                cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
                results["initial_products"] = cursor.fetchone()[0]
            
            # Check Stripe mappings
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stripe_product_mappings'")
            results["stripe_mappings"] = cursor.fetchone() is not None
            
            if results["stripe_mappings"]:
                cursor.execute("SELECT COUNT(*) FROM stripe_product_mappings WHERE active = 1")
                results["stripe_synced"] = cursor.fetchone()[0] > 0
    
    except Exception as e:
        logger.error(f"Error verifying revenue operations: {e}")
    
    # Check Stripe configuration
    try:
        stripe_processor = StripePaymentProcessor()
        results["stripe_configured"] = stripe_processor.stripe_config.get("configured", False)
    except Exception as e:
        logger.error(f"Error checking Stripe: {e}")
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Verifying production readiness...")
    
    # Ensure database schema
    ensure_products_table_schema(BUSINESS_DB_PATH)
    ensure_stripe_mappings_table(BUSINESS_DB_PATH)
    
    # Check Stripe
    stripe_processor = None
    try:
        stripe_processor = StripePaymentProcessor()
    except Exception as e:
        logger.warning(f"Stripe processor not available: {e}")
    
    # Ensure initial products
    products_created = ensure_initial_products(BUSINESS_DB_PATH, stripe_processor)
    
    # Verify everything
    results = verify_revenue_operations()
    
    print("\n📊 Production Readiness Report:")
    print(f"  Products Table: {'✅' if results['products_table'] else '❌'}")
    print(f"  Stripe Mappings: {'✅' if results['stripe_mappings'] else '❌'}")
    print(f"  Active Products: {results['initial_products']}")
    print(f"  Stripe Configured: {'✅' if results['stripe_configured'] else '❌'}")
    print(f"  Products Synced: {'✅' if results['stripe_synced'] else '❌'}")
    
    if all([results['products_table'], results['stripe_mappings'], results['initial_products'] > 0]):
        print("\n✅ System is production-ready for revenue generation!")
    else:
        print("\n⚠️ Some components need attention - check logs above")

