"""Tests for the Stripe payment processor and related endpoints."""

import importlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from stripe_integration import StripePaymentProcessor


@pytest.fixture
def stripe_stubs(monkeypatch):
    class DummyProductAPI:
        def __init__(self):
            self.store = {}

        def create(self, *, name, description, active, metadata):
            product_id = f"prod_{len(self.store) + 1}"
            self.store[product_id] = {
                "name": name,
                "description": description,
                "active": active,
                "metadata": metadata,
            }
            return SimpleNamespace(id=product_id)

        def modify(self, product_id, **kwargs):
            self.store.setdefault(product_id, {}).update(kwargs)
            return SimpleNamespace(id=product_id)

    class DummyPriceAPI:
        def __init__(self):
            self.created = {}

        def create(self, *, product, unit_amount, currency):
            price_id = f"price_{len(self.created) + 1}"
            self.created[price_id] = {
                "product": product,
                "unit_amount": unit_amount,
                "currency": currency,
            }
            return SimpleNamespace(id=price_id)

        def modify(self, price_id, **kwargs):
            record = self.created.get(price_id)
            if record:
                record.update(kwargs)
            return SimpleNamespace(id=price_id)

    class DummyCheckoutSessionAPI:
        def __init__(self):
            self.last_call = None

        def create(self, **kwargs):
            self.last_call = kwargs
            return SimpleNamespace(
                id="cs_test_123",
                url="https://example.com/checkout",
                payment_status="open",
                expires_at=1234567890,
            )

    product_api = DummyProductAPI()
    price_api = DummyPriceAPI()
    checkout_api = DummyCheckoutSessionAPI()

    monkeypatch.setattr("stripe.Product", product_api, raising=False)
    monkeypatch.setattr("stripe.Price", price_api, raising=False)
    monkeypatch.setattr("stripe.checkout", SimpleNamespace(Session=checkout_api), raising=False)
    monkeypatch.setattr("stripe.Account", SimpleNamespace(retrieve=lambda: SimpleNamespace(id="acct_test", charges_enabled=True, payouts_enabled=True)), raising=False)

    return product_api, price_api, checkout_api


def _init_products_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active'
        );
        """
    )
    cur.execute(
        "INSERT INTO products (name, price, description, status) VALUES (?, ?, ?, ?)",
        ("Automation Audit", 197.0, "Comprehensive automation review", "active"),
    )
    conn.commit()
    conn.close()


def test_sync_corporate_products_creates_mapping(tmp_path, stripe_stubs):
    db_path = tmp_path / "business.db"
    _init_products_db(db_path)

    processor = StripePaymentProcessor(db_path=db_path)
    processor.stripe_config.update({"configured": True, "api_key": "sk_test_123"})

    result = processor.sync_corporate_products()
    assert result["success"]
    assert result["count"] == 1

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM stripe_product_mappings").fetchone()
    assert row is not None
    assert row["stripe_product_id"].startswith("prod_")
    assert row["unit_amount"] == 19700


def test_create_checkout_session_uses_mapping(tmp_path, stripe_stubs):
    db_path = tmp_path / "business.db"
    _init_products_db(db_path)

    processor = StripePaymentProcessor(db_path=db_path)
    processor.stripe_config.update({"configured": True, "api_key": "sk_test_123"})

    # Manually insert mapping to avoid calling sync logic again
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO stripe_product_mappings (
                product_id, stripe_product_id, stripe_price_id, currency,
                unit_amount, active, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "prod_test", "price_test", "usd", 19700, 1, datetime.utcnow().isoformat()),
        )
        conn.commit()

    _, _, checkout_api = stripe_stubs

    session = processor.create_checkout_session(
        product_id=1,
        quantity=2,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        customer_email="buyer@example.com",
    )

    assert session["id"].startswith("cs_")
    assert checkout_api.last_call is not None
    assert checkout_api.last_call["line_items"][0]["price"] == "price_test"
    assert checkout_api.last_call["line_items"][0]["quantity"] == 2

def test_create_product_endpoint_persists_and_syncs(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTONOMY_SCHEDULER_ENABLED", "0")

    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    import backend.corporate_memory as corporate_memory  # noqa: WPS433
    importlib.reload(corporate_memory)

    import backend.executive_reasoning as executive_reasoning  # noqa: WPS433
    importlib.reload(executive_reasoning)

    import backend.main_server as main_server  # noqa: WPS433
    main_server = importlib.reload(main_server)

    def fake_create_product(*_, **__):
        return {"product": {"id": "PROD_TEST"}}

    monkeypatch.setattr(main_server, "create_product", fake_create_product)

    main_server.stripe_processor.stripe_config.update({"configured": True})

    sync_calls = {}

    def fake_sync(include_inactive: bool = False):
        sync_calls["include_inactive"] = include_inactive
        return {"success": True, "count": 1, "synced": []}

    monkeypatch.setattr(
        main_server.stripe_processor,
        "sync_corporate_products",
        fake_sync,
    )

    client = TestClient(main_server.app)

    payload = {
        "product_type": "AI Strategy Blueprint",
        "target_audience": "Growth Teams",
        "price_point": 249.0,
        "description": "Battle-tested GTM plan",
    }

    response = client.post("/api/products/create", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "success", body
    assert body["product_record"]["name"] == payload["product_type"]
    assert sync_calls.get("include_inactive") is False

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT name, price, description, category, status FROM products WHERE id = ?",
            (body["product_record"]["id"],),
        ).fetchone()

    assert row is not None
    assert row["name"] == payload["product_type"]
    assert row["price"] == payload["price_point"]
    assert row["description"] == payload["description"]
    assert row["category"] == payload["product_type"]
    assert row["status"] == "active"


def test_stripe_webhook_processes_checkout_session(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTONOMY_SCHEDULER_ENABLED", "0")

    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    import backend.corporate_memory as corporate_memory  # noqa: WPS433
    importlib.reload(corporate_memory)

    import backend.executive_reasoning as executive_reasoning  # noqa: WPS433
    importlib.reload(executive_reasoning)

    import backend.main_server as main_server  # noqa: WPS433
    main_server = importlib.reload(main_server)

    main_server.stripe_processor.stripe_config.update(
        {"configured": True, "webhook_secret": "whsec_test"}
    )

    event_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "payment_intent": "pi_test_123",
                "amount_total": 24900,
                "currency": "usd",
                "customer_details": {"email": "buyer@example.com"},
                "metadata": {"product_id": "1"},
            }
        },
    }

    monkeypatch.setattr(
        "stripe.Webhook.construct_event",
        lambda payload, sig, secret: event_payload,
    )

    payment_intent = SimpleNamespace(
        id="pi_test_123",
        amount=24900,
        currency="usd",
        status="succeeded",
        metadata={"product_id": "1", "customer_email": "buyer@example.com"},
        created=int(datetime.utcnow().timestamp()),
    )

    monkeypatch.setattr(
        "stripe.PaymentIntent.retrieve",
        lambda intent_id: payment_intent,
    )

    recorded = {}

    original_revenue = main_server.FinancialDepartment.process_revenue_distribution

    def capture_revenue(
        transaction_id: int,
        gross: float,
        *,
        currency: str = "usd",
        stripe_fees: float = 0.0,
        net_revenue: Optional[float] = None,
    ):
        recorded["transaction_id"] = transaction_id
        recorded["gross"] = gross
        recorded["currency"] = currency
        recorded["fees"] = stripe_fees
        recorded["net"] = net_revenue
        return original_revenue(
            transaction_id,
            gross,
            currency=currency,
            stripe_fees=stripe_fees,
            net_revenue=net_revenue,
        )

    monkeypatch.setattr(
        main_server.FinancialDepartment,
        "process_revenue_distribution",
        staticmethod(capture_revenue),
    )

    client = TestClient(main_server.app)
    response = client.post(
        "/api/stripe/webhook",
        data=json.dumps({"dummy": "value"}),
        headers={"stripe-signature": "sig_test"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "processed"
    transaction_id = body["transaction_id"]
    assert recorded["transaction_id"] == transaction_id
    assert recorded["gross"] == 249.0
    assert recorded["currency"] == "usd"
    assert recorded["fees"] == pytest.approx(249.0 * 0.029 + 0.30, rel=1e-6)
    assert recorded["net"] == pytest.approx(249.0 - recorded["fees"], rel=1e-6)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        txn_row = conn.execute(
            "SELECT amount, source, stripe_transaction_id, customer_email, description FROM transactions WHERE id = ?",
            (transaction_id,),
        ).fetchone()
        stripe_row = conn.execute(
            "SELECT transaction_id, amount, stripe_payment_intent_id FROM stripe_transactions WHERE stripe_payment_intent_id = ?",
            ("pi_test_123",),
        ).fetchone()
        financial_row = conn.execute(
            "SELECT currency, stripe_fees, net_revenue FROM financial_operations WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()

    assert txn_row is not None
    assert txn_row["amount"] == 249.0
    assert txn_row["source"] == "Stripe Checkout"
    assert txn_row["stripe_transaction_id"] == "pi_test_123"
    assert txn_row["customer_email"] == "buyer@example.com"
    assert "product 1" in (txn_row["description"] or "")

    assert stripe_row is not None
    assert int(stripe_row["transaction_id"]) == transaction_id
    assert stripe_row["amount"] == 249.0

    assert financial_row is not None
    assert financial_row["currency"] == "usd"
    assert financial_row["stripe_fees"] == pytest.approx(recorded["fees"], rel=1e-6)
    assert financial_row["net_revenue"] == pytest.approx(recorded["net"], rel=1e-6)


def test_stripe_webhook_rejects_missing_signature(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTONOMY_SCHEDULER_ENABLED", "0")

    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    import backend.corporate_memory as corporate_memory  # noqa: WPS433
    importlib.reload(corporate_memory)

    import backend.executive_reasoning as executive_reasoning  # noqa: WPS433
    importlib.reload(executive_reasoning)

    import backend.main_server as main_server  # noqa: WPS433
    main_server = importlib.reload(main_server)

    main_server.stripe_processor.stripe_config.update(
        {"configured": True, "webhook_secret": "whsec_test"}
    )

    client = TestClient(main_server.app)
    response = client.post(
        "/api/stripe/webhook",
        data=json.dumps({}),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Stripe signature header"
