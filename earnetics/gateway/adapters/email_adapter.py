"""
Email Adapter: Sends emails through configured providers
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.gateway.adapters.base_adapter import BaseAdapter


class EmailAdapter(BaseAdapter):
    """Adapter for sending emails via Mailgun, SendGrid, etc."""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        super().__init__(config, credential_vault)
        self.providers = config.get("email_providers", {})
    
    def execute(self, action: str, params: Dict[str, Any], 
               agent_id: str, role: str) -> Dict[str, Any]:
        """
        Execute email send action
        
        Params:
            provider: str - "mailgun" | "sendgrid" | "smtp"
            to_list_ref: str - Reference to recipient list (email or list ID)
            subject: str
            body: str
            from_email: Optional[str]
            from_name: Optional[str]
        """
        if action != "email.send":
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Unsupported action: {action}"
            }
        
        provider = params.get("provider", "mailgun")
        to_list_ref = params.get("to_list_ref", "")
        subject = params.get("subject", "")
        body = params.get("body", "")
        from_email = params.get("from_email")
        from_name = params.get("from_name", "Earnetics")
        
        try:
            # Get credentials from vault
            if provider == "mailgun":
                api_key = self.credential_vault.get_secret("mailgun_api_key") if self.credential_vault else os.getenv("MAILGUN_API_KEY")
                domain = self.credential_vault.get_secret("mailgun_domain") if self.credential_vault else os.getenv("MAILGUN_DOMAIN")
                
                if not api_key or not domain:
                    return {
                        "success": False,
                        "data": None,
                        "metadata": {},
                        "citation": {},
                        "error": "Mailgun credentials not configured"
                    }
                
                # Use backend email service if available
                try:
                    from backend.services.email_service import EmailService
                    email_service = EmailService()
                    result = email_service.send_email(
                        to=to_list_ref,
                        subject=subject,
                        body=body,
                        from_email=from_email or f"noreply@{domain}",
                        from_name=from_name
                    )
                    
                    return {
                        "success": True,
                        "data": {
                            "message_id": result.get("message_id", ""),
                            "provider": "mailgun",
                            "to": to_list_ref,
                            "subject": subject
                        },
                        "metadata": {
                            "provider": provider,
                            "sent_at": datetime.utcnow().isoformat()
                        },
                        "citation": self.create_citation(f"mailgun://{domain}", datetime.utcnow().isoformat())
                    }
                except ImportError:
                    # Fallback: Use requests directly
                    import requests
                    response = requests.post(
                        f"https://api.mailgun.net/v3/{domain}/messages",
                        auth=("api", api_key),
                        data={
                            "from": f"{from_name} <{from_email or f'noreply@{domain}'}>",
                            "to": to_list_ref,
                            "subject": subject,
                            "text": body
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "data": {
                                "message_id": result.get("id", ""),
                                "provider": "mailgun",
                                "to": to_list_ref,
                                "subject": subject
                            },
                            "metadata": {
                                "provider": provider,
                                "sent_at": datetime.utcnow().isoformat()
                            },
                            "citation": self.create_citation(f"mailgun://{domain}", datetime.utcnow().isoformat())
                        }
                    else:
                        return {
                            "success": False,
                            "data": None,
                            "metadata": {},
                            "citation": {},
                            "error": f"Mailgun API error: {response.status_code} - {response.text}"
                        }
            
            elif provider == "sendgrid":
                api_key = self.credential_vault.get_secret("sendgrid_api_key") if self.credential_vault else os.getenv("SENDGRID_API_KEY")
                
                if not api_key:
                    return {
                        "success": False,
                        "data": None,
                        "metadata": {},
                        "citation": {},
                        "error": "SendGrid credentials not configured"
                    }
                
                import requests
                response = requests.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{
                            "to": [{"email": to_list_ref}]
                        }],
                        "from": {
                            "email": from_email or "noreply@earnetics.live",
                            "name": from_name
                        },
                        "subject": subject,
                        "content": [{
                            "type": "text/plain",
                            "value": body
                        }]
                    },
                    timeout=10
                )
                
                if response.status_code in [200, 202]:
                    return {
                        "success": True,
                        "data": {
                            "message_id": response.headers.get("X-Message-Id", ""),
                            "provider": "sendgrid",
                            "to": to_list_ref,
                            "subject": subject
                        },
                        "metadata": {
                            "provider": provider,
                            "sent_at": datetime.utcnow().isoformat()
                        },
                        "citation": self.create_citation("sendgrid://api.sendgrid.com", datetime.utcnow().isoformat())
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "metadata": {},
                        "citation": {},
                        "error": f"SendGrid API error: {response.status_code} - {response.text}"
                    }
            
            else:
                return {
                    "success": False,
                    "data": None,
                    "metadata": {},
                    "citation": {},
                    "error": f"Unsupported email provider: {provider}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Email send error: {str(e)}"
            }
