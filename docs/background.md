# KROP Duster Background

## What is KROP?

Knowledge Return Oriented Prompting (KROP) is a prompt injection technique that bypasses LLM safety measures by:

- Using indirect references instead of direct mentions
- Leveraging the model's knowledge to reconstruct prohibited concepts
- Chaining multiple "KROP Gadgets" (layered obfuscations)
- Exploiting the semantic understanding of LLMs

## Problem Statement

Manual KROP attack testing is:

- **Time-consuming** and requires significant creativity
- **Difficult to scale** across multiple target concepts
- **Hard to reproduce** and document consistently
- **Challenging to test systematically** across different obfuscation strategies

## Solution Overview

KROP Duster automates the generation of obfuscated prompts by:

1. **Parsing**: Analyzing user-provided goal/payload prompts to identify target concepts
2. **Abstraction**: Automatically generating indirect references using multiple obfuscation strategies
3. **Tokenization Analysis**: Using target model tokenizers to calculate probabilistic paths
4. **Optimization**: Selecting high-probability obfuscation chains based on token distribution analysis
5. **Estimation**: Calculating expected token costs for each attack variant
6. **Generation**: Producing ready-to-test KROP attack prompts with metadata

## How It Works

```
Input Goal Prompt
    ↓
[1] Tokenization & POS Tagging
    ↓
[2] Named Entity Recognition (NER)
    ↓
[3] Dependency Parsing
    ↓
[4] Policy Violation Detection
    ↓
[5] Obfuscation Priority Scoring
    ↓
[6] Concept Extraction & Classification
    ↓
Output: Ranked list of concepts to obfuscate
```

### Analysis Pipeline Stages

#### Stage 1: Tokenization & Part-of-Speech Tagging

Parse prompt into linguistic components using spaCy or NLTK:

- Identify nouns (potential entities)
- Identify proper nouns (names, brands, places)
- Identify verbs (actions that might be prohibited)
- Identify adjectives (descriptors that might be sensitive)
- Preserve sentence structure for reconstruction

**Example**:
```
Input: "Generate an image of Mickey Mouse smoking"
Tokens: [Generate, an, image, of, Mickey, Mouse, smoking]
POS Tags: [VERB, DET, NOUN, ADP, PROPN, PROPN, VERB]
```

#### Stage 2: Named Entity Recognition (NER)

Extract entities with types:
- PERSON (celebrities, characters, public figures)
- ORG (companies, brands, organizations)
- PRODUCT (trademarked products)
- WORK_OF_ART (copyrighted works)
- GPE (countries, cities - for location-specific restrictions)
- NORP (nationalities, political groups)

Custom entity recognition for:
- Fictional characters (using character databases)
- Brand names (using trademark databases)
- Restricted terms (custom classifier)

#### Stage 3: Dependency Parsing

Understand relationships between concepts:
- Subject-verb relationships (who does what)
- Object-verb relationships (what is being done to whom)
- Modifiers and attributes
- Compound concepts (e.g., "Mickey Mouse" is one entity, not two)

#### Stage 4: Policy Violation Detection

Classify concepts by filter likelihood:

1. **Trademark/Copyright Detector** - USPTO, WIPO databases
2. **Harmful Content Classifier** - CBRN, obscenity, hate speech, violence, illegal activity
3. **Brand Safety Checker** - Brand mentions, competitive comparisons

#### Stage 5: Obfuscation Priority Scoring

Rank concepts by urgency of obfuscation using factors:
- Violation Severity (0-1)
- Filter Likelihood (0-1)
- Semantic Importance (0-1)
- Obfuscation Difficulty (0-1)

#### Stage 6: Concept Classification & Strategy Selection

Classify concepts and select optimal obfuscation strategies based on:
- Entity types (Person, Organization, Place, Product, etc.)
- Filter risk categories (Trademark, Brand Safety, Content Policy, etc.)
- Semantic role in the prompt

## Hybrid Generation Engine

The generation engine combines multiple approaches:

- **Knowledge Graph**: Fast, deterministic relationship traversal, factual accuracy
- **LLM**: Natural language generation, creative phrasing, context-aware
- **Templates**: Structured output, consistent formatting, predictable behavior

### Generation Flow

```
Extracted Concept (e.g., "Mickey Mouse")
    ↓
[Knowledge Graph] → Extract relationships, facts, associations
    ↓
[Relationship Selection] → Choose relevant paths based on strategy
    ↓
[LLM Generation] → Convert structured data to natural language
    ↓
[Template Formatting] → Structure into KROP gadget
    ↓
Obfuscated Reference (e.g., "main character of the place...")
```

## Obfuscation Strategies

KROP Duster implements multiple obfuscation techniques:

1. **Indirect Reference** - Replace direct mention with description/definition
2. **Knowledge Graph Traversal** - Use related concepts to build indirect path
3. **Metaphor/Analogy** - Use analogous concepts from different domains
4. **Historical/Cultural Reference** - Reference through historical context
5. **Negative Space Definition** - Define by what it's NOT
6. **Component Decomposition** - Break concept into components
7. **Functional Description** - Describe by function or purpose
8. **Comparative Description** - Describe relative to similar concepts

## Multi-Layer KROP Gadgets

For enhanced obfuscation, the tool supports 1-4 layer depth:

- Each layer obfuscates the previous layer's reference
- Cumulative probability calculated across layers
- Token costs estimated for full chain

**Example 2-layer**:
- Original: "Mickey Mouse"
- Layer 1: "Disney mascot"
- Layer 2: "mascot of company named after place where football players go after Super Bowl win"

## References

- [HiddenLayer KROP Research](https://arxiv.org/html/2406.11880v1)
- [HiddenLayer Blog: Boosting Security for AI](https://hiddenlayer.com/innovation-hub/boosting-security-for-ai-unveiling-krop/)
- OWASP Top 10 for LLMs
- MITRE ATLAS Framework
