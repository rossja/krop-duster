"""
Priority scoring module for concepts.
"""

import logging
from typing import Dict, List

from krop_duster.core.models import EntityType, ViolationType


logger = logging.getLogger(__name__)


class PriorityScorer:
    """Calculate priority scores for concepts."""

    def __init__(self):
        """Initialize the priority scorer."""
        pass

    def calculate_priority_score(
        self,
        entity_type: EntityType,
        violations: Dict[ViolationType, List[dict]],
        filter_likelihood: float,
        semantic_role: str,
    ) -> float:
        """
        Calculate priority score for a concept.

        Priority score formula:
        priority = (violation_severity * 0.4) +
                   (filter_likelihood * 0.3) +
                   (semantic_importance * 0.2) +
                   (1 - obfuscation_difficulty) * 0.1

        Args:
            entity_type: Type of entity
            violations: Dictionary of violations
            filter_likelihood: Likelihood of being filtered (0-1)
            semantic_role: Semantic role in sentence

        Returns:
            Priority score (0-1)
        """
        # Calculate violation severity
        violation_severity = self._calculate_violation_severity(violations)

        # Calculate semantic importance
        semantic_importance = self._calculate_semantic_importance(
            entity_type, semantic_role
        )

        # Calculate obfuscation difficulty (lower is easier)
        obfuscation_difficulty = self._calculate_obfuscation_difficulty(entity_type)

        # Apply formula
        priority_score = (
            violation_severity * 0.4
            + filter_likelihood * 0.3
            + semantic_importance * 0.2
            + (1 - obfuscation_difficulty) * 0.1
        )

        # Clamp to [0, 1]
        priority_score = max(0.0, min(1.0, priority_score))

        return priority_score

    def _calculate_violation_severity(
        self, violations: Dict[ViolationType, List[dict]]
    ) -> float:
        """
        Calculate violation severity score.

        Args:
            violations: Dictionary of violations

        Returns:
            Severity score (0-1)
        """
        if not violations:
            return 0.0

        severity_weights = {
            ViolationType.CBRN: 1.0,
            ViolationType.VIOLENCE_HARM: 0.95,
            ViolationType.ILLEGAL_ACTIVITY: 0.95,
            ViolationType.TOXICITY: 0.9,
            ViolationType.NSFW: 0.9,
            ViolationType.NSFW_LANGUAGE: 0.88,
            ViolationType.PROFANITY: 0.85,
            ViolationType.TRADEMARK: 0.85,
            ViolationType.COPYRIGHT: 0.85,
            ViolationType.CONTENT_POLICY: 0.8,
            ViolationType.BRAND_SAFETY: 0.75,
            ViolationType.AGE_INAPPROPRIATE: 0.7,
        }

        max_severity = 0.0

        for violation_type, violation_list in violations.items():
            if violation_list:
                severity = severity_weights.get(violation_type, 0.5)
                max_severity = max(max_severity, severity)

        return max_severity

    def _calculate_semantic_importance(
        self, entity_type: EntityType, semantic_role: str
    ) -> float:
        """
        Calculate semantic importance of concept.

        Args:
            entity_type: Type of entity
            semantic_role: Semantic role in sentence

        Returns:
            Importance score (0-1)
        """
        # Role-based importance
        role_scores = {
            "subject": 1.0,
            "object": 0.9,
            "action": 0.95,
            "modifier": 0.6,
            "unknown": 0.5,
        }

        role_score = role_scores.get(semantic_role, 0.5)

        # Entity type importance
        entity_scores = {
            EntityType.PERSON: 0.9,
            EntityType.ORGANIZATION: 0.85,
            EntityType.PRODUCT: 0.85,
            EntityType.WORK_OF_ART: 0.9,
            EntityType.ACTION: 0.95,
            EntityType.PLACE: 0.7,
            EntityType.ABSTRACT_CONCEPT: 0.75,
            EntityType.TABOO_WORD: 0.9,  # High importance - likely to trigger filters
            EntityType.CULTURAL_REFERENCE: 0.85,  # High importance - copyright concerns
            EntityType.OTHER: 0.5,
        }

        entity_score = entity_scores.get(entity_type, 0.5)

        # Combine (weighted average)
        importance = role_score * 0.6 + entity_score * 0.4

        return importance

    def _calculate_obfuscation_difficulty(self, entity_type: EntityType) -> float:
        """
        Calculate obfuscation difficulty.

        Lower score = easier to obfuscate (better for priority)

        Args:
            entity_type: Type of entity

        Returns:
            Difficulty score (0-1)
        """
        difficulty_scores = {
            EntityType.PERSON: 0.3,  # Easy: many relationships
            EntityType.ORGANIZATION: 0.3,  # Easy: many relationships
            EntityType.PRODUCT: 0.4,  # Medium: some relationships
            EntityType.WORK_OF_ART: 0.35,  # Medium-easy: creator, genre, etc.
            EntityType.PLACE: 0.4,  # Medium: location, features
            EntityType.ACTION: 0.5,  # Medium: can use metaphor, functional
            EntityType.ABSTRACT_CONCEPT: 0.6,  # Harder: fewer concrete relationships
            EntityType.TABOO_WORD: 0.4,  # Medium: use euphemisms, metaphors
            EntityType.CULTURAL_REFERENCE: 0.35,  # Medium-easy: Wikidata relationships available
            EntityType.OTHER: 0.7,  # Hardest: unknown type
        }

        return difficulty_scores.get(entity_type, 0.7)
