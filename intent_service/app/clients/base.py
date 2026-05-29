"""Abstract base client interface for model calling."""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for language model clients."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the language model."""
        raise NotImplementedError
