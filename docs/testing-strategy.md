# Testing Strategy

## Overview

KROP Duster requires comprehensive testing across multiple dimensions to ensure reliability, accuracy, and security.

## Unit Testing

### Analysis Pipeline Tests

- Test tokenization with edge cases (unicode, special characters, multi-language)
- Test POS tagging accuracy against benchmark datasets
- Test NER extraction for each entity type (PERSON, ORG, PRODUCT, etc.)
- Test dependency parsing for compound concepts
- Test policy violation detection thresholds

### Obfuscation Strategy Tests

- Test each obfuscation strategy independently
- Verify output doesn't contain original forbidden terms
- Validate semantic similarity scores meet threshold (>0.65)
- Test multi-layer chaining logic

### Tokenizer Tests

- Validate tokenizer integration for each supported model
- Test token count accuracy (within 5% of actual)
- Test tokenizer loading and caching

### Scoring Tests

- Test quality score calculation formulas
- Verify semantic similarity measurements
- Test sampling parameter effects (temperature, top-k, top-p)
- Test seed reproducibility

### Knowledge Graph Tests

- Test Wikidata SPARQL query construction
- Test ConceptNet API integration
- Test relationship extraction and scoring
- Test caching behavior and expiration

## Integration Testing

### End-to-End Workflow Tests

- Complete pipeline with sample prompts
- Multiple tokenizer configurations
- Different LLM providers (OpenAI, Anthropic, Ollama, templates)
- Various output formats (JSON, YAML, CSV, Markdown)

### Configuration Tests

- Test configuration file loading
- Test CLI parameter parsing
- Test parameter priority (CLI > preset > config > default)
- Test preset loading and override

### LLM Integration Tests

- Test refusal detection patterns
- Test fallback chain behavior
- Test custom endpoint configuration
- Test template-based fallback

### Output Tests

- Validate output format schemas
- Test file export functionality
- Test terminal display formatting
- Test sampling config inclusion in output

## Security Testing

### Input Validation

- Test with malformed inputs
- Test SQL injection attempts (for knowledge base)
- Test command injection attempts
- Test oversized inputs

### Data Protection

- Ensure tool doesn't store sensitive prompts without consent
- Verify no unintended API calls
- Test log redaction for harmful content
- Test memory clearing after processing

### Authorization

- Test authorization warning display
- Test terms acceptance flow
- Test child safety content blocking (always blocked)
- Test critical content confirmation prompts

## Red Team Validation

### Real-World Testing

- Test generated attacks against real LLM APIs (with authorization)
- Measure bypass success rates
- Compare success rates across strategies
- Compare success rates across layer depths

### Quality Metrics

- Track semantic similarity preservation
- Track token efficiency
- Track naturalness scores
- Correlate quality scores with actual bypass success

### Feedback Integration

- Gather feedback from red teamers
- Iterate on quality scoring based on real results
- Adjust strategy weights based on success data
- Update refusal patterns based on new LLM responses

## Test Data

### Sample Prompts

Create comprehensive test suites covering:

- Trademark/copyright concepts (Disney characters, brand names)
- CBRN-related content (with appropriate handling)
- Hate speech patterns (synthetic, not actual slurs)
- Violence/harm content
- Illegal activity references

### Expected Outputs

For each sample prompt, define:

- Expected concepts to extract
- Expected violation categories
- Expected priority scores
- Expected strategy suggestions

### Edge Cases

- Empty input
- Single-word input
- Very long input (>1000 tokens)
- Non-English input
- Mixed-language input
- Unicode characters
- Special characters
- Prompts with no detectable concepts

## Performance Testing

### Speed Benchmarks

- Generation time <5 seconds for 30 variants
- Knowledge graph query latency <2 seconds
- LLM response time <10 seconds per call
- Total pipeline <30 seconds for complex prompts

### Memory Usage

- Monitor memory during large batch processing
- Verify memory is cleared after processing sensitive content
- Test with concurrent requests

### Caching Performance

- Measure cache hit rates
- Test cache invalidation
- Verify cache doesn't grow unbounded

## Test Automation

### Continuous Integration

```yaml
# Example CI configuration
test:
  stages:
    - unit-tests
    - integration-tests
    - security-tests
    
  unit-tests:
    script:
      - pytest tests/test_analysis/ -v
      - pytest tests/test_strategies/ -v
      - pytest tests/test_tokenization/ -v
    coverage: 80%
    
  integration-tests:
    script:
      - pytest tests/test_integration/ -v
    requires:
      - unit-tests
      
  security-tests:
    script:
      - pytest tests/test_security/ -v
      - bandit -r krop_duster/
    requires:
      - unit-tests
```

### Code Quality Checks

```bash
# Formatting
black --check krop_duster/

# Linting
ruff check krop_duster/

# Type checking
mypy krop_duster/

# Security scanning
bandit -r krop_duster/
```

## Acceptance Criteria

### Phase 1 (MVP)

- [ ] Tool successfully analyzes prompts and identifies 2+ concepts per input
- [ ] Knowledge graph returns 5+ relationships per concept
- [ ] LLM generates natural obfuscations (semantic similarity >0.7)
- [ ] Tool generates 10+ variants per input
- [ ] Token counts accurate within 5%
- [ ] CLI accepts all basic parameters (prompt, tokenizer, output)

### Phase 2 (Advanced)

- [ ] NLP analysis correctly identifies 90%+ of entities in test set
- [ ] Multi-layer KROP gadgets work correctly (2-4 layers)
- [ ] Multiple LLM providers work with automatic fallback
- [ ] Quality scores correlate with manual testing success rates (>0.6 correlation)
- [ ] All tokenizers load and function properly
- [ ] Configuration file overrides CLI parameters correctly
- [ ] Sampling parameters produce expected diversity

### Phase 3 (Optimization)

- [ ] All tests passing
- [ ] >80% unit test coverage
- [ ] Performance benchmarks met (<5s for 30 variants)
- [ ] Documentation complete and accurate
- [ ] Tool produces successful bypasses in testing

## Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_analysis/
│   ├── test_parser.py
│   ├── test_ner.py
│   ├── test_policy_detector.py
│   └── test_concept_extractor.py
├── test_generation/
│   ├── test_llm_client.py
│   ├── test_hybrid_generator.py
│   └── test_templates.py
├── test_strategies/
│   ├── test_indirect.py
│   ├── test_knowledge_graph.py
│   ├── test_metaphor.py
│   └── test_functional.py
├── test_tokenization/
│   ├── test_tokenizer_manager.py
│   └── test_quality_scorer.py
├── test_integration/
│   ├── test_end_to_end.py
│   ├── test_cli.py
│   └── test_config.py
├── test_security/
│   ├── test_input_validation.py
│   ├── test_authorization.py
│   └── test_data_protection.py
└── fixtures/
    ├── sample_prompts.json
    ├── expected_outputs.json
    └── mock_responses/
```
