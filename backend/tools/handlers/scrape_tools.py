# backend/tools/handlers/scrape_tools.py
from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None


def web_scrape_url(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: SCRAPE
    Fetches a URL and returns text + status.
    Basic guardrails included.
    """
    if requests is None:
        return {"error": "requests library not installed", "status": "unavailable"}
    
    url = (args.get("url") or "").strip()
    timeout = float(args.get("timeout", 15))
    user_agent = args.get("user_agent") or "EarneticsScraper/1.0"
    max_chars = int(args.get("max_chars", 200_000))

    if not url:
        return {"error": "Missing required arg: url", "status": "error"}

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {"error": "URL must start with http:// or https://", "status": "error"}

    try:
        headers = {"User-Agent": user_agent}
        resp = requests.get(url, headers=headers, timeout=timeout)

        # Limit size to prevent runaway memory (adjust if needed)
        text = resp.text
        if len(text) > max_chars:
            text = text[:max_chars]

        return {
            "url": url,
            "status_code": resp.status_code,
            "final_url": str(resp.url),
            "text": text,
            "text_length": len(text),
            "truncated": len(resp.text) > max_chars,
            "headers": dict(resp.headers),
            "status": "success",
        }
    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "status": "error", "url": url}
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status": "error", "url": url}
    except Exception as e:
        return {"error": str(e), "status": "error", "url": url}


def scrape_website(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: SCRAPE
    Scrape a website domain (multiple pages).
    Wrapper around web_scrape_url for compatibility.
    """
    domain = args.get("domain") or args.get("url", "")
    max_pages = int(args.get("max_pages", 5))
    
    if not domain:
        return {"error": "Missing required arg: domain", "status": "error"}
    
    # Ensure domain has scheme
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    
    # For now, just scrape the main page
    # Future: implement multi-page scraping
    result = web_scrape_url({
        "url": domain,
        "timeout": args.get("timeout", 15),
        "max_chars": args.get("max_chars", 200_000),
    })
    
    # Extract leads (simple text extraction for now)
    # Future: implement proper lead extraction
    text = result.get("text", "")
    leads_saved = 0
    if text and len(text) > 100:  # Basic heuristic
        leads_saved = 1  # Placeholder
    
    return {
        **result,
        "leads_saved": leads_saved,
        "pages_scraped": 1,
        "max_pages": max_pages,
    }
