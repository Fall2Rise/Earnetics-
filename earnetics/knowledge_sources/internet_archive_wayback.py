"""
Internet Archive Wayback Machine connector with proper citations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import re
from urllib.parse import quote, urlparse

from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class WaybackSource(KnowledgeSource):
    """Internet Archive Wayback Machine connector with snapshot citations"""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.cdx_api = "https://web.archive.org/cdx/search/cdx"
        self.wayback_api = "https://web.archive.org/web"
    
    def search(self, query: str, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """Search Wayback for snapshots of a URL or query"""
        results = []
        
        # If query looks like a URL, search for snapshots
        if query.startswith("http://") or query.startswith("https://"):
            return self._search_snapshots(query, limit)
        
        # Otherwise, use CDX API to find URLs matching query
        try:
            params = {
                "url": query,
                "output": "json",
                "limit": limit
            }
            response = requests.get(self.cdx_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:  # First row is headers
                    for row in data[1:limit+1]:
                        if len(row) >= 3:
                            timestamp = row[1]
                            original_url = row[2]
                            wayback_url = f"{self.wayback_api}/{timestamp}/{original_url}"
                            
                            results.append({
                                "id": f"wayback_{timestamp}_{hash(original_url)}",
                                "title": f"Snapshot: {original_url}",
                                "url": original_url,
                                "wayback_url": wayback_url,
                                "timestamp": timestamp,
                                "summary": f"Archived snapshot from {self._format_timestamp(timestamp)}"
                            })
        except Exception as e:
            print(f"Error searching Wayback: {e}")
        
        return results
    
    def _search_snapshots(self, url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for snapshots of a specific URL"""
        results = []
        try:
            params = {
                "url": url,
                "output": "json",
                "limit": limit,
                "collapse": "timestamp:8"  # One per day
            }
            response = requests.get(self.cdx_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    for row in data[1:limit+1]:
                        if len(row) >= 3:
                            timestamp = row[1]
                            original_url = row[2]
                            wayback_url = f"{self.wayback_api}/{timestamp}/{original_url}"
                            
                            results.append({
                                "id": f"wayback_{timestamp}_{hash(original_url)}",
                                "title": f"Snapshot: {original_url}",
                                "url": original_url,
                                "wayback_url": wayback_url,
                                "timestamp": timestamp,
                                "summary": f"Archived snapshot from {self._format_timestamp(timestamp)}"
                            })
        except Exception as e:
            print(f"Error searching snapshots: {e}")
        
        return results
    
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """Fetch snapshot content with proper citation"""
        wayback_url = ref.get("wayback_url")
        original_url = ref.get("url")
        timestamp = ref.get("timestamp")
        
        if not wayback_url and timestamp and original_url:
            wayback_url = f"{self.wayback_api}/{timestamp}/{original_url}"
        
        if not wayback_url:
            raise ValueError("Wayback URL or timestamp required")
        
        try:
            response = requests.get(wayback_url, timeout=30, headers={
                "User-Agent": "Earnetics-Knowledge-Bot/1.0"
            })
            response.raise_for_status()
            
            # Extract text content (simple HTML stripping)
            content_text = self._extract_text(response.text)
            
            # Create citation with snapshot info
            citation = self.create_citation(
                url=original_url or wayback_url,
                retrieved_at=datetime.utcnow().isoformat(),
                snapshot={
                    "timestamp": timestamp or self._extract_timestamp(wayback_url),
                    "wayback_url": wayback_url
                }
            )
            
            record_id = KnowledgeRecord.create_id(
                self.source_id,
                wayback_url,
                datetime.utcnow().isoformat()
            )
            
            return KnowledgeRecord(
                id=record_id,
                source_id=self.source_id,
                tier=self.tier,
                title=ref.get("title", f"Wayback Snapshot: {original_url}"),
                url=original_url or wayback_url,
                retrieved_at=datetime.utcnow().isoformat(),
                summary=content_text[:500] if content_text else "",
                content_text=content_text,
                citation=citation,
                trust_score=self.trust_score,
                raw={
                    "wayback_url": wayback_url,
                    "timestamp": timestamp or self._extract_timestamp(wayback_url)
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to fetch Wayback snapshot: {e}")
    
    def _extract_text(self, html: str) -> str:
        """Simple HTML text extraction"""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text from common tags
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format Wayback timestamp (YYYYMMDDhhmmss) to readable date"""
        if len(timestamp) >= 8:
            year = timestamp[0:4]
            month = timestamp[4:6]
            day = timestamp[6:8]
            return f"{year}-{month}-{day}"
        return timestamp
    
    def _extract_timestamp(self, wayback_url: str) -> str:
        """Extract timestamp from Wayback URL"""
        match = re.search(r'/web/(\d{14})/', wayback_url)
        if match:
            return match.group(1)
        return datetime.utcnow().strftime("%Y%m%d%H%M%S")
