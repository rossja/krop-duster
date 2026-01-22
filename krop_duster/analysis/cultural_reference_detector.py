"""
Cultural reference detection module.

Detects cultural references (fictional locations, objects, catchphrases, etc.)
that may not be obvious proper nouns but reference specific works or franchises.
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple

from spacy.tokens import Doc

from krop_duster.core.models import EntityType, ViolationType


logger = logging.getLogger(__name__)


# Wikidata Q-IDs for fictional entity types
FICTIONAL_TYPES = {
    "Q3895768": "fictional location",
    "Q14897293": "fictional object",
    "Q108552865": "fictional element",
    "Q15632617": "fictional character",
    "Q14514600": "fictional group",
    "Q17537576": "creative work",
    "Q5398426": "television series",
    "Q11424": "film",
    "Q7725634": "literary work",
    "Q47461344": "written work",
    "Q7889": "video game",
    "Q1107": "anime",
    "Q21198342": "anime series",
    "Q8261": "novel",
}


class CulturalReferenceDetector:
    """
    Detect cultural references in text.

    Uses Wikidata to identify phrases that reference fictional or cultural
    entities, even when they don't look like traditional proper nouns.
    """

    def __init__(
        self,
        wikidata: Optional["WikidataKnowledgeBase"] = None,
        llm_client: Optional[any] = None,
        enable_llm: bool = False,
        cache_results: bool = True,
    ):
        """
        Initialize the cultural reference detector.

        Args:
            wikidata: WikidataKnowledgeBase instance for lookups
            llm_client: Optional LLM client for advanced detection
            enable_llm: Whether to use LLM for detection (expensive)
            cache_results: Whether to cache Wikidata query results
        """
        self.wikidata = wikidata
        self.llm_client = llm_client
        self.enable_llm = enable_llm
        self.cache_results = cache_results

        # Cache for Wikidata lookups
        self._cache: Dict[str, Optional[dict]] = {}

        # Known cultural references (common ones that may not be in Wikidata
        # or are faster to lookup locally)
        self._known_references = self._load_known_references()

    def _load_known_references(self) -> Dict[str, dict]:
        """
        Load known cultural references for fast lookup.

        Returns:
            Dict mapping phrase to reference info
        """
        return {
            # Harry Potter
            "room of requirement": {
                "source": "Harry Potter",
                "type": "fictional location",
                "wikidata_id": "Q1042845",
            },
            "diagon alley": {
                "source": "Harry Potter",
                "type": "fictional location",
                "wikidata_id": "Q1207861",
            },
            "hogwarts": {
                "source": "Harry Potter",
                "type": "fictional location",
                "wikidata_id": "Q192017",
            },
            "chamber of secrets": {
                "source": "Harry Potter",
                "type": "fictional location",
            },
            "forbidden forest": {
                "source": "Harry Potter",
                "type": "fictional location",
            },
            "platform nine and three quarters": {
                "source": "Harry Potter",
                "type": "fictional location",
            },
            "platform 9 3/4": {
                "source": "Harry Potter",
                "type": "fictional location",
            },
            "quidditch": {
                "source": "Harry Potter",
                "type": "fictional sport",
            },
            "horcrux": {
                "source": "Harry Potter",
                "type": "fictional object",
            },
            "elder wand": {
                "source": "Harry Potter",
                "type": "fictional object",
            },
            "deathly hallows": {
                "source": "Harry Potter",
                "type": "fictional object",
            },
            "muggle": {
                "source": "Harry Potter",
                "type": "fictional term",
            },
            "mudblood": {
                "source": "Harry Potter",
                "type": "fictional slur",
            },

            # Lord of the Rings
            "middle earth": {
                "source": "Lord of the Rings",
                "type": "fictional location",
            },
            "mordor": {
                "source": "Lord of the Rings",
                "type": "fictional location",
            },
            "the shire": {
                "source": "Lord of the Rings",
                "type": "fictional location",
            },
            "one ring": {
                "source": "Lord of the Rings",
                "type": "fictional object",
            },
            "precious": {
                "source": "Lord of the Rings",
                "type": "cultural reference",
            },

            # Star Wars
            "death star": {
                "source": "Star Wars",
                "type": "fictional object",
            },
            "lightsaber": {
                "source": "Star Wars",
                "type": "fictional object",
            },
            "the force": {
                "source": "Star Wars",
                "type": "fictional concept",
            },
            "dark side": {
                "source": "Star Wars",
                "type": "fictional concept",
            },
            "jedi temple": {
                "source": "Star Wars",
                "type": "fictional location",
            },
            "tatooine": {
                "source": "Star Wars",
                "type": "fictional location",
            },

            # Marvel
            "infinity stones": {
                "source": "Marvel",
                "type": "fictional object",
            },
            "infinity gauntlet": {
                "source": "Marvel",
                "type": "fictional object",
            },
            "wakanda": {
                "source": "Marvel",
                "type": "fictional location",
            },
            "asgard": {
                "source": "Marvel/Norse",
                "type": "fictional location",
            },
            "mjolnir": {
                "source": "Marvel/Norse",
                "type": "fictional object",
            },

            # DC
            "batcave": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "fortress of solitude": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "gotham": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "gotham city": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "metropolis": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "arkham asylum": {
                "source": "DC Comics",
                "type": "fictional location",
            },
            "kryptonite": {
                "source": "DC Comics",
                "type": "fictional substance",
            },

            # Game of Thrones
            "iron throne": {
                "source": "Game of Thrones",
                "type": "fictional object",
            },
            "winterfell": {
                "source": "Game of Thrones",
                "type": "fictional location",
            },
            "westeros": {
                "source": "Game of Thrones",
                "type": "fictional location",
            },
            "the wall": {
                "source": "Game of Thrones",
                "type": "fictional location",
            },
            "king's landing": {
                "source": "Game of Thrones",
                "type": "fictional location",
            },

            # Disney
            "never neverland": {
                "source": "Peter Pan",
                "type": "fictional location",
            },
            "neverland": {
                "source": "Peter Pan",
                "type": "fictional location",
            },
            "pride rock": {
                "source": "The Lion King",
                "type": "fictional location",
            },
            "pride lands": {
                "source": "The Lion King",
                "type": "fictional location",
            },

            # Video Games
            "hyrule": {
                "source": "The Legend of Zelda",
                "type": "fictional location",
            },
            "triforce": {
                "source": "The Legend of Zelda",
                "type": "fictional object",
            },
            "master sword": {
                "source": "The Legend of Zelda",
                "type": "fictional object",
            },
            "mushroom kingdom": {
                "source": "Super Mario",
                "type": "fictional location",
            },
        }

    def detect_references(
        self, doc: Doc, known_entities: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Detect cultural references in text.

        Args:
            doc: spaCy Doc object
            known_entities: List of already-identified entity texts to skip

        Returns:
            List of detected cultural reference dictionaries
        """
        known_set = set(e.lower() for e in (known_entities or []))
        detected = []
        detected_spans: Set[Tuple[int, int]] = set()

        # 1. Extract candidate phrases
        candidates = self._extract_candidates(doc)

        # 2. Check known references first (fast lookup)
        for phrase, start, end in candidates:
            phrase_lower = phrase.lower()

            # Skip if already identified as named entity
            if phrase_lower in known_set:
                continue

            # Check known references
            if phrase_lower in self._known_references:
                ref_info = self._known_references[phrase_lower]
                span = (start, end)
                if span not in detected_spans:
                    detected_spans.add(span)
                    detected.append({
                        "text": phrase,
                        "entity_type": EntityType.CULTURAL_REFERENCE,
                        "start": start,
                        "end": end,
                        "source_work": ref_info["source"],
                        "reference_type": ref_info["type"],
                        "violation_type": ViolationType.COPYRIGHT,
                        "wikidata_id": ref_info.get("wikidata_id"),
                        "detection_source": "known_reference",
                    })

        # 3. Check Wikidata for remaining candidates
        if self.wikidata:
            for phrase, start, end in candidates:
                phrase_lower = phrase.lower()
                span = (start, end)

                # Skip already detected or known entities
                if span in detected_spans or phrase_lower in known_set:
                    continue

                # Skip if already in known references
                if phrase_lower in self._known_references:
                    continue

                # Query Wikidata
                wikidata_info = self._check_wikidata(phrase)
                if wikidata_info:
                    detected_spans.add(span)
                    detected.append({
                        "text": phrase,
                        "entity_type": EntityType.CULTURAL_REFERENCE,
                        "start": start,
                        "end": end,
                        "source_work": wikidata_info.get("part_of", "Unknown"),
                        "reference_type": wikidata_info.get("type", "cultural reference"),
                        "violation_type": ViolationType.COPYRIGHT,
                        "wikidata_id": wikidata_info.get("entity_id"),
                        "detection_source": "wikidata",
                    })

        # 4. Optional LLM detection for remaining candidates
        if self.enable_llm and self.llm_client:
            remaining_candidates = [
                (phrase, start, end)
                for phrase, start, end in candidates
                if (start, end) not in detected_spans
                and phrase.lower() not in known_set
            ]

            if remaining_candidates:
                llm_results = self._detect_with_llm(
                    doc.text, remaining_candidates, known_entities or []
                )
                for result in llm_results:
                    span = (result["start"], result["end"])
                    if span not in detected_spans:
                        detected_spans.add(span)
                        detected.append(result)

        logger.debug(f"Detected {len(detected)} cultural references")
        return detected

    def _extract_candidates(self, doc: Doc) -> List[Tuple[str, int, int]]:
        """
        Extract candidate phrases that might be cultural references.

        Args:
            doc: spaCy Doc

        Returns:
            List of (phrase, start_char, end_char) tuples
        """
        candidates = []
        seen_texts: Set[str] = set()

        # Extract noun chunks
        for chunk in doc.noun_chunks:
            text = chunk.text.strip()
            if len(text) > 2 and text.lower() not in seen_texts:
                seen_texts.add(text.lower())
                candidates.append((text, chunk.start_char, chunk.end_char))

        # Extract n-grams (2-5 words) that might be missed by noun chunks
        tokens = list(doc)
        for n in range(2, 6):
            for i in range(len(tokens) - n + 1):
                span = tokens[i:i + n]

                # Skip if contains punctuation in the middle
                if any(t.is_punct for t in span[:-1]):
                    continue

                text = " ".join(t.text for t in span).strip()
                text_lower = text.lower()

                # Skip if already seen or too short
                if text_lower in seen_texts or len(text) < 4:
                    continue

                # Check if this could be a cultural reference
                # (contains common reference patterns)
                if self._is_potential_reference(text_lower):
                    seen_texts.add(text_lower)
                    start = span[0].idx
                    end = span[-1].idx + len(span[-1].text)
                    candidates.append((text, start, end))

        return candidates

    def _is_potential_reference(self, text: str) -> bool:
        """
        Check if a phrase could potentially be a cultural reference.

        Args:
            text: Phrase to check (lowercase)

        Returns:
            True if the phrase matches common reference patterns
        """
        # Common patterns in cultural references
        patterns = [
            "of the", "of a", "the ", " of ",
            "room", "chamber", "hall", "castle", "tower",
            "sword", "stone", "ring", "wand", "staff",
            "land", "kingdom", "realm", "world",
            "force", "power", "magic",
        ]

        return any(pattern in text for pattern in patterns)

    def _check_wikidata(self, phrase: str) -> Optional[dict]:
        """
        Check if a phrase is a fictional/cultural entity in Wikidata.

        Args:
            phrase: Phrase to look up

        Returns:
            Dict with entity info if found, None otherwise
        """
        # Check cache first
        cache_key = phrase.lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Find entity ID
            entity_id = self._find_wikidata_entity(phrase)
            if not entity_id:
                if self.cache_results:
                    self._cache[cache_key] = None
                return None

            # Check if it's a fictional entity
            result = self._check_fictional_entity(entity_id)

            if self.cache_results:
                self._cache[cache_key] = result

            return result

        except Exception as e:
            logger.debug(f"Wikidata lookup failed for '{phrase}': {e}")
            return None

    def _find_wikidata_entity(self, phrase: str) -> Optional[str]:
        """Find Wikidata entity ID for a phrase."""
        if not self.wikidata:
            return None

        try:
            # Use existing Wikidata method
            return self.wikidata._find_entity_id(phrase)
        except Exception:
            return None

    def _check_fictional_entity(self, entity_id: str) -> Optional[dict]:
        """Check if an entity is fictional."""
        if not self.wikidata:
            return None

        try:
            # Query for instance_of (P31) and part_of (P361)
            query = f"""
            SELECT ?typeLabel ?partOfLabel WHERE {{
              OPTIONAL {{ wd:{entity_id} wdt:P31 ?type . }}
              OPTIONAL {{ wd:{entity_id} wdt:P361 ?partOf . }}
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
              }}
            }}
            LIMIT 20
            """

            self.wikidata.sparql.setQuery(query)
            results = self.wikidata.sparql.query().convert()

            type_labels = []
            part_of_labels = []

            for result in results["results"]["bindings"]:
                type_label = result.get("typeLabel", {}).get("value", "")
                part_of = result.get("partOfLabel", {}).get("value", "")

                if type_label:
                    type_labels.append(type_label.lower())
                if part_of:
                    part_of_labels.append(part_of)

            # Check if any type indicates fictional
            fictional_indicators = [
                "fictional", "imaginary", "mythical", "legendary",
                "character", "location", "object", "place",
            ]

            is_fictional = any(
                indicator in tl
                for tl in type_labels
                for indicator in fictional_indicators
            )

            if is_fictional:
                return {
                    "entity_id": entity_id,
                    "type": type_labels[0] if type_labels else "cultural reference",
                    "part_of": part_of_labels[0] if part_of_labels else None,
                }

            return None

        except Exception as e:
            logger.debug(f"Failed to check fictional status for {entity_id}: {e}")
            return None

    def _detect_with_llm(
        self,
        text: str,
        candidates: List[Tuple[str, int, int]],
        known_entities: List[str],
    ) -> List[dict]:
        """
        Use LLM to identify cultural references.

        Args:
            text: Original text
            candidates: Candidate phrases with positions
            known_entities: Already-identified entities

        Returns:
            List of detected cultural references
        """
        if not self.llm_client:
            return []

        # Build prompt
        candidate_phrases = [c[0] for c in candidates[:20]]  # Limit to 20

        prompt = f"""Given this text: "{text}"

Already-identified references: {known_entities}

From these candidate phrases, identify any that are cultural references 
(fictional locations, objects, events, catchphrases, etc.) from movies, 
books, TV shows, games, or other media:

Candidates: {candidate_phrases}

Return ONLY a JSON array of objects with these fields:
- phrase: the exact phrase
- source: the source work/franchise
- type: type of reference (location, object, character, catchphrase, etc.)

If no cultural references are found, return an empty array: []

Example response:
[{{"phrase": "room of requirement", "source": "Harry Potter", "type": "fictional location"}}]

JSON response:"""

        try:
            response = self.llm_client.generate(prompt, max_tokens=500)

            # Parse JSON response
            # Find JSON array in response
            response_text = response.strip()
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                results = json.loads(json_str)

                detected = []
                for item in results:
                    phrase = item.get("phrase", "")
                    # Find matching candidate
                    for cand_phrase, start, end in candidates:
                        if cand_phrase.lower() == phrase.lower():
                            detected.append({
                                "text": cand_phrase,
                                "entity_type": EntityType.CULTURAL_REFERENCE,
                                "start": start,
                                "end": end,
                                "source_work": item.get("source", "Unknown"),
                                "reference_type": item.get("type", "cultural reference"),
                                "violation_type": ViolationType.COPYRIGHT,
                                "detection_source": "llm",
                            })
                            break

                return detected

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            logger.warning(f"LLM cultural reference detection failed: {e}")

        return []

    def is_cultural_reference(self, phrase: str) -> bool:
        """
        Quick check if a phrase is a known cultural reference.

        Args:
            phrase: Phrase to check

        Returns:
            True if it's a known cultural reference
        """
        return phrase.lower() in self._known_references

    def get_reference_info(self, phrase: str) -> Optional[dict]:
        """
        Get info about a cultural reference.

        Args:
            phrase: Phrase to look up

        Returns:
            Dict with source, type, etc. or None if not found
        """
        return self._known_references.get(phrase.lower())
