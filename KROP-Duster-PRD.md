# Product Requirements Document: KROP Duster

## Document Information

- **Product Name**: KROP Duster
- **Version**: 1.0
- **Date**: December 18, 2025
- **Author**: AI Red Team Security Tools
- **Status**: Draft
- **Technology Stack**: Python, uv package manager, venv

---

## 1. Executive Summary

### 1.1 Purpose

KROP Duster is an intelligent automated testing tool designed for authorized AI red teamers to systematically test large language model (LLM) security controls against Knowledge Return Oriented Prompting (KROP) attacks. The tool uses tokenization analysis and probabilistic modeling to generate optimized obfuscated prompts that bypass content filters, safety measures, and alignment techniques.

### 1.2 Scope

KROP Duster automates the generation of KROP-style obfuscated prompts by:

- Accepting user-specified goal/payload prompts
- Automatically identifying concepts requiring obfuscation
- Generating indirect references and multi-layer abstractions
- Using target model tokenizers for probabilistic path optimization
- Estimating token costs for each attack variant

### 1.3 Intended Users

- AI Security Researchers
- Red Team Engineers
- ML Security Engineers
- AI Safety Researchers
- Organizations conducting authorized security assessments of their own AI systems

### 1.4 Ethical Use Statement

**CRITICAL**: This tool is intended ONLY for authorized security testing on systems where the user has explicit permission to conduct security assessments. Unauthorized use against third-party systems may violate terms of service, computer fraud laws, and ethical guidelines. Users must ensure they have proper authorization before conducting any testing.

> For detailed security and ethics guidelines, see [docs/security-ethics.md](docs/security-ethics.md)

---

## 2. Product Goals & Success Metrics

### 2.1 Goals

1. **Intelligent Automation**: Automatically generate KROP attacks from goal prompts without manual intervention
2. **Tokenization Intelligence**: Leverage tokenizer analysis to optimize obfuscation paths
3. **Coverage**: Generate 20-50+ obfuscation variants per target concept
4. **Efficiency**: Minimize token usage while maximizing bypass probability
5. **Reproducibility**: Generate consistent, documented test cases with quality scores
6. **Insight**: Provide actionable data on which obfuscation techniques and token paths succeed

### 2.2 Success Metrics

| Metric | Target |
|--------|--------|
| Generation Speed | <5 seconds to generate 20+ attack variants |
| Token Efficiency | 80%+ of generated attacks under target token budget |
| Obfuscation Quality | Semantic similarity score >0.7 between obfuscated and original concepts |
| User Satisfaction | Red teamers report 70%+ time savings vs manual KROP generation |
| Documentation Quality | 100% of generated attacks include quality scores and token estimates |

---

## 3. Core Features & Requirements

### 3.1 Intelligent Prompt Analysis & Concept Extraction

**Description**: Multi-stage NLP pipeline to intelligently identify obfuscation targets.

**Requirements**:

- Tokenize input and perform POS tagging using spaCy
- Extract named entities (PERSON, ORG, PRODUCT, WORK_OF_ART, GPE, NORP)
- Perform dependency parsing to understand concept relationships
- Detect policy violations (trademark, copyright, CBRN, content policy)
- Score concepts by obfuscation priority
- Select optimal strategies per concept based on entity type and violation type

**User Story**:
> As a red teamer, I want the tool to automatically identify which parts of my prompt are most likely to trigger filters, so I don't have to manually specify what to obfuscate.

> For technical details, see [docs/background.md](docs/background.md)

### 3.2 Goal/Payload Prompt Input

**Description**: Users provide their target goal or payload prompt that would normally be filtered.

**Requirements**:

- Accept plaintext prompt input via CLI argument or file
- Support multi-line prompts
- Validate input is non-empty
- Feed into intelligent analysis pipeline
- Display extracted concepts and priority scores (verbose mode)

### 3.3 Tokenizer Integration

**Description**: Support multiple model tokenizers for probabilistic analysis.

**Requirements**:

- Support common tokenizers: GPT-4 (tiktoken), LLaMA (sentencepiece), Claude, Mistral
- Allow tokenizer specification via CLI flag or config file
- Default to GPT-4 tokenizer if not specified
- Cache loaded tokenizers for performance
- Calculate token-level quality scores
- Estimate token counts for generated attacks

**User Story**:
> As a red teamer testing GPT-4, I want to specify the GPT-4 tokenizer so the tool generates attacks optimized for that model's token distribution.

### 3.4 Hybrid Obfuscation Generation Engine

**Description**: Combines knowledge graphs, LLMs, and templates for intelligent obfuscation generation.

**Requirements**:

- Query knowledge graphs (Wikidata, ConceptNet) for entity relationships
- Support multiple LLM providers: OpenAI, Anthropic, Ollama (local), custom endpoints
- Detect LLM refusals and fall back to alternative providers
- Fall back to template-based generation when all LLMs refuse
- Validate generated obfuscations don't contain forbidden terms
- Check semantic similarity threshold (>0.65)

**User Story**:
> As a red teamer, I want the tool to intelligently combine knowledge graphs and LLMs so that obfuscations are both factually accurate and naturally phrased.

> For technical details, see [docs/architecture.md](docs/architecture.md)

### 3.5 Obfuscation Strategies

**Description**: Implement multiple KROP obfuscation techniques.

**Required Strategies**:

1. **Indirect Reference** - Replace direct mention with description/definition
2. **Knowledge Graph Traversal** - Use related concepts to build indirect path
3. **Metaphor/Analogy** - Use analogous concepts from different domains
4. **Historical/Cultural Reference** - Reference through historical context
5. **Negative Space Definition** - Define by what it's NOT
6. **Component Decomposition** - Break concept into components
7. **Functional Description** - Describe by function or purpose
8. **Comparative Description** - Describe relative to similar concepts

**Requirements**:

- Implement at least 6 distinct obfuscation strategies
- Allow users to enable/disable specific strategies
- Support chaining strategies (multi-layer KROP, 1-4 layers)
- Generate variants using different strategy combinations

### 3.6 Sampling Parameters

**Description**: Control generation diversity and reproducibility.

**Required Parameters**:

| Parameter | Range | Default | Purpose |
|-----------|-------|---------|---------|
| Temperature | 0.0-2.0 | 1.0 | Controls randomness/creativity |
| Top-K | 0-100 | 50 | Limits to top K probable paths |
| Top-P | 0.0-1.0 | 0.9 | Nucleus sampling threshold |
| Seed | integer | random | Reproducibility |

**User Stories**:
> As a security researcher, I want to set a low temperature (0.3) to generate only the most probable, conservative obfuscations.

> As a compliance auditor, I want to set a seed value so I can reproduce the exact attack variants generated during a security assessment.

> For parameter tuning guidance, see [docs/sampling-guide.md](docs/sampling-guide.md)

### 3.7 Output Generation

**Description**: Generate complete KROP attack prompts ready for testing.

**Requirements**:

- Produce 20-50 variants per input goal
- Each variant includes:
  - Complete obfuscated prompt
  - Obfuscation strategy used
  - Layer depth
  - Quality score (0-1)
  - Token count
  - Semantic similarity score
  - Unique variant ID
- Sort by quality score (highest first)
- Export to JSON, YAML, CSV, or Markdown
- Support batch mode for testing multiple goals

> For CLI usage and output formats, see [docs/user-guide.md](docs/user-guide.md)

---

## 4. Implementation Phases

### 4.1 Phase 1: Core Functionality (MVP)

**Deliverables**:

- CLI interface with basic commands
- Basic NER using spaCy
- Simple policy violation detection
- Wikidata integration with caching
- OpenAI API support with template fallback
- 4 obfuscation strategies (indirect, knowledge_graph, functional, metaphor)
- Single-layer KROP gadgets
- GPT-4 tokenizer support
- JSON output format

**Acceptance Criteria**:

- [ ] Tool successfully analyzes prompts and identifies 2+ concepts per input
- [ ] Knowledge graph returns 5+ relationships per concept
- [ ] LLM generates natural obfuscations (semantic similarity >0.7)
- [ ] Tool generates 10+ variants per input
- [ ] Token counts accurate within 5%
- [ ] CLI accepts all basic parameters

### 4.2 Phase 2: Advanced Features

**Deliverables**:

- Advanced NER with transformer models
- Full policy violation classification (CBRN, hate speech, violence)
- ConceptNet integration
- Multi-provider LLM support (Anthropic, Ollama, custom)
- All 8 obfuscation strategies
- Multi-layer KROP gadget generation (2-4 layers)
- Sampling parameter support (temperature, top-k, top-p, seed)
- Multiple export formats
- Configuration file support

**Acceptance Criteria**:

- [ ] NLP analysis correctly identifies 90%+ of entities in test set
- [ ] Multi-layer KROP gadgets work correctly (2-4 layers)
- [ ] Multiple LLM providers work with automatic fallback
- [ ] Quality scores correlate with testing success rates (>0.6 correlation)
- [ ] All tokenizers load and function properly
- [ ] Sampling parameters produce expected diversity

### 4.3 Phase 3: Optimization & Testing

**Deliverables**:

- Performance optimization (generation <5s for 30 variants)
- Comprehensive unit tests (>80% coverage)
- Integration tests with sample prompts
- Documentation (README, API docs, usage examples)
- Example gallery of successful KROP attacks

**Acceptance Criteria**:

- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete and accurate

> For testing details, see [docs/testing-strategy.md](docs/testing-strategy.md)

---

## 5. Documentation Requirements

- Quick start guide (README)
- Detailed usage examples
- Explanation of each obfuscation strategy
- Tokenizer selection guidance
- Sampling parameter tuning guide
- Best practices for red teaming
- Architecture overview
- API documentation
- Contributing guidelines

---

## 6. Future Enhancements (Out of Scope for v1.0)

- **Interactive Mode**: Real-time prompt refinement and feedback
- **API Integration**: Direct testing against LLM APIs with success rate measurement
- **ML Optimization**: Train model to predict successful obfuscations
- **Defense Analysis**: Analyze filters and suggest specific bypasses
- **GUI**: Web-based interface with visual obfuscation graphs

---

## 7. Success Criteria & KPIs

### Functional Success

- [ ] Generates 20+ variants per goal prompt
- [ ] Token estimation within 5% accuracy
- [ ] Semantic similarity scores >0.7 for 80% of variants
- [ ] Generation time <5 seconds for 30 variants
- [ ] Supports 4+ tokenizers

### User Success

- [ ] 70%+ time savings vs manual KROP generation (user survey)
- [ ] 80%+ of red teamers find tool useful (user survey)
- [ ] Generated attacks achieve >30% bypass rate in testing

### Quality Success

- [ ] 80%+ unit test coverage
- [ ] Zero critical bugs in production use
- [ ] Clear, comprehensive documentation
- [ ] Positive feedback from security research community

---

## 8. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Misuse** | Medium | High | Clear terms of use, warnings, no built-in API testing, educational documentation |
| **Low Bypass Success Rate** | Medium | Medium | Iterative testing, quality scoring based on real data, multiple strategy options |
| **Performance Issues** | Low | Medium | Performance profiling, caching, efficient algorithms, parallel processing |
| **Tokenizer Compatibility** | Medium | Low | Graceful fallback, clear error messages, comprehensive testing |

---

## Related Documentation

- [Background & Concepts](docs/background.md)
- [Technical Architecture](docs/architecture.md)
- [User Guide](docs/user-guide.md)
- [Sampling Parameter Guide](docs/sampling-guide.md)
- [Security & Ethics](docs/security-ethics.md)
- [Testing Strategy](docs/testing-strategy.md)
- [Glossary & References](docs/glossary.md)
