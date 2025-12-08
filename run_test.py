#!/usr/bin/env python3
"""Quick test runner that changes to the correct directory first"""
import os
import sys
from pathlib import Path

# Find the workspace root
workspace = Path(__file__).parent
os.chdir(workspace)
sys.path.insert(0, str(workspace))

# Now run the test
exec(open("tests/test_autonomous_financial.py", encoding="utf-8").read())
