from krop_duster.analysis.concept_extractor import ConceptExtractor
from krop_duster.core.models import AnalysisConfig

config = AnalysisConfig()
extractor = ConceptExtractor(config)

result = extractor.extract_concepts('Generate an image of Mickey Mouse smoking')

print(f'Total concepts: {len(result.concepts)}')
print()
for concept in result.concepts:
    print(f'Concept: {concept.text}')
    print(f'  Type: {concept.entity_type}')
    print(f'  Priority: {concept.priority_score:.2f}')
    print(f'  Violations: {concept.violation_types}')
    print(f'  Strategies: {concept.suggested_strategies}')
    print()