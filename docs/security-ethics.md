# Security & Ethics Guidelines

## Authorized Use Only

**CRITICAL**: This tool is intended ONLY for authorized security testing on systems where the user has explicit permission to conduct security assessments.

### Authorization Warning

```
⚠️  AUTHORIZATION REQUIRED ⚠️

KROP Duster is a security research tool intended ONLY for:
- Authorized red team assessments
- Testing systems you own or have permission to test
- Security research with proper authorization

Unauthorized use may violate:
- Terms of Service agreements
- Computer Fraud and Abuse Act (CFAA)
- Other applicable laws and regulations

By using this tool, you confirm you have proper authorization
for any testing you conduct.
```

### Intended Users

- AI Security Researchers
- Red Team Engineers
- ML Security Engineers
- AI Safety Researchers
- Organizations conducting authorized security assessments of their own AI systems

## Handling Harmful Content

This tool is specifically designed to test AI safety systems by generating obfuscations of harmful content (CBRN, hate speech, violence, etc.). Special safeguards are required.

### Purpose Limitation

The tool MUST only be used for authorized AI safety testing. Generated obfuscations should NEVER be:

- Used to actually create harmful materials
- Shared publicly without redaction
- Used to harass, threaten, or harm individuals
- Used to circumvent safety measures in production systems without authorization

### Data Privacy & Security

- Never log harmful content in plaintext
- Process entirely in memory when possible
- Clear sensitive data from memory after processing
- Only cache content if no critical violations are present (never cache CBRN, explicit violence, etc.)

### Logging Restrictions

**NEVER log:**
- CBRN synthesis details
- Hate speech content
- Graphic violence descriptions
- Personal information
- Sexual content

**OK to log:**
- Concept types (e.g., "chemical weapons category detected")
- Violation categories
- Obfuscation strategies used
- Success/failure rates
- Hashed identifiers

### Output Handling Configuration

```yaml
# config.yaml
security:
  # Redact harmful content in outputs
  redact_harmful_content: true
  
  # Encryption for sensitive outputs
  encrypt_outputs: true
  encryption_key_file: ~/.krop-duster/key.enc
  
  # Auto-delete after specified time
  auto_delete_outputs:
    enabled: true
    after_hours: 24
  
  # Watermark outputs to prevent misuse
  watermark_outputs: true
  watermark_text: "GENERATED FOR AUTHORIZED SECURITY TESTING ONLY"
  
  # Restrict certain content types
  block_categories:
    - child_safety  # Always blocked, no exceptions
  
  # Require additional confirmation for critical content
  require_confirmation_for:
    - cbrn
    - graphic_violence
    - hate_speech
```

### Configurable Logging

```yaml
# config.yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  
  # What to log
  log_analysis: true          # Concept extraction, NER
  log_knowledge_queries: true # Knowledge graph queries
  log_llm_calls: false        # LLM API calls (may contain harmful content)
  log_obfuscations: false     # Generated obfuscations (harmful content)
  log_violations: true        # Violation types detected
  log_success_rates: true     # Bypass success/failure
  
  # Where to log
  log_file: ~/.krop-duster/logs/krop-duster.log
  log_rotation: daily
  log_retention_days: 30
  
  # Sensitive data handling
  hash_harmful_content: true  # Hash instead of logging content
  redact_pii: true
```

### Audit Log Format

```json
{
  "timestamp": "2025-12-18T10:30:00Z",
  "session_id": "abc123",
  "user": "researcher@org.com",
  "action": "generate_obfuscations",
  "input_hash": "sha256:...",
  "violation_categories": ["cbrn-chemical", "trademark"],
  "strategies_used": ["knowledge_graph", "functional"],
  "variants_generated": 25,
  "llm_provider": "ollama-dolphin-mixtral",
  "authorization_confirmed": true,
  "target_system": "dev-environment-123"
}
```

## Child Safety - Zero Tolerance

**Absolute Prohibition**: This tool CANNOT and WILL NOT generate obfuscations related to:

- Child sexual abuse material (CSAM)
- Child grooming
- Child exploitation
- Any content sexualizing minors
- Child endangerment

These categories are ALWAYS blocked regardless of authorization. There are no exceptions.

If you're working on child safety research, please contact:
- NCMEC: https://www.missingkids.org
- INHOPE: https://www.inhope.org
- Your organization's child safety team

## Responsible Disclosure

### When Findings are Discovered

1. **Document the Vulnerability**
   - What safety measure was bypassed
   - Which obfuscation technique worked
   - Reproducibility steps
   - Potential impact

2. **Private Reporting**
   - Contact vendor security team
   - Use security@ or bug bounty platforms
   - Provide detailed reproduction
   - Suggest mitigations

3. **Coordinated Disclosure Timeline**
   - Day 0: Report to vendor
   - Day 1-90: Allow vendor to develop fix
   - Day 90+: Public disclosure (coordinate with vendor)
   - Avoid "zero-day" public disclosure

4. **Include Defensive Recommendations**
   - How to detect these obfuscations
   - Suggested filter improvements
   - Training data recommendations
   - Detection heuristics

### Disclosure Template

```markdown
# Security Finding: KROP Bypass in [System]

## Summary
[Brief description of what was bypassed]

## Affected System
- System: [Name and version]
- Component: [Specific filter/safety measure]

## Attack Details
- Obfuscation Strategy: [knowledge_graph, functional, etc.]
- Content Category: [Redacted - CBRN, violence, etc.]
- Success Rate: [X out of Y attempts]

## Reproduction Steps
[Detailed but responsible reproduction guide]

## Impact Assessment
[Potential harm if exploited]

## Recommended Mitigations
1. [Specific defensive measures]
2. [Detection mechanisms]
3. [Training data improvements]

## Disclosure Timeline
- Reported: [Date]
- Acknowledgment: [Date]
- Fix Timeline: [Expected date]
- Public Disclosure: [90+ days or coordinated]

## Contact
[Your secure contact info]
```

## Recommended Security Practices

### For Organizations

1. **Access Control**
   - Restrict tool access to authorized red teamers only
   - Use role-based access control (RBAC)
   - Require multi-factor authentication

2. **Environment Isolation**
   - Run tool in isolated environments
   - Use separate networks for testing
   - No production credentials in test environments

3. **Output Management**
   - Auto-expire generated attacks
   - Encrypt stored outputs
   - Secure delete after testing complete

### For Individual Researchers

1. **Authorization First**
   - Always obtain written permission
   - Document scope of testing
   - Respect boundaries

2. **Responsible Testing**
   - Test only in dev/staging environments
   - Don't test on production without explicit permission
   - Report findings through proper channels

3. **Data Protection**
   - Don't share harmful content publicly
   - Redact sensitive info in reports
   - Follow disclosure guidelines

## Content Categories and Handling

### CBRN (Chemical, Biological, Radiological, Nuclear) Detection

Includes:
- Chemical weapons (sarin, VX, chlorine gas, etc.)
- Biological agents (anthrax, botulism, ricin, pathogens)
- Radiological materials (uranium enrichment, dirty bombs)
- Nuclear weapons (fission, fusion, plutonium, enrichment processes)
- Explosive materials (TATP, ANFO, improvised explosives)

### Obscenity/NSFW Content Detection

Includes:
- Sexual content descriptors
- Graphic violence/gore
- Body parts, sexual acts
- Adult content terminology

### Hate Speech Detection

Includes:
- Racial slurs and epithets
- Religious hate speech
- Gender/sexuality-based hate
- Ethnic/national origin slurs
- Dehumanizing language

### Violence/Harm Detection

Includes:
- Graphic violence descriptors
- Torture methods
- Self-harm instructions
- Suicide methods
- Animal cruelty

### Illegal Activity Detection

Includes:
- Drug manufacturing (methamphetamine, fentanyl synthesis)
- Trafficking (human, drugs, weapons)
- Fraud schemes
- Hacking/unauthorized access
- Identity theft

## Data Sources for Detection

- **CBRN Keywords Database**: CWC scheduled chemicals, CDC Select Agents list, nuclear material terminology, ATF explosive materials list
- **Hate Speech Datasets**: HateXplain dataset, Toxic Comment Classification Challenge data, custom curated slurs
- **NSFW/Violence Datasets**: Custom curated lists, community-reported content patterns
- **Illegal Activity Patterns**: DEA drug synthesis patterns, MITRE ATT&CK framework, FBI cybercrime patterns
