"""
Utility functions for KROP Duster.
"""

import hashlib
import logging
import random
from typing import Any, List, Optional

import numpy as np


logger = logging.getLogger(__name__)


def set_seed(seed: Optional[int] = None) -> None:
    """
    Set random seed for reproducibility.

    Args:
        seed: Random seed value. If None, uses random seed.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        logger.debug(f"Set random seed to {seed}")


def hash_text(text: str) -> str:
    """
    Create a hash of text for logging/caching without revealing content.

    Args:
        text: Text to hash

    Returns:
        SHA256 hash of text
    """
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def apply_temperature(scores: List[float], temperature: float = 1.0) -> List[float]:
    """
    Apply temperature scaling to scores.

    Args:
        scores: List of scores
        temperature: Temperature value (higher = more random)

    Returns:
        Temperature-adjusted scores
    """
    if temperature == 1.0:
        return scores

    # Avoid division by zero
    if temperature == 0.0:
        temperature = 0.01

    adjusted = [s / temperature for s in scores]
    return adjusted


def apply_top_k(items: List[Any], scores: List[float], k: int) -> tuple[List[Any], List[float]]:
    """
    Apply top-k filtering to items based on scores.

    Args:
        items: List of items
        scores: Corresponding scores
        k: Number of top items to keep (0 = no filtering)

    Returns:
        Filtered items and scores
    """
    if k == 0 or k >= len(items):
        return items, scores

    # Get indices of top-k scores
    top_indices = np.argsort(scores)[-k:][::-1]

    filtered_items = [items[i] for i in top_indices]
    filtered_scores = [scores[i] for i in top_indices]

    return filtered_items, filtered_scores


def apply_top_p(items: List[Any], scores: List[float], p: float) -> tuple[List[Any], List[float]]:
    """
    Apply nucleus/top-p sampling to items based on scores.

    Args:
        items: List of items
        scores: Corresponding scores (will be normalized to probabilities)
        p: Cumulative probability threshold

    Returns:
        Filtered items and scores
    """
    if p >= 1.0:
        return items, scores

    # Normalize scores to probabilities
    total = sum(scores)
    if total == 0:
        return items, scores

    probs = [s / total for s in scores]

    # Sort by probability (descending)
    sorted_indices = np.argsort(probs)[::-1]

    # Select items until cumulative probability exceeds p
    cumulative = 0.0
    selected_indices = []

    for idx in sorted_indices:
        cumulative += probs[idx]
        selected_indices.append(idx)
        if cumulative >= p:
            break

    filtered_items = [items[i] for i in selected_indices]
    filtered_scores = [scores[i] for i in selected_indices]

    return filtered_items, filtered_scores


def sample_with_scores(
    items: List[Any],
    scores: List[float],
    n: int = 1,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    seed: Optional[int] = None,
) -> List[Any]:
    """
    Sample items based on scores with temperature, top-k, and top-p.

    Args:
        items: List of items to sample from
        scores: Corresponding scores
        n: Number of items to sample
        temperature: Temperature for scaling
        top_k: Top-k filtering (0 = disabled)
        top_p: Nucleus sampling threshold (1.0 = disabled)
        seed: Random seed for reproducibility

    Returns:
        Sampled items
    """
    if not items:
        return []

    # Set seed if provided
    set_seed(seed)

    # Apply temperature
    adjusted_scores = apply_temperature(scores, temperature)

    # Apply top-k filtering
    filtered_items, filtered_scores = apply_top_k(items, adjusted_scores, top_k)

    # Apply top-p filtering
    filtered_items, filtered_scores = apply_top_p(filtered_items, filtered_scores, top_p)

    # If we have fewer items than requested, return all
    if len(filtered_items) <= n:
        return filtered_items

    # Normalize to probabilities for sampling
    total = sum(filtered_scores)
    if total == 0:
        # If all scores are 0, sample uniformly
        return random.sample(filtered_items, min(n, len(filtered_items)))

    probs = [s / total for s in filtered_scores]

    # Sample without replacement
    sampled = np.random.choice(
        filtered_items,
        size=min(n, len(filtered_items)),
        replace=False,
        p=probs,
    )

    return sampled.tolist()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_for_logging(text: str, redact_sensitive: bool = True) -> str:
    """
    Sanitize text for safe logging.

    Args:
        text: Text to sanitize
        redact_sensitive: Whether to redact sensitive content

    Returns:
        Sanitized text (hash if sensitive)
    """
    if redact_sensitive:
        return f"<hash:{hash_text(text)}>"
    return truncate_text(text)
