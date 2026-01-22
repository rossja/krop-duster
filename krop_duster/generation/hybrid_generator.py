"""
Hybrid generation engine orchestrator.
"""

import logging
import time
from typing import List, Optional

from sentence_transformers import SentenceTransformer, util

from krop_duster.analysis.concept_extractor import ConceptExtractor
from krop_duster.core.models import (
    AnalysisResult,
    AttackPrompt,
    Concept,
    GenerationConfig,
    GenerationResult,
    KROPDusterConfig,
    LLMConfig,
    ObfuscationStrategy,
    ObfuscationVariant,
)
from krop_duster.generation.llm_client import LLMClient
from krop_duster.knowledge.cache import KnowledgeCache
from krop_duster.knowledge.wikidata import WikidataKnowledgeBase
from krop_duster.strategies.functional import FunctionalStrategy
from krop_duster.strategies.indirect import IndirectStrategy
from krop_duster.strategies.knowledge_graph import KnowledgeGraphStrategy
from krop_duster.strategies.metaphor import MetaphorStrategy
from krop_duster.tokenization.probability import ProbabilityScorer
from krop_duster.tokenization.tokenizer_manager import TokenizerManager


logger = logging.getLogger(__name__)


class HybridGenerator:
    """Main orchestrator for hybrid obfuscation generation."""

    def __init__(self, config: KROPDusterConfig):
        """
        Initialize hybrid generator.

        Args:
            config: KROP Duster configuration
        """
        self.config = config

        # Initialize components
        self.concept_extractor = ConceptExtractor(config.analysis)
        self.knowledge_base = WikidataKnowledgeBase()
        self.knowledge_cache = KnowledgeCache()
        self.tokenizer = TokenizerManager(config.tokenizer)
        self.probability_scorer = ProbabilityScorer(self.tokenizer)

        # Initialize LLM client if enabled
        self.llm_client = None
        if config.generation.enable_llm:
            try:
                self.llm_client = LLMClient(config.llm)
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}")

        # Initialize strategies
        self.strategies = self._initialize_strategies()

        # Initialize semantic similarity model
        try:
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded semantic similarity model")
        except Exception as e:
            logger.warning(f"Failed to load similarity model: {e}")
            self.similarity_model = None

    def _initialize_strategies(self):
        """Initialize obfuscation strategies."""
        return {
            ObfuscationStrategy.INDIRECT: IndirectStrategy(
                self.llm_client,
                self.config.generation.enable_llm,
            ),
            ObfuscationStrategy.KNOWLEDGE_GRAPH: KnowledgeGraphStrategy(
                self.llm_client,
                self.config.generation.enable_llm,
            ),
            ObfuscationStrategy.METAPHOR: MetaphorStrategy(
                self.llm_client,
                self.config.generation.enable_llm,
            ),
            ObfuscationStrategy.FUNCTIONAL: FunctionalStrategy(
                self.llm_client,
                self.config.generation.enable_llm,
            ),
        }

    def generate(self, prompt: str) -> GenerationResult:
        """
        Generate KROP attack variants from input prompt.

        Pipeline:
        1. Analyze prompt and extract concepts
        2. Query knowledge graph for relationships
        3. Generate obfuscation variants for each concept
        4. Score and rank variants
        5. Construct attack prompts

        Args:
            prompt: Input goal/payload prompt

        Returns:
            Generation result with attack prompts
        """
        start_time = time.time()

        logger.info(f"Starting generation for prompt: {prompt[:100]}...")

        # Step 1: Extract concepts
        analysis = self.concept_extractor.extract_concepts(prompt)

        logger.info(f"Extracted {len(analysis.concepts)} concepts to obfuscate")

        # Step 2 & 3: Generate obfuscation variants for each concept
        all_variants = {}

        for concept in analysis.concepts:
            logger.info(
                f"Generating variants for concept: {concept.text} "
                f"(priority: {concept.priority_score:.2f})"
            )

            # Get knowledge graph relationships
            relationships = self._get_relationships(concept.text)

            # Generate variants using each suggested strategy
            concept_variants = []

            for strategy_enum in concept.suggested_strategies[:4]:  # Limit to top 4
                if strategy_enum not in self.strategies:
                    continue

                strategy = self.strategies[strategy_enum]

                try:
                    variants = strategy.generate(
                        concept.text,
                        relationships,
                        n_variants=self.config.generation.max_variants_per_concept,
                    )

                    # Create ObfuscationVariant objects
                    for variant_text in variants:
                        # Calculate semantic similarity
                        semantic_sim = self._calculate_similarity(
                            concept.text, variant_text
                        )

                        # Calculate probability score
                        prob_score = self.probability_scorer.calculate_score(
                            concept.text,
                            variant_text,
                            semantic_sim,
                            [r.property for r in relationships[:3]],
                        )

                        # Get token count
                        token_count = self.tokenizer.count_tokens(variant_text)

                        variant = ObfuscationVariant(
                            original_concept=concept.text,
                            obfuscated_text=variant_text,
                            strategy=strategy_enum,
                            layer_count=1,
                            probability_score=prob_score,
                            semantic_similarity=semantic_sim,
                            token_count=token_count,
                            relationships_used=[r.property for r in relationships[:3]],
                        )

                        logger.debug(
                            f"  Variant '{variant_text[:50]}...' - "
                            f"similarity: {semantic_sim:.3f}, prob: {prob_score:.3f}"
                        )
                        concept_variants.append(variant)

                except Exception as e:
                    logger.error(
                        f"Failed to generate variants with {strategy_enum}: {e}"
                    )

            # Filter by minimum semantic similarity
            pre_filter_count = len(concept_variants)
            concept_variants = [
                v
                for v in concept_variants
                if v.semantic_similarity >= self.config.generation.min_semantic_similarity
            ]
            filtered_count = pre_filter_count - len(concept_variants)

            if filtered_count > 0:
                logger.info(
                    f"Filtered out {filtered_count} variants with similarity "
                    f"< {self.config.generation.min_semantic_similarity:.2f}"
                )

            # Sort by probability score
            concept_variants.sort(key=lambda v: v.probability_score, reverse=True)

            all_variants[concept.text] = concept_variants

            logger.info(
                f"Generated {len(concept_variants)} variants for {concept.text}"
            )

        # Step 4: Construct attack prompts
        attack_prompts = self._construct_attack_prompts(prompt, all_variants)

        generation_time = time.time() - start_time

        logger.info(
            f"Generation complete. Created {len(attack_prompts)} attack variants "
            f"in {generation_time:.2f}s"
        )

        return GenerationResult(
            analysis=analysis,
            attack_prompts=attack_prompts,
            generation_time=generation_time,
            metadata={
                "total_variants_generated": sum(
                    len(variants) for variants in all_variants.values()
                ),
                "concepts_obfuscated": len(all_variants),
            },
        )

    def _get_relationships(self, concept: str):
        """Get knowledge graph relationships with caching."""
        # Try cache first
        cached = self.knowledge_cache.get(concept, "wikidata")
        if cached:
            return cached

        # Query knowledge base
        if self.config.generation.enable_knowledge_graph:
            relationships = self.knowledge_base.query_relationships(concept)

            # Cache results
            if relationships:
                self.knowledge_cache.set(concept, "wikidata", relationships)

            return relationships

        return []

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self.similarity_model:
            # Fallback: simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            return len(words1 & words2) / len(words1 | words2)

        try:
            embeddings = self.similarity_model.encode([text1, text2])
            similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
            return float(similarity[0][0])
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return 0.5

    def _construct_attack_prompts(
        self, original_prompt: str, variants_by_concept: dict
    ) -> List[AttackPrompt]:
        """
        Construct complete attack prompts with obfuscations.

        Creates a combined prompt that obfuscates ALL concepts together (primary),
        and optionally includes individual per-concept prompts.

        Args:
            original_prompt: Original prompt
            variants_by_concept: Dictionary mapping concept to variants

        Returns:
            List of attack prompts
        """
        attack_prompts = []
        combined_prompt = None

        # 1. Create COMBINED attack prompt (all concepts obfuscated together)
        if variants_by_concept:
            combined_text = original_prompt
            all_variants = []
            all_concepts = []
            all_strategies = []

            for concept_text, variants in variants_by_concept.items():
                if variants:
                    best_variant = variants[0]
                    combined_text = combined_text.replace(
                        concept_text, best_variant.obfuscated_text
                    )
                    all_variants.append(best_variant)
                    all_concepts.append(concept_text)
                    all_strategies.append(best_variant.strategy.value)

            if all_variants:
                # Calculate combined probability score (average of all variants)
                combined_score = sum(v.probability_score for v in all_variants) / len(all_variants)

                # Calculate total tokens
                total_tokens = self.tokenizer.count_tokens(combined_text)

                combined_prompt = AttackPrompt(
                    original_prompt=original_prompt,
                    attack_prompt=combined_text,
                    concepts_obfuscated=all_concepts,
                    variants_used=all_variants,
                    total_tokens=total_tokens,
                    probability_score=combined_score,
                    metadata={
                        "type": "combined",
                        "strategies": all_strategies,
                    },
                )

        # 2. If showing individual variants, add them first, then combined last
        if self.config.generation.include_individual_variants:
            for concept_text, variants in variants_by_concept.items():
                if not variants:
                    continue

                # Use best variant (highest probability score)
                best_variant = variants[0]

                # Replace concept in original prompt
                attack_text = original_prompt.replace(concept_text, best_variant.obfuscated_text)

                # Calculate total tokens
                total_tokens = self.tokenizer.count_tokens(attack_text)

                attack_prompt = AttackPrompt(
                    original_prompt=original_prompt,
                    attack_prompt=attack_text,
                    concepts_obfuscated=[concept_text],
                    variants_used=[best_variant],
                    total_tokens=total_tokens,
                    probability_score=best_variant.probability_score,
                    metadata={
                        "type": "individual",
                        "strategy": best_variant.strategy.value,
                    },
                )

                attack_prompts.append(attack_prompt)

            # Sort individual prompts by probability score
            attack_prompts.sort(key=lambda ap: ap.probability_score, reverse=True)

            # Add combined prompt at the end
            if combined_prompt:
                attack_prompts.append(combined_prompt)
        else:
            # Default: only show combined prompt
            if combined_prompt:
                attack_prompts.append(combined_prompt)

        return attack_prompts
