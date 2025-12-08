"""Test core plays seeding mechanism"""
import pytest
from backend.ewc import CORE_PLAYS_SEED, WealthPortfolio


def test_core_plays_seed_exists():
    assert CORE_PLAYS_SEED is not None
    assert isinstance(CORE_PLAYS_SEED, list)
    assert len(CORE_PLAYS_SEED) == 5


def test_core_plays_structure():
    for play in CORE_PLAYS_SEED:
        assert "name" in play
        assert "description" in play
        assert "status" in play
        assert "risk_tier" in play
        assert "tags" in play
        assert "budget" in play
        assert "kpis" in play
        assert "execution_plan" in play
        assert "metadata" in play


def test_wealth_portfolio_seeding():
    portfolio = WealthPortfolio()
    assert len(portfolio.list_plays()) == 0
    
    seeded = portfolio.seed_core_plays(CORE_PLAYS_SEED)
    assert seeded == 5
    assert len(portfolio.list_plays()) == 5
    
    seeded_again = portfolio.seed_core_plays(CORE_PLAYS_SEED)
    assert seeded_again == 0
    assert len(portfolio.list_plays()) == 5


def test_seeded_plays_have_ids():
    portfolio = WealthPortfolio()
    portfolio.seed_core_plays(CORE_PLAYS_SEED)
    
    plays = portfolio.list_plays()
    for play in plays:
        assert "id" in play
        assert "created_at" in play
        assert play["status"] in ["draft", "ACTIVE"]
