"""
Web Tools: Agent-facing API for internet gateway
Agents call these functions instead of direct network requests
"""
from typing import Dict, Any, Optional, List
from pathlib import Path

from earnetics.gateway.internet_gateway import InternetGateway


# Global gateway instance (singleton)
_gateway_instance: Optional[InternetGateway] = None


def get_gateway() -> InternetGateway:
    """Get or create gateway instance"""
    global _gateway_instance
    if _gateway_instance is None:
        config_path = Path(__file__).parent.parent / "config" / "internet_gateway.json"
        _gateway_instance = InternetGateway(config_path)
    return _gateway_instance


# READ OPERATIONS

def web_search(query: str, recency_days: Optional[int] = None,
              sources_hint: Optional[List[str]] = None,
              agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Search the web (uses internal knowledge router by default)
    
    Returns: {
        "success": bool,
        "results": List[Dict],
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="web.search",
        params={
            "query": query,
            "recency_days": recency_days,
            "sources_hint": sources_hint
        }
    )
    
    if result["success"]:
        return {
            "success": True,
            "results": result.get("data", {}).get("results", []),
            "total": result.get("data", {}).get("total", 0),
            "citation": result.get("citation", {})
        }
    else:
        return {
            "success": False,
            "results": [],
            "total": 0,
            "error": result.get("error") or result.get("policy_reason")
        }


def web_fetch(url: str, agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Fetch content from URL (read-only)
    
    Returns: {
        "success": bool,
        "text": str,
        "metadata": Dict,
        "citation": Dict,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="web.fetch",
        params={"url": url}
    )
    
    if result["success"]:
        data = result.get("data", {})
        return {
            "success": True,
            "text": data.get("text", ""),
            "url": data.get("url", url),
            "status_code": data.get("status_code"),
            "metadata": result.get("metadata", {}),
            "citation": result.get("citation", {})
        }
    else:
        return {
            "success": False,
            "text": "",
            "url": url,
            "metadata": {},
            "citation": {},
            "error": result.get("error") or result.get("policy_reason")
        }


def web_render_fetch(url: str, agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Fetch content using browser rendering (Playwright - optional)
    
    Returns: Same as web_fetch
    """
    # For MVP, fallback to regular fetch
    # Playwright adapter can be added later
    return web_fetch(url, agent_id, role)


def web_head(url: str, agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Fetch HEAD request (metadata only)
    
    Returns: {
        "success": bool,
        "status_code": int,
        "headers": Dict,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="web.head",
        params={"url": url}
    )
    
    if result["success"]:
        data = result.get("data", {})
        return {
            "success": True,
            "status_code": data.get("status_code"),
            "headers": result.get("metadata", {}).get("headers", {}),
            "url": data.get("url", url)
        }
    else:
        return {
            "success": False,
            "status_code": None,
            "headers": {},
            "error": result.get("error") or result.get("policy_reason")
        }


# RESTRICTED OPERATIONS

def web_download(url: str, quarantine: bool = True,
                agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Download file (restricted, requires permissions)
    
    Returns: {
        "success": bool,
        "file_ref": str,
        "quarantine_path": str,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="web.download",
        params={"url": url, "quarantine": quarantine}
    )
    
    if result["success"]:
        return {
            "success": True,
            "file_ref": result.get("data", {}).get("file_ref", ""),
            "quarantine_path": result.get("data", {}).get("quarantine_path", "")
        }
    else:
        return {
            "success": False,
            "file_ref": "",
            "quarantine_path": "",
            "error": result.get("error") or result.get("policy_reason")
        }


# WRITE OPERATIONS (require approval tokens)

def social_post(platform: str, content: str, media_refs: Optional[List[str]] = None,
               approval_token: Optional[str] = None,
               agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Post to social media (write operation, requires approval)
    
    Returns: {
        "success": bool,
        "post_id": str,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="social.post",
        params={
            "platform": platform,
            "content": content,
            "media_refs": media_refs or []
        },
        approval_token=approval_token
    )
    
    if result["success"]:
        return {
            "success": True,
            "post_id": result.get("data", {}).get("post_id", ""),
            "platform": platform
        }
    else:
        return {
            "success": False,
            "post_id": "",
            "error": result.get("error") or result.get("policy_reason")
        }


def email_send(provider: str, to_list_ref: str, subject: str, body: str,
              approval_token: Optional[str] = None,
              agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Send email (write operation, requires approval)
    
    Returns: {
        "success": bool,
        "message_id": str,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="email.send",
        params={
            "provider": provider,
            "to_list_ref": to_list_ref,
            "subject": subject,
            "body": body
        },
        approval_token=approval_token
    )
    
    if result["success"]:
        return {
            "success": True,
            "message_id": result.get("data", {}).get("message_id", "")
        }
    else:
        return {
            "success": False,
            "message_id": "",
            "error": result.get("error") or result.get("policy_reason")
        }


def stripe_call(endpoint: str, method: str, payload: Dict[str, Any],
                approval_token: Optional[str] = None,
                agent_id: str = "system", role: str = "DEFAULT") -> Dict[str, Any]:
    """
    Call Stripe API (write operation, requires approval)
    
    Returns: {
        "success": bool,
        "data": Any,
        "error": Optional[str]
    }
    """
    gateway = get_gateway()
    
    result = gateway.execute(
        agent_id=agent_id,
        role=role,
        action="stripe.write" if method != "GET" else "stripe.read",
        params={
            "endpoint": endpoint,
            "method": method,
            "payload": payload
        },
        approval_token=approval_token
    )
    
    if result["success"]:
        return {
            "success": True,
            "data": result.get("data", {})
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": result.get("error") or result.get("policy_reason")
        }
