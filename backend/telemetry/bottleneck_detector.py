"""Bottleneck Detector - identifies current revenue bottleneck."""

from typing import Any, Dict, Optional

BOTTLENECKS = ["LEADS", "REPLIES", "CALLS", "CLOSES", "FULFILLMENT"]


class BottleneckDetector:
    """Deterministic bottleneck detection based on signals."""

    @staticmethod
    def detect(signals: Dict[str, Any], recent_strategy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect current bottleneck.
        
        Logic:
        - If leads < 10/day → LEADS
        - If replies < 20% of leads → REPLIES
        - If calls < 30% of replies → CALLS
        - If closes < 10% of calls → CLOSES
        - If fulfillment errors > 5% → FULFILLMENT
        """
        leads = signals.get("leads_created_24h", 0)
        replies = signals.get("replies_24h", 0)
        calls = signals.get("calls_booked_24h", 0)
        closes = signals.get("closes_24h", 0)
        failures = len(signals.get("last_24h_failures", []))
        
        # Calculate rates
        reply_rate = (replies / leads * 100) if leads > 0 else 0
        call_rate = (calls / replies * 100) if replies > 0 else 0
        close_rate = (closes / calls * 100) if calls > 0 else 0
        
        bottleneck = "LEADS"
        explanation = "Not enough leads being generated"
        recommended_focus = "Focus on lead generation channels and outreach volume"
        
        # Check fulfillment first (highest priority)
        if failures > 5:
            bottleneck = "FULFILLMENT"
            explanation = f"High failure rate detected: {failures} failures in last 24h"
            recommended_focus = "Fix operational issues and fulfillment processes"
        # Check closes
        elif calls > 0 and close_rate < 10:
            bottleneck = "CLOSES"
            explanation = f"Low close rate: {close_rate:.1f}% (target: 10%+)"
            recommended_focus = "Improve sales process, objection handling, and offer positioning"
        # Check calls
        elif replies > 0 and call_rate < 30:
            bottleneck = "CALLS"
            explanation = f"Low call booking rate: {call_rate:.1f}% (target: 30%+)"
            recommended_focus = "Improve call-to-action and booking process"
        # Check replies
        elif leads > 0 and reply_rate < 20:
            bottleneck = "REPLIES"
            explanation = f"Low reply rate: {reply_rate:.1f}% (target: 20%+)"
            recommended_focus = "Improve messaging, hooks, and follow-up sequences"
        # Check leads (default)
        elif leads < 10:
            bottleneck = "LEADS"
            explanation = f"Insufficient leads: {leads} in last 24h (target: 10+)"
            recommended_focus = "Increase outreach volume and lead generation channels"
        
        return {
            "bottleneck": bottleneck,
            "explanation": explanation,
            "recommended_focus": recommended_focus,
            "metrics": {
                "leads": leads,
                "replies": replies,
                "calls": calls,
                "closes": closes,
                "reply_rate": reply_rate,
                "call_rate": call_rate,
                "close_rate": close_rate,
                "failures": failures,
            },
        }

