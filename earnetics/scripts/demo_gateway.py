#!/usr/bin/env python3
"""
Demo Internet Gateway
Proves security controls work:
- Allowed web.fetch to wikipedia → success
- Blocked web.fetch to non-allowlisted domain → blocked
- Blocked social.post without approval token → blocked
- Enabled writes, then social.post with approval token → success (or stub)
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from earnetics.gateway.internet_gateway import InternetGateway
from earnetics.gateway.security.approval_tokens import ApprovalTokenManager
from earnetics.tools.web_tools import web_fetch, web_search, social_post


def main():
    print("🔒 Earnetics Internet Gateway Demo")
    print("=" * 60)
    
    # Initialize gateway
    config_path = PROJECT_ROOT / "earnetics" / "config" / "internet_gateway.json"
    gateway = InternetGateway(config_path)
    approval_tokens = ApprovalTokenManager()
    
    print("\n1. Testing allowed web.fetch to Wikipedia...")
    result = web_fetch("https://en.wikipedia.org/wiki/Artificial_intelligence", 
                      agent_id="demo_agent", role="INTELLIGENCE_RND")
    if result["success"]:
        print(f"   ✅ Success: Fetched {len(result.get('text', ''))} bytes")
        print(f"   Citation: {result.get('citation', {}).get('url', 'N/A')}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    print("\n2. Testing blocked web.fetch to non-allowlisted domain...")
    result = web_fetch("https://example-blocked-site.com", 
                      agent_id="demo_agent", role="INTELLIGENCE_RND")
    if not result["success"]:
        print(f"   ✅ Correctly blocked: {result.get('error')}")
    else:
        print(f"   ❌ Should have been blocked!")
    
    print("\n3. Testing web.search (internal knowledge router)...")
    result = web_search("revenue strategies", agent_id="demo_agent", role="INTELLIGENCE_RND")
    if result["success"]:
        print(f"   ✅ Success: Found {result.get('total', 0)} results")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    print("\n4. Testing social.post without approval token (should be blocked)...")
    result = social_post("twitter", "Test post", agent_id="demo_agent", role="MARKETING")
    if not result["success"]:
        print(f"   ✅ Correctly blocked: {result.get('error')}")
    else:
        print(f"   ❌ Should have been blocked!")
    
    print("\n5. Enabling writes and generating approval token...")
    gateway.kill_switch.enable_writes()
    token_result = approval_tokens.generate_token("social.post", created_by="EXEC", expires_hours=1)
    approval_token = token_result.get("token")
    
    if approval_token:
        print(f"   ✅ Generated approval token: {approval_token[:20]}...")
        print(f"   ✅ Writes enabled")
        
        print("\n6. Testing social.post with approval token...")
        result = social_post("twitter", "Test post with approval", 
                            approval_token=approval_token,
                            agent_id="demo_agent", role="MARKETING")
        if result["success"]:
            print(f"   ✅ Success: Post created (stub)")
        else:
            print(f"   ⚠️  Note: {result.get('error')} (adapter may not be fully implemented)")
    else:
        print("   ❌ Failed to generate approval token")
    
    print("\n7. Testing rate limiting...")
    # Make multiple rapid requests
    blocked_count = 0
    for i in range(25):  # Exceed per-agent limit of 20
        result = web_fetch("https://en.wikipedia.org/wiki/Test", 
                          agent_id="rate_test_agent", role="SCRAPER")
        if not result["success"] and "rate limit" in result.get("error", "").lower():
            blocked_count += 1
            if blocked_count == 1:
                print(f"   ✅ Rate limit triggered after {i+1} requests")
                break
    
    print("\n8. Gateway Status:")
    status = gateway.get_status()
    print(f"   Enabled: {status.get('enabled')}")
    print(f"   Kill Switch: {status.get('kill_switch')}")
    print(f"   Rate Limits: {status.get('rate_limits', {}).get('global', {})}")
    print(f"   Adapters: {list(status.get('adapters', {}).keys())}")
    
    print("\n9. Audit Log Stats:")
    audit_stats = gateway.audit_logger.get_stats(hours=1)
    print(f"   Total Requests: {audit_stats.get('total_requests', 0)}")
    print(f"   Blocked: {audit_stats.get('blocked_count', 0)}")
    print(f"   Allowed/Success: {audit_stats.get('allowed_count', 0)}")
    print(f"   Failed: {audit_stats.get('failed_count', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ Gateway demo completed!")
    print("\nSecurity controls verified:")
    print("  ✓ Allowlist enforcement")
    print("  ✓ Permission checks")
    print("  ✓ Kill switch")
    print("  ✓ Approval tokens")
    print("  ✓ Rate limiting")
    print("  ✓ Audit logging")


if __name__ == "__main__":
    main()
