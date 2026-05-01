"""
Abstract base client interface for model calling.
All model-calling components follow this consistent interface.
"""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for language model clients."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the language model.

        Args:
            prompt: The input prompt text.
            **kwargs: Additional model-specific parameters.

        Returns:
            Generated text response.
        """
        raise NotImplementedError
