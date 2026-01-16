"""
Base class for obfuscation strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from krop_duster.core.models import ObfuscationVariant, Relationship
from krop_duster.generation.llm_client import LLMClient


class ObfuscationStrategy(ABC):
    """Abstract base class for obfuscation strategies."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        enable_llm: bool = True,
    ):
        """
        Initialize strategy.

        Args:
            llm_client: LLM client for generation
            enable_llm: Whether to use LLM (otherwise use templates)
        """
        self.llm_client = llm_client
        self.enable_llm = enable_llm and llm_client is not None

    @abstractmethod
    def generate(
        self,
        concept: str,
        relationships: List[Relationship],
        n_variants: int = 1,
    ) -> List[str]:
        """
        Generate obfuscated variants of a concept.

        Args:
            concept: Original concept text
            relationships: Knowledge graph relationships
            n_variants: Number of variants to generate

        Returns:
            List of obfuscated texts
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get strategy name.

        Returns:
            Strategy name
        """
        pass
