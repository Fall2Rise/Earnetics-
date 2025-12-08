"""
API Key Guardian Agent
Monitors, validates, and auto-rotates API keys to prevent expiration issues.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv, set_key
import stripe

logger = logging.getLogger(__name__)

class APIKeyGuardian:
    """Autonomous agent that manages API key health and rotation."""
    
    def __init__(self):
        load_dotenv()
        self.env_file = ".env"
        self.alert_days = [7, 3, 1]  # Alert at 7, 3, and 1 day before expiration
        
    def check_stripe_key_health(self) -> Dict:
        """Check if Stripe key is valid and get account info."""
        api_key = os.getenv("STRIPE_SECRET_KEY")
        if not api_key:
            return {"status": "missing", "error": "No Stripe key configured"}
        
        try:
            stripe.api_key = api_key
            account = stripe.Account.retrieve()
            return {
                "status": "valid",
                "account_id": account.id,
                "email": account.email,
                "created": account.created
            }
        except stripe.error.AuthenticationError as e:
            if "expired" in str(e).lower():
                return {"status": "expired", "error": str(e)}
            return {"status": "invalid", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def rotate_stripe_key(self) -> Dict:
        """
        Rotate Stripe API key.
        Note: Requires a valid key to create a new one.
        """
        current_key = os.getenv("STRIPE_SECRET_KEY")
        if not current_key:
            return {"success": False, "error": "No current key to rotate"}
        
        try:
            stripe.api_key = current_key
            
            # Create a new restricted key with same permissions
            new_key = stripe.ApiKey.create(
                name=f"Auto-rotated-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            
            # Update .env file
            set_key(self.env_file, "STRIPE_SECRET_KEY", new_key.secret)
            
            # Delete old key (optional - keep for grace period)
            # stripe.ApiKey.delete(current_key)
            
            logger.info(f"Stripe key rotated successfully: {new_key.id}")
            return {
                "success": True,
                "new_key_id": new_key.id,
                "message": "Stripe key rotated and .env updated"
            }
        except Exception as e:
            logger.error(f"Failed to rotate Stripe key: {e}")
            return {"success": False, "error": str(e)}
    
    def check_google_key_health(self) -> Dict:
        """Check if Google API key is valid."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "missing", "error": "No Google API key configured"}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = list(genai.list_models())
            return {
                "status": "valid",
                "models_available": len(models)
            }
        except Exception as e:
            return {"status": "invalid", "error": str(e)}
    
    def check_smtp_health(self) -> Dict:
        """Check if SMTP credentials are valid."""
        import smtplib
        
        server = os.getenv("SMTP_SERVER")
        port = os.getenv("SMTP_PORT")
        email = os.getenv("SMTP_EMAIL")
        password = os.getenv("SMTP_PASSWORD")
        
        if not all([server, port, email, password]):
            return {"status": "incomplete", "error": "Missing SMTP credentials"}
        
        try:
            smtp = smtplib.SMTP(server, int(port), timeout=10)
            smtp.starttls()
            smtp.login(email, password)
            smtp.quit()
            return {"status": "valid"}
        except Exception as e:
            return {"status": "invalid", "error": str(e)}
    
    def run_health_check(self) -> Dict:
        """Run comprehensive health check on all API keys."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "stripe": self.check_stripe_key_health(),
            "google": self.check_google_key_health(),
            "smtp": self.check_smtp_health()
        }
        
        # Log results
        for service, status in results.items():
            if service == "timestamp":
                continue
            if isinstance(status, dict) and status.get("status") != "valid":
                logger.warning(f"{service.upper()} key issue: {status}")
        
        return results
    
    def auto_fix_issues(self) -> List[str]:
        """Attempt to automatically fix detected issues."""
        fixes = []
        
        # Check Stripe
        stripe_health = self.check_stripe_key_health()
        if stripe_health.get("status") == "expired":
            logger.info("Attempting to rotate expired Stripe key...")
            result = self.rotate_stripe_key()
            if result.get("success"):
                fixes.append("Rotated expired Stripe key")
            else:
                fixes.append(f"Failed to rotate Stripe key: {result.get('error')}")
        
        return fixes

# Standalone function for autonomy worker
def guardian_health_check():
    """Run API Key Guardian health check (called by autonomy worker)."""
    guardian = APIKeyGuardian()
    results = guardian.run_health_check()
    
    # Auto-fix if needed
    fixes = guardian.auto_fix_issues()
    if fixes:
        logger.info(f"API Key Guardian applied fixes: {fixes}")
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    guardian = APIKeyGuardian()
    
    print("🔐 API KEY GUARDIAN - Health Check")
    print("=" * 50)
    
    results = guardian.run_health_check()
    
    for service, status in results.items():
        if service == "timestamp":
            continue
        
        status_emoji = "✅" if status.get("status") == "valid" else "❌"
        print(f"{status_emoji} {service.upper()}: {status.get('status', 'unknown')}")
        if status.get("error"):
            print(f"   Error: {status['error']}")
    
    print("\n🔧 Attempting auto-fixes...")
    fixes = guardian.auto_fix_issues()
    for fix in fixes:
        print(f"   • {fix}")
