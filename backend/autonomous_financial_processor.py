#!/usr/bin/env python3
"""
AUTONOMOUS FINANCIAL PROCESSOR
Handles 80/20 revenue split, automatic payouts, and reinvestment decisions
Runs continuously to ensure money flows automatically
"""

import asyncio
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("AutonomousFinancial")

try:
    from backend.stripe_integration import StripePaymentProcessor
    from backend.corporate_memory import BUSINESS_DB_PATH
except ModuleNotFoundError:
    from stripe_integration import StripePaymentProcessor
    from corporate_memory import BUSINESS_DB_PATH


class AutonomousFinancialProcessor:
    """
    Autonomous financial processor that:
    1. Monitors incoming revenue
    2. Automatically processes 80/20 splits
    3. Initiates payouts to owner
    4. Makes reinvestment decisions
    5. Tracks financial health
    """

    def __init__(self, db_path: Path | str = BUSINESS_DB_PATH):
        self.db_path = Path(db_path)
        self.stripe_processor = StripePaymentProcessor(db_path=db_path)
        self.running = False
        self.min_payout_threshold = 10.0  # Minimum $10 before initiating payout
        self.payout_batch_interval = 3600  # Batch payouts every hour
        self.last_payout_check = 0
        
        # Ensure database schema exists
        self._ensure_schema()
        
        # Configure Stripe
        config_result = self.stripe_processor.configure_from_environment()
        if config_result.get("success"):
            logger.info("✅ Stripe configured successfully for autonomous payouts")
            self.stripe_configured = True
        else:
            logger.warning(
                f"⚠️ Stripe not configured: {config_result.get('error')}. "
                "Payouts will be queued until configuration is complete."
            )
            self.stripe_configured = False
    
    def _ensure_schema(self) -> None:
        """Ensure financial_operations and reinvestment_operations tables exist with correct schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create financial_operations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS financial_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    gross_revenue REAL NOT NULL,
                    owner_payout REAL NOT NULL,
                    reinvestment_amount REAL NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'usd',
                    payout_status TEXT NOT NULL DEFAULT 'pending',
                    reinvestment_status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            
            # Check if currency column exists, add if missing (for existing databases)
            cursor.execute("PRAGMA table_info(financial_operations)")
            columns = {row[1] for row in cursor.fetchall()}
            if "currency" not in columns:
                cursor.execute("ALTER TABLE financial_operations ADD COLUMN currency TEXT NOT NULL DEFAULT 'usd'")
            
            # Create reinvestment_operations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reinvestment_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    allocation_category TEXT,
                    purpose TEXT,
                    remaining_amount REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'available',
                    priority TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            
            # Check if priority column exists, add if missing (for existing databases)
            cursor.execute("PRAGMA table_info(reinvestment_operations)")
            columns = {row[1] for row in cursor.fetchall()}
            if "priority" not in columns:
                cursor.execute("ALTER TABLE reinvestment_operations ADD COLUMN priority TEXT")
            if "created_at" not in columns:
                cursor.execute("ALTER TABLE reinvestment_operations ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
            if "updated_at" not in columns:
                cursor.execute("ALTER TABLE reinvestment_operations ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
            
            # Create transactions table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'usd',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    processed INTEGER DEFAULT 0,
                    processed_at TEXT
                )
                """
            )
            
            # Check if processed columns exist in transactions table
            cursor.execute("PRAGMA table_info(transactions)")
            columns = {row[1] for row in cursor.fetchall()}
            if "processed" not in columns:
                cursor.execute("ALTER TABLE transactions ADD COLUMN processed INTEGER DEFAULT 0")
            if "processed_at" not in columns:
                cursor.execute("ALTER TABLE transactions ADD COLUMN processed_at TEXT")
            if "currency" not in columns:
                cursor.execute("ALTER TABLE transactions ADD COLUMN currency TEXT NOT NULL DEFAULT 'usd'")
            
            conn.commit()

    async def start_autonomous_processing(self):
        """Start the autonomous financial processing loop"""
        self.running = True
        logger.info("🚀 Starting Autonomous Financial Processor")
        
        tasks = [
            self.process_pending_revenue(),
            self.sync_payout_statuses(),
            self.make_reinvestment_decisions(),
            self.monitor_financial_health(),
        ]
        
        await asyncio.gather(*tasks)

    async def process_pending_revenue(self):
        """Continuously process pending revenue and initiate payouts"""
        while self.running:
            try:
                # Check for unprocessed transactions
                pending_transactions = self._get_pending_transactions()
                
                for transaction in pending_transactions:
                    await self._process_transaction(transaction)
                
                # Check if we should batch process payouts
                current_time = time.time()
                if current_time - self.last_payout_check >= self.payout_batch_interval:
                    await self._batch_process_payouts()
                    self.last_payout_check = current_time
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in revenue processing: {e}")
                await asyncio.sleep(60)

    async def _process_transaction(self, transaction: Dict):
        """Process a single transaction through the 80/20 split"""
        try:
            transaction_id = transaction["id"]
            amount = transaction["amount"]
            currency = transaction.get("currency", "usd")
            
            # Calculate 80/20 split
            owner_payout = amount * 0.80
            reinvestment = amount * 0.20
            
            # Record financial operation
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO financial_operations 
                    (transaction_id, gross_revenue, owner_payout, reinvestment_amount, 
                     currency, payout_status, reinvestment_status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'pending', 'pending', ?, ?)
                    """,
                    (transaction_id, amount, owner_payout, reinvestment, currency, now, now),
                )
                
                financial_op_id = cursor.lastrowid
                
                # Add to reinvestment fund
                now = datetime.now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO reinvestment_operations 
                    (amount, allocation_category, purpose, remaining_amount, status, created_at, updated_at)
                    VALUES (?, 'operations', 'Automatic 20% reinvestment', ?, 'available', ?, ?)
                    """,
                    (reinvestment, reinvestment, now, now),
                )
                
                # Mark transaction as processed
                cursor.execute(
                    """
                    UPDATE transactions 
                    SET processed = 1, processed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (transaction_id,),
                )
                
                conn.commit()
            
            logger.info(
                f"💰 Processed transaction #{transaction_id}: "
                f"${amount:.2f} → Owner: ${owner_payout:.2f}, Reinvest: ${reinvestment:.2f}"
            )
            
            # Queue payout if above threshold
            if owner_payout >= self.min_payout_threshold:
                await self._queue_payout(financial_op_id, owner_payout, currency)
            else:
                logger.info(
                    f"   Payout ${owner_payout:.2f} below threshold ${self.min_payout_threshold:.2f}, "
                    "will batch with others"
                )
                
        except Exception as e:
            logger.error(f"Error processing transaction {transaction.get('id')}: {e}")

    async def _queue_payout(self, financial_op_id: int, amount: float, currency: str = "usd"):
        """Queue a payout for processing"""
        try:
            if not self.stripe_configured:
                logger.info(f"💳 Payout queued (Stripe not configured): ${amount:.2f}")
                return
            
            # Create payout
            result = self.stripe_processor.create_payout_to_owner(
                amount=amount,
                currency=currency,
                description=f"Owner distribution (Op #{financial_op_id})",
                financial_op_id=financial_op_id,
            )
            
            if result.get("success"):
                # Update financial operation
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE financial_operations 
                        SET payout_status = ?, stripe_payout_id = ?
                        WHERE id = ?
                        """,
                        (result["status"], result["payout_id"], financial_op_id),
                    )
                    conn.commit()
                
                logger.info(
                    f"✅ Payout initiated: ${amount:.2f} (ID: {result['payout_id']})"
                )
            else:
                logger.error(f"❌ Payout failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error queueing payout: {e}")

    async def _batch_process_payouts(self):
        """Batch process small payouts that are below threshold"""
        try:
            # Ensure schema is up to date before querying
            self._ensure_schema()
            
            # Get all pending payouts below threshold
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if currency column exists
                cursor.execute("PRAGMA table_info(financial_operations)")
                columns = {row[1] for row in cursor.fetchall()}
                
                if "currency" in columns:
                    cursor.execute(
                        """
                        SELECT id, owner_payout, currency
                        FROM financial_operations
                        WHERE payout_status = 'pending' 
                        AND owner_payout < ?
                        """,
                        (self.min_payout_threshold,),
                    )
                else:
                    # Fallback: select without currency (default to usd)
                    cursor.execute(
                        """
                        SELECT id, owner_payout
                        FROM financial_operations
                        WHERE payout_status = 'pending' 
                        AND owner_payout < ?
                        """,
                        (self.min_payout_threshold,),
                    )
                pending = cursor.fetchall()
            
            if not pending:
                return
            
            # Group by currency
            by_currency = {}
            for row in pending:
                if len(row) == 3:
                    # Has currency column
                    op_id, amount, currency = row
                    currency = currency or "usd"
                else:
                    # No currency column, default to usd
                    op_id, amount = row
                    currency = "usd"
                
                if currency not in by_currency:
                    by_currency[currency] = []
                by_currency[currency].append((op_id, amount))
            
            # Process each currency batch
            for currency, operations in by_currency.items():
                total_amount = sum(amount for _, amount in operations)
                
                if total_amount >= self.min_payout_threshold:
                    logger.info(
                        f"💰 Batching {len(operations)} small payouts: "
                        f"${total_amount:.2f} {currency.upper()}"
                    )
                    
                    # Create combined payout
                    op_ids = [op_id for op_id, _ in operations]
                    result = self.stripe_processor.create_payout_to_owner(
                        amount=total_amount,
                        currency=currency,
                        description=f"Batched owner distribution ({len(operations)} ops)",
                    )
                    
                    if result.get("success"):
                        # Update all operations
                        with sqlite3.connect(self.db_path) as conn:
                            cursor = conn.cursor()
                            for op_id in op_ids:
                                cursor.execute(
                                    """
                                    UPDATE financial_operations 
                                    SET payout_status = ?, stripe_payout_id = ?
                                    WHERE id = ?
                                    """,
                                    (result["status"], result["payout_id"], op_id),
                                )
                            conn.commit()
                        
                        logger.info(
                            f"✅ Batch payout created: ${total_amount:.2f} "
                            f"(ID: {result['payout_id']})"
                        )
                        
        except Exception as e:
            logger.error(f"Error in batch payout processing: {e}")

    async def sync_payout_statuses(self):
        """Continuously sync payout statuses with Stripe"""
        while self.running:
            try:
                # Ensure schema is up to date before syncing
                self._ensure_schema()
                
                if not self.stripe_configured:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    continue
                
                result = self.stripe_processor.sync_payout_statuses()
                
                if result.get("updated_count", 0) > 0:
                    logger.info(
                        f"🔄 Synced {result['updated_count']} payout statuses"
                    )
                
                await asyncio.sleep(300)  # Sync every 5 minutes
                
            except Exception as e:
                logger.error(f"Error syncing payout statuses: {e}")
                await asyncio.sleep(300)

    async def make_reinvestment_decisions(self):
        """Autonomously decide how to allocate reinvestment funds"""
        while self.running:
            try:
                # Get available reinvestment funds
                available_funds = self._get_available_reinvestment_funds()
                
                if available_funds > 100:  # Only make decisions if we have $100+
                    decisions = await self._analyze_reinvestment_opportunities(
                        available_funds
                    )
                    
                    for decision in decisions:
                        await self._execute_reinvestment_decision(decision)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in reinvestment decisions: {e}")
                await asyncio.sleep(3600)

    async def _analyze_reinvestment_opportunities(
        self, available_funds: float
    ) -> List[Dict]:
        """Analyze and prioritize reinvestment opportunities"""
        decisions = []
        
        # Priority 1: Infrastructure costs (API credits, hosting)
        infrastructure_need = self._calculate_infrastructure_needs()
        if infrastructure_need > 0:
            allocation = min(available_funds * 0.4, infrastructure_need)
            decisions.append(
                {
                    "category": "infrastructure",
                    "amount": allocation,
                    "purpose": "API credits and hosting",
                    "priority": 1,
                }
            )
            available_funds -= allocation
        
        # Priority 2: Marketing and growth
        if available_funds > 50:
            marketing_allocation = available_funds * 0.3
            decisions.append(
                {
                    "category": "marketing",
                    "amount": marketing_allocation,
                    "purpose": "Automated marketing campaigns",
                    "priority": 2,
                }
            )
            available_funds -= marketing_allocation
        
        # Priority 3: Product development
        if available_funds > 30:
            decisions.append(
                {
                    "category": "product",
                    "amount": available_funds,
                    "purpose": "New product development",
                    "priority": 3,
                }
            )
        
        return decisions

    async def _execute_reinvestment_decision(self, decision: Dict):
        """Execute a reinvestment decision"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Allocate funds
                now = datetime.now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO reinvestment_operations 
                    (amount, allocation_category, purpose, remaining_amount, 
                     status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'allocated', ?, ?, ?)
                    """,
                    (
                        decision["amount"],
                        decision["category"],
                        decision["purpose"],
                        decision["amount"],
                        decision.get("priority"),
                        now,
                        now,
                    ),
                )
                
                conn.commit()
            
            logger.info(
                f"💡 Reinvestment decision: ${decision['amount']:.2f} → "
                f"{decision['category']} ({decision['purpose']})"
            )
            
        except Exception as e:
            logger.error(f"Error executing reinvestment decision: {e}")

    async def monitor_financial_health(self):
        """Monitor overall financial health and alert on issues"""
        while self.running:
            try:
                metrics = self._calculate_financial_metrics()
                
                # Check for issues
                if metrics["pending_payouts_count"] > 10:
                    logger.warning(
                        f"⚠️ High number of pending payouts: {metrics['pending_payouts_count']}"
                    )
                
                if metrics["failed_payouts_count"] > 0:
                    logger.error(
                        f"❌ Failed payouts detected: {metrics['failed_payouts_count']}"
                    )
                
                # Log health summary every hour
                logger.info(
                    f"📊 Financial Health: "
                    f"Total Revenue: ${metrics['total_revenue']:.2f}, "
                    f"Paid Out: ${metrics['total_paid_out']:.2f}, "
                    f"Reinvested: ${metrics['total_reinvested']:.2f}, "
                    f"Pending: ${metrics['pending_payout_amount']:.2f}"
                )
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error monitoring financial health: {e}")
                await asyncio.sleep(3600)

    def _get_pending_transactions(self) -> List[Dict]:
        """Get transactions that haven't been processed through 80/20 split"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if processed column exists
            cursor.execute("PRAGMA table_info(transactions)")
            columns = {row[1] for row in cursor.fetchall()}
            
            if "processed" not in columns:
                # Add processed column if it doesn't exist
                cursor.execute(
                    "ALTER TABLE transactions ADD COLUMN processed INTEGER DEFAULT 0"
                )
                cursor.execute(
                    "ALTER TABLE transactions ADD COLUMN processed_at TIMESTAMP"
                )
                conn.commit()
            
            cursor.execute(
                """
                SELECT id, amount, currency, created_at
                FROM transactions
                WHERE (processed IS NULL OR processed = 0)
                AND status = 'completed'
                ORDER BY created_at ASC
                LIMIT 100
                """
            )
            
            return [dict(row) for row in cursor.fetchall()]

    def _get_available_reinvestment_funds(self) -> float:
        """Get total available reinvestment funds"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT SUM(remaining_amount) 
                FROM reinvestment_operations
                WHERE status = 'available'
                """
            )
            result = cursor.fetchone()[0]
            return result or 0.0

    def _calculate_infrastructure_needs(self) -> float:
        """Calculate infrastructure funding needs"""
        # This would analyze API usage, hosting costs, etc.
        # For now, return a simple estimate
        return 50.0  # $50 baseline infrastructure need

    def _calculate_financial_metrics(self) -> Dict:
        """Calculate comprehensive financial metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total revenue
            cursor.execute("SELECT SUM(gross_revenue) FROM financial_operations")
            total_revenue = cursor.fetchone()[0] or 0.0
            
            # Total paid out
            cursor.execute(
                """
                SELECT SUM(owner_payout) FROM financial_operations
                WHERE payout_status IN ('paid', 'in_transit')
                """
            )
            total_paid_out = cursor.fetchone()[0] or 0.0
            
            # Total reinvested
            cursor.execute("SELECT SUM(amount) FROM reinvestment_operations")
            total_reinvested = cursor.fetchone()[0] or 0.0
            
            # Pending payouts
            cursor.execute(
                """
                SELECT COUNT(*), SUM(owner_payout) FROM financial_operations
                WHERE payout_status = 'pending'
                """
            )
            pending_result = cursor.fetchone()
            pending_payouts_count = pending_result[0] or 0
            pending_payout_amount = pending_result[1] or 0.0
            
            # Failed payouts
            cursor.execute(
                """
                SELECT COUNT(*) FROM financial_operations
                WHERE payout_status = 'failed'
                """
            )
            failed_payouts_count = cursor.fetchone()[0] or 0
            
            return {
                "total_revenue": total_revenue,
                "total_paid_out": total_paid_out,
                "total_reinvested": total_reinvested,
                "pending_payouts_count": pending_payouts_count,
                "pending_payout_amount": pending_payout_amount,
                "failed_payouts_count": failed_payouts_count,
            }

    def stop(self):
        """Stop the autonomous processor"""
        self.running = False
        logger.info("🛑 Stopping Autonomous Financial Processor")


async def main():
    """Main entry point for autonomous financial processing"""
    processor = AutonomousFinancialProcessor()
    
    try:
        await processor.start_autonomous_processing()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        processor.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(main())
