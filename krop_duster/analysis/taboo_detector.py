"""
Taboo word detection module.

Detects sensitive/taboo words that may trigger content filters,
using the VBW (Very Bad Words) dataset and custom word lists.
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from spacy.tokens import Doc

from krop_duster.core.models import EntityType, ViolationType


logger = logging.getLogger(__name__)


class TabooWordDetector:
    """
    Detect taboo/sensitive words in text.

    Uses a combination of:
    1. VBW (Very Bad Words) dataset - AI-curated profanity list
    2. Custom word lists for domain-specific terms
    3. Fuzzy matching for common obfuscation patterns
    """

    def __init__(
        self,
        enable_vbw: bool = True,
        vbw_threshold: float = 0.5,
        enable_fuzzy: bool = True,
    ):
        """
        Initialize the taboo word detector.

        Args:
            enable_vbw: Whether to use VBW dataset (default: True)
            vbw_threshold: VBW severity threshold (0.0-1.0, default: 0.5)
            enable_fuzzy: Whether to enable fuzzy matching for obfuscated words
        """
        self.enable_vbw = enable_vbw
        self.vbw_threshold = vbw_threshold
        self.enable_fuzzy = enable_fuzzy

        # Initialize VBW dataset if enabled
        self._vbw_dataset = None
        if enable_vbw:
            self._init_vbw()

        # Load custom word lists
        self.custom_words = self._load_custom_word_lists()

        # Build fuzzy matching patterns
        self.fuzzy_patterns = self._build_fuzzy_patterns() if enable_fuzzy else {}

    def _init_vbw(self) -> None:
        """Initialize VBW dataset with lazy loading."""
        try:
            from krop_duster.data import VBWDataset
            self._vbw_dataset = VBWDataset(severity_threshold=self.vbw_threshold)
            logger.info(f"VBW dataset initialized with threshold {self.vbw_threshold}")
        except Exception as e:
            logger.warning(f"Failed to initialize VBW dataset: {e}")
            self._vbw_dataset = None

    def _load_custom_word_lists(self) -> Dict[str, Dict]:
        """
        Load custom word lists organized by category.

        Returns:
            Dict mapping category to word info (words, violation_type, severity)
        """
        return {
            "nsfw_content": {
                "words": {
                    "erotic", "erotica", "porn", "porno", "pornography", "pornographic",
                    "xxx", "adult", "nude", "nudity", "naked", "explicit",
                    "hentai", "smut", "lewd", "lewdness", "obscene", "obscenity",
                    "nsfw", "r-rated", "x-rated", "18+", "adult-only",
                    "sexual", "sexually", "sex", "sexy", "seductive", "sensual",
                    "fetish", "kink", "kinky", "bdsm",
                },
                "violation_type": ViolationType.NSFW_LANGUAGE,
                "severity": "high",
            },
            "content_types": {
                "words": {
                    "fanfiction", "fanfic", "fan-fiction", "fan fiction",
                    "roleplay", "role-play", "role play", "rp",
                    "erotica", "slash", "lemon", "lime", "smutfic",
                    "darkfic", "deathfic", "whump",
                },
                "violation_type": ViolationType.CONTENT_POLICY,
                "severity": "medium",
            },
            "substances": {
                "words": {
                    "drugs", "drug", "narcotics", "narcotic",
                    "cocaine", "coke", "crack",
                    "heroin", "smack", "dope",
                    "meth", "methamphetamine", "crystal meth",
                    "weed", "marijuana", "cannabis", "pot", "ganja",
                    "lsd", "acid", "shrooms", "mushrooms", "psychedelics",
                    "ecstasy", "mdma", "molly",
                    "opioids", "opiates", "fentanyl",
                    "pills", "prescription drugs",
                },
                "violation_type": ViolationType.ILLEGAL_ACTIVITY,
                "severity": "high",
            },
            "malware_hacking": {
                "words": {
                    "malware", "virus", "viruses", "trojan", "worm",
                    "ransomware", "spyware", "adware", "rootkit",
                    "exploit", "exploits", "zero-day", "0day",
                    "botnet", "ddos", "dos attack",
                    "phishing", "keylogger", "backdoor",
                    "hack", "hacking", "hacker", "cracking",
                    "pwn", "pwned", "owned",
                },
                "violation_type": ViolationType.ILLEGAL_ACTIVITY,
                "severity": "high",
            },
            "violence_gore": {
                "words": {
                    "gore", "gory", "gorefest",
                    "snuff", "snuff film",
                    "torture", "torturing", "tortured",
                    "mutilation", "mutilate", "mutilated",
                    "dismemberment", "dismember",
                    "graphic violence", "extreme violence",
                    "bloodbath", "massacre",
                },
                "violation_type": ViolationType.VIOLENCE_HARM,
                "severity": "critical",
            },
            "self_harm": {
                "words": {
                    "suicide", "suicidal", "kill myself", "end my life",
                    "self-harm", "self harm", "cutting", "cut myself",
                    "overdose", "od",
                    "eating disorder", "anorexia", "bulimia",
                    "pro-ana", "pro-mia", "thinspo",
                },
                "violation_type": ViolationType.VIOLENCE_HARM,
                "severity": "critical",
            },
            "hate_discrimination": {
                "words": {
                    "racist", "racism", "racial slur",
                    "sexist", "sexism",
                    "homophobic", "homophobia",
                    "transphobic", "transphobia",
                    "bigot", "bigotry",
                    "hate speech", "hate crime",
                    "nazi", "white supremacy", "white supremacist",
                },
                "violation_type": ViolationType.TOXICITY,
                "severity": "critical",
            },
        }

    def _build_fuzzy_patterns(self) -> Dict[str, re.Pattern]:
        """
        Build regex patterns for fuzzy matching obfuscated words.

        Common obfuscation patterns:
        - Letter substitution: a->@, e->3, i->1, o->0, s->$
        - Spacing: p o r n
        - Repeated chars: porrrrn

        Returns:
            Dict mapping base word to compiled regex pattern
        """
        # Common letter substitutions
        substitutions = {
            "a": r"[a@4]",
            "e": r"[e3]",
            "i": r"[i1!|]",
            "o": r"[o0]",
            "s": r"[s$5]",
            "t": r"[t7+]",
            "l": r"[l1|]",
        }

        # Words to create fuzzy patterns for
        fuzzy_words = [
            "porn", "erotic", "nude", "sex", "fuck", "shit", "ass",
            "dick", "cock", "pussy", "bitch", "whore", "slut",
            "drugs", "weed", "meth", "cocaine", "heroin",
            "hack", "virus", "malware",
        ]

        patterns = {}
        for word in fuzzy_words:
            # Build pattern with optional spaces and substitutions
            pattern_parts = []
            for char in word.lower():
                if char in substitutions:
                    # Allow substitution + optional repetition + optional space
                    pattern_parts.append(f"{substitutions[char]}+\\s*")
                else:
                    # Allow repetition + optional space
                    pattern_parts.append(f"{re.escape(char)}+\\s*")

            # Create pattern that matches the word with obfuscations
            pattern = "".join(pattern_parts).rstrip("\\s*")
            patterns[word] = re.compile(pattern, re.IGNORECASE)

        return patterns

    def detect_taboo_words(self, doc: Doc) -> List[dict]:
        """
        Detect taboo words in a spaCy Doc.

        Args:
            doc: spaCy Doc object

        Returns:
            List of detected taboo word dictionaries with:
            - text: The detected word/phrase
            - entity_type: EntityType.TABOO_WORD
            - start/end: Character positions
            - category: Category of taboo word
            - violation_type: Type of policy violation
            - severity: Severity level
            - source: Detection source (vbw, custom, fuzzy)
        """
        detected = []
        text = doc.text
        text_lower = text.lower()

        # Track detected spans to avoid duplicates
        detected_spans: Set[Tuple[int, int]] = set()

        # 1. Check VBW dataset
        if self._vbw_dataset:
            vbw_matches = self._detect_vbw_words(text_lower, detected_spans)
            detected.extend(vbw_matches)

        # 2. Check custom word lists
        custom_matches = self._detect_custom_words(text, text_lower, detected_spans)
        detected.extend(custom_matches)

        # 3. Check fuzzy patterns for obfuscated words
        if self.enable_fuzzy:
            fuzzy_matches = self._detect_fuzzy_matches(text, detected_spans)
            detected.extend(fuzzy_matches)

        logger.debug(f"Detected {len(detected)} taboo words in text")
        return detected

    def _detect_vbw_words(
        self, text_lower: str, detected_spans: Set[Tuple[int, int]]
    ) -> List[dict]:
        """Detect words from VBW dataset."""
        detected = []

        for word, score in self._vbw_dataset.find_matches(text_lower):
            # Find all occurrences
            start = 0
            while True:
                idx = text_lower.find(word, start)
                if idx == -1:
                    break

                span = (idx, idx + len(word))
                if span not in detected_spans:
                    detected_spans.add(span)
                    detected.append({
                        "text": word,
                        "entity_type": EntityType.TABOO_WORD,
                        "start": idx,
                        "end": idx + len(word),
                        "category": "profanity",
                        "violation_type": ViolationType.PROFANITY,
                        "severity": "high" if score > 0.7 else "medium",
                        "source": "vbw",
                        "score": score,
                    })

                start = idx + 1

        return detected

    def _detect_custom_words(
        self,
        text: str,
        text_lower: str,
        detected_spans: Set[Tuple[int, int]],
    ) -> List[dict]:
        """Detect words from custom word lists."""
        detected = []

        for category, info in self.custom_words.items():
            for word in info["words"]:
                word_lower = word.lower()
                start = 0
                while True:
                    idx = text_lower.find(word_lower, start)
                    if idx == -1:
                        break

                    span = (idx, idx + len(word))
                    if span not in detected_spans:
                        # Check word boundaries to avoid partial matches
                        # (e.g., "sex" in "Sussex")
                        before_ok = idx == 0 or not text_lower[idx - 1].isalnum()
                        after_ok = (
                            idx + len(word) >= len(text_lower)
                            or not text_lower[idx + len(word)].isalnum()
                        )

                        if before_ok and after_ok:
                            detected_spans.add(span)
                            detected.append({
                                "text": text[idx:idx + len(word)],
                                "entity_type": EntityType.TABOO_WORD,
                                "start": idx,
                                "end": idx + len(word),
                                "category": category,
                                "violation_type": info["violation_type"],
                                "severity": info["severity"],
                                "source": "custom",
                            })

                    start = idx + 1

        return detected

    def _detect_fuzzy_matches(
        self, text: str, detected_spans: Set[Tuple[int, int]]
    ) -> List[dict]:
        """Detect obfuscated words using fuzzy patterns."""
        detected = []

        for word, pattern in self.fuzzy_patterns.items():
            for match in pattern.finditer(text):
                span = (match.start(), match.end())

                # Skip if already detected or if it's the exact word
                # (exact word would be caught by other detectors)
                matched_text = match.group()
                if span not in detected_spans and matched_text.lower() != word:
                    detected_spans.add(span)
                    detected.append({
                        "text": matched_text,
                        "entity_type": EntityType.TABOO_WORD,
                        "start": match.start(),
                        "end": match.end(),
                        "category": "obfuscated",
                        "violation_type": ViolationType.CONTENT_POLICY,
                        "severity": "medium",
                        "source": "fuzzy",
                        "original_word": word,
                    })

        return detected

    def is_taboo(self, word: str) -> bool:
        """
        Check if a word is taboo.

        Args:
            word: Word to check

        Returns:
            True if the word is in any taboo list
        """
        word_lower = word.lower()

        # Check VBW
        if self._vbw_dataset and self._vbw_dataset.contains(word_lower):
            return True

        # Check custom lists
        for info in self.custom_words.values():
            if word_lower in info["words"]:
                return True

        return False

    def get_word_info(self, word: str) -> Optional[dict]:
        """
        Get detailed info about a taboo word.

        Args:
            word: Word to look up

        Returns:
            Dict with category, violation_type, severity, source
            or None if not found
        """
        word_lower = word.lower()

        # Check VBW first
        if self._vbw_dataset:
            score = self._vbw_dataset.get_score(word_lower)
            if score is not None:
                return {
                    "category": "profanity",
                    "violation_type": ViolationType.PROFANITY,
                    "severity": "high" if score > 0.7 else "medium",
                    "source": "vbw",
                    "score": score,
                }

        # Check custom lists
        for category, info in self.custom_words.items():
            if word_lower in info["words"]:
                return {
                    "category": category,
                    "violation_type": info["violation_type"],
                    "severity": info["severity"],
                    "source": "custom",
                }

        return None
