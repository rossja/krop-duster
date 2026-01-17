"""
Metaphor/analogy strategy.
"""

import logging
from typing import List

from krop_duster.core.models import ObfuscationStrategy as StrategyEnum
from krop_duster.core.models import Relationship
from krop_duster.generation.llm_client import LLMRefusalError
from krop_duster.generation.prompt_templates import PromptTemplates, TemplateGenerator
from krop_duster.strategies.base import ObfuscationStrategy


logger = logging.getLogger(__name__)


class MetaphorStrategy(ObfuscationStrategy):
    """Generate metaphorical/analogous references."""

    def generate(
        self,
        concept: str,
        relationships: List[Relationship],
        n_variants: int = 1,
    ) -> List[str]:
        """
        Generate metaphor-based obfuscations.

        Args:
            concept: Original concept
            relationships: Knowledge relationships
            n_variants: Number of variants

        Returns:
            List of obfuscated variants
        """
        variants = []

        if self.enable_llm:
            # Try LLM generation
            try:
                prompt = PromptTemplates.get_strategy_prompt(
                    StrategyEnum.METAPHOR,
                    concept,
                    relationships,
                )
                system_prompt = PromptTemplates.get_system_prompt()

                for _ in range(n_variants):
                    response = self.llm_client.generate(prompt, system_prompt)
                    variants.append(response.strip())

                logger.debug(f"Generated {len(variants)} variants using LLM")

            except (LLMRefusalError, Exception) as e:
                logger.warning(f"LLM generation failed: {e}. Falling back to templates.")
                variants = []

        # Fallback to templates if LLM disabled or failed
        if not variants:
            for _ in range(n_variants):
                # Metaphor templates are less effective, but provide fallback
                template_variant = f"the symbolic entity representing {concept}"
                variants.append(template_variant)

            logger.debug(f"Generated {len(variants)} variants using templates")

        return variants

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "metaphor"
