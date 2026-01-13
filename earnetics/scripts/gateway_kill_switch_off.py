#!/usr/bin/env python3
"""
CLI: Disable Internet Gateway write operations (activate kill switch)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from earnetics.gateway.security.kill_switch import KillSwitch

def main():
    config_path = PROJECT_ROOT / "earnetics" / "config" / "internet_gateway.json"
    kill_switch = KillSwitch(config_path)
    
    if kill_switch.disable_writes():
        print("🔒 Write operations DISABLED (kill switch active)")
        print(f"   Status: {kill_switch.get_status()}")
    else:
        print("❌ Failed to disable writes")

if __name__ == "__main__":
    main()
