
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main_server import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_smoke_test():
    print("\n🚀 STARTING FINAL END-TO-END SMOKE TEST 🚀\n")
    
    client = TestClient(app)
    
    tests = [
        ("System Health", "/health", 200),
        ("Dashboard Metrics", "/api/system/status", 200),
        ("Stripe Products", "/api/stripe/products", 200),
        ("Email Campaigns", "/api/campaigns", 200),
        ("Content Engine Status", "/api/content/status", 200), # Assuming this exists or similar
        ("Agent List", "/api/agents", 200),
    ]
    
    passed = 0
    failed = 0
    
    print(f"{'COMPONENT':<25} | {'ENDPOINT':<25} | {'STATUS':<10} | {'RESULT'}")
    print("-" * 80)
    
    for name, endpoint, expected_status in tests:
        try:
            # For some endpoints we might need to mock auth headers if enabled
            # But for now assuming localhost/dev mode allows access or we add headers
            headers = {"X-Fallat-Token": os.getenv("FALLAT_API_TOKEN", "")}
            
            response = client.get(endpoint, headers=headers)
            
            status_code = response.status_code
            result = "✅ PASS" if status_code == expected_status else f"❌ FAIL ({status_code})"
            
            if status_code == expected_status:
                passed += 1
            else:
                failed += 1
                
            print(f"{name:<25} | {endpoint:<25} | {status_code:<10} | {result}")
            
            # Deep check for Stripe
            if name == "Stripe Products" and status_code == 200:
                data = response.json()
                product_count = len(data.get("products", []))
                print(f"   ↳ Found {product_count} Stripe products.")
                if product_count == 0:
                    print("   ⚠️  WARNING: No products found in Stripe!")

        except Exception as e:
            print(f"{name:<25} | {endpoint:<25} | {'ERR':<10} | ❌ CRASH: {str(e)}")
            failed += 1

    print("-" * 80)
    print(f"\n🏁 TEST COMPLETE: {passed} Passed, {failed} Failed")
    
    if failed == 0:
        print("\n✅ SYSTEM IS READY FOR LAUNCH.")
    else:
        print("\n⚠️  SYSTEM HAS ISSUES. CHECK LOGS ABOVE.")

if __name__ == "__main__":
    # Suppress other logs
    logging.getLogger("backend").setLevel(logging.WARNING)
    run_smoke_test()
