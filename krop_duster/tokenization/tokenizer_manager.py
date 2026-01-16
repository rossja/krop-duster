"""
Tokenizer management for multiple model types.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TokenizerManager:
    """Manage tokenizers for different model types."""

    def __init__(self, tokenizer_name: str = "gpt-4"):
        """
        Initialize tokenizer manager.

        Args:
            tokenizer_name: Name of tokenizer (gpt-4, gpt-3.5-turbo, llama2, etc.)
        """
        self.tokenizer_name = tokenizer_name
        self.tokenizer = self._load_tokenizer()

    def _load_tokenizer(self):
        """Load appropriate tokenizer based on name."""
        try:
            # Try OpenAI tokenizers first (most common)
            if any(name in self.tokenizer_name.lower() for name in ["gpt-4", "gpt-3.5", "gpt-35"]):
                return self._load_openai_tokenizer()

            # Try HuggingFace tokenizers
            elif any(name in self.tokenizer_name.lower() for name in ["llama", "mistral", "mixtral"]):
                return self._load_huggingface_tokenizer()

            # Default to OpenAI
            else:
                logger.warning(
                    f"Unknown tokenizer {self.tokenizer_name}, defaulting to GPT-4"
                )
                return self._load_openai_tokenizer()

        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
            raise

    def _load_openai_tokenizer(self):
        """Load OpenAI tokenizer using tiktoken."""
        try:
            import tiktoken

            # Map model names to encodings
            encoding_map = {
                "gpt-4": "cl100k_base",
                "gpt-3.5-turbo": "cl100k_base",
                "gpt-35-turbo": "cl100k_base",
            }

            encoding_name = encoding_map.get(self.tokenizer_name, "cl100k_base")
            tokenizer = tiktoken.get_encoding(encoding_name)

            logger.info(f"Loaded OpenAI tokenizer: {encoding_name}")
            return tokenizer

        except ImportError:
            raise ImportError(
                "tiktoken not installed. Install with: pip install tiktoken"
            )

    def _load_huggingface_tokenizer(self):
        """Load HuggingFace tokenizer."""
        try:
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
            logger.info(f"Loaded HuggingFace tokenizer: {self.tokenizer_name}")
            return tokenizer

        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers"
            )

    def encode(self, text: str) -> List[int]:
        """
        Encode text to tokens.

        Args:
            text: Text to encode

        Returns:
            List of token IDs
        """
        try:
            # Handle tiktoken (OpenAI)
            if hasattr(self.tokenizer, "encode"):
                return self.tokenizer.encode(text)

            # Handle HuggingFace
            elif hasattr(self.tokenizer, "tokenize"):
                return self.tokenizer.encode(text, add_special_tokens=True)

            else:
                raise ValueError("Unsupported tokenizer type")

        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            # Fallback: rough approximation
            return text.split()

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            tokens = self.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using approximation")
            # Rough approximation: 1 token ≈ 0.75 words
            return int(len(text.split()) * 1.33)

    def decode(self, tokens: List[int]) -> str:
        """
        Decode tokens to text.

        Args:
            tokens: Token IDs

        Returns:
            Decoded text
        """
        try:
            # Handle tiktoken (OpenAI)
            if hasattr(self.tokenizer, "decode"):
                return self.tokenizer.decode(tokens)

            # Handle HuggingFace
            elif hasattr(self.tokenizer, "decode"):
                return self.tokenizer.decode(tokens, skip_special_tokens=True)

            else:
                raise ValueError("Unsupported tokenizer type")

        except Exception as e:
            logger.error(f"Decoding failed: {e}")
            return " ".join(str(t) for t in tokens)
