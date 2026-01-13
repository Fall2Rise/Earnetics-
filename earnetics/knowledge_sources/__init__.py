"""Knowledge source connectors"""
from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_sources.internal_vault import InternalVaultSource
from earnetics.knowledge_sources.internet_archive_wayback import WaybackSource
from earnetics.knowledge_sources.wikipedia import WikipediaSource
from earnetics.knowledge_sources.wikidata import WikidataSource

__all__ = [
    "KnowledgeSource",
    "InternalVaultSource",
    "WaybackSource",
    "WikipediaSource",
    "WikidataSource"
]
