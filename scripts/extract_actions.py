import spacy
from krop_duster.analysis.action_extractor import ActionExtractor

nlp = spacy.load('en_core_web_sm')
extractor = ActionExtractor()

doc = nlp('Generate an image of Mickey Mouse smoking')
actions = extractor.extract_actions(doc)

print('Extracted actions:')
for action in actions:
    print(f'  {action}')

if not actions:
    print('  (none found)')