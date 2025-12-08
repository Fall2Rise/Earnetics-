"""Tests for wealth execution runs and revenue cycle persistence."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from backend.api.wealth_router import router, get_ewc, get_run_store, get_cycle_store
from backend.ewc.wealth_runs import WealthRunStore
from backend.ewc.revenue_store import RevenueCycleStore
from backend.main_server import app


@pytest.fixture
def temp_run_store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    store = WealthRunStore(db_path=db_path)
    yield store
    
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def sample_play():
    return {
        "id": "test-play-123",
        "name": "Test Play",
        "description": "A test play for execution",
        "status": "draft",
        "risk_tier": "low",
        "execution_plan": {
            "channels": ["test"],
            "steps": [
                {
                    "key": "step1",
                    "agent": "TestAgent1",
                    "desc": "First test step",
                },
                {
                    "key": "step2",
                    "agent": "TestAgent2",
                    "desc": "Second test step",
                },
                {
                    "key": "step3",
                    "agent": "TestAgent3",
                    "desc": "Third test step",
                },
            ],
        },
    }


def test_wealth_run_store_create_run(temp_run_store, sample_play):
    run = temp_run_store.create_run(sample_play)
    
    assert run is not None
    assert "run_id" in run
    assert run["play_id"] == "test-play-123"
    assert run["status"] == "planned"
    assert "created_at" in run
    assert "steps" in run
    assert len(run["steps"]) == 3
    
    for step in run["steps"]:
        assert "key" in step
        assert "agent" in step
        assert "desc" in step
        assert step["status"] == "planned"


def test_wealth_run_store_get_run(temp_run_store, sample_play):
    created_run = temp_run_store.create_run(sample_play)
    run_id = created_run["run_id"]
    
    retrieved_run = temp_run_store.get_run(run_id)
    
    assert retrieved_run is not None
    assert retrieved_run["run_id"] == run_id
    assert retrieved_run["play_id"] == "test-play-123"
    assert retrieved_run["status"] == "planned"
    assert len(retrieved_run["steps"]) == 3


def test_wealth_run_store_get_nonexistent_run(temp_run_store):
    run = temp_run_store.get_run("nonexistent-run-id")
    assert run is None


def test_wealth_run_store_list_runs_for_play(temp_run_store, sample_play):
    run1 = temp_run_store.create_run(sample_play)
    run2 = temp_run_store.create_run(sample_play)
    run3 = temp_run_store.create_run(sample_play)
    
    runs = temp_run_store.list_runs_for_play("test-play-123")
    
    assert len(runs) == 3
    run_ids = [r["run_id"] for r in runs]
    assert run1["run_id"] in run_ids
    assert run2["run_id"] in run_ids
    assert run3["run_id"] in run_ids


def test_wealth_run_store_list_runs_empty(temp_run_store):
    runs = temp_run_store.list_runs_for_play("nonexistent-play")
    assert runs == []


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_revenue_loop(monkeypatch):
    from backend.ewc import revenue_loop as revenue_loop_module

    sample_result = revenue_loop_module.RevenueLoopResult(
        product_roadmap={"play": "mock"},
        validated_opportunity={"score": 0.9},
        automation_module_spec={"module": "mock"},
        approved_module={"status": "approved"},
        revenue_play_report={"status": "ready"},
    )

    monkeypatch.setattr(revenue_loop_module, "_ensure_crewai_available", lambda: None)
    monkeypatch.setattr(
        revenue_loop_module.RevenueLoopRunner,
        "run",
        lambda self, market_context: sample_result,
    )

    return sample_result


@pytest.fixture
def temp_cycle_store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    store = RevenueCycleStore(db_path=db_path)
    yield store

    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def setup_test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    if hasattr(router, "_run_store_instance"):
        delattr(router, "_run_store_instance")

    router._run_store_instance = WealthRunStore(db_path=db_path)

    yield

    if hasattr(router, "_run_store_instance"):
        delattr(router, "_run_store_instance")

    try:
        os.unlink(db_path)
    except Exception:
        pass


def test_execute_play_endpoint(client, setup_test_db):
    ewc = get_ewc()
    plays = ewc.list_plays()
    
    assert len(plays) > 0, "No plays seeded"
    
    play = plays[0]
    play_id = play["id"]
    
    response = client.post(f"/wealth/plays/{play_id}/execute")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "run_id" in data
    assert data["play_id"] == play_id
    assert data["status"] == "planned"
    assert "created_at" in data
    assert "steps" in data
    assert len(data["steps"]) > 0


def test_execute_nonexistent_play(client, setup_test_db):
    response = client.post("/wealth/plays/nonexistent-play-id/execute")
    assert response.status_code == 404


def test_list_play_runs_endpoint(client, setup_test_db):
    ewc = get_ewc()
    plays = ewc.list_plays()
    play = plays[0]
    play_id = play["id"]
    
    client.post(f"/wealth/plays/{play_id}/execute")
    client.post(f"/wealth/plays/{play_id}/execute")
    
    response = client.get(f"/wealth/plays/{play_id}/runs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "play_id" in data
    assert data["play_id"] == play_id
    assert "runs" in data
    assert len(data["runs"]) == 2


def test_list_runs_for_nonexistent_play(client, setup_test_db):
    response = client.get("/wealth/plays/nonexistent-play-id/runs")
    assert response.status_code == 404


def test_autonomous_cycle_endpoint(client, temp_cycle_store, mock_revenue_loop):
    if hasattr(router, "_cycle_store_instance"):
        delattr(router, "_cycle_store_instance")
    router._cycle_store_instance = temp_cycle_store

    response = client.post(
        "/wealth/autonomous_cycle",
        json={"signal": "TikTok", "budget": 20},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "cycle" in data
    assert data["cycle"]["revenue_play_report"] == mock_revenue_loop.revenue_play_report
    assert "cycle_id" in data["cycle"]
    records = temp_cycle_store.list_cycles()
    assert len(records) == 1


def test_cycle_store_isolation(client, temp_cycle_store, mock_revenue_loop):
    if hasattr(router, "_cycle_store_instance"):
        delattr(router, "_cycle_store_instance")
    router._cycle_store_instance = temp_cycle_store

    client.post("/wealth/autonomous_cycle", json={"signal": "Trend", "budget": 5})
    client.post("/wealth/autonomous_cycle", json={"signal": "Trend", "budget": 5})

    records = temp_cycle_store.list_cycles()
    assert len(records) == 2


def test_revenue_cycle_store_persistence(temp_cycle_store):
    market = {"signal": "Trend"}
    cycle = {
        "product_roadmap": {"plan": "Roadmap"},
        "validated_opportunity": {"score": 0.9},
        "automation_module_spec": {"tasks": ["t1"]},
        "approved_module": {"status": "ok"},
        "revenue_play_report": {"status": "ready"},
    }

    stored = temp_cycle_store.record_cycle(market, cycle)

    assert "cycle_id" in stored
    records = temp_cycle_store.list_cycles()
    assert len(records) == 1
    record = records[0]
    assert record["market_context"]["signal"] == "Trend"
    assert record["product_roadmap"]["plan"] == "Roadmap"


def test_revenue_cycle_store_list_limit(temp_cycle_store):
    market = {"signal": "Trend"}
    cycle = {
        "product_roadmap": {"plan": "Roadmap"},
        "validated_opportunity": {"score": 0.9},
        "automation_module_spec": {"tasks": ["t1"]},
        "approved_module": {"status": "ok"},
        "revenue_play_report": {"status": "ready"},
    }

    for _ in range(5):
        temp_cycle_store.record_cycle(market, cycle)

    limited = temp_cycle_store.list_cycles(limit=3)
    assert len(limited) == 3


def test_get_run_endpoint(client, setup_test_db):
    ewc = get_ewc()
    plays = ewc.list_plays()
    play = plays[0]
    play_id = play["id"]

    exec_response = client.post(f"/wealth/plays/{play_id}/execute")
    run_id = exec_response.json()["run_id"]

    response = client.get(f"/wealth/runs/{run_id}")

    assert response.status_code == 200
    data = response.json()

    assert "run" in data
    assert data["run"]["run_id"] == run_id
    assert data["run"]["play_id"] == play_id


def test_get_nonexistent_run(client, setup_test_db):
    response = client.get("/wealth/runs/nonexistent-run-id")
    assert response.status_code == 404


def test_tiktok_play_execution(client, setup_test_db):
    ewc = get_ewc()
    plays = ewc.list_plays()

    tiktok_play = None
    for play in plays:
        if "TikTok" in play.get("name", ""):
            tiktok_play = play
            break

    assert tiktok_play is not None, "TikTok play not found in seeded plays"

    play_id = tiktok_play["id"]

    response = client.post(f"/wealth/plays/{play_id}/execute")

    assert response.status_code == 200
    data = response.json()

    assert data["play_id"] == play_id
    assert "steps" in data
    assert len(data["steps"]) > 0

    for step in data["steps"]:
        assert step["status"] == "planned"
        assert "key" in step
        assert "agent" in step
        assert "desc" in step



