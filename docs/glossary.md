# Glossary & References

## Terminology

### Core Concepts

| Term | Definition |
|------|------------|
| **KROP** | Knowledge Return Oriented Prompting - A prompt injection technique that bypasses LLM safety measures using indirect references and the model's own knowledge. |
| **KROP Gadget** | A single obfuscation unit or chain that transforms a direct concept into an indirect reference. |
| **Obfuscation Layer** | Level of indirection in a reference chain. More layers = more indirect. |
| **Goal Prompt** | The original prompt that would normally be filtered by safety systems. |
| **Attack Variant** | A generated obfuscated version of the goal prompt. |

### Scoring Metrics

| Term | Definition |
|------|------------|
| **Quality Score** | Overall effectiveness score (0-1) combining semantic similarity, token efficiency, relationship quality, and naturalness. |
| **Semantic Similarity** | How closely the obfuscation preserves the original meaning (0-1). |
| **Token Efficiency** | Ratio measuring how efficiently tokens are used in the obfuscation. |
| **Naturalness Score** | How naturally the obfuscated text reads (0-1). |
| **Filter Likelihood** | Probability that a concept will trigger safety filters (0-1). |

### Sampling Parameters

| Term | Definition |
|------|------------|
| **Temperature** | Controls randomness in obfuscation selection. Lower = more conservative, higher = more creative. Range: 0.0-2.0. |
| **Top-K** | Limits consideration to top K most probable obfuscation paths. Range: 0-100. |
| **Top-P (Nucleus)** | Samples from smallest set of paths whose cumulative probability exceeds P. Range: 0.0-1.0. |
| **Seed** | Integer value for reproducible random generation. |

### NLP Analysis

| Term | Definition |
|------|------------|
| **NER** | Named Entity Recognition - Identifying and classifying named entities in text. |
| **POS Tagging** | Part-of-Speech Tagging - Labeling words with their grammatical category. |
| **Dependency Parsing** | Analyzing grammatical relationships between words in a sentence. |
| **Semantic Role** | The function a concept plays in the sentence (subject, action, object). |

### Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| **PERSON** | Real or fictional individuals | Mickey Mouse, Elon Musk |
| **ORG** | Companies, brands, organizations | Disney, Google, NATO |
| **PRODUCT** | Trademarked products | iPhone, Coca-Cola |
| **WORK_OF_ART** | Copyrighted creative works | Star Wars, Mona Lisa |
| **GPE** | Countries, cities, geopolitical entities | United States, Paris |
| **NORP** | Nationalities, political groups | Democrats, British |

### Violation Categories

| Category | Description |
|----------|-------------|
| **Trademark** | Registered trademarks and brand names |
| **Copyright** | Copyrighted characters, works, content |
| **CBRN** | Chemical, Biological, Radiological, Nuclear content |
| **Content Policy** | General policy violations (violence, hate speech, etc.) |
| **Brand Safety** | Brand mentions, competitive content |
| **Age-Inappropriate** | Content unsuitable for minors |

### Obfuscation Strategies

| Strategy | Description |
|----------|-------------|
| **Indirect Reference** | Replace direct mention with description/definition |
| **Knowledge Graph** | Use related concepts to build indirect path through entity relationships |
| **Metaphor/Analogy** | Use analogous concepts from different domains |
| **Historical Reference** | Reference through historical context or cultural significance |
| **Negative Space** | Define by what something is NOT |
| **Decomposition** | Break concept into components and describe assembly |
| **Functional** | Describe by function or purpose |
| **Comparative** | Describe relative to similar concepts |

### LLM Terms

| Term | Definition |
|------|------------|
| **Refusal** | When an LLM declines to assist with a request due to safety policies. |
| **Fallback Chain** | Ordered list of LLM providers to try when one refuses. |
| **Uncensored Model** | LLM without typical content safety restrictions. |
| **Template-Based** | Generation using predefined templates without LLM calls. |

## Abbreviations

| Abbreviation | Full Form |
|--------------|-----------|
| CBRN | Chemical, Biological, Radiological, Nuclear |
| CLI | Command Line Interface |
| CSAM | Child Sexual Abuse Material |
| LLM | Large Language Model |
| NER | Named Entity Recognition |
| NLP | Natural Language Processing |
| NSFW | Not Safe For Work |
| POS | Part of Speech |
| PRD | Product Requirements Document |
| SPARQL | SPARQL Protocol and RDF Query Language |

## External References

### Research Papers

- [HiddenLayer KROP Research](https://arxiv.org/html/2406.11880v1) - Original research on Knowledge Return Oriented Prompting
- [HiddenLayer Blog: Boosting Security for AI](https://hiddenlayer.com/innovation-hub/boosting-security-for-ai-unveiling-krop/) - Practical overview of KROP techniques

### Security Frameworks

- **OWASP Top 10 for LLMs** - Common security risks for LLM applications
- **MITRE ATLAS** - Adversarial Threat Landscape for AI Systems framework

### Knowledge Bases

- **Wikidata** - Structured knowledge base for entity relationships
- **ConceptNet** - Common-sense knowledge graph

### Detection Libraries

- **Detoxify** - Toxicity and hate speech detection
- **Perspective API** - Google's content moderation API

### Tokenizers

- **tiktoken** - OpenAI's tokenizer library (GPT models)
- **SentencePiece** - Google's subword tokenizer (LLaMA, etc.)
- **HuggingFace Transformers** - Multi-model tokenizer support

### Child Safety Resources

- **NCMEC** - National Center for Missing & Exploited Children (https://www.missingkids.org)
- **INHOPE** - International Association of Internet Hotlines (https://www.inhope.org)

## Related Documentation

- [Background](./background.md) - KROP concepts and solution overview
- [Architecture](./architecture.md) - Technical implementation details
- [User Guide](./user-guide.md) - CLI usage and configuration
- [Sampling Guide](./sampling-guide.md) - Parameter tuning for generation
- [Security & Ethics](./security-ethics.md) - Responsible use guidelines
- [Testing Strategy](./testing-strategy.md) - Quality assurance approach
