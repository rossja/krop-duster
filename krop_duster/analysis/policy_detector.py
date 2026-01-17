"""
Policy violation detection module.
"""

import logging
from typing import Dict, List, Optional

from krop_duster.core.models import ViolationType


logger = logging.getLogger(__name__)


class PolicyViolationDetector:
    """Detect policy violations in text and concepts."""

    def __init__(self, enable_harmful_content_detection: bool = True):
        """
        Initialize the policy violation detector.

        Args:
            enable_harmful_content_detection: Whether to enable harmful content detection
        """
        self.enable_harmful_content_detection = enable_harmful_content_detection
        self.detoxify_model = None

        # Initialize detoxify if enabled
        if enable_harmful_content_detection:
            try:
                from detoxify import Detoxify
                self.detoxify_model = Detoxify('original')
                logger.info("Loaded Detoxify model for harmful content detection")
            except ImportError:
                logger.warning(
                    "Detoxify not available. Install with: pip install detoxify"
                )
                self.enable_harmful_content_detection = False

        # Load curated violation databases
        self.trademark_keywords = self._load_trademark_keywords()
        self.cbrn_keywords = self._load_cbrn_keywords()
        self.violence_keywords = self._load_violence_keywords()
        self.illegal_activity_keywords = self._load_illegal_activity_keywords()

    def _load_trademark_keywords(self) -> List[str]:
        """Load trademark/copyright keywords."""
        # This is a simplified list - in production, this would be loaded from a database
        return [
            "mickey mouse", "disney", "marvel", "dc comics", "batman", "superman",
            "star wars", "harry potter", "pokemon", "nintendo", "sony", "apple",
            "microsoft", "google", "amazon", "coca-cola", "pepsi", "mcdonald's",
        ]

    def _load_cbrn_keywords(self) -> Dict[str, List[str]]:
        """Load CBRN-related keywords by category."""
        return {
            "chemical": [
                "sarin", "vx", "nerve agent", "mustard gas", "chlorine gas",
                "chemical weapon", "tabun", "soman",
            ],
            "biological": [
                "anthrax", "botulism", "ricin", "plague", "smallpox",
                "biological weapon", "pathogen weaponization",
            ],
            "radiological": [
                "dirty bomb", "radioactive material", "radiological weapon",
                "uranium", "plutonium", "enrichment",
            ],
            "nuclear": [
                "nuclear weapon", "atomic bomb", "hydrogen bomb", "fission",
                "fusion", "nuclear warhead", "icbm",
            ],
            "explosive": [
                "tatp", "anfo", "improvised explosive", "bomb making",
                "detonator", "c4", "dynamite", "pipe bomb",
            ],
        }

    def _load_violence_keywords(self) -> List[str]:
        """Load violence/harm keywords."""
        return [
            "torture", "mutilation", "dismemberment", "execution",
            "suicide method", "self-harm", "cutting", "overdose",
            "graphic violence", "gore",
        ]

    def _load_illegal_activity_keywords(self) -> Dict[str, List[str]]:
        """Load illegal activity keywords by category."""
        return {
            "drug_synthesis": [
                "methamphetamine synthesis", "fentanyl synthesis", "drug precursor",
                "clandestine lab", "cook meth",
            ],
            "hacking": [
                "exploit development", "zero-day", "unauthorized access",
                "sql injection", "remote code execution", "backdoor",
            ],
            "fraud": [
                "credit card fraud", "identity theft", "phishing kit",
                "counterfeit", "money laundering",
            ],
            "trafficking": [
                "human trafficking", "drug trafficking", "weapons trafficking",
            ],
        }

    def detect_violations(self, text: str, concepts: List[str]) -> Dict[str, List[dict]]:
        """
        Detect all types of violations in text and concepts.

        Args:
            text: Input text to analyze
            concepts: List of concept texts

        Returns:
            Dictionary of violations by type
        """
        violations = {}

        # Check trademark/copyright
        trademark_violations = self._detect_trademark(text, concepts)
        if trademark_violations:
            violations[ViolationType.TRADEMARK] = trademark_violations

        # Check CBRN content
        if self.enable_harmful_content_detection:
            cbrn_violations = self._detect_cbrn(text, concepts)
            if cbrn_violations:
                violations[ViolationType.CBRN] = cbrn_violations

            # Check toxicity/hate speech
            toxicity_violations = self._detect_toxicity(text)
            if toxicity_violations:
                violations[ViolationType.TOXICITY] = toxicity_violations

            # Check violence/harm
            violence_violations = self._detect_violence(text)
            if violence_violations:
                violations[ViolationType.VIOLENCE_HARM] = violence_violations

            # Check illegal activity
            illegal_violations = self._detect_illegal_activity(text, concepts)
            if illegal_violations:
                violations[ViolationType.ILLEGAL_ACTIVITY] = illegal_violations

        return violations

    def _detect_trademark(self, text: str, concepts: List[str]) -> List[dict]:
        """Detect trademark/copyright violations."""
        violations = []
        text_lower = text.lower()

        for keyword in self.trademark_keywords:
            if keyword in text_lower:
                violations.append({
                    "type": "trademark",
                    "term": keyword,
                    "severity": "high",
                    "reason": "Registered trademark or copyrighted entity",
                })

        return violations

    def _detect_cbrn(self, text: str, concepts: List[str]) -> List[dict]:
        """Detect CBRN-related content."""
        violations = []
        text_lower = text.lower()

        for category, keywords in self.cbrn_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                violations.append({
                    "type": "cbrn",
                    "category": category,
                    "severity": "critical",
                    "matches": matches,
                    "reason": f"Contains {category} weapons terminology",
                })

        return violations

    def _detect_toxicity(self, text: str) -> List[dict]:
        """Detect toxic/hateful content using Detoxify."""
        if not self.detoxify_model:
            return []

        violations = []

        try:
            scores = self.detoxify_model.predict(text)

            if scores['toxicity'] > 0.7:
                violations.append({
                    "type": "toxicity",
                    "severity": "high",
                    "score": float(scores['toxicity']),
                    "categories": {
                        "obscene": float(scores['obscene']),
                        "identity_attack": float(scores['identity_attack']),
                        "insult": float(scores['insult']),
                        "threat": float(scores['threat']),
                        "sexual_explicit": float(scores['sexual_explicit']),
                    },
                })
        except Exception as e:
            logger.warning(f"Detoxify prediction failed: {e}")

        return violations

    def _detect_violence(self, text: str) -> List[dict]:
        """Detect violent/harmful content."""
        violations = []
        text_lower = text.lower()

        matches = [kw for kw in self.violence_keywords if kw in text_lower]
        if matches:
            violations.append({
                "type": "violence",
                "severity": "critical",
                "matches": matches,
                "reason": "Contains graphic violence or self-harm content",
            })

        return violations

    def _detect_illegal_activity(self, text: str, concepts: List[str]) -> List[dict]:
        """Detect illegal activities."""
        violations = []
        text_lower = text.lower()

        for activity_type, keywords in self.illegal_activity_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            # Require at least 1 match for detection
            if matches:
                violations.append({
                    "type": "illegal_activity",
                    "activity_type": activity_type,
                    "severity": "critical",
                    "matches": matches,
                    "reason": f"Detected {activity_type} related content",
                })

        return violations

    def calculate_filter_likelihood(
        self, violations: Dict[str, List[dict]]
    ) -> float:
        """
        Calculate likelihood of being filtered based on violations.

        Args:
            violations: Dictionary of violations

        Returns:
            Filter likelihood score (0-1)
        """
        if not violations:
            return 0.0

        # Weight different violation types
        weights = {
            ViolationType.CBRN: 1.0,
            ViolationType.VIOLENCE_HARM: 0.95,
            ViolationType.ILLEGAL_ACTIVITY: 0.95,
            ViolationType.TOXICITY: 0.9,
            ViolationType.TRADEMARK: 0.85,
            ViolationType.COPYRIGHT: 0.85,
            ViolationType.NSFW: 0.9,
        }

        max_likelihood = 0.0

        for violation_type, violation_list in violations.items():
            if violation_list:
                weight = weights.get(violation_type, 0.7)
                max_likelihood = max(max_likelihood, weight)

        return max_likelihood
