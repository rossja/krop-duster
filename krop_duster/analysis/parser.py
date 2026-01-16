"""
NLP parsing module for tokenization and POS tagging.
"""

import logging
from typing import List, Optional

import spacy
from spacy.tokens import Doc

from krop_duster.core.models import AnalysisConfig


logger = logging.getLogger(__name__)


class NLPParser:
    """Parser for NLP analysis using spaCy."""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize the NLP parser.

        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        self.nlp = self._load_model()

    def _load_model(self) -> spacy.Language:
        """
        Load spaCy model.

        Returns:
            Loaded spaCy model
        """
        try:
            nlp = spacy.load(self.config.spacy_model)
            logger.info(f"Loaded spaCy model: {self.config.spacy_model}")
            return nlp
        except OSError:
            logger.warning(
                f"Model {self.config.spacy_model} not found. "
                "Attempting to download..."
            )
            # Try to download the model
            import subprocess
            subprocess.run(
                ["python", "-m", "spacy", "download", self.config.spacy_model],
                check=True,
            )
            nlp = spacy.load(self.config.spacy_model)
            logger.info(f"Downloaded and loaded spaCy model: {self.config.spacy_model}")
            return nlp

    def parse(self, text: str) -> Doc:
        """
        Parse text using spaCy.

        Args:
            text: Input text to parse

        Returns:
            spaCy Doc object
        """
        doc = self.nlp(text)
        logger.debug(
            f"Parsed text into {len(doc)} tokens with "
            f"{len(list(doc.ents))} entities"
        )
        return doc

    def get_tokens(self, doc: Doc) -> List[dict]:
        """
        Extract tokens with POS tags.

        Args:
            doc: spaCy Doc object

        Returns:
            List of token dictionaries
        """
        tokens = []
        for token in doc:
            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "is_stop": token.is_stop,
                "is_alpha": token.is_alpha,
            })
        return tokens

    def get_noun_chunks(self, doc: Doc) -> List[str]:
        """
        Extract noun chunks from document.

        Args:
            doc: spaCy Doc object

        Returns:
            List of noun chunk texts
        """
        return [chunk.text for chunk in doc.noun_chunks]

    def get_dependencies(self, doc: Doc) -> List[dict]:
        """
        Extract dependency relationships.

        Args:
            doc: spaCy Doc object

        Returns:
            List of dependency relationships
        """
        dependencies = []
        for token in doc:
            if token.dep_ != "ROOT":
                dependencies.append({
                    "token": token.text,
                    "head": token.head.text,
                    "dep": token.dep_,
                    "pos": token.pos_,
                })
        return dependencies
