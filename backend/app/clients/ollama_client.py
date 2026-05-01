"""
Ollama client used to call the language model (gpt-oss:20b).
Handles sending prompts to Ollama and receiving model outputs.
"""

import logging
from typing import List, Optional

import httpx

from app.clients.base import BaseLLMClient
from app.core.settings import settings

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """HTTP client for the Ollama API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Send a chat-style prompt to Ollama and return the response text.

        Args:
            prompt: The user message / prompt.
            **kwargs: Optional overrides (model, temperature, etc.)

        Returns:
            Generated text from the LLM.
        """
        model = kwargs.pop("model", self.model)
        system_msg = kwargs.pop("system", None)

        messages: List[dict] = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs,
        }

        url = f"{self.base_url}/api/chat"
        logger.info(f"Calling Ollama: model={model}, url={url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "")

            logger.info(f"Ollama response received ({len(content)} chars)")
            return content

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise
