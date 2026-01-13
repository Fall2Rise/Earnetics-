"""
Stripe Adapter: Makes Stripe API calls
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.gateway.adapters.base_adapter import BaseAdapter


class StripeAdapter(BaseAdapter):
    """Adapter for Stripe API calls"""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        super().__init__(config, credential_vault)
        self.api_version = config.get("stripe_api_version", "2023-10-16")
    
    def execute(self, action: str, params: Dict[str, Any], 
               agent_id: str, role: str) -> Dict[str, Any]:
        """
        Execute Stripe API call
        
        Params:
            endpoint: str - API endpoint (e.g., "products", "customers", "payment_intents")
            method: str - "GET", "POST", "PUT", "DELETE"
            payload: Dict[str, Any] - Request payload
        """
        if action not in ["stripe.read", "stripe.write"]:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Unsupported action: {action}"
            }
        
        endpoint = params.get("endpoint", "")
        method = params.get("method", "GET").upper()
        payload = params.get("payload", {})
        
        if not endpoint:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": "Endpoint is required"
            }
        
        try:
            # Get Stripe API key
            api_key = self.credential_vault.get_secret("stripe_secret_key") if self.credential_vault else os.getenv("STRIPE_SECRET_KEY")
            
            if not api_key:
                return {
                    "success": False,
                    "data": None,
                    "metadata": {},
                    "citation": {},
                    "error": "Stripe API key not configured"
                }
            
            # Use Stripe Python library if available
            try:
                import stripe
                stripe.api_key = api_key
                stripe.api_version = self.api_version
                
                # Map endpoint to Stripe resource
                resource_map = {
                    "products": stripe.Product,
                    "customers": stripe.Customer,
                    "payment_intents": stripe.PaymentIntent,
                    "payment_links": stripe.PaymentLink,
                    "prices": stripe.Price,
                    "subscriptions": stripe.Subscription,
                    "invoices": stripe.Invoice,
                    "charges": stripe.Charge,
                    "refunds": stripe.Refund
                }
                
                resource_class = resource_map.get(endpoint.split("/")[0])
                if not resource_class:
                    # Try direct API call
                    if method == "GET":
                        result = stripe.api_requestor.APIRequestor(api_key).request(
                            method.lower(),
                            f"/v1/{endpoint}",
                            {}
                        )
                    else:
                        result = stripe.api_requestor.APIRequestor(api_key).request(
                            method.lower(),
                            f"/v1/{endpoint}",
                            payload
                        )
                    
                    return {
                        "success": True,
                        "data": result,
                        "metadata": {
                            "endpoint": endpoint,
                            "method": method,
                            "api_version": self.api_version
                        },
                        "citation": self.create_citation(f"stripe://api.stripe.com/v1/{endpoint}", datetime.utcnow().isoformat())
                    }
                
                # Use resource class methods
                if method == "GET":
                    if "/" in endpoint:
                        # Retrieve specific resource
                        resource_id = endpoint.split("/")[-1]
                        result = resource_class.retrieve(resource_id)
                    else:
                        # List resources
                        result = resource_class.list(**payload)
                elif method == "POST":
                    if "/" in endpoint and endpoint.split("/")[-1] not in ["create", "new"]:
                        # Update existing
                        resource_id = endpoint.split("/")[-1]
                        result = resource_class.modify(resource_id, **payload)
                    else:
                        # Create new
                        result = resource_class.create(**payload)
                elif method == "PUT":
                    resource_id = endpoint.split("/")[-1]
                    result = resource_class.modify(resource_id, **payload)
                elif method == "DELETE":
                    resource_id = endpoint.split("/")[-1]
                    result = resource_class.delete(resource_id)
                else:
                    return {
                        "success": False,
                        "data": None,
                        "metadata": {},
                        "citation": {},
                        "error": f"Unsupported HTTP method: {method}"
                    }
                
                # Convert Stripe object to dict
                if hasattr(result, "to_dict"):
                    result_dict = result.to_dict()
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    result_dict = {"id": str(result)}
                
                return {
                    "success": True,
                    "data": result_dict,
                    "metadata": {
                        "endpoint": endpoint,
                        "method": method,
                        "api_version": self.api_version,
                        "resource": endpoint.split("/")[0]
                    },
                    "citation": self.create_citation(f"stripe://api.stripe.com/v1/{endpoint}", datetime.utcnow().isoformat())
                }
            
            except ImportError:
                # Fallback: Use requests directly
                import requests
                
                base_url = "https://api.stripe.com/v1"
                url = f"{base_url}/{endpoint}"
                
                response = requests.request(
                    method,
                    url,
                    auth=(api_key, ""),
                    json=payload if method in ["POST", "PUT"] else None,
                    params=payload if method == "GET" else None,
                    headers={
                        "Stripe-Version": self.api_version
                    },
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "data": response.json(),
                        "metadata": {
                            "endpoint": endpoint,
                            "method": method,
                            "api_version": self.api_version,
                            "status_code": response.status_code
                        },
                        "citation": self.create_citation(f"stripe://api.stripe.com/v1/{endpoint}", datetime.utcnow().isoformat())
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "metadata": {},
                        "citation": {},
                        "error": f"Stripe API error: {response.status_code} - {response.text}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Stripe API call error: {str(e)}"
            }
