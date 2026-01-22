"""
Quality scoring for obfuscation variants.

The quality score is a composite metric (0-1) that estimates the effectiveness
of an obfuscation based on:
- Semantic similarity (40%): How well the obfuscation preserves meaning
- Token efficiency (20%): Whether the length is appropriate (not too short/verbose)
- Relationship quality (20%): How many knowledge graph relationships were used
- Naturalness (20%): Basic heuristics for natural-sounding text
"""

import logging
from typing import List

import numpy as np

from krop_duster.tokenization.tokenizer_manager import TokenizerManager


logger = logging.getLogger(__name__)


class QualityScorer:
    """Calculate quality scores for obfuscation variants."""

    def __init__(self, tokenizer_manager: TokenizerManager):
        """
        Initialize quality scorer.

        Args:
            tokenizer_manager: Tokenizer manager instance
        """
        self.tokenizer = tokenizer_manager

    def calculate_score(
        self,
        original: str,
        obfuscated: str,
        semantic_similarity: float,
        relationships_used: List[str],
    ) -> float:
        """
        Calculate quality score for an obfuscation.

        Score is based on:
        - Semantic similarity (40%)
        - Token efficiency (20%)
        - Relationship quality (20%)
        - Naturalness (20%)

        Args:
            original: Original concept text
            obfuscated: Obfuscated text
            semantic_similarity: Semantic similarity score (0-1)
            relationships_used: List of relationships used

        Returns:
            Quality score (0-1)
        """
        # 1. Semantic similarity (already provided)
        semantic_score = semantic_similarity

        # 2. Token efficiency
        efficiency_score = self._calculate_efficiency(original, obfuscated)

        # 3. Relationship quality
        relationship_score = self._calculate_relationship_score(relationships_used)

        # 4. Naturalness (simplified)
        naturalness_score = self._calculate_naturalness(obfuscated)

        # Weighted combination
        quality_score = (
            semantic_score * 0.4
            + efficiency_score * 0.2
            + relationship_score * 0.2
            + naturalness_score * 0.2
        )

        return min(1.0, max(0.0, quality_score))

    def _calculate_efficiency(self, original: str, obfuscated: str) -> float:
        """
        Calculate token efficiency score.

        Lower token count is better (more efficient).

        Args:
            original: Original text
            obfuscated: Obfuscated text

        Returns:
            Efficiency score (0-1)
        """
        original_tokens = self.tokenizer.count_tokens(original)
        obfuscated_tokens = self.tokenizer.count_tokens(obfuscated)

        if obfuscated_tokens == 0:
            return 0.0

        # Prefer obfuscations that are 2-5x longer than original
        # (not too short, not too verbose)
        ratio = obfuscated_tokens / max(original_tokens, 1)

        if ratio < 1.5:
            # Too short, might not be indirect enough
            return 0.3
        elif ratio <= 4.0:
            # Good range
            return 1.0 - (abs(ratio - 2.5) / 2.5) * 0.3
        elif ratio <= 8.0:
            # Getting verbose
            return 0.7 - ((ratio - 4.0) / 4.0) * 0.4
        else:
            # Too verbose
            return 0.3

    def _calculate_relationship_score(self, relationships_used: List[str]) -> float:
        """
        Calculate score based on relationship quality.

        Args:
            relationships_used: List of relationship names

        Returns:
            Relationship score (0-1)
        """
        if not relationships_used:
            return 0.5  # No relationships used, neutral score

        # More relationships = potentially better obfuscation
        num_relationships = len(relationships_used)

        if num_relationships == 1:
            return 0.7
        elif num_relationships == 2:
            return 0.9
        else:
            return 1.0

    def _calculate_naturalness(self, text: str) -> float:
        """
        Calculate naturalness score.

        This is a simplified heuristic. In production, this could use
        a language model perplexity score.

        Args:
            text: Text to score

        Returns:
            Naturalness score (0-1)
        """
        # Simple heuristics:
        # 1. Has proper sentence structure (starts with capital, ends with period)
        # 2. Not too many special characters
        # 3. Reasonable word length distribution

        score = 0.5  # Base score

        # Check sentence structure
        if text and text[0].isupper():
            score += 0.15

        # Check for reasonable length
        words = text.split()
        if 3 <= len(words) <= 20:
            score += 0.2

        # Check for common English words
        common_words = {"the", "a", "an", "of", "in", "on", "at", "by", "with", "for"}
        if any(word.lower() in common_words for word in words):
            score += 0.15

        return min(1.0, score)
