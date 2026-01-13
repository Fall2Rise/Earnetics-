"""
Wikipedia Connector: Tier 1 knowledge source
"""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class WikipediaSource(KnowledgeSource):
    """Wikipedia knowledge source connector"""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.rate_limit_per_min = config.get("rate_limit_per_min", 60)
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search Wikipedia articles
        
        Returns list of article references
        """
        try:
            # Use Wikipedia API search
            search_url = f"{self.base_url}/page/summary/{query.replace(' ', '_')}"
            
            response = requests.get(
                search_url,
                headers={"User-Agent": "Earnetics-Knowledge-Bot/1.0"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return [{
                    "id": data.get("pageid", ""),
                    "title": data.get("title", query),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "summary": data.get("extract", ""),
                    "source_id": self.source_id
                }]
            else:
                # Try search endpoint
                search_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                    "srlimit": limit
                }
                
                response = requests.get(search_url, params=params, timeout=10)
                if response.status_code == 200:
                    results = []
                    data = response.json()
                    for item in data.get("query", {}).get("search", [])[:limit]:
                        results.append({
                            "id": str(item.get("pageid", "")),
                            "title": item.get("title", ""),
                            "url": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                            "summary": item.get("snippet", ""),
                            "source_id": self.source_id
                        })
                    return results
                
                return []
        
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """
        Fetch full Wikipedia article
        
        Returns KnowledgeRecord with citation
        """
        try:
            title = ref.get("title", "")
            page_id = ref.get("id", "")
            
            # Get full article
            if page_id:
                url = f"{self.base_url}/page/html/{title.replace(' ', '_')}"
            else:
                url = f"{self.base_url}/page/html/{title.replace(' ', '_')}"
            
            response = requests.get(
                url,
                headers={"User-Agent": "Earnetics-Knowledge-Bot/1.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                content_text = response.text
                
                # Also get summary
                summary_url = f"{self.base_url}/page/summary/{title.replace(' ', '_')}"
                summary_response = requests.get(summary_url, timeout=10)
                summary = ""
                if summary_response.status_code == 200:
                    summary = summary_response.json().get("extract", "")
            else:
                # Fallback to summary only
                summary_url = f"{self.base_url}/page/summary/{title.replace(' ', '_')}"
                summary_response = requests.get(summary_url, timeout=10)
                if summary_response.status_code == 200:
                    data = summary_response.json()
                    content_text = data.get("extract", "")
                    summary = content_text[:500]
                else:
                    content_text = ref.get("summary", "")
                    summary = content_text
            
            article_url = ref.get("url", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
            
            # Create citation
            citation = CitationObject(
                source_id=self.source_id,
                url=article_url,
                retrieved_at=datetime.utcnow().isoformat(),
                published_at=None,  # Wikipedia articles don't have single publish date
                provenance=f"{self.__class__.__name__}.fetch",
                confidence=0.85
            )
            
            # Create knowledge record
            record = KnowledgeRecord(
                id=f"wikipedia_{page_id or title.replace(' ', '_')}",
                source_id=self.source_id,
                tier=self.config.get("tier", 1),
                title=title,
                url=article_url,
                retrieved_at=datetime.utcnow().isoformat(),
                published_at=None,
                summary=summary[:500] if summary else "",
                content_text=content_text[:50000],  # Limit content size
                citation=citation,
                trust_score=self.config.get("trust_score", 85),
                tags=["wikipedia", "encyclopedia"]
            )
            
            return record
        
        except Exception as e:
            print(f"Wikipedia fetch error: {e}")
            # Return minimal record
            return KnowledgeRecord(
                id=f"wikipedia_{ref.get('id', 'unknown')}",
                source_id=self.source_id,
                tier=self.config.get("tier", 1),
                title=ref.get("title", ""),
                url=ref.get("url", ""),
                retrieved_at=datetime.utcnow().isoformat(),
                summary=ref.get("summary", ""),
                content_text=ref.get("summary", ""),
                citation=CitationObject(
                    source_id=self.source_id,
                    url=ref.get("url", ""),
                    retrieved_at=datetime.utcnow().isoformat(),
                    provenance=f"{self.__class__.__name__}.fetch",
                    confidence=0.7
                ),
                trust_score=self.config.get("trust_score", 85)
            )
