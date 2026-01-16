"""
Abstract knowledge base interface.
"""

from abc import ABC, abstractmethod
from typing import List

from krop_duster.core.models import Relationship


class KnowledgeBase(ABC):
    """Abstract base class for knowledge sources."""

    @abstractmethod
    def query_relationships(self, concept: str) -> List[Relationship]:
        """
        Query relationships for a concept.

        Args:
            concept: Concept to query

        Returns:
            List of relationships
        """
        pass

    @abstractmethod
    def get_related_entities(self, concept: str, property_name: str) -> List[str]:
        """
        Get entities related to concept via a specific property.

        Args:
            concept: Source concept
            property_name: Property/relationship name

        Returns:
            List of related entity names
        """
        pass
