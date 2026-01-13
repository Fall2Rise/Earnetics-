"""API routes for Signal Collection."""

from typing import Any, Dict

from fastapi import APIRouter

from backend.audit_log import log_event
from backend.telemetry.signal_collector import SignalCollector

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/latest")
def get_latest_signals() -> Dict[str, Any]:
    """Get latest collected signals."""
    collector = SignalCollector()
    signals = collector.load_latest_signals()
    return signals


@router.post("/ingest")
def ingest_signals(signals: Dict[str, Any]) -> Dict[str, Any]:
    """Manually ingest signals (override)."""
    collector = SignalCollector()
    filepath = collector.save_signals(signals)
    
    log_event(
        "signals.ingested",
        agent="manual",
        message="Signals manually ingested",
    )
    
    return {
        "status": "saved",
        "filepath": str(filepath),
        "signals": signals,
    }

