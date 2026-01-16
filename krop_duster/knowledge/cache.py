"""
Caching system for knowledge base queries.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from krop_duster.core.models import Relationship
from krop_duster.core.utils import hash_text


logger = logging.getLogger(__name__)


class KnowledgeCache:
    """Cache for knowledge base query results."""

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl_days: int = 7,
    ):
        """
        Initialize knowledge cache.

        Args:
            cache_dir: Directory for cache files
            ttl_days: Time-to-live for cache entries in days
        """
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "knowledge_cache",
            )

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)

        logger.info(f"Initialized knowledge cache at {self.cache_dir}")

    def get(self, concept: str, source: str) -> Optional[List[Relationship]]:
        """
        Get cached relationships for a concept.

        Args:
            concept: Concept key
            source: Knowledge source (e.g., 'wikidata')

        Returns:
            List of relationships or None if not cached/expired
        """
        cache_key = self._get_cache_key(concept, source)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for {concept} ({source})")
                return None

            # Deserialize relationships
            relationships = []
            for rel_data in data["relationships"]:
                relationships.append(
                    Relationship(
                        property=rel_data["property"],
                        value=rel_data["value"],
                        score=rel_data["score"],
                        source=rel_data["source"],
                    )
                )

            logger.debug(f"Cache hit for {concept} ({source})")
            return relationships

        except Exception as e:
            logger.warning(f"Failed to load cache for {concept}: {e}")
            return None

    def set(
        self,
        concept: str,
        source: str,
        relationships: List[Relationship],
    ) -> None:
        """
        Cache relationships for a concept.

        Args:
            concept: Concept key
            source: Knowledge source
            relationships: Relationships to cache
        """
        cache_key = self._get_cache_key(concept, source)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            # Serialize relationships
            rel_data = []
            for rel in relationships:
                rel_data.append({
                    "property": rel.property,
                    "value": rel.value,
                    "score": rel.score,
                    "source": rel.source,
                })

            data = {
                "concept": concept,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "relationships": rel_data,
            }

            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Cached {len(relationships)} relationships for {concept}")

        except Exception as e:
            logger.warning(f"Failed to cache relationships for {concept}: {e}")

    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cleared knowledge cache")

    def _get_cache_key(self, concept: str, source: str) -> str:
        """
        Generate cache key for concept and source.

        Args:
            concept: Concept text
            source: Knowledge source

        Returns:
            Cache key
        """
        # Use hash to create filename-safe key
        concept_hash = hash_text(concept.lower())
        return f"{source}_{concept_hash}"
