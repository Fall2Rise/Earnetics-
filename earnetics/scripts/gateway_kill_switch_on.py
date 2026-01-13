#!/usr/bin/env python3
"""
CLI: Enable Internet Gateway write operations
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from earnetics.gateway.security.kill_switch import KillSwitch

def main():
    config_path = PROJECT_ROOT / "earnetics" / "config" / "internet_gateway.json"
    kill_switch = KillSwitch(config_path)
    
    if kill_switch.enable_writes():
        print("✅ Write operations ENABLED")
        print(f"   Status: {kill_switch.get_status()}")
    else:
        print("❌ Failed to enable writes (gateway may be disabled)")

if __name__ == "__main__":
    main()
