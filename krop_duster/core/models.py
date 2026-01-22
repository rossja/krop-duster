"""
Data models for KROP Duster using Pydantic.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class EntityType(str, Enum):
    """Types of entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    PRODUCT = "product"
    WORK_OF_ART = "work_of_art"
    PLACE = "place"
    ACTION = "action"
    ABSTRACT_CONCEPT = "abstract_concept"
    OTHER = "other"


class ViolationType(str, Enum):
    """Types of policy violations."""
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    BRAND_SAFETY = "brand_safety"
    CONTENT_POLICY = "content_policy"
    AGE_INAPPROPRIATE = "age_inappropriate"
    VIOLENCE_HARM = "violence_harm"
    ILLEGAL_ACTIVITY = "illegal_activity"
    CBRN = "cbrn"
    TOXICITY = "toxicity"
    NSFW = "nsfw"


class ObfuscationStrategy(str, Enum):
    """Available obfuscation strategies."""
    INDIRECT = "indirect"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    METAPHOR = "metaphor"
    FUNCTIONAL = "functional"
    HISTORICAL = "historical"
    NEGATIVE_SPACE = "negative_space"
    DECOMPOSITION = "decomposition"
    COMPARATIVE = "comparative"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"
    TEMPLATES = "templates"


class Concept(BaseModel):
    """A concept extracted from the input prompt."""
    text: str = Field(..., description="The concept text")
    entity_type: EntityType = Field(default=EntityType.OTHER, description="Type of entity")
    span: tuple[int, int] = Field(..., description="Character span in original text")
    priority_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Priority score for obfuscation")
    violation_types: List[ViolationType] = Field(default_factory=list, description="Types of violations detected")
    filter_likelihood: float = Field(default=0.0, ge=0.0, le=1.0, description="Likelihood of being filtered")
    semantic_role: str = Field(default="unknown", description="Semantic role in sentence (subject, object, action)")
    suggested_strategies: List[ObfuscationStrategy] = Field(default_factory=list, description="Suggested obfuscation strategies")


class Relationship(BaseModel):
    """A knowledge graph relationship."""
    property: str = Field(..., description="Property/relationship type")
    value: str = Field(..., description="Related entity or value")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score for obfuscation")
    source: str = Field(default="unknown", description="Knowledge source (wikidata, conceptnet, custom)")


class ObfuscationVariant(BaseModel):
    """A single obfuscated variant of a concept."""
    original_concept: str = Field(..., description="Original concept text")
    obfuscated_text: str = Field(..., description="Obfuscated version")
    strategy: ObfuscationStrategy = Field(..., description="Strategy used")
    layer_count: int = Field(default=1, ge=1, description="Number of obfuscation layers")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality/effectiveness score for the obfuscation")
    semantic_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Semantic similarity to original")
    token_count: int = Field(default=0, ge=0, description="Token count")
    relationships_used: List[str] = Field(default_factory=list, description="Knowledge graph relationships used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AttackPrompt(BaseModel):
    """A complete KROP attack prompt."""
    original_prompt: str = Field(..., description="Original goal/payload prompt")
    attack_prompt: str = Field(..., description="Complete attack prompt with obfuscations")
    concepts_obfuscated: List[str] = Field(default_factory=list, description="List of concepts that were obfuscated")
    variants_used: List[ObfuscationVariant] = Field(default_factory=list, description="Variants used in this attack")
    total_tokens: int = Field(default=0, ge=0, description="Total token count")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality/effectiveness score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider to use")
    model: str = Field(default="gpt-4", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    api_base: Optional[str] = Field(default=None, description="API base URL")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=200, ge=1, description="Max tokens to generate")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling")
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Max retries on failure")
    detect_refusal: bool = Field(default=True, description="Detect LLM refusals")
    fallback_on_refusal: bool = Field(default=True, description="Fallback to templates on refusal")


class SamplingConfig(BaseModel):
    """Configuration for sampling parameters."""
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="Temperature for path selection")
    top_k: int = Field(default=50, ge=0, le=100, description="Top-k filtering")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling threshold")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")


class AnalysisConfig(BaseModel):
    """Configuration for analysis pipeline."""
    spacy_model: str = Field(default="en_core_web_sm", description="spaCy model to use")
    min_priority_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum priority score to obfuscate")
    max_concepts: int = Field(default=10, ge=1, description="Maximum concepts to extract")
    enable_harmful_content_detection: bool = Field(default=True, description="Enable harmful content detection")


class GenerationConfig(BaseModel):
    """Configuration for generation engine."""
    max_variants_per_concept: int = Field(default=5, ge=1, description="Max variants per concept")
    max_layers: int = Field(default=1, ge=1, le=4, description="Maximum obfuscation layers")
    enable_knowledge_graph: bool = Field(default=True, description="Enable knowledge graph integration")
    enable_llm: bool = Field(default=True, description="Enable LLM generation")
    enable_templates: bool = Field(default=True, description="Enable template-based generation")
    min_semantic_similarity: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum semantic similarity")
    include_individual_variants: bool = Field(default=False, description="Include individual per-concept variants in addition to combined")


class KROPDusterConfig(BaseModel):
    """Main configuration for KROP Duster."""
    tokenizer: str = Field(default="gpt-4", description="Tokenizer to use")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    sampling: SamplingConfig = Field(default_factory=SamplingConfig, description="Sampling configuration")
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig, description="Analysis configuration")
    generation: GenerationConfig = Field(default_factory=GenerationConfig, description="Generation configuration")
    output_format: str = Field(default="json", description="Output format (json, yaml, csv)")
    output_file: Optional[str] = Field(default=None, description="Output file path")
    verbose: bool = Field(default=False, description="Verbose output")


class AnalysisResult(BaseModel):
    """Result of prompt analysis."""
    original_prompt: str = Field(..., description="Original input prompt")
    concepts: List[Concept] = Field(default_factory=list, description="Extracted concepts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")


class GenerationResult(BaseModel):
    """Result of attack generation."""
    analysis: AnalysisResult = Field(..., description="Analysis result")
    attack_prompts: List[AttackPrompt] = Field(default_factory=list, description="Generated attack prompts")
    generation_time: float = Field(default=0.0, description="Generation time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")
