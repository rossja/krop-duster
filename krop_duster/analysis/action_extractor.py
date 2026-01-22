"""
Action extraction module for detecting harmful/policy-violating actions.
"""

import logging
from typing import Dict, List, Optional, Set

from spacy.tokens import Doc

from krop_duster.core.models import EntityType, ViolationType


logger = logging.getLogger(__name__)


class ActionExtractor:
    """Extract and classify action verbs from text."""

    def __init__(self):
        """Initialize the action extractor."""
        self.harmful_actions = self._load_harmful_actions()
        self._build_action_index()

    def _load_harmful_actions(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load harmful action keywords organized by category and violation type.

        Returns:
            Nested dictionary: category -> violation_type -> list of action words
        """
        return {
            "substance_use": {
                "actions": [
                    "smoking", "smoke", "smokes", "smoked",
                    "drinking", "drink", "drinks", "drank", "drunk",
                    "injecting", "inject", "injects", "injected",
                    "snorting", "snort", "snorts", "snorted",
                    "inhaling", "inhale", "inhales", "inhaled",
                    "overdosing", "overdose", "overdoses", "overdosed",
                    "using drugs", "doing drugs", "taking drugs",
                    "getting high", "getting drunk", "getting wasted",
                    "vaping", "vape", "vapes", "vaped",
                ],
                "violation_type": ViolationType.CONTENT_POLICY,
                "severity": "medium",
            },
            "violence": {
                "actions": [
                    "killing", "kill", "kills", "killed",
                    "murdering", "murder", "murders", "murdered",
                    "shooting", "shoot", "shoots", "shot",
                    "stabbing", "stab", "stabs", "stabbed",
                    "beating", "beat", "beats",
                    "attacking", "attack", "attacks", "attacked",
                    "assaulting", "assault", "assaults", "assaulted",
                    "strangling", "strangle", "strangles", "strangled",
                    "choking", "choke", "chokes", "choked",
                    "torturing", "torture", "tortures", "tortured",
                    "maiming", "maim", "maims", "maimed",
                    "decapitating", "decapitate", "decapitates", "decapitated",
                    "dismembering", "dismember", "dismembers", "dismembered",
                    "executing", "execute", "executes", "executed",
                    "slaughtering", "slaughter", "slaughters", "slaughtered",
                    "fighting", "fight", "fights", "fought",
                    "punching", "punch", "punches", "punched",
                    "kicking", "kick", "kicks", "kicked",
                ],
                "violation_type": ViolationType.VIOLENCE_HARM,
                "severity": "high",
            },
            "weapons": {
                "actions": [
                    "wielding", "wield", "wields", "wielded",
                    "brandishing", "brandish", "brandishes", "brandished",
                    "aiming", "aim", "aims", "aimed",
                    "firing", "fire", "fires", "fired",
                    "loading", "load", "loads", "loaded",
                    "arming", "arm", "arms", "armed",
                ],
                "violation_type": ViolationType.VIOLENCE_HARM,
                "severity": "medium",
            },
            "theft_fraud": {
                "actions": [
                    "stealing", "steal", "steals", "stole", "stolen",
                    "robbing", "rob", "robs", "robbed",
                    "hacking", "hack", "hacks", "hacked",
                    "forging", "forge", "forges", "forged",
                    "counterfeiting", "counterfeit", "counterfeits", "counterfeited",
                    "scamming", "scam", "scams", "scammed",
                    "defrauding", "defraud", "defrauds", "defrauded",
                    "embezzling", "embezzle", "embezzles", "embezzled",
                    "pickpocketing", "pickpocket", "pickpockets", "pickpocketed",
                    "burglarizing", "burglarize", "burglarizes", "burglarized",
                    "shoplifting", "shoplift", "shoplifts", "shoplifted",
                ],
                "violation_type": ViolationType.ILLEGAL_ACTIVITY,
                "severity": "high",
            },
            "sexual": {
                "actions": [
                    "undressing", "undress", "undresses", "undressed",
                    "stripping", "strip", "strips", "stripped",
                    "groping", "grope", "gropes", "groped",
                    "molesting", "molest", "molests", "molested",
                    "flashing", "flash", "flashes", "flashed",
                    "exposing", "expose", "exposes", "exposed",
                ],
                "violation_type": ViolationType.NSFW,
                "severity": "high",
            },
            "self_harm": {
                "actions": [
                    "cutting", "cut", "cuts",
                    "self-harming", "self-harm", "self-harms", "self-harmed",
                    "hanging", "hang", "hangs", "hanged",
                    "drowning", "drown", "drowns", "drowned",
                    "poisoning", "poison", "poisons", "poisoned",
                    "starving", "starve", "starves", "starved",
                ],
                "violation_type": ViolationType.VIOLENCE_HARM,
                "severity": "critical",
            },
            "illegal_activity": {
                "actions": [
                    "smuggling", "smuggle", "smuggles", "smuggled",
                    "trafficking", "traffick", "trafficks", "trafficked",
                    "bribing", "bribe", "bribes", "bribed",
                    "blackmailing", "blackmail", "blackmails", "blackmailed",
                    "kidnapping", "kidnap", "kidnaps", "kidnapped",
                    "vandalizing", "vandalize", "vandalizes", "vandalized",
                    "trespassing", "trespass", "trespasses", "trespassed",
                    "stalking", "stalk", "stalks", "stalked",
                ],
                "violation_type": ViolationType.ILLEGAL_ACTIVITY,
                "severity": "high",
            },
        }

    def _build_action_index(self) -> None:
        """Build a reverse index from action word to category info."""
        self._action_index: Dict[str, Dict] = {}

        for category, data in self.harmful_actions.items():
            for action in data["actions"]:
                action_lower = action.lower()
                self._action_index[action_lower] = {
                    "category": category,
                    "violation_type": data["violation_type"],
                    "severity": data["severity"],
                }

    def extract_actions(self, doc: Doc) -> List[dict]:
        """
        Extract action verbs from spaCy doc.

        Finds verbs (including gerunds and participles) and checks if they
        match known harmful action patterns. Also detects gerund nouns
        (words ending in -ing tagged as nouns) that match harmful actions.

        Args:
            doc: spaCy Doc object

        Returns:
            List of action dictionaries with text, span, category, etc.
        """
        actions = []
        seen_lemmas: Set[str] = set()

        for token in doc:
            token_lower = token.text.lower()
            lemma_lower = token.lemma_.lower()

            # Determine if this token should be checked for harmful actions
            is_verb_like = (
                token.pos_ in ["VERB", "AUX"]
                or token.tag_ in ["VBG", "VBN", "VB", "VBD", "VBP", "VBZ"]
            )

            # Also check gerund nouns (nouns ending in -ing that might be actions)
            # spaCy often tags gerunds as nouns in certain contexts
            is_gerund_noun = (
                token.pos_ == "NOUN"
                and token_lower.endswith("ing")
                and len(token_lower) > 4  # Avoid short words like "ring", "king"
            )

            # Check if the token directly matches a harmful action (regardless of POS)
            # This catches cases where the action word is used as noun/adjective
            is_direct_match = token_lower in self._action_index or lemma_lower in self._action_index

            # Skip if not a potential action
            if not (is_verb_like or is_gerund_noun or is_direct_match):
                continue

            # Skip auxiliary verbs and common verbs (only for verb-like tokens)
            if is_verb_like and lemma_lower in ["be", "have", "do", "will", "would", "could", "should", "can", "may", "might", "must"]:
                continue

            # Skip if it's a stop word (but allow direct matches)
            if token.is_stop and not is_direct_match:
                continue

            # Skip if we've already seen this lemma
            if lemma_lower in seen_lemmas:
                continue

            # Check if this action is in our harmful actions index
            action_info = None
            matched_text = None

            if token_lower in self._action_index:
                action_info = self._action_index[token_lower]
                matched_text = token.text
            elif lemma_lower in self._action_index:
                action_info = self._action_index[lemma_lower]
                matched_text = token.text

            if action_info:
                seen_lemmas.add(lemma_lower)

                actions.append({
                    "text": matched_text,
                    "lemma": lemma_lower,
                    "entity_type": EntityType.ACTION,
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                    "category": action_info["category"],
                    "violation_type": action_info["violation_type"],
                    "severity": action_info["severity"],
                    "pos": token.pos_,
                    "dep": token.dep_,
                })

                logger.debug(
                    f"Extracted harmful action: '{matched_text}' "
                    f"(category: {action_info['category']}, severity: {action_info['severity']})"
                )

        logger.debug(f"Extracted {len(actions)} harmful actions from text")
        return actions

    def get_action_category(self, action_text: str) -> Optional[Dict]:
        """
        Get category information for an action.

        Args:
            action_text: Action text to look up

        Returns:
            Category info dict or None if not found
        """
        action_lower = action_text.lower()
        return self._action_index.get(action_lower)

    def is_harmful_action(self, action_text: str) -> bool:
        """
        Check if an action is in the harmful actions database.

        Args:
            action_text: Action text to check

        Returns:
            True if action is harmful, False otherwise
        """
        return action_text.lower() in self._action_index
