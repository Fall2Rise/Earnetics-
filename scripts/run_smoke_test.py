import os
import sys
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main_server import app

def run_smoke_test():
    client = TestClient(app)
    tests = [
        ("System Health", "/health"),
        ("Consolidated Status", "/api/system/status"),
        ("Agent Status", "/api/agents/status"),
        ("Integration Status", "/api/system/integrations"),
        ("Financial Metrics", "/api/financial/metrics"),
        ("ATOM Evolution", "/api/atom/evolution_metrics"),
    ]
    headers = {"X-Fallat-Token": os.getenv("FALLAT_API_TOKEN", "")}
    for name, endpoint in tests:
        try:
            response = client.get(endpoint, headers=headers)
            sys.stdout.write(f"TEST {name}: {response.status_code}\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"TEST {name}: ERROR {str(e)}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_smoke_test()
