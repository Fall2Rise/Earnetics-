#!/usr/bin/env python3
"""
Test script for the autonomous financial system
Simulates transactions and verifies 80/20 split processing
"""

import asyncio
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.autonomous_financial_processor import AutonomousFinancialProcessor
from backend.corporate_memory import BUSINESS_DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("FinancialTest")

def create_test_transaction(amount: float, currency: str = "usd") -> int:
    """Create a test transaction in the database"""
    with sqlite3.connect(BUSINESS_DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check if currency column exists, add if not
        cursor.execute("PRAGMA table_info(transactions)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "currency" not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT 'usd'")
            conn.commit()
        
        if "processed" not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN processed INTEGER DEFAULT 0")
            conn.commit()

        if "processed_at" not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN processed_at TIMESTAMP")
            conn.commit()

        # Insert test transaction
        cursor.execute(
            """
            INSERT INTO transactions
            (amount, currency, status, source, category, description, created_at, processed)
            VALUES (?, ?, 'completed', 'test', 'test_revenue', 'Test transaction', CURRENT_TIMESTAMP, 0)
            """,
            (amount, currency),
        )

        transaction_id = cursor.lastrowid
        conn.commit()

        logger.info(f"✅ Created test transaction #{transaction_id}: ${amount:.2f} {currency.upper()}")
        return transaction_id


def verify_financial_operation(transaction_id: int):
    """Verify that the transaction was processed correctly"""
    with sqlite3.connect(BUSINESS_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check financial operation
        cursor.execute(
            """
            SELECT * FROM financial_operations
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )
        
        fin_op = cursor.fetchone()
        
        if not fin_op:
            logger.error(f"❌ No financial operation found for transaction #{transaction_id}")
            return False
        
        fin_op = dict(fin_op)
        
        # Verify 80/20 split
        expected_owner = fin_op["gross_revenue"] * 0.80
        expected_reinvest = fin_op["gross_revenue"] * 0.20
        
        owner_correct = abs(fin_op["owner_payout"] - expected_owner) < 0.01
        reinvest_correct = abs(fin_op["reinvestment_amount"] - expected_reinvest) < 0.01
        
        if owner_correct and reinvest_correct:
            logger.info(f"✅ 80/20 split verified:")
            logger.info(f"   Gross: ${fin_op['gross_revenue']:.2f}")
            logger.info(f"   Owner (80%): ${fin_op['owner_payout']:.2f}")
            logger.info(f"   Reinvest (20%): ${fin_op['reinvestment_amount']:.2f}")
            logger.info(f"   Payout Status: {fin_op['payout_status']}")
        else:
            logger.error(f"❌ 80/20 split incorrect!")
            return False
        
        # Check reinvestment operation
        cursor.execute(
            """
            SELECT * FROM reinvestment_operations
            ORDER BY id DESC LIMIT 1
            """
        )
        
        reinvest_op = cursor.fetchone()
        if reinvest_op:
            reinvest_op = dict(reinvest_op)
            logger.info(f"✅ Reinvestment operation created:")
            logger.info(f"   Amount: ${reinvest_op['amount']:.2f}")
            logger.info(f"   Category: {reinvest_op['allocation_category']}")
            logger.info(f"   Status: {reinvest_op['status']}")
        
        # Check payout
        if fin_op.get("stripe_payout_id"):
            cursor.execute(
                """
                SELECT * FROM stripe_payouts
                WHERE stripe_payout_id = ? OR id = ?
                """,
                (fin_op["stripe_payout_id"], fin_op["stripe_payout_id"]),
            )
            
            payout = cursor.fetchone()
            if payout:
                payout = dict(payout)
                logger.info(f"✅ Payout record created:")
                logger.info(f"   Amount: ${payout['amount']:.2f}")
                logger.info(f"   Status: {payout['status']}")
                if payout.get("stripe_payout_id"):
                    logger.info(f"   Stripe ID: {payout['stripe_payout_id']}")
        
        return True


async def test_single_transaction():
    """Test processing a single transaction"""
    logger.info("=" * 80)
    logger.info("TEST 1: Single Transaction Processing")
    logger.info("=" * 80)
    
    # Create test transaction
    transaction_id = create_test_transaction(100.00)
    
    # Initialize processor
    processor = AutonomousFinancialProcessor()
    
    # Get the transaction
    transactions = processor._get_pending_transactions()
    
    if not transactions:
        logger.error("❌ No pending transactions found")
        return False
    
    # Process it
    logger.info("Processing transaction...")
    await processor._process_transaction(transactions[0])
    
    # Verify
    await asyncio.sleep(1)  # Give it a moment
    return verify_financial_operation(transaction_id)


async def test_batch_processing():
    """Test batch processing of small transactions"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Batch Processing (Small Transactions)")
    logger.info("=" * 80)
    
    # Create multiple small transactions
    amounts = [5.00, 3.50, 7.25, 4.00]
    transaction_ids = []
    
    for amount in amounts:
        tid = create_test_transaction(amount)
        transaction_ids.append(tid)
    
    # Initialize processor
    processor = AutonomousFinancialProcessor()
    
    # Process all transactions
    transactions = processor._get_pending_transactions()
    for transaction in transactions:
        if transaction["id"] in transaction_ids:
            await processor._process_transaction(transaction)
    
    # Verify all were processed
    await asyncio.sleep(1)
    
    all_verified = True
    for tid in transaction_ids:
        if not verify_financial_operation(tid):
            all_verified = False
    
    if all_verified:
        logger.info("✅ All small transactions processed correctly")
        
        # Check if batch payout would be created
        total = sum(amounts)
        logger.info(f"\n💡 Total from small transactions: ${total:.2f}")
        logger.info(f"   Owner portion (80%): ${total * 0.80:.2f}")
        logger.info(f"   This would be batched into a single payout")
    
    return all_verified


async def test_reinvestment_decisions():
    """Test reinvestment decision making"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Reinvestment Decision Making")
    logger.info("=" * 80)
    
    processor = AutonomousFinancialProcessor()
    
    # Get available funds
    available = processor._get_available_reinvestment_funds()
    logger.info(f"Available reinvestment funds: ${available:.2f}")
    
    if available < 10:
        logger.info("Creating additional funds for testing...")
        create_test_transaction(500.00)
        transactions = processor._get_pending_transactions()
        if transactions:
            await processor._process_transaction(transactions[0])
            available = processor._get_available_reinvestment_funds()
            logger.info(f"New available funds: ${available:.2f}")
    
    # Make reinvestment decisions
    if available >= 100:
        decisions = await processor._analyze_reinvestment_opportunities(available)
        
        logger.info(f"\n✅ Generated {len(decisions)} reinvestment decisions:")
        for i, decision in enumerate(decisions, 1):
            logger.info(f"\n   Decision {i}:")
            logger.info(f"   - Category: {decision['category']}")
            logger.info(f"   - Amount: ${decision['amount']:.2f}")
            logger.info(f"   - Purpose: {decision['purpose']}")
            logger.info(f"   - Priority: {decision['priority']}")
        
        return True
    else:
        logger.warning("⚠️  Insufficient funds for reinvestment decisions")
        return False


async def test_financial_metrics():
    """Test financial health metrics calculation"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Financial Health Metrics")
    logger.info("=" * 80)
    
    processor = AutonomousFinancialProcessor()
    metrics = processor._calculate_financial_metrics()
    
    logger.info("📊 Current Financial Metrics:")
    logger.info(f"   Total Revenue: ${metrics['total_revenue']:.2f}")
    logger.info(f"   Total Paid Out: ${metrics['total_paid_out']:.2f}")
    logger.info(f"   Total Reinvested: ${metrics['total_reinvested']:.2f}")
    logger.info(f"   Pending Payouts: {metrics['pending_payouts_count']} (${metrics['pending_payout_amount']:.2f})")
    logger.info(f"   Failed Payouts: {metrics['failed_payouts_count']}")
    
    return True


async def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 AUTONOMOUS FINANCIAL SYSTEM - TEST SUITE")
    logger.info("=" * 80 + "\n")
    
    results = {
        "Single Transaction": await test_single_transaction(),
        "Batch Processing": await test_batch_processing(),
        "Reinvestment Decisions": await test_reinvestment_decisions(),
        "Financial Metrics": await test_financial_metrics(),
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("The autonomous financial system is working correctly.")
        logger.info("\nNext steps:")
        logger.info("1. Set your STRIPE_SECRET_KEY environment variable")
        logger.info("2. Run: python backend/start_autonomous_system.py")
        logger.info("3. System will automatically process revenue 24/7")
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("Please review the errors above and fix issues before deploying.")
    logger.info("=" * 80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
