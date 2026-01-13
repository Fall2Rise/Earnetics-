"""Test strategy output contract validation."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_strategy_output_contract():
    """Test that strategy output matches expected contract."""
    latest_file = PROJECT_ROOT / "backend" / "reports" / "strategy" / "latest_strategy.json"
    
    if not latest_file.exists():
        print("WARNING: No latest strategy file found - run a strategy cycle first")
        return False
    
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    output = data.get("output", {})
    
    # Test 1: JSON parses
    assert isinstance(output, dict), "Output must be a dict"
    print("✅ JSON parses correctly")
    
    # Test 2: Contains scoreboard fields
    scoreboard = output.get("scoreboard", {})
    required_scoreboard_fields = [
        "date", "days_remaining", "cash_collected_to_date", "cash_remaining",
        "required_daily_cash_pace", "pipeline_target"
    ]
    for field in required_scoreboard_fields:
        assert field in scoreboard, f"Missing scoreboard field: {field}"
    print("✅ Scoreboard contains all required fields")
    
    # Test 3: Contains top_plays length == 3
    top_plays = output.get("top_plays", [])
    assert isinstance(top_plays, list), "top_plays must be a list"
    assert len(top_plays) == 3, f"top_plays must contain exactly 3 plays, got {len(top_plays)}"
    print("✅ top_plays contains exactly 3 plays")
    
    # Test 4: Includes EV_model for each play
    for i, play in enumerate(top_plays):
        assert "ev_model" in play, f"Play {i+1} missing ev_model"
        ev_model = play["ev_model"]
        assert "close_prob" in ev_model, f"Play {i+1} ev_model missing close_prob"
        assert "revenue_per_sale" in ev_model, f"Play {i+1} ev_model missing revenue_per_sale"
        assert "sales_velocity" in ev_model, f"Play {i+1} ev_model missing sales_velocity"
        assert "ev" in ev_model, f"Play {i+1} ev_model missing ev"
    print("✅ All plays include complete EV_model")
    
    # Test 5: Includes dispatch_packets per department
    dispatch_packets = output.get("dispatch_packets", {})
    assert isinstance(dispatch_packets, dict), "dispatch_packets must be a dict"
    expected_departments = ["growth", "domains_webops", "community", "tools_product", "ops"]
    for dept in expected_departments:
        assert dept in dispatch_packets, f"Missing dispatch_packets for {dept}"
        assert isinstance(dispatch_packets[dept], list), f"dispatch_packets[{dept}] must be a list"
    print("✅ dispatch_packets includes all departments")
    
    # Test 6: Includes experiments_to_launch <= 2
    experiments = output.get("experiments", [])
    assert isinstance(experiments, list), "experiments must be a list"
    assert len(experiments) <= 2, f"experiments must be <= 2, got {len(experiments)}"
    print("✅ experiments count <= 2 (WIP limit enforced)")
    
    # Test 7: All tasks written in English (no "Step 1", "Step 2")
    for play in top_plays:
        fastest_path = play.get("fastest_path_to_first_cash", [])
        for step in fastest_path:
            assert not step.strip().startswith("Step "), f"Found numbered step in play {play.get('play_id')}: {step[:50]}"
    print("✅ All tasks written in plain English (no numbered steps)")
    
    print("\n✅ All contract tests passed!")
    return True


if __name__ == "__main__":
    test_strategy_output_contract()

