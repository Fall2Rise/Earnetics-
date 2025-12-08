#!/usr/bin/env python3
"""Stripe integration services for Fallat CrewAI.

Provides catalog synchronisation, checkout session creation, and
transaction recording while keeping secrets outside of the repository.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import stripe

logger = logging.getLogger("StripePayments")

try:
    from backend.corporate_memory import BUSINESS_DB_PATH as DEFAULT_DB_PATH
except ModuleNotFoundError:  # pragma: no cover - legacy path fallback
    from corporate_memory import BUSINESS_DB_PATH as DEFAULT_DB_PATH


@dataclass
class PaymentTransaction:
    """Represents a processed Stripe payment."""

    transaction_id: str
    stripe_payment_intent_id: str
    amount: float
    currency: str
    status: str
    customer_email: Optional[str]
    product_id: Optional[int]
    created_at: str
    completed_at: Optional[str]
    fees: float
    net_amount: float


class StripePaymentProcessor:
    """High-level Stripe helper that persists catalog and transaction data."""

    def __init__(self, *, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.stripe_config: Dict[str, Optional[str] | bool] = {
            "api_key": None,
            "webhook_secret": None,
            "configured": False,
        }
        self._ensure_tables()

    # ------------------------------------------------------------------
    # Configuration helpers

    def configure_stripe(self, api_key: str, webhook_secret: Optional[str] = None) -> Dict:
        """Configure Stripe API access and verify credentials."""
        try:
            stripe.api_key = api_key
            account = stripe.Account.retrieve()
        except stripe.error.AuthenticationError as exc:  # pragma: no cover - bad key
            logger.error("Stripe authentication failed: %s", exc)
            return {"success": False, "error": "Invalid Stripe API key"}
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Stripe configuration failed: %s", exc)
            return {"success": False, "error": str(exc)}

        self.stripe_config.update(
            {
                "api_key": api_key,
                "webhook_secret": webhook_secret,
                "configured": True,
                "account_id": account.id,
                "test_mode": account.get("charges_enabled", False) is False,
            }
        )

        return {
            "success": True,
            "account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "test_mode": not account.charges_enabled,
        }

    def configure_from_environment(self) -> Dict:
        """Attempt to configure Stripe using environment variables."""
        api_key = os.getenv("STRIPE_SECRET_KEY")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not api_key:
            return {"success": False, "error": "STRIPE_SECRET_KEY not set"}
        return self.configure_stripe(api_key, webhook_secret)

    def create_product_with_price(
        self,
        *,
        name: str,
        description: Optional[str],
        unit_amount: float,
        currency: str = "usd",
        interval: str = "month",
    ) -> Dict:
        """Create a Stripe product and recurring price for local catalogue entries."""
        if not self.stripe_config.get("configured"):
            raise RuntimeError("Stripe not configured")

        amount_cents = int(round(unit_amount * 100))
        product = stripe.Product.create(name=name, description=description or name)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount_cents,
            currency=currency,
            recurring={"interval": interval},
        )
        return {
            "product_id": product.id,
            "price_id": price.id,
            "currency": currency,
            "interval": interval,
            "amount": unit_amount,
        }

    # ------------------------------------------------------------------
    # Product catalogue synchronisation

    def sync_corporate_products(self, *, include_inactive: bool = False) -> Dict:
        """Push products from the corporate catalogue to Stripe."""
        if not self.stripe_config.get("configured"):
            return {"success": False, "error": "Stripe not configured"}

        products = self._load_local_products(include_inactive=include_inactive)
        synced: List[Dict] = []
        for product in products:
            try:
                mapping = self._sync_product_record(product)
                synced.append(mapping)
            except stripe.error.StripeError as exc:
                logger.exception("Stripe product sync failed for %s: %s", product["id"], exc)
                return {"success": False, "error": str(exc)}
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Product sync error for %s: %s", product["id"], exc)
                return {"success": False, "error": str(exc)}

        return {"success": True, "synced": synced, "count": len(synced)}

    def _load_local_products(self, *, include_inactive: bool) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, name, price, description, status FROM products"
            ).fetchall()
        products: List[Dict] = []
        for row in rows:
            status = (row["status"] or "active").lower()
            active = status not in {"inactive", "archived", "retired"}
            if not include_inactive and not active:
                continue
            products.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "price": float(row["price"] or 0),
                    "active": active,
                }
            )
        return products

    def _sync_product_record(self, product: Dict) -> Dict:
        product_id = int(product["id"])
        amount_cents = int(round(product["price"] * 100))
        currency = "usd"
        mapping = self._get_mapping(product_id)

        if mapping:
            stripe_product_id = mapping["stripe_product_id"]
            stripe.Product.modify(
                stripe_product_id,
                name=product["name"],
                description=product["description"],
                active=product["active"],
            )
            if mapping["unit_amount"] != amount_cents or mapping["currency"] != currency:
                try:
                    stripe.Price.modify(mapping["stripe_price_id"], active=False)
                except stripe.error.InvalidRequestError:
                    logger.debug(
                        "Stripe price %s already inactive", mapping["stripe_price_id"]
                    )
                price = stripe.Price.create(
                    product=stripe_product_id,
                    unit_amount=amount_cents,
                    currency=currency,
                )
                mapping["stripe_price_id"] = price.id
                mapping["unit_amount"] = amount_cents
                mapping["currency"] = currency
            mapping["active"] = 1 if product["active"] else 0
        else:
            stripe_product = stripe.Product.create(
                name=product["name"],
                description=product["description"],
                active=product["active"],
                metadata={"local_product_id": product_id},
            )
            price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=amount_cents,
                currency=currency,
            )
            mapping = {
                "product_id": product_id,
                "stripe_product_id": stripe_product.id,
                "stripe_price_id": price.id,
                "unit_amount": amount_cents,
                "currency": currency,
                "active": 1 if product["active"] else 0,
            }

        mapping["synced_at"] = datetime.utcnow().isoformat()
        self._upsert_mapping(mapping)
        return mapping

    def create_checkout_session(
        self,
        *,
        product_id: int,
        quantity: int,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
    ) -> Dict:
        """Create a Stripe Checkout Session for a catalog product."""
        if not self.stripe_config.get("configured"):
            raise RuntimeError("Stripe not configured")

        mapping = self._get_mapping(product_id)
        if not mapping:
            raise ValueError("Product not synced to Stripe")

        metadata = {"product_id": str(product_id)}
        session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[
                {
                    "price": mapping["stripe_price_id"],
                    "quantity": max(1, quantity),
                }
            ],
            mode="payment",
            customer_email=customer_email,
            automatic_tax={"enabled": False},
            allow_promotion_codes=True,
            metadata=metadata,
            payment_intent_data={
                "metadata": metadata,
                "receipt_email": customer_email,
            },
        )

        return {
            "id": session.id,
            "url": session.url,
        }

    def create_payment_intent(
        self,
        *,
        amount: float,
        currency: str = "usd",
        customer_email: Optional[str] = None,
        product_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """Create a Stripe PaymentIntent for direct payment processing."""
        if not self.stripe_config.get("configured"):
            raise RuntimeError("Stripe not configured")

            raise RuntimeError("Stripe not configured")

        amount_cents = int(round(amount * 100))
        metadata = {}
        if product_id:
            metadata["product_id"] = str(product_id)

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            receipt_email=customer_email,
            description=description,
            metadata=metadata,
        )

        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "amount": amount,
            "currency": currency,
            "status": intent.status,
        }

    # ------------------------------------------------------------------
    # Payout functionality for 80/20 revenue distribution

    def create_payout_to_owner(
        self,
        *,
        amount: float,
        currency: str = "usd",
        description: Optional[str] = None,
        financial_op_id: Optional[int] = None,
    ) -> Dict:
        """Create a Stripe payout to transfer funds to the owner's bank account.
        
        This is used for the 80% owner distribution in the revenue split.
        Requires that Stripe account has payouts enabled and a connected bank account.
        
        Args:
            amount: Amount to payout in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            description: Optional description for the payout
            financial_op_id: Optional reference to the financial operation record
            
        Returns:
            Dict with payout details including id, status, and arrival_date
        """
        if not self.stripe_config.get("configured"):
            return {"success": False, "error": "Stripe not configured"}

        # Check if payouts are enabled
        if not self.stripe_config.get("payouts_enabled", False):
            logger.warning("Stripe payouts not enabled for this account")
            return {
                "success": False,
                "error": "Payouts not enabled. Please complete Stripe account setup.",
            }

        try:
            amount_cents = int(round(amount * 100))
            
            # Minimum payout is $1.00 for most currencies
            if amount_cents < 100:
                return {
                    "success": False,
                    "error": f"Payout amount ${amount:.2f} is below minimum ($1.00)",
                }

            metadata = {"type": "owner_distribution", "split": "80_percent"}
            if financial_op_id:
                metadata["financial_op_id"] = str(financial_op_id)
            if description:
                metadata["description"] = description

            # Create the payout
            payout = stripe.Payout.create(
                amount=amount_cents,
                currency=currency,
                description=description or f"Owner distribution: ${amount:.2f}",
                metadata=metadata,
                statement_descriptor="FALLAT AI REV",  # Shows on bank statement
            )

            # Record in database
            payout_record = {
                "stripe_payout_id": payout.id,
                "amount": amount,
                "currency": currency,
                "status": payout.status,
                "arrival_date": datetime.fromtimestamp(payout.arrival_date).isoformat()
                if payout.arrival_date
                else None,
                "financial_op_id": financial_op_id,
                "created_at": datetime.utcnow().isoformat(),
            }
            self._record_payout(payout_record)

            logger.info(
                f"💳 Stripe payout created: ${amount:.2f} {currency.upper()} "
                f"(ID: {payout.id}, Status: {payout.status})"
            )

            return {
                "success": True,
                "payout_id": payout.id,
                "amount": amount,
                "currency": currency,
                "status": payout.status,
                "arrival_date": payout_record["arrival_date"],
                "description": description,
            }

        except stripe.error.InsufficientFundsError as exc:
            logger.error(f"Insufficient funds for payout: {exc}")
            return {
                "success": False,
                "error": "Insufficient funds in Stripe balance",
                "details": str(exc),
            }
        except stripe.error.StripeError as exc:
            logger.error(f"Stripe payout error: {exc}")
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            logger.exception(f"Unexpected payout error: {exc}")
            return {"success": False, "error": str(exc)}

    def get_payout_status(self, payout_id: str) -> Dict:
        """Retrieve the current status of a Stripe payout."""
        if not self.stripe_config.get("configured"):
            return {"success": False, "error": "Stripe not configured"}

        try:
            payout = stripe.Payout.retrieve(payout_id)
            
            # Update database record
            self._update_payout_status(
                payout_id,
                payout.status,
                datetime.fromtimestamp(payout.arrival_date).isoformat()
                if payout.arrival_date
                else None,
            )

            return {
                "success": True,
                "payout_id": payout.id,
                "amount": payout.amount / 100,
                "currency": payout.currency,
                "status": payout.status,
                "arrival_date": datetime.fromtimestamp(payout.arrival_date).isoformat()
                if payout.arrival_date
                else None,
                "failure_message": payout.failure_message,
            }
        except stripe.error.StripeError as exc:
            logger.error(f"Error retrieving payout status: {exc}")
            return {"success": False, "error": str(exc)}

    def list_pending_payouts(self) -> List[Dict]:
        """List all pending payouts from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, stripe_payout_id, amount, currency, status, 
                       created_at, arrival_date, financial_op_id
                FROM stripe_payouts 
                WHERE status IN ('pending', 'in_transit')
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def sync_payout_statuses(self) -> Dict:
        """Sync status of all pending payouts with Stripe.
        
        This should be called periodically to update payout statuses.
        """
        if not self.stripe_config.get("configured"):
            return {"success": False, "error": "Stripe not configured"}

        pending = self.list_pending_payouts()
        updated = []
        errors = []

        for payout_record in pending:
            stripe_id = payout_record["stripe_payout_id"]
            if not stripe_id:
                continue

            result = self.get_payout_status(stripe_id)
            if result.get("success"):
                updated.append(
                    {
                        "payout_id": stripe_id,
                        "old_status": payout_record["status"],
                        "new_status": result["status"],
                    }
                )
            else:
                errors.append({"payout_id": stripe_id, "error": result.get("error")})

        return {
            "success": True,
            "updated_count": len(updated),
            "error_count": len(errors),
            "updated": updated,
            "errors": errors,
        }

    def get_stripe_balance(self) -> Dict:
        """Get current Stripe account balance."""
        if not self.stripe_config.get("configured"):
            return {"success": False, "error": "Stripe not configured"}

        try:
            balance = stripe.Balance.retrieve()
            
            available = []
            for bal in balance.available:
                available.append(
                    {
                        "amount": bal.amount / 100,
                        "currency": bal.currency,
                        "source_types": bal.source_types,
                    }
                )

            pending = []
            for bal in balance.pending:
                pending.append(
                    {
                        "amount": bal.amount / 100,
                        "currency": bal.currency,
                        "source_types": bal.source_types,
                    }
                )

            return {
                "success": True,
                "available": available,
                "pending": pending,
                "livemode": balance.livemode,
            }
        except stripe.error.StripeError as exc:
            logger.error(f"Error retrieving balance: {exc}")
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Database helpers for payouts

    def _record_payout(self, payout_data: Dict) -> None:
        """Record a payout in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO stripe_payouts 
                (stripe_payout_id, amount, currency, status, arrival_date, 
                 financial_op_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payout_data["stripe_payout_id"],
                    payout_data["amount"],
                    payout_data.get("currency", "usd"),
                    payout_data["status"],
                    payout_data.get("arrival_date"),
                    payout_data.get("financial_op_id"),
                    payout_data.get("created_at", datetime.utcnow().isoformat()),
                ),
            )
            conn.commit()

    def _update_payout_status(
        self, stripe_payout_id: str, status: str, arrival_date: Optional[str] = None
    ) -> None:
        """Update payout status in database."""
        with sqlite3.connect(self.db_path) as conn:
            if status in ("paid", "failed", "canceled"):
                conn.execute(
                    """
                    UPDATE stripe_payouts 
                    SET status = ?, completed_at = ?, arrival_date = ?\
                    WHERE stripe_payout_id = ?
                    """,
                    (status, datetime.utcnow().isoformat(), arrival_date, stripe_payout_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE stripe_payouts 
                    SET status = ?, arrival_date = ?
                    WHERE stripe_payout_id = ?
                    """,
                    (status, arrival_date, stripe_payout_id),
                )
            conn.commit()


    # ------------------------------------------------------------------
    # Existing database helpers
    # (Database helper methods are defined later in the file)

    # ------------------------------------------------------------------
    # Transaction recording

    def process_successful_payment(self, payment_intent_id: str) -> Dict:
        """Record a successful payment using PaymentIntent information."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception as exc:
            logger.error("Could not retrieve PaymentIntent %s: %s", payment_intent_id, exc)
            return {"success": False, "error": str(exc)}

        if intent.status != "succeeded":
            return {
                "success": False,
                "error": f"PaymentIntent not succeeded: {intent.status}",
            }

        amount = intent.amount / 100
        fees = (amount * 0.029) + 0.30
        net_amount = amount - fees
        metadata = intent.metadata or {}
        transaction = PaymentTransaction(
            transaction_id=metadata.get("transaction_id", f"TXN_{intent.id}"),
            stripe_payment_intent_id=payment_intent_id,
            amount=amount,
            currency=intent.currency,
            status="completed",
            customer_email=metadata.get("customer_email"),
            product_id=int(metadata.get("product_id")) if metadata.get("product_id") else None,
            created_at=datetime.fromtimestamp(intent.created).isoformat(),
            completed_at=datetime.utcnow().isoformat(),
            fees=fees,
            net_amount=net_amount,
        )
        self._record_transaction(transaction)
        return {"success": True, "transaction": asdict(transaction)}

    def get_revenue_summary(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(amount),0), COALESCE(SUM(fees),0), COALESCE(SUM(net_amount),0) FROM stripe_transactions"
            )
            count, gross, fees, net = cursor.fetchone()
            cursor.execute(
                "SELECT stripe_payment_intent_id, amount, currency, status, completed_at FROM stripe_transactions ORDER BY completed_at DESC LIMIT 5"
            )
            recent = cursor.fetchall()
        return {
            "total_transactions": count,
            "total_revenue": gross,
            "total_fees": fees,
            "net_revenue": net,
            "recent_transactions": [
                {
                    "payment_intent_id": row[0],
                    "amount": row[1],
                    "currency": row[2],
                    "status": row[3],
                    "completed_at": row[4],
                }
                for row in recent
            ],
        }

    # ------------------------------------------------------------------
    # Internal helpers

    def _ensure_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stripe_product_mappings (
                    product_id INTEGER PRIMARY KEY,
                    stripe_product_id TEXT NOT NULL,
                    stripe_price_id TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    unit_amount INTEGER NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    synced_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stripe_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    stripe_payment_intent_id TEXT UNIQUE,
                    product_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    status TEXT,
                    customer_email TEXT,
                    fees REAL,
                    net_amount REAL,
                    created_at TEXT,
                    completed_at TEXT
                )
                """
            )
            conn.commit()

    def _get_mapping(self, product_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM stripe_product_mappings WHERE product_id = ?",
                (product_id,),
            ).fetchone()
        return dict(row) if row else None

    def _upsert_mapping(self, mapping: Dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO stripe_product_mappings (
                    product_id, stripe_product_id, stripe_price_id, currency,
                    unit_amount, active, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    stripe_product_id = excluded.stripe_product_id,
                    stripe_price_id = excluded.stripe_price_id,
                    currency = excluded.currency,
                    unit_amount = excluded.unit_amount,
                    active = excluded.active,
                    synced_at = excluded.synced_at
                """,
                (
                    mapping["product_id"],
                    mapping["stripe_product_id"],
                    mapping["stripe_price_id"],
                    mapping["currency"],
                    mapping["unit_amount"],
                    mapping["active"],
                    mapping["synced_at"],
                ),
            )
            conn.commit()

    def _record_transaction(self, transaction: PaymentTransaction) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO stripe_transactions (
                    transaction_id,
                    stripe_payment_intent_id,
                    product_id,
                    amount,
                    currency,
                    status,
                    customer_email,
                    fees,
                    net_amount,
                    created_at,
                    completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction.transaction_id,
                    transaction.stripe_payment_intent_id,
                    transaction.product_id,
                    transaction.amount,
                    transaction.currency,
                    transaction.status,
                    transaction.customer_email,
                    transaction.fees,
                    transaction.net_amount,
                    transaction.created_at,
                    transaction.completed_at,
                ),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Webhook helpers

    def construct_event(self, payload: bytes, sig_header: str) -> Dict:
        secret = self.stripe_config.get("webhook_secret")
        if not secret:
            raise ValueError("Stripe webhook secret not configured")
        return stripe.Webhook.construct_event(payload, sig_header, secret)

    def get_transaction_by_intent(self, payment_intent_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM stripe_transactions WHERE stripe_payment_intent_id = ?",
                (payment_intent_id,),
            ).fetchone()
        return dict(row) if row else None

    def attach_transaction_to_payment_intent(
        self, payment_intent_id: str, transaction_id: int
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE stripe_transactions SET transaction_id = ? WHERE stripe_payment_intent_id = ?",
                (transaction_id, payment_intent_id),
            )
            conn.commit()

    def handle_checkout_session_completed(self, session: Dict) -> Dict:
        payment_intent_id = session.get("payment_intent")
        if not payment_intent_id:
            return {"success": False, "error": "checkout session missing payment_intent"}

        existing = self.get_transaction_by_intent(payment_intent_id)
        if existing and existing.get("transaction_id"):
            return {
                "success": True,
                "transaction": existing,
                "product_id": existing.get("product_id"),
                "customer_email": existing.get("customer_email"),
                "already_processed": True,
            }

        result = self.process_successful_payment(payment_intent_id)
        if not result.get("success"):
            return result

        transaction = result["transaction"]
        metadata = session.get("metadata") or {}
        product_id = metadata.get("product_id") or transaction.get("product_id")
        try:
            product_id_int = int(product_id) if product_id is not None else None
        except (TypeError, ValueError):
            product_id_int = None

        customer_email = None
        customer_details = session.get("customer_details") or {}
        if customer_details:
            customer_email = customer_details.get("email")
        customer_email = customer_email or session.get("customer_email") or transaction.get("customer_email")

        return {
            "success": True,
            "transaction": transaction,
            "product_id": product_id_int,
            "customer_email": customer_email,
            "already_processed": False,
        }



class StripeIntegrationManager:
    """Orchestrates Stripe setup for higher level systems."""

    def __init__(self, corporate_system, *, db_path: Path | str = DEFAULT_DB_PATH):
        self.corporate_system = corporate_system
        self.stripe_processor = StripePaymentProcessor(db_path=db_path)

    async def setup_corporate_payment_system(self, stripe_api_key: str) -> Dict:
        config_result = self.stripe_processor.configure_stripe(stripe_api_key)
        if not config_result.get("success"):
            return config_result

        sync_result = self.stripe_processor.sync_corporate_products(include_inactive=False)
        return {
            "success": True,
            "stripe_configuration": config_result,
            "catalog_sync": sync_result,
            "setup_completed_at": datetime.utcnow().isoformat(),
        }

    async def create_default_products(self) -> Dict:
        """Ensure the local products table contains baseline offers."""
        default_products = [
            {
                "name": "AI Automation Audit",
                "price": 197.0,
                "description": "Comprehensive audit of automation opportunities",
            },
            {
                "name": "Growth Playbook",
                "price": 97.0,
                "description": "Step-by-step marketing and revenue blueprint",
            },
        ]
        created = []
        with sqlite3.connect(self.stripe_processor.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            has_products = cursor.fetchone()[0] > 0
            if not has_products:
                for product in default_products:
                    cursor.execute(
                        """
                        INSERT INTO products (name, price, description, status)
                        VALUES (?, ?, ?, 'active')
                        """,
                        (
                            product["name"],
                            product["price"],
                            product["description"],
                        ),
                    )
                    created.append(product)
                conn.commit()
        if created:
            return {"success": True, "created": created}
        return {"success": True, "created": []}
