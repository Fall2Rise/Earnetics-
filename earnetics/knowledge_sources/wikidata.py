"""
Wikidata Connector: Tier 1 knowledge source (structured data)
"""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class WikidataSource(KnowledgeSource):
    """Wikidata knowledge source connector for structured data"""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.base_url = "https://www.wikidata.org/w/api.php"
        self.sparql_url = "https://query.wikidata.org/sparql"
        self.rate_limit_per_min = config.get("rate_limit_per_min", 60)
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search Wikidata entities
        
        Returns list of entity references
        """
        try:
            # Use Wikidata search API
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "format": "json",
                "limit": limit
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers={"User-Agent": "Earnetics-Knowledge-Bot/1.0"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("search", [])[:limit]:
                    results.append({
                        "id": item.get("id", ""),
                        "title": item.get("label", query),
                        "description": item.get("description", ""),
                        "url": f"https://www.wikidata.org/wiki/{item.get('id', '')}",
                        "source_id": self.source_id
                    })
                return results
            
            return []
        
        except Exception as e:
            print(f"Wikidata search error: {e}")
            return []
    
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """
        Fetch full Wikidata entity data
        
        Returns KnowledgeRecord with citation
        """
        try:
            entity_id = ref.get("id", "")
            title = ref.get("title", "")
            description = ref.get("description", "")
            
            # Get entity claims (properties)
            params = {
                "action": "wbgetentities",
                "ids": entity_id,
                "props": "labels|descriptions|claims|sitelinks",
                "languages": "en",
                "format": "json"
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers={"User-Agent": "Earnetics-Knowledge-Bot/1.0"},
                timeout=10
            )
            
            entity_data = {}
            if response.status_code == 200:
                data = response.json()
                entities = data.get("entities", {})
                if entity_id in entities:
                    entity_data = entities[entity_id]
            
            # Format content as structured text
            labels = entity_data.get("labels", {}).get("en", {}).get("value", title)
            descriptions = entity_data.get("descriptions", {}).get("en", {}).get("value", description)
            claims = entity_data.get("claims", {})
            
            # Build content summary
            content_parts = [f"Entity: {labels}"]
            if descriptions:
                content_parts.append(f"Description: {descriptions}")
            
            # Add key properties
            if "P31" in claims:  # instance of
                instance_of = []
                for claim in claims["P31"][:3]:
                    mainsnak = claim.get("mainsnak", {})
                    if mainsnak.get("datatype") == "wikibase-item":
                        datavalue = mainsnak.get("datavalue", {})
                        if datavalue:
                            instance_of.append(f"Q{datavalue.get('value', {}).get('numeric-id', '')}")
                if instance_of:
                    content_parts.append(f"Type: {', '.join(instance_of)}")
            
            content_text = "\n".join(content_parts)
            
            entity_url = ref.get("url", f"https://www.wikidata.org/wiki/{entity_id}")
            
            # Create citation
            citation = CitationObject(
                source_id=self.source_id,
                url=entity_url,
                retrieved_at=datetime.utcnow().isoformat(),
                published_at=None,
                provenance=f"{self.__class__.__name__}.fetch",
                confidence=0.90  # Wikidata is highly structured and reliable
            )
            
            # Create knowledge record
            record = KnowledgeRecord(
                id=f"wikidata_{entity_id}",
                source_id=self.source_id,
                tier=self.config.get("tier", 1),
                title=labels or title,
                url=entity_url,
                retrieved_at=datetime.utcnow().isoformat(),
                published_at=None,
                summary=descriptions or description or "",
                content_text=content_text,
                citation=citation,
                trust_score=self.config.get("trust_score", 90),
                tags=["wikidata", "structured_data", "entity"]
            )
            
            return record
        
        except Exception as e:
            print(f"Wikidata fetch error: {e}")
            # Return minimal record
            return KnowledgeRecord(
                id=f"wikidata_{ref.get('id', 'unknown')}",
                source_id=self.source_id,
                tier=self.config.get("tier", 1),
                title=ref.get("title", ""),
                url=ref.get("url", ""),
                retrieved_at=datetime.utcnow().isoformat(),
                summary=ref.get("description", ""),
                content_text=ref.get("description", ""),
                citation=CitationObject(
                    source_id=self.source_id,
                    url=ref.get("url", ""),
                    retrieved_at=datetime.utcnow().isoformat(),
                    provenance=f"{self.__class__.__name__}.fetch",
                    confidence=0.7
                ),
                trust_score=self.config.get("trust_score", 90)
            )
