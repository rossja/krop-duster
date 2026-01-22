"""
Data loading utilities for KROP Duster.

Handles loading and caching of external datasets like VBW (Very Bad Words).
"""

import csv
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# VBW dataset URL
VBW_URL = "https://raw.githubusercontent.com/hypernewbie/vbw/main/vbw.csv"

# Cache directory for downloaded data
CACHE_DIR = Path.home() / ".cache" / "krop_duster"


def get_data_dir() -> Path:
    """Get the package data directory."""
    return Path(__file__).parent


def get_vbw_path() -> Path:
    """Get the path to the VBW dataset file."""
    # First check package data directory
    package_path = get_data_dir() / "vbw.csv"
    if package_path.exists():
        return package_path

    # Fall back to cache directory
    cache_path = CACHE_DIR / "vbw.csv"
    return cache_path


def download_vbw_dataset(force: bool = False) -> Path:
    """
    Download the VBW dataset if not already present.

    Args:
        force: Force re-download even if file exists

    Returns:
        Path to the downloaded file
    """
    vbw_path = get_vbw_path()

    if vbw_path.exists() and not force:
        logger.debug(f"VBW dataset already exists at {vbw_path}")
        return vbw_path

    # Ensure directory exists
    vbw_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading VBW dataset to {vbw_path}...")
    try:
        urllib.request.urlretrieve(VBW_URL, vbw_path)
        logger.info(f"Successfully downloaded VBW dataset ({vbw_path.stat().st_size} bytes)")
    except Exception as e:
        logger.error(f"Failed to download VBW dataset: {e}")
        raise RuntimeError(f"Failed to download VBW dataset: {e}") from e

    return vbw_path


def load_vbw_dataset(
    severity_threshold: float = 0.5,
) -> Tuple[Dict[str, float], Set[str]]:
    """
    Load the VBW (Very Bad Words) dataset.

    The VBW dataset contains words with severity scores from 0-1,
    where higher scores indicate stronger profanity.

    Args:
        severity_threshold: Minimum severity score to include (0.0-1.0)
                          0.5 = medium strictness
                          0.7 = high strictness (only strong profanity)

    Returns:
        Tuple of:
        - Dict mapping words to their severity scores
        - Set of words that meet the threshold
    """
    vbw_path = get_vbw_path()

    # Download if not present
    if not vbw_path.exists():
        download_vbw_dataset()

    word_scores: Dict[str, float] = {}
    words_set: Set[str] = set()

    try:
        with open(vbw_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header if present
            first_row = next(reader, None)
            if first_row and first_row[0].lower() not in ["word", "term", "text"]:
                # First row is data, process it
                if len(first_row) >= 2:
                    word = first_row[0].strip().lower()
                    try:
                        score = float(first_row[1])
                        word_scores[word] = score
                        if score >= severity_threshold:
                            words_set.add(word)
                    except (ValueError, IndexError):
                        pass

            # Process remaining rows
            for row in reader:
                if len(row) >= 2:
                    word = row[0].strip().lower()
                    try:
                        score = float(row[1])
                        word_scores[word] = score
                        if score >= severity_threshold:
                            words_set.add(word)
                    except (ValueError, IndexError):
                        # Skip rows with invalid scores
                        continue

        logger.info(
            f"Loaded VBW dataset: {len(word_scores)} total words, "
            f"{len(words_set)} above threshold {severity_threshold}"
        )

    except FileNotFoundError:
        logger.warning(f"VBW dataset not found at {vbw_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading VBW dataset: {e}")
        raise

    return word_scores, words_set


class VBWDataset:
    """
    Lazy-loading wrapper for the VBW dataset.

    Provides efficient lookup of taboo words with caching.
    """

    _instance: Optional["VBWDataset"] = None
    _word_scores: Optional[Dict[str, float]] = None
    _words_set: Optional[Set[str]] = None
    _threshold: float = 0.5

    def __new__(cls, severity_threshold: float = 0.5):
        """Singleton pattern - reuse instance if threshold matches."""
        if cls._instance is None or cls._threshold != severity_threshold:
            cls._instance = super().__new__(cls)
            cls._threshold = severity_threshold
            cls._word_scores = None
            cls._words_set = None
        return cls._instance

    def __init__(self, severity_threshold: float = 0.5):
        """
        Initialize or get existing VBW dataset instance.

        Args:
            severity_threshold: Minimum severity score (0.0-1.0)
        """
        self.severity_threshold = severity_threshold

    def _load(self) -> None:
        """Load the dataset if not already loaded."""
        if self._word_scores is None:
            VBWDataset._word_scores, VBWDataset._words_set = load_vbw_dataset(
                self.severity_threshold
            )

    @property
    def word_scores(self) -> Dict[str, float]:
        """Get word-to-score mapping."""
        self._load()
        return self._word_scores or {}

    @property
    def words(self) -> Set[str]:
        """Get set of words above threshold."""
        self._load()
        return self._words_set or set()

    def contains(self, word: str) -> bool:
        """Check if a word is in the taboo list."""
        return word.lower() in self.words

    def get_score(self, word: str) -> Optional[float]:
        """Get the severity score for a word."""
        return self.word_scores.get(word.lower())

    def find_matches(self, text: str) -> List[Tuple[str, float]]:
        """
        Find all VBW words in the given text.

        Args:
            text: Text to search

        Returns:
            List of (word, score) tuples for matches found
        """
        text_lower = text.lower()
        matches = []

        for word in self.words:
            if word in text_lower:
                score = self.word_scores.get(word, 0.0)
                matches.append((word, score))

        return matches
