"""
HTTP Reader Adapter: Read-only HTTP requests with allowlist/rate limiting
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

from earnetics.gateway.adapters.base_adapter import BaseAdapter


class HTTPReaderAdapter(BaseAdapter):
    """HTTP reader adapter for web.fetch and web.head"""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        super().__init__(config, credential_vault)
        adapter_config = config.get("adapters", {}).get("http_reader", {})
        self.user_agent = adapter_config.get("user_agent", "Earnetics-Knowledge-Bot/1.0")
        self.max_content_size = adapter_config.get("max_content_size_bytes", 10485760)  # 10MB
        self.follow_redirects = adapter_config.get("follow_redirects", True)
        self.max_redirects = adapter_config.get("max_redirects", 5)
        self.timeout = config.get("default_timeout_seconds", 25)
    
    def execute(self, action: str, params: Dict[str, Any],
               agent_id: str, role: str) -> Dict[str, Any]:
        """Execute HTTP read action"""
        url = params.get("url")
        if not url:
            return {
                "success": False,
                "error": "URL parameter required",
                "data": None,
                "metadata": {},
                "citation": {}
            }
        
        try:
            if action == "web.fetch":
                return self._fetch(url, params)
            elif action == "web.head":
                return self._head(url, params)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported action: {action}",
                    "data": None,
                    "metadata": {},
                    "citation": {}
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "metadata": {},
                "citation": {}
            }
    
    def _fetch(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch full content from URL"""
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=self.follow_redirects,
                stream=True  # Stream to check size
            )
            response.raise_for_status()
            
            # Check content size
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_content_size:
                return {
                    "success": False,
                    "error": f"Content too large: {content_length} bytes (max: {self.max_content_size})",
                    "data": None,
                    "metadata": {},
                    "citation": {}
                }
            
            # Read content (with size limit)
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_content_size:
                    return {
                        "success": False,
                        "error": f"Content exceeds size limit: {self.max_content_size} bytes",
                        "data": None,
                        "metadata": {},
                        "citation": {}
                    }
            
            text_content = content.decode('utf-8', errors='ignore')
            
            citation = self.create_citation(url)
            
            return {
                "success": True,
                "data": {
                    "text": text_content,
                    "url": url,
                    "status_code": response.status_code
                },
                "metadata": {
                    "content_type": response.headers.get("Content-Type", ""),
                    "content_length": len(content),
                    "final_url": response.url,
                    "encoding": response.encoding
                },
                "citation": citation,
                "error": None
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timeout after {self.timeout} seconds",
                "data": None,
                "metadata": {},
                "citation": {}
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}",
                "data": None,
                "metadata": {},
                "citation": {}
            }
    
    def _head(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch HEAD request (metadata only)"""
        try:
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.head(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=self.follow_redirects
            )
            
            citation = self.create_citation(url)
            
            return {
                "success": True,
                "data": {
                    "status_code": response.status_code,
                    "url": url
                },
                "metadata": {
                    "headers": dict(response.headers),
                    "final_url": response.url
                },
                "citation": citation,
                "error": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"HTTP HEAD error: {str(e)}",
                "data": None,
                "metadata": {},
                "citation": {}
            }
