from __future__ import annotations

import sys
import types

import pytest

if "sentence_transformers" not in sys.modules:
    stub_module = types.ModuleType("sentence_transformers")

    class _StubModel:
        def __init__(self, *args, **kwargs):
            pass

        def eval(self):
            return self

        def encode(self, texts, convert_to_numpy=False):
            if isinstance(texts, str):
                texts = [texts]
            if convert_to_numpy:
                import numpy as np

                return np.zeros((len(texts), 384))
            return [[0.0] * 5 for _ in texts]

    stub_module.SentenceTransformer = _StubModel
    sys.modules["sentence_transformers"] = stub_module

from backend import ai_corporation_agents as agents
from backend.api.corporate_router import (
    DirectiveRequest,
    MarketResearchRequest,
    ProductRequest,
    RevenueRequest,
    execute_directive_endpoint,
    financial_summary_endpoint,
    market_research_endpoint,
    process_revenue_endpoint,
    system_status_endpoint,
    create_product_endpoint,
)


def test_process_revenue_endpoint(monkeypatch):
    payload = {"status": "ok"}
    events = []

    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )

    def fake_process(amount, source, category, description=""):
        assert amount == 123.45
        assert source == "Test Source"
        assert category == "testing"
        assert description == "note"
        return payload

    monkeypatch.setattr(agents, "process_revenue", fake_process)
    response = process_revenue_endpoint(
        RevenueRequest(
            amount=123.45,
            source="Test Source",
            category="testing",
            description="note",
        )
    )
    assert response == {"status": "processed", "result": payload}
    assert any(event[0][0] == "revenue.process" for event in events)


def test_execute_directive_endpoint(monkeypatch):
    events = []
    monkeypatch.setattr(
        agents, "execute_directive", lambda directive, priority: {"directive": directive, "priority": priority}
    )
    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )
    result = execute_directive_endpoint(
        DirectiveRequest(
            directive="Grow revenue",
            priority="urgent",
            departments=["sales"],
        )
    )
    assert result["status"] == "queued"
    assert result["departments"] == ["sales"]
    assert result["result"]["priority"] == "urgent"
    assert any(event[0][0] == "directive.execute" for event in events)


def test_system_status_endpoint(monkeypatch):
    events = []
    monkeypatch.setattr(agents, "system_status", lambda: {"status": "operational"})
    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )
    assert system_status_endpoint()["status"] == "operational"
    assert any(event[0][0] == "system.status" for event in events)


def test_create_product_endpoint(monkeypatch):
    events = []
    monkeypatch.setattr(
        agents,
        "create_product",
        lambda product_type, target_audience, price_point, description: {
            "product_type": product_type,
            "target_audience": target_audience,
            "price_point": price_point,
        },
    )
    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )
    monkeypatch.setattr(
        "backend.api.corporate_router._sync_product_to_stripe",
        lambda request: {"price_id": "price_test", "product_id": "prod_test"},
    )
    result = create_product_endpoint(
        ProductRequest(
            product_type="course",
            target_audience="founders",
            price_point=199.0,
            description="Automations",
        )
    )
    assert result["status"] == "created"
    assert result["product"]["target_audience"] == "founders"
    assert result["stripe"]["price_id"] == "price_test"
    assert any(event[0][0] == "product.create" for event in events)


def test_market_research_endpoint(monkeypatch):
    events = []
    monkeypatch.setattr(
        agents,
        "market_research",
        lambda industry, target_market: {"industry": industry, "target_market": target_market},
    )
    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )
    result = market_research_endpoint(
        MarketResearchRequest(industry="AI", target_market="consultants", research_depth="deep")
    )
    assert result["status"] == "completed"
    assert result["requested_depth"] == "deep"
    assert any(event[0][0] == "market.research" for event in events)


def test_financial_summary_endpoint(monkeypatch):
    summary = {"financial_summary": {}, "timestamp": "now"}
    events = []
    monkeypatch.setattr(agents, "financial_summary", lambda: summary)
    monkeypatch.setattr(
        "backend.api.corporate_router.log_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )
    assert financial_summary_endpoint() == summary
    assert any(event[0][0] == "financial.summary" for event in events)
