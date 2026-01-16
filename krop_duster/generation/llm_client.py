"""
LLM client with multi-provider support.
"""

import logging
import os
from typing import Optional

from krop_duster.core.models import LLMConfig, LLMProvider


logger = logging.getLogger(__name__)


class LLMRefusalError(Exception):
    """Exception raised when LLM refuses to generate content."""

    pass


class LLMClient:
    """Multi-provider LLM client."""

    def __init__(self, config: LLMConfig):
        """
        Initialize LLM client.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider."""
        if self.config.provider == LLMProvider.OPENAI:
            return self._initialize_openai()
        elif self.config.provider == LLMProvider.OLLAMA:
            return self._initialize_ollama()
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return self._initialize_anthropic()
        elif self.config.provider == LLMProvider.TEMPLATES:
            return None  # No client needed for templates
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")

    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                    "or provide in config."
                )

            client = OpenAI(
                api_key=api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout,
            )

            logger.info(f"Initialized OpenAI client with model {self.config.model}")
            return client

        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")

    def _initialize_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama

            # Test connection
            if self.config.api_base:
                os.environ["OLLAMA_HOST"] = self.config.api_base

            logger.info(f"Initialized Ollama client with model {self.config.model}")
            return ollama

        except ImportError:
            raise ImportError("Ollama package not installed. Install with: pip install ollama")

    def _initialize_anthropic(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic

            api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                    "or provide in config."
                )

            client = Anthropic(
                api_key=api_key,
                timeout=self.config.timeout,
            )

            logger.info(f"Initialized Anthropic client with model {self.config.model}")
            return client

        except ImportError:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate text using the configured LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text

        Raises:
            LLMRefusalError: If LLM refuses to generate
        """
        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.provider == LLMProvider.OPENAI:
                    response = self._generate_openai(prompt, system_prompt)
                elif self.config.provider == LLMProvider.OLLAMA:
                    response = self._generate_ollama(prompt, system_prompt)
                elif self.config.provider == LLMProvider.ANTHROPIC:
                    response = self._generate_anthropic(prompt, system_prompt)
                elif self.config.provider == LLMProvider.TEMPLATES:
                    raise ValueError("Template-based generation should not call LLMClient.generate()")
                else:
                    raise ValueError(f"Unsupported provider: {self.config.provider}")

                # Check for refusal
                if self.config.detect_refusal and self._is_refusal(response):
                    logger.warning(f"LLM refused to generate content (attempt {attempt + 1})")
                    if self.config.fallback_on_refusal:
                        raise LLMRefusalError("LLM refused to generate content")
                    else:
                        return response

                return response

            except LLMRefusalError:
                raise
            except Exception as e:
                if attempt < self.config.max_retries:
                    logger.warning(f"LLM generation failed (attempt {attempt + 1}): {e}")
                else:
                    logger.error(f"LLM generation failed after {attempt + 1} attempts: {e}")
                    raise

        return ""

    def _generate_openai(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
        )

        return response.choices[0].message.content

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using Ollama."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.config.model,
            messages=messages,
            options={
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
                "top_p": self.config.top_p,
            },
        )

        return response["message"]["content"]

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using Anthropic API."""
        kwargs = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text

    def _is_refusal(self, text: str) -> bool:
        """
        Check if response is a refusal.

        Args:
            text: Generated text

        Returns:
            True if refusal detected
        """
        refusal_patterns = [
            "i cannot",
            "i can't",
            "i'm unable to",
            "i cannot assist",
            "against my ethical",
            "i'm not comfortable",
            "inappropriate",
            "i apologize, but",
            "i must decline",
        ]

        text_lower = text.lower()[:200]  # Check first 200 chars

        return any(pattern in text_lower for pattern in refusal_patterns)
