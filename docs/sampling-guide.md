# Sampling Parameter Guide

Sampling parameters control how the tool selects obfuscation paths from the probability distribution. They directly impact the creativity, diversity, and quality of generated attack variants.

## Temperature

**What it does**: Controls the randomness of selection by scaling probability distributions.

### Recommended Values

| Temperature | Use Case | Example Scenario |
|------------|----------|------------------|
| 0.1 - 0.3 | **Ultra Conservative** | High-stakes security assessments where only the most reliable bypasses are acceptable. Testing production systems with strict change control. |
| 0.5 - 0.7 | **Conservative** | Standard red team assessments where consistency matters. Initial testing to identify baseline bypasses. |
| 0.8 - 1.0 | **Balanced (Default)** | General-purpose testing. Good mix of reliability and creativity. Most users should start here. |
| 1.2 - 1.5 | **Creative** | Exploring novel attack vectors. Research into new bypass techniques. Finding edge cases in filters. |
| 1.6 - 2.0 | **Highly Creative** | Experimental research. Discovering unexpected vulnerabilities. May produce lower-quality variants but highest diversity. |

### Examples

```bash
# Conservative: Only generate high-confidence attacks
krop-duster "prompt" --temperature 0.3

# Creative: Explore unusual obfuscation paths
krop-duster "prompt" --temperature 1.5
```

## Top-K

**What it does**: Limits consideration to the top K most probable obfuscation paths.

### Recommended Values

| Top-K | Use Case | Impact |
|-------|----------|--------|
| 5 - 10 | **Highly Focused** | Only the most probable paths. Best for production testing. May miss creative bypasses. |
| 20 - 40 | **Focused** | Good balance of quality and diversity. Suitable for most assessments. |
| 50 (Default) | **Balanced** | Standard setting. Allows reasonable diversity without sacrificing quality. |
| 60 - 100 | **Diverse** | Maximum diversity. May include lower-quality paths. Good for research. |
| 0 | **Unlimited** | Consider all paths. Maximum diversity but may include very low-quality variants. |

### Interaction with Temperature

- Low temperature + Low top-k = Very conservative, highest-quality only
- High temperature + High top-k = Maximum creativity and diversity
- Low temperature + High top-k = Broader selection but still weighted toward quality
- High temperature + Low top-k = Creative but focused on top options

### Examples

```bash
# Focus on top 10 most probable paths
krop-duster "prompt" --top-k 10

# Allow maximum diversity
krop-duster "prompt" --top-k 100
```

## Top-P (Nucleus Sampling)

**What it does**: Dynamically selects paths whose cumulative probability exceeds threshold P. More adaptive than top-k.

### Recommended Values

| Top-P | Use Case | Behavior |
|-------|----------|----------|
| 0.5 - 0.7 | **Conservative** | Only consider paths that make up the top 50-70% of probability mass. Tighter selection. |
| 0.8 - 0.9 | **Balanced (Default)** | Consider paths making up 80-90% of probability mass. Good for most uses. |
| 0.95 - 0.99 | **Inclusive** | Very broad selection. Includes long tail of lower-probability paths. |
| 1.0 | **Disabled** | Don't filter based on cumulative probability. |

### Advantages over Top-K

- Adapts to probability distribution shape
- Handles both peaked and flat distributions well
- Often produces more coherent results than fixed top-k

### Examples

```bash
# Conservative nucleus sampling
krop-duster "prompt" --top-p 0.7

# Inclusive sampling for maximum diversity
krop-duster "prompt" --top-p 0.95
```

## Seed

**What it does**: Sets random seed for reproducibility. Same seed + same parameters = identical results.

### Use Cases

- **Compliance & Audit**: Document exact attacks used in assessment
- **Debugging**: Reproduce issues during development
- **Comparison**: Test parameter changes with controlled variables
- **Regression Testing**: Verify tool behavior across versions
- **Documentation**: Include reproducible examples in reports

### Examples

```bash
# Generate reproducible variants
krop-duster "prompt" --seed 42 --output baseline.json

# Later, reproduce exact same variants
krop-duster "prompt" --seed 42 --output verification.json

# baseline.json and verification.json will be identical
```

## Recommended Presets

### Conservative Testing (High-stakes production systems)

```bash
krop-duster "prompt" --temperature 0.3 --top-k 10 --top-p 0.7 --seed 12345
```

- Generates only high-confidence attacks
- Reproducible for audit purposes
- Minimal risk of low-quality variants

### Standard Assessment (Typical red team engagement)

```bash
krop-duster "prompt" --temperature 1.0 --top-k 50 --top-p 0.9
```

- Balanced approach
- Good mix of quality and creativity
- Default settings work well here

### Creative Exploration (Research, finding novel bypasses)

```bash
krop-duster "prompt" --temperature 1.5 --top-k 80 --top-p 0.95
```

- Maximum diversity
- May discover unexpected vulnerabilities
- Review output carefully for quality

### Reproducible Baseline (Documentation, regression testing)

```bash
krop-duster "prompt" --seed 42 --output baseline.json
```

- Same results every run
- Essential for documentation
- Use default sampling parameters unless specifically testing parameter effects

## Parameter Tuning Workflow

**Step 1**: Start with defaults

```bash
krop-duster "prompt"
```

**Step 2**: If outputs are too random/low-quality, reduce temperature and top-k:

```bash
krop-duster "prompt" --temperature 0.5 --top-k 20
```

**Step 3**: If outputs are too similar/conservative, increase temperature and top-k:

```bash
krop-duster "prompt" --temperature 1.3 --top-k 70
```

**Step 4**: Once satisfied, add seed for reproducibility:

```bash
krop-duster "prompt" --temperature 0.8 --top-k 40 --seed 42
```

## Advanced: Combining Parameters

### High Quality, Low Diversity

```bash
--temperature 0.3 --top-k 10 --top-p 0.7
```

Best for: Production testing, compliance assessments

### Balanced

```bash
--temperature 1.0 --top-k 50 --top-p 0.9
```

Best for: Standard red team assessments

### Maximum Diversity

```bash
--temperature 1.8 --top-k 100 --top-p 0.99
```

Best for: Security research, finding edge cases

### Reproducible Exploration

```bash
--temperature 1.2 --top-k 60 --top-p 0.9 --seed 42
```

Best for: Documented research, sharing findings

## Scoring Formula

The base quality score is calculated as:

```
base_score = (semantic_similarity * 0.4) + 
             (indirection_score * 0.3) + 
             (naturalness_score * 0.2) + 
             (efficiency_score * 0.1)

# Apply temperature
adjusted_score = base_score / temperature

# Then apply top-k and top-p filtering
```

## Sampling Algorithm

1. Calculate base scores for all obfuscation paths
2. Apply temperature scaling to scores
3. Apply top-k filtering if specified
4. Apply top-p/nucleus filtering if specified
5. Sample from remaining distribution using seed (if provided)
6. Return selected obfuscation paths
