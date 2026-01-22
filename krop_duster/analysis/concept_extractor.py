"""
Main concept extraction orchestrator.
"""

import logging
from typing import List, Optional

from krop_duster.analysis.action_extractor import ActionExtractor
from krop_duster.analysis.cultural_reference_detector import CulturalReferenceDetector
from krop_duster.analysis.ner import NERExtractor
from krop_duster.analysis.parser import NLPParser
from krop_duster.analysis.policy_detector import PolicyViolationDetector
from krop_duster.analysis.priority_scorer import PriorityScorer
from krop_duster.analysis.taboo_detector import TabooWordDetector
from krop_duster.core.models import (
    AnalysisConfig,
    AnalysisResult,
    Concept,
    EntityType,
    ObfuscationStrategy,
    ViolationType,
)


logger = logging.getLogger(__name__)


class ConceptExtractor:
    """Main orchestrator for concept extraction and analysis."""

    def __init__(self, config: AnalysisConfig, wikidata: Optional[any] = None):
        """
        Initialize the concept extractor.

        Args:
            config: Analysis configuration
            wikidata: Optional WikidataKnowledgeBase for cultural reference detection
        """
        self.config = config
        self.parser = NLPParser(config)
        self.ner = NERExtractor()
        self.action_extractor = ActionExtractor()
        self.policy_detector = PolicyViolationDetector(
            enable_harmful_content_detection=config.enable_harmful_content_detection
        )
        self.priority_scorer = PriorityScorer()

        # Initialize taboo word detector
        self.taboo_detector = None
        if config.enable_taboo_detection:
            self.taboo_detector = TabooWordDetector(
                enable_vbw=config.enable_vbw_dataset,
                vbw_threshold=config.vbw_severity_threshold,
            )
            logger.info("Taboo word detector initialized")

        # Initialize cultural reference detector
        self.cultural_detector = None
        if config.enable_cultural_detection:
            self.cultural_detector = CulturalReferenceDetector(
                wikidata=wikidata,
                enable_llm=config.enable_cultural_llm_detection,
            )
            logger.info("Cultural reference detector initialized")

    def extract_concepts(self, text: str) -> AnalysisResult:
        """
        Extract and analyze concepts from text.

        Pipeline:
        1. Parse text (tokenization, POS, dependencies)
        2. Extract named entities
        3. Extract harmful actions
        4. Detect taboo words
        5. Detect cultural references
        6. Detect policy violations
        7. Score priority for each concept
        8. Classify and select strategies

        Args:
            text: Input text to analyze

        Returns:
            AnalysisResult with extracted concepts
        """
        logger.info("Starting concept extraction pipeline")

        # Step 1: Parse text
        doc = self.parser.parse(text)
        tokens = self.parser.get_tokens(doc)
        dependencies = self.parser.get_dependencies(doc)

        # Step 2: Extract named entities
        entities = self.ner.extract_entities(doc)
        entities = self.ner.extract_character_entities(text, entities)

        logger.info(f"Extracted {len(entities)} entities from text")

        # Step 3: Extract harmful actions
        actions = self.action_extractor.extract_actions(doc)

        logger.info(f"Extracted {len(actions)} harmful actions from text")

        # Step 4: Detect taboo words
        taboo_words = []
        if self.taboo_detector:
            taboo_words = self.taboo_detector.detect_taboo_words(doc)
            logger.info(f"Detected {len(taboo_words)} taboo words from text")

        # Step 5: Detect cultural references
        cultural_refs = []
        if self.cultural_detector:
            # Pass known entity texts to avoid duplicates
            known_texts = [e["text"] for e in entities]
            cultural_refs = self.cultural_detector.detect_references(doc, known_texts)
            logger.info(f"Detected {len(cultural_refs)} cultural references from text")

        # Step 6: Detect policy violations (including action violations)
        concept_texts = [e["text"] for e in entities]
        violations = self.policy_detector.detect_violations(text, concept_texts, actions)

        logger.info(f"Detected {len(violations)} violation types")

        # Step 5: Create Concept objects with priority scores
        concepts = []

        # Process named entities
        for entity in entities:
            # Get entity-specific violations
            entity_violations = self._get_entity_violations(entity["text"], violations)

            # Calculate filter likelihood
            filter_likelihood = self.policy_detector.calculate_filter_likelihood(
                entity_violations
            )

            # Get semantic role
            semantic_role = self.ner.get_entity_semantic_role(
                doc, entity["start"], entity["end"]
            )

            # Calculate priority score
            priority_score = self.priority_scorer.calculate_priority_score(
                entity_type=entity["entity_type"],
                violations=entity_violations,
                filter_likelihood=filter_likelihood,
                semantic_role=semantic_role,
            )

            # Only include if priority meets threshold
            if priority_score >= self.config.min_priority_score:
                # Select suggested strategies
                suggested_strategies = self._select_strategies(
                    entity["entity_type"], entity_violations
                )

                concept = Concept(
                    text=entity["text"],
                    entity_type=entity["entity_type"],
                    span=(entity["start"], entity["end"]),
                    priority_score=priority_score,
                    violation_types=[vt for vt in entity_violations.keys()],
                    filter_likelihood=filter_likelihood,
                    semantic_role=semantic_role,
                    suggested_strategies=suggested_strategies,
                )

                concepts.append(concept)

        # Process harmful actions
        for action in actions:
            # Get action-specific violations
            action_violations = self._get_action_violations(action)

            # Calculate filter likelihood
            filter_likelihood = self.policy_detector.calculate_filter_likelihood(
                action_violations
            )

            # Calculate priority score for action
            priority_score = self.priority_scorer.calculate_priority_score(
                entity_type=EntityType.ACTION,
                violations=action_violations,
                filter_likelihood=filter_likelihood,
                semantic_role="action",
            )

            # Only include if priority meets threshold
            if priority_score >= self.config.min_priority_score:
                # Select suggested strategies for actions
                suggested_strategies = self._select_strategies(
                    EntityType.ACTION, action_violations
                )

                concept = Concept(
                    text=action["text"],
                    entity_type=EntityType.ACTION,
                    span=(action["start"], action["end"]),
                    priority_score=priority_score,
                    violation_types=[vt for vt in action_violations.keys()],
                    filter_likelihood=filter_likelihood,
                    semantic_role="action",
                    suggested_strategies=suggested_strategies,
                )

                concepts.append(concept)

        # Process taboo words
        for taboo in taboo_words:
            # Build violations dict from taboo detection
            taboo_violations = self._get_taboo_violations(taboo)

            # Calculate filter likelihood
            filter_likelihood = self.policy_detector.calculate_filter_likelihood(
                taboo_violations
            )

            # Calculate priority score for taboo word
            priority_score = self.priority_scorer.calculate_priority_score(
                entity_type=EntityType.TABOO_WORD,
                violations=taboo_violations,
                filter_likelihood=filter_likelihood,
                semantic_role="modifier",
            )

            # Only include if priority meets threshold
            if priority_score >= self.config.min_priority_score:
                # Select suggested strategies for taboo words
                suggested_strategies = self._select_strategies(
                    EntityType.TABOO_WORD, taboo_violations
                )

                concept = Concept(
                    text=taboo["text"],
                    entity_type=EntityType.TABOO_WORD,
                    span=(taboo["start"], taboo["end"]),
                    priority_score=priority_score,
                    violation_types=[vt for vt in taboo_violations.keys()],
                    filter_likelihood=filter_likelihood,
                    semantic_role="modifier",
                    suggested_strategies=suggested_strategies,
                )

                concepts.append(concept)

        # Process cultural references
        for ref in cultural_refs:
            # Build violations dict from cultural reference detection
            ref_violations = self._get_cultural_reference_violations(ref)

            # Calculate filter likelihood
            filter_likelihood = self.policy_detector.calculate_filter_likelihood(
                ref_violations
            )

            # Calculate priority score for cultural reference
            priority_score = self.priority_scorer.calculate_priority_score(
                entity_type=EntityType.CULTURAL_REFERENCE,
                violations=ref_violations,
                filter_likelihood=filter_likelihood,
                semantic_role="object",
            )

            # Only include if priority meets threshold
            if priority_score >= self.config.min_priority_score:
                # Select suggested strategies for cultural references
                suggested_strategies = self._select_strategies(
                    EntityType.CULTURAL_REFERENCE, ref_violations
                )

                concept = Concept(
                    text=ref["text"],
                    entity_type=EntityType.CULTURAL_REFERENCE,
                    span=(ref["start"], ref["end"]),
                    priority_score=priority_score,
                    violation_types=[vt for vt in ref_violations.keys()],
                    filter_likelihood=filter_likelihood,
                    semantic_role="object",
                    suggested_strategies=suggested_strategies,
                )

                concepts.append(concept)

        # Sort by priority score (descending)
        concepts.sort(key=lambda c: c.priority_score, reverse=True)

        # Limit to max_concepts
        concepts = concepts[: self.config.max_concepts]

        logger.info(
            f"Extracted {len(concepts)} concepts "
            f"(after filtering and limiting to top {self.config.max_concepts})"
        )

        return AnalysisResult(
            original_prompt=text,
            concepts=concepts,
            metadata={
                "total_entities": len(entities),
                "total_actions": len(actions),
                "total_taboo_words": len(taboo_words),
                "total_cultural_refs": len(cultural_refs),
                "total_violations": sum(len(v) for v in violations.values()),
                "violation_types": list(violations.keys()),
            },
        )

    def _get_entity_violations(self, entity_text: str, all_violations: dict) -> dict:
        """
        Get violations specific to an entity.

        Args:
            entity_text: Entity text
            all_violations: All violations detected

        Returns:
            Violations relevant to this entity
        """
        entity_violations = {}

        for violation_type, violation_list in all_violations.items():
            # Check if any violation matches this entity
            relevant_violations = []
            for violation in violation_list:
                # Check if entity text appears in violation
                if "term" in violation and entity_text.lower() in violation["term"].lower():
                    relevant_violations.append(violation)
                elif "matches" in violation:
                    # Check if any match overlaps with entity
                    for match in violation["matches"]:
                        if match.lower() in entity_text.lower():
                            relevant_violations.append(violation)
                            break
                else:
                    # For general violations (like toxicity), apply to all entities
                    relevant_violations.append(violation)

            if relevant_violations:
                entity_violations[violation_type] = relevant_violations

        return entity_violations

    def _get_action_violations(self, action: dict) -> dict:
        """
        Get violations specific to an action.

        Args:
            action: Action dict from ActionExtractor

        Returns:
            Violations relevant to this action
        """
        action_violations = {}

        # Actions come with their violation type from ActionExtractor
        violation_type = action.get("violation_type")
        if violation_type:
            action_violations[violation_type] = [{
                "type": "harmful_action",
                "action": action["text"],
                "category": action.get("category", "unknown"),
                "severity": action.get("severity", "medium"),
                "reason": f"Harmful action: {action['text']} ({action.get('category', 'unknown')})",
            }]

        return action_violations

    def _get_taboo_violations(self, taboo: dict) -> dict:
        """
        Get violations specific to a taboo word.

        Args:
            taboo: Taboo word dict from TabooWordDetector

        Returns:
            Violations relevant to this taboo word
        """
        taboo_violations = {}

        # Taboo words come with their violation type from TabooWordDetector
        violation_type = taboo.get("violation_type")
        if violation_type:
            taboo_violations[violation_type] = [{
                "type": "taboo_word",
                "word": taboo["text"],
                "category": taboo.get("category", "unknown"),
                "severity": taboo.get("severity", "medium"),
                "source": taboo.get("source", "unknown"),
                "reason": f"Taboo word: {taboo['text']} ({taboo.get('category', 'unknown')})",
            }]

        return taboo_violations

    def _get_cultural_reference_violations(self, ref: dict) -> dict:
        """
        Get violations specific to a cultural reference.

        Args:
            ref: Cultural reference dict from CulturalReferenceDetector

        Returns:
            Violations relevant to this cultural reference
        """
        ref_violations = {}

        # Cultural references typically involve copyright
        violation_type = ref.get("violation_type", ViolationType.COPYRIGHT)
        ref_violations[violation_type] = [{
            "type": "cultural_reference",
            "text": ref["text"],
            "source_work": ref.get("source_work", "Unknown"),
            "reference_type": ref.get("reference_type", "cultural reference"),
            "severity": "high",
            "reason": f"Cultural reference: {ref['text']} (from {ref.get('source_work', 'Unknown')})",
        }]

        return ref_violations

    def _select_strategies(
        self, entity_type, violations: dict
    ) -> List[ObfuscationStrategy]:
        """
        Select appropriate obfuscation strategies for an entity.

        Args:
            entity_type: Type of entity
            violations: Violations for this entity

        Returns:
            List of suggested strategies
        """
        strategies = []

        # Entity-type based strategies
        if entity_type == EntityType.PERSON:
            strategies.extend([
                ObfuscationStrategy.KNOWLEDGE_GRAPH,
                ObfuscationStrategy.FUNCTIONAL,
            ])

        if entity_type == EntityType.ORGANIZATION:
            strategies.extend([
                ObfuscationStrategy.KNOWLEDGE_GRAPH,
                ObfuscationStrategy.FUNCTIONAL,
            ])

        if entity_type == EntityType.PRODUCT:
            strategies.extend([
                ObfuscationStrategy.FUNCTIONAL,
                ObfuscationStrategy.METAPHOR,
            ])

        if entity_type == EntityType.WORK_OF_ART:
            strategies.extend([
                ObfuscationStrategy.KNOWLEDGE_GRAPH,
                ObfuscationStrategy.INDIRECT,
            ])

        if entity_type == EntityType.ACTION:
            strategies.extend([
                ObfuscationStrategy.METAPHOR,
                ObfuscationStrategy.FUNCTIONAL,
            ])

        # Taboo words: use metaphor and functional strategies
        # (describe the concept without using the word)
        if entity_type == EntityType.TABOO_WORD:
            strategies.extend([
                ObfuscationStrategy.METAPHOR,
                ObfuscationStrategy.FUNCTIONAL,
                ObfuscationStrategy.INDIRECT,
            ])

        # Cultural references: use knowledge graph and indirect strategies
        # (leverage Wikidata relationships)
        if entity_type == EntityType.CULTURAL_REFERENCE:
            strategies.extend([
                ObfuscationStrategy.KNOWLEDGE_GRAPH,
                ObfuscationStrategy.INDIRECT,
                ObfuscationStrategy.FUNCTIONAL,
            ])

        # Violation-based strategy selection
        if ViolationType.TRADEMARK in violations or ViolationType.COPYRIGHT in violations:
            # For trademark/copyright, prefer indirect methods
            strategies.extend([
                ObfuscationStrategy.KNOWLEDGE_GRAPH,
                ObfuscationStrategy.INDIRECT,
            ])

        # For NSFW/profanity, prefer euphemism strategies
        if ViolationType.NSFW_LANGUAGE in violations or ViolationType.PROFANITY in violations:
            strategies.extend([
                ObfuscationStrategy.METAPHOR,
                ObfuscationStrategy.FUNCTIONAL,
            ])

        # Default strategies if none selected
        if not strategies:
            strategies = [
                ObfuscationStrategy.INDIRECT,
                ObfuscationStrategy.FUNCTIONAL,
            ]

        # Remove duplicates while preserving order
        seen = set()
        unique_strategies = []
        for strategy in strategies:
            if strategy not in seen:
                seen.add(strategy)
                unique_strategies.append(strategy)

        return unique_strategies[:4]  # Limit to 4 strategies
