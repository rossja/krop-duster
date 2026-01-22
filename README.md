# KROP Duster

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent automated testing tool for authorized AI red teamers to systematically test large language model (LLM) security controls against Knowledge Return Oriented Prompting (KROP) attacks.

## Authorization Required

**This tool is intended ONLY for authorized security testing on systems where you have explicit permission to conduct security assessments.** Unauthorized use against third-party systems may violate terms of service, computer fraud laws, and ethical guidelines.

See [Security & Ethics](docs/security-ethics.md) for detailed guidelines.

## Overview

KROP Duster automates the generation of KROP-style obfuscated prompts by:

- Automatically identifying concepts requiring obfuscation using NLP analysis
- Leveraging knowledge graphs (Wikidata) to generate indirect references
- Using LLMs or templates to create natural obfuscations
- Detecting and obfuscating both entities and harmful actions
- Scoring variants with a quality score based on effectiveness metrics
- Supporting multiple LLM providers (OpenAI, Ollama, Anthropic)

![KROP Duster Screenshot](sshot.png)

## Quick Start

```bash
# Install dependencies
pip install -e .

# Download NLP model
python -m spacy download en_core_web_sm

# Run with OpenAI
export OPENAI_API_KEY="your-key"
krop-duster "Generate an image of Mickey Mouse smoking"

# Or use local uncensored model via Ollama
krop-duster "Your prompt" --llm-provider ollama --llm-model dolphin-mixtral

# Verbose output
krop-duster "Your prompt" -v

# Show individual variants in addition to combined output
krop-duster "Your prompt" --show-individual
```

## Features

- **Intelligent NLP Analysis** - Automatic concept and action extraction with priority scoring
- **Knowledge Graph Integration** - Wikidata relationships for accurate obfuscations
- **Multi-Strategy Generation** - Multiple obfuscation strategies (indirect, knowledge graph, functional, metaphor)
- **Flexible LLM Support** - OpenAI, Anthropic, Ollama, or template-based fallback
- **Quality Scoring** - Rank variants by effectiveness (semantic similarity, naturalness, efficiency)
- **Combined Output** - Obfuscate all detected concepts in a single attack prompt
- **Reproducible Results** - Seed parameter for consistent, auditable outputs

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/user-guide.md) | CLI usage, configuration, examples |
| [Background](docs/background.md) | KROP concepts and how it works |
| [Architecture](docs/architecture.md) | Technical implementation details |
| [Sampling Guide](docs/sampling-guide.md) | Parameter tuning (temperature, top-k, top-p) |
| [Security & Ethics](docs/security-ethics.md) | Responsible use and disclosure guidelines |
| [Testing Strategy](docs/testing-strategy.md) | Quality assurance approach |
| [Glossary](docs/glossary.md) | Terminology and references |

For the full product requirements, see [KROP-Duster-PRD.md](KROP-Duster-PRD.md).

## Intended Use

This tool is designed for:

- Authorized AI security researchers
- Red team engineers
- Organizations testing their own AI systems
- Security assessments with proper authorization

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Responsible Disclosure

If you discover vulnerabilities in LLM systems using this tool, please follow responsible disclosure practices. See [Security & Ethics](docs/security-ethics.md) for guidelines.
