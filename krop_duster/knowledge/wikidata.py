"""
Wikidata SPARQL query integration.
"""

import logging
from typing import List, Optional

from SPARQLWrapper import JSON, SPARQLWrapper

from krop_duster.core.models import Relationship
from krop_duster.knowledge.knowledge_base import KnowledgeBase


logger = logging.getLogger(__name__)


class WikidataKnowledgeBase(KnowledgeBase):
    """Knowledge base using Wikidata SPARQL queries."""

    def __init__(self, endpoint: str = "https://query.wikidata.org/sparql"):
        """
        Initialize Wikidata knowledge base.

        Args:
            endpoint: SPARQL endpoint URL
        """
        self.endpoint = endpoint
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        logger.info(f"Initialized Wikidata knowledge base: {endpoint}")

    def query_relationships(self, concept: str) -> List[Relationship]:
        """
        Query Wikidata for relationships related to concept.

        Args:
            concept: Concept to query

        Returns:
            List of relationships
        """
        relationships = []

        try:
            # Query for entity ID first
            entity_id = self._find_entity_id(concept)

            if not entity_id:
                logger.debug(f"No Wikidata entity found for: {concept}")
                return relationships

            # Query for properties and values
            query = f"""
            SELECT ?propertyLabel ?valueLabel WHERE {{
              wd:{entity_id} ?property ?value .
              ?prop wikibase:directClaim ?property .
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
              }}
              FILTER(isIRI(?value))
            }}
            LIMIT 50
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            for result in results["results"]["bindings"]:
                prop = result.get("propertyLabel", {}).get("value", "")
                val = result.get("valueLabel", {}).get("value", "")

                if prop and val:
                    # Score based on relevance (simplified)
                    score = self._score_relationship(prop, val)

                    relationships.append(
                        Relationship(
                            property=prop,
                            value=val,
                            score=score,
                            source="wikidata",
                        )
                    )

            logger.info(
                f"Retrieved {len(relationships)} relationships for '{concept}' from Wikidata"
            )

        except Exception as e:
            logger.error(f"Wikidata query failed for '{concept}': {e}")

        return relationships

    def get_related_entities(self, concept: str, property_name: str) -> List[str]:
        """
        Get entities related via a specific property.

        Args:
            concept: Source concept
            property_name: Property name

        Returns:
            List of related entity names
        """
        entities = []

        try:
            entity_id = self._find_entity_id(concept)
            if not entity_id:
                return entities

            # Find property ID
            property_id = self._find_property_id(property_name)
            if not property_id:
                return entities

            query = f"""
            SELECT ?valueLabel WHERE {{
              wd:{entity_id} wdt:{property_id} ?value .
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
              }}
            }}
            LIMIT 10
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            for result in results["results"]["bindings"]:
                value = result.get("valueLabel", {}).get("value", "")
                if value:
                    entities.append(value)

        except Exception as e:
            logger.error(f"Failed to get related entities: {e}")

        return entities

    def _find_entity_id(self, concept: str) -> Optional[str]:
        """
        Find Wikidata entity ID for concept.

        Args:
            concept: Concept text

        Returns:
            Entity ID (e.g., 'Q123') or None
        """
        try:
            query = f"""
            SELECT ?item WHERE {{
              ?item rdfs:label "{concept}"@en .
            }}
            LIMIT 1
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            if results["results"]["bindings"]:
                uri = results["results"]["bindings"][0]["item"]["value"]
                # Extract ID from URI (e.g., http://www.wikidata.org/entity/Q123 -> Q123)
                entity_id = uri.split("/")[-1]
                logger.debug(f"Found entity ID {entity_id} for '{concept}'")
                return entity_id

        except Exception as e:
            logger.debug(f"Failed to find entity ID for '{concept}': {e}")

        return None

    def _find_property_id(self, property_name: str) -> Optional[str]:
        """
        Find Wikidata property ID for property name.

        Args:
            property_name: Property name

        Returns:
            Property ID (e.g., 'P31') or None
        """
        # Common property mappings
        common_properties = {
            "instance of": "P31",
            "creator": "P170",
            "author": "P50",
            "country": "P17",
            "occupation": "P106",
            "part of": "P361",
            "owned by": "P127",
            "manufacturer": "P176",
            "genre": "P136",
        }

        prop_lower = property_name.lower()
        if prop_lower in common_properties:
            return common_properties[prop_lower]

        # Try to query for property
        try:
            query = f"""
            SELECT ?property WHERE {{
              ?property rdfs:label "{property_name}"@en .
              ?property a wikibase:Property .
            }}
            LIMIT 1
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            if results["results"]["bindings"]:
                uri = results["results"]["bindings"][0]["property"]["value"]
                property_id = uri.split("/")[-1]
                return property_id

        except Exception as e:
            logger.warning(f"Failed to find property ID for '{property_name}': {e}")

        return None

    def _score_relationship(self, property_name: str, value: str) -> float:
        """
        Score relationship relevance for obfuscation.

        Args:
            property_name: Property name
            value: Property value

        Returns:
            Relevance score (0-1)
        """
        # Properties useful for obfuscation
        high_value_properties = [
            "creator",
            "author",
            "instance of",
            "occupation",
            "known for",
            "part of",
            "owned by",
            "manufacturer",
            "country",
            "genre",
            "first appearance",
        ]

        prop_lower = property_name.lower()

        if any(hvp in prop_lower for hvp in high_value_properties):
            return 0.9

        # Medium value properties
        if any(
            keyword in prop_lower
            for keyword in ["date", "time", "location", "member"]
        ):
            return 0.6

        # Default score
        return 0.4
