"""
Named Entity Recognition module.
"""

import logging
from typing import List

from spacy.tokens import Doc

from krop_duster.core.models import EntityType


logger = logging.getLogger(__name__)


# Mapping from spaCy entity types to our EntityType enum
ENTITY_TYPE_MAPPING = {
    "PERSON": EntityType.PERSON,
    "ORG": EntityType.ORGANIZATION,
    "PRODUCT": EntityType.PRODUCT,
    "WORK_OF_ART": EntityType.WORK_OF_ART,
    "GPE": EntityType.PLACE,
    "LOC": EntityType.PLACE,
    "FAC": EntityType.PLACE,
    "NORP": EntityType.ABSTRACT_CONCEPT,
    "EVENT": EntityType.ABSTRACT_CONCEPT,
    "LAW": EntityType.ABSTRACT_CONCEPT,
}


class NERExtractor:
    """Extract named entities from text."""

    def __init__(self):
        """Initialize the NER extractor."""
        pass

    def extract_entities(self, doc: Doc) -> List[dict]:
        """
        Extract named entities from spaCy Doc.

        Args:
            doc: spaCy Doc object

        Returns:
            List of entity dictionaries
        """
        entities = []

        for ent in doc.ents:
            entity_type = ENTITY_TYPE_MAPPING.get(ent.label_, EntityType.OTHER)

            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "entity_type": entity_type,
                "start": ent.start_char,
                "end": ent.end_char,
            })

        logger.debug(f"Extracted {len(entities)} named entities")
        return entities

    def extract_character_entities(self, text: str, entities: List[dict]) -> List[dict]:
        """
        Extract fictional character entities (simplified version).

        This is a basic implementation that could be enhanced with
        a character database lookup.

        Args:
            text: Original text
            entities: Existing entities

        Returns:
            Enhanced entity list with character entities
        """
        # Common character indicators
        character_indicators = [
            "character",
            "fictional",
            "superhero",
            "cartoon",
            "anime",
            "manga",
        ]

        # Check if any person entity is mentioned with character indicators
        enhanced_entities = entities.copy()

        for entity in entities:
            if entity["entity_type"] == EntityType.PERSON:
                text_lower = text.lower()
                # Simple heuristic: if "character" appears near the entity name
                if any(indicator in text_lower for indicator in character_indicators):
                    entity["is_character"] = True

        return enhanced_entities

    def get_entity_semantic_role(self, doc: Doc, entity_start: int, entity_end: int) -> str:
        """
        Determine semantic role of entity in sentence.

        Args:
            doc: spaCy Doc object
            entity_start: Entity start character index
            entity_end: Entity end character index

        Returns:
            Semantic role (subject, object, action, modifier, unknown)
        """
        # Find the span corresponding to this entity
        for token in doc:
            if token.idx == entity_start:
                # Check dependency role
                if token.dep_ in ["nsubj", "nsubjpass"]:
                    return "subject"
                elif token.dep_ in ["dobj", "pobj", "attr"]:
                    return "object"
                elif token.dep_ in ["ROOT"] and token.pos_ == "VERB":
                    return "action"
                elif token.dep_ in ["amod", "advmod"]:
                    return "modifier"

        return "unknown"
