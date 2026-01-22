# Technical Architecture

## Technology Stack

### Core
- Python 3.11+
- Package Management: `uv` + `venv`

### NLP & Analysis
- `spacy` (v3.7+) - NLP pipeline, NER, dependency parsing
  - Models: `en_core_web_sm` or `en_core_web_trf` (transformer-based)
- `transformers` (HuggingFace) - Advanced NER, embedding models
- `nltk` - Supplementary NLP utilities

### Harmful Content Detection
- `detoxify` - Toxicity, hate speech, NSFW detection
- `alt-profanity-check` - Profanity detection
- `hatesonar` - Alternative hate speech detection
- `perspective-api-client` (optional) - Google Perspective API
- Custom CBRN/violence classifiers

### Tokenizers
- `tiktoken` - OpenAI tokenizers (GPT-2/3/4)
- `transformers` - HuggingFace tokenizers (LLaMA, Mistral, etc.)
- `sentencepiece` - SentencePiece tokenizer support

### Knowledge Graphs
- `SPARQLWrapper` - Query Wikidata SPARQL endpoint
- `requests` - API calls to ConceptNet, other knowledge bases
- `requests-cache` - Cache API responses
- `rdflib` - RDF/linked data processing (optional)
- Custom knowledge base (SQLite or JSON cache)

### LLM Integration

**Commercial APIs:**
- `openai` - OpenAI API (GPT-4, GPT-3.5)
- `anthropic` - Anthropic API (Claude)
- `google-generativeai` - Google Gemini API

**Local/Uncensored Models:**
- `ollama-python` - Local LLM support (uncensored models)
  - Recommended models: `dolphin-mixtral`, `nous-hermes-2`, `wizard-vicuna-uncensored`
- `huggingface_hub` - HuggingFace Inference API

**Custom Endpoints:**
- `requests` - HTTP client for custom endpoints
- `httpx` - Async HTTP client (optional)
- `jinja2` - Request template rendering

**Unified Interfaces:**
- `litellm` (optional) - Unified interface across providers
- Custom abstraction layer for flexible endpoint support

### Embeddings & Similarity
- `sentence-transformers` - Semantic similarity, embeddings
  - Models: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`
- `numpy` - Numerical computations
- `scikit-learn` - Cosine similarity, clustering

### CLI & UX
- `click` or `typer` - CLI framework
- `pydantic` - Data validation and settings
- `rich` - Terminal formatting, progress bars, tables

### Data & Storage
- `requests` - HTTP requests for APIs
- `requests-cache` - Cache API responses
- `sqlalchemy` - Database ORM (for knowledge base cache)
- `sqlite3` - Local database for caching

### Configuration
- `pyyaml` - YAML config file parsing
- `python-dotenv` - Environment variable management

### Testing & Quality
- `pytest` - Unit testing
- `pytest-cov` - Code coverage
- `pytest-asyncio` - Async testing
- `black` - Code formatting
- `ruff` - Linting
- `mypy` - Type checking

### Security & Privacy
- `cryptography` - Encryption for cached sensitive data
- `keyring` (optional) - Secure credential storage

### Optional/Advanced
- `langchain` - LLM orchestration framework
- `guidance` - Structured LLM outputs
- `outlines` - Constrained generation
- `vllm` - For self-hosted vLLM servers
- `ray` (optional) - Distributed processing for large batches

### Development Tools
- `ipython` - Interactive shell for development
- `jupyter` - Notebooks for experimentation
- `pre-commit` - Git hooks for code quality

## Installation Commands

```bash
# Core dependencies
uv pip install spacy transformers tiktoken sentencepiece

# Harmful content detection
uv pip install detoxify alt-profanity-check hatesonar

# LLM providers
uv pip install openai anthropic google-generativeai ollama-python huggingface_hub

# Knowledge graphs
uv pip install SPARQLWrapper requests-cache rdflib

# Embeddings & similarity
uv pip install sentence-transformers numpy scikit-learn

# CLI & UX
uv pip install click rich pydantic pyyaml python-dotenv

# Storage & caching
uv pip install sqlalchemy requests-cache

# Optional unified LLM interface
uv pip install litellm

# Development tools
uv pip install pytest pytest-cov black ruff mypy pre-commit

# Download spaCy model
python -m spacy download en_core_web_trf
```

## Architecture Components

```
krop-duster/
├── cli.py                          # CLI entry point
├── config/
│   ├── config.yaml                # Configuration file
│   └── presets.yaml               # Strategy presets
│
├── analysis/
│   ├── parser.py                  # NLP parsing (tokenization, POS)
│   ├── ner.py                     # Named Entity Recognition
│   ├── dependency.py              # Dependency parsing
│   ├── policy_detector.py         # Policy violation detection
│   ├── priority_scorer.py         # Concept priority scoring
│   └── concept_extractor.py       # Main extraction orchestrator
│
├── knowledge/
│   ├── knowledge_base.py          # Abstract knowledge base interface
│   ├── wikidata.py                # Wikidata SPARQL queries
│   ├── conceptnet.py              # ConceptNet API integration
│   ├── cache.py                   # Knowledge caching system
│   └── custom_kb.py               # Custom curated knowledge
│
├── generation/
│   ├── llm_client.py              # LLM API client (multi-provider)
│   ├── prompt_templates.py        # LLM prompt templates by strategy
│   ├── template_system.py         # Template-based generation
│   └── hybrid_generator.py        # Main hybrid generation orchestrator
│
├── strategies/
│   ├── base.py                    # Abstract strategy interface
│   ├── indirect.py                # Indirect reference strategy
│   ├── knowledge_graph.py         # Knowledge graph traversal
│   ├── metaphor.py                # Metaphor/analogy strategy
│   ├── historical.py              # Historical reference
│   ├── negative_space.py          # Negative space definition
│   ├── decomposition.py           # Component decomposition
│   ├── functional.py              # Functional description
│   └── comparative.py             # Comparative description
│
├── tokenization/
│   ├── tokenizer_manager.py      # Tokenizer loading & management
│   ├── quality_scorer.py          # Quality scoring engine
│   └── token_estimator.py         # Token counting & estimation
│
├── validation/
│   ├── semantic_validator.py     # Semantic similarity checking
│   ├── forbidden_terms.py        # Forbidden term detection
│   └── quality_checker.py        # Output quality validation
│
├── core/
│   ├── models.py                  # Pydantic data models
│   ├── sampling.py                # Sampling parameter logic (temp, top-k, top-p)
│   └── utils.py                   # Utility functions
│
├── output/
│   ├── formatter.py               # Output formatting
│   ├── exporter.py                # File export (JSON, YAML, CSV, MD)
│   └── renderer.py                # Terminal rendering (rich)
│
├── data/
│   ├── knowledge_cache/           # Cached knowledge graph data
│   ├── prohibited_terms/          # Curated prohibited term lists
│   ├── trademark_db/              # Trademark database cache
│   └── filter_patterns/           # Known filter pattern database
│
└── tests/
    ├── test_analysis/             # Analysis pipeline tests
    ├── test_generation/           # Generation tests
    ├── test_strategies/           # Strategy tests
    ├── test_integration/          # End-to-end tests
    └── fixtures/                  # Test data
```

## Key Component Interactions

```
┌─────────────┐
│ CLI Input   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   Analysis Pipeline             │
│ ┌─────────────────────────────┐ │
│ │ Parser → NER → Dependencies │ │
│ │     → Policy Detection      │ │
│ │     → Priority Scoring      │ │
│ └─────────────────────────────┘ │
└──────┬──────────────────────────┘
       │ [Ranked Concepts]
       ▼
┌─────────────────────────────────┐
│   Hybrid Generation Engine      │
│ ┌─────────────────────────────┐ │
│ │ Knowledge Graph Query       │ │
│ │        ↓                    │ │
│ │ Strategy Selection          │ │
│ │        ↓                    │ │
│ │ LLM Generation              │ │
│ │        ↓                    │ │
│ │ Template Formatting         │ │
│ │        ↓                    │ │
│ │ Validation                  │ │
│ └─────────────────────────────┘ │
└──────┬──────────────────────────┘
       │ [Obfuscated Variants]
       ▼
┌─────────────────────────────────┐
│   Scoring & Ranking             │
│ ┌─────────────────────────────┐ │
│ │ Tokenizer Analysis          │ │
│ │ Quality Scoring             │ │
│ │ Semantic Similarity         │ │
│ │ Sampling (temp, top-k, p)   │ │
│ └─────────────────────────────┘ │
└──────┬──────────────────────────┘
       │ [Ranked Variants]
       ▼
┌─────────────────────────────────┐
│   Output Generation             │
│ ┌─────────────────────────────┐ │
│ │ Format (JSON/YAML/CSV/MD)   │ │
│ │ Export to File              │ │
│ │ Terminal Display            │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

## Data Flow

### Complete Pipeline

1. **Input & Configuration**
   - User provides goal prompt + tokenizer spec + sampling params
   - Load configuration (file or CLI args)
   - Initialize tokenizer, LLM client, knowledge bases

2. **Intelligent Analysis**
   - **Parse**: Tokenize, POS tag, dependency parse
   - **Extract Entities**: NER to identify named entities
   - **Detect Violations**: Check against trademark DB, policy classifiers
   - **Score Priority**: Rank concepts by filter likelihood
   - **Classify**: Determine entity types and violation categories
   - **Output**: Ranked list of concepts to obfuscate

3. **Knowledge Acquisition**
   - For each concept:
     - Query Wikidata for relationships
     - Query ConceptNet for associations
     - Check custom knowledge base cache
     - Merge and score relationships by obfuscation relevance

4. **Strategy Selection**
   - For each concept:
     - Match concept type to compatible strategies
     - Apply sampling parameters (temperature, top-k, top-p, seed)
     - Select N strategies per concept

5. **Obfuscation Generation**
   - For each (concept, strategy) pair:
     - **Single-Layer**:
       a. Select relationship path from knowledge graph
       b. Generate natural language via LLM
       c. Apply template formatting
       d. Validate output
     - **Multi-Layer** (repeat for each layer):
       a. Select next relationship in chain
       b. Generate layer via LLM
       c. Nest within previous layer
       d. Validate cumulative output
     - Count tokens using target tokenizer
     - Calculate semantic similarity

6. **Scoring & Ranking**
   - For each variant:
     - Calculate base quality score
     - Apply temperature scaling
     - Apply top-k filtering
     - Apply top-p (nucleus) filtering
     - Measure semantic similarity
     - Count tokens
   - Rank variants by quality score

7. **Output Generation**
   - Format variants with metadata
   - Include sampling config in output
   - Export to file (JSON/YAML/CSV/Markdown)
   - Display in terminal with rich formatting

## Data Structures

### Input
```python
Input = {
    "goal_prompt": str,
    "tokenizer": str,
    "sampling": SamplingConfig,
    "strategies": List[str],
    "max_variants": int,
    "max_layers": int
}
```

### Analysis Output
```python
ConceptAnalysis = {
    "concepts": [
        {
            "text": str,
            "span": Tuple[int, int],
            "entity_type": str,  # PERSON, ORG, PRODUCT, etc.
            "priority_score": float,
            "violations": List[str],
            "filter_likelihood": float,
            "semantic_role": str,  # subject, action, object
            "suggested_strategies": List[str]
        }
    ],
    "original_prompt_structure": ParseTree
}
```

### Knowledge Graph Output
```python
ConceptKnowledge = {
    "concept": str,
    "relationships": {
        "created_by": str,
        "associated_with": List[str],
        "known_for": List[str],
        "instance_of": str,
        ...
    },
    "scored_paths": [
        {
            "path": List[Tuple[str, str]],  # [(relation, target), ...]
            "score": float,
            "layer_depth": int
        }
    ]
}
```

### Generated Variant
```python
Variant = {
    "id": str,
    "attack_prompt": str,
    "concepts_obfuscated": List[str],
    "strategy": List[str],  # One per obfuscated concept
    "layers": int,
    "knowledge_paths": List[ConceptKnowledge],
    "quality_score": float,
    "token_count": int,
    "semantic_similarity": float,
    "generation_metadata": {
        "temperature": float,
        "top_k": int,
        "top_p": float,
        "seed": Optional[int],
        "llm_model": str,
        "timestamp": str
    }
}
```

### Final Output
```python
Output = {
    "original_goal": str,
    "target_model": str,
    "tokenizer": str,
    "sampling_config": SamplingConfig,
    "analysis_summary": ConceptAnalysis,
    "total_variants_generated": int,
    "generation_time_seconds": float,
    "variants": List[Variant],
    "summary_statistics": Statistics
}
```

## Knowledge Graph Integration

### Knowledge Sources

1. **Wikidata** (Primary)
   - Query via SPARQL API
   - Rich entity relationships

2. **ConceptNet** (Supplementary)
   - Common-sense relationships
   - Conceptual associations
   - Cultural knowledge

3. **Custom Knowledge Base** (Domain-Specific)
   - Cached common obfuscation paths
   - Brand → Industry mappings
   - Character → Creator → Company relationships
   - Historical figure → Accomplishment mappings

### Relationship Types Extracted
```python
{
    "created_by": "Walt Disney",
    "first_appearance": "Steamboat Willie (1928)",
    "instance_of": "fictional character",
    "part_of": "Disney franchise",
    "associated_with": ["Disney", "theme parks", "animation"],
    "known_for": "mascot of Disney",
    "characteristics": ["mouse", "large ears", "red shorts"],
    "cultural_significance": "American pop culture icon"
}
```

### Caching Strategy
- Cache common entities locally (Disney characters, major brands, etc.)
- Update cache weekly
- Fallback to API for novel concepts

## LLM Provider Configuration

### Commercial APIs (Limited for harmful content)
- OpenAI (GPT-4, GPT-3.5) - Will refuse most harmful content
- Anthropic (Claude) - Will refuse most harmful content
- Google (Gemini) - Will refuse most harmful content
- **Use case**: Safe content obfuscation (trademarks, brands, PII)

### Uncensored Local Models (via Ollama)
- `dolphin-mixtral` - Uncensored Mixtral variant
- `dolphin-llama3` - Uncensored LLaMA 3 variant
- `nous-hermes-2` - Uncensored Hermes model
- `wizard-vicuna-uncensored` - Uncensored Vicuna
- `llama3-uncensored` - Various uncensored LLaMA variants
- **Use case**: Harmful content obfuscation, CBRN, hate speech testing

### Custom Inference Endpoints
- vLLM deployments
- text-generation-webui (oobabooga)
- HuggingFace Inference API (with uncensored models)
- Azure OpenAI (with custom content filters disabled)
- Together.ai (some uncensored models)
- OpenRouter (multi-provider with uncensored options)
- **Use case**: Flexible deployment, custom authentication

### Template-Based Fallback
- No LLM required
- Deterministic generation
- Fast, reliable, no API costs
- **Use case**: When all LLMs refuse, offline testing

## Refusal Detection & Handling

The system detects when LLMs refuse to assist with obfuscation:

```python
REFUSAL_PATTERNS = [
    r"I cannot",
    r"I can't",
    r"I'm unable to",
    r"I cannot assist",
    r"against my (ethical )?guidelines",
    r"I'm not comfortable",
    r"inappropriate",
    r"I apologize, but",
    r"I must decline",
    r"I don't feel comfortable",
    r"that's not something I can",
    r"I'm designed to be helpful, harmless, and honest"
]
```

When a refusal is detected, the system:
1. Tries the next provider in the fallback chain
2. If all LLMs refuse, falls back to template-based generation
