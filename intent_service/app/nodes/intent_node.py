"""Intent classification node using Ollama LLM."""

import json
import logging

from app.clients.ollama_client import OllamaClient
from app.core.schemas import IntentResult
from app.data.policies import VALID_INTENTS

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """You are a banking intent classifier. Your task is to classify customer messages into one of the predefined banking intent categories.

Rules:
- Choose the MOST specific intent that matches the customer's message.
- If no intent clearly matches, use "unknown".
- Provide a confidence score between 0.0 and 1.0.
- Provide a brief reason for your classification.
- Respond ONLY in the exact JSON format specified."""

INTENT_USER_TEMPLATE = """Classify the following customer message into one of these banking intents:

{intents}

Customer Message: "{message}"

Respond in this exact JSON format:
{{
    "intent": "<intent_label>",
    "confidence": <float between 0.0 and 1.0>,
    "reason": "<brief explanation>"
}}"""


class IntentNode:
    """Classifies customer messages into banking intents using Ollama."""

    def __init__(self):
        self.client = OllamaClient()
        self.valid_intents = VALID_INTENTS

    async def run(self, message: str) -> IntentResult:
        """Classify the intent of a customer message."""
        logger.info(f"[IntentNode] Classifying intent for: '{message[:80]}...'")

        intents_str = ", ".join(self.valid_intents)
        prompt = INTENT_USER_TEMPLATE.format(
            intents=intents_str,
            message=message,
        )

        try:
            raw_response = await self.client.generate(
                prompt=prompt,
                system=INTENT_SYSTEM_PROMPT,
            )
            result = self._parse_response(raw_response)
            logger.info(
                f"[IntentNode] intent='{result.intent}' "
                f"confidence={result.confidence:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"[IntentNode] Classification failed: {e}")
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                reason=f"Classification failed: {str(e)}",
            )

    def _parse_response(self, raw: str) -> IntentResult:
        """Parse the LLM response into an IntentResult."""
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(raw[start:end])
                intent = data.get("intent", "unknown")
                confidence = float(data.get("confidence", 0.0))
                reason = data.get("reason", "")

                # Validate intent is in our known list
                if intent not in self.valid_intents:
                    logger.warning(
                        f"[IntentNode] Unknown intent '{intent}', "
                        "keeping as-is"
                    )

                # Clamp confidence to [0, 1]
                confidence = max(0.0, min(1.0, confidence))

                return IntentResult(
                    intent=intent,
                    confidence=confidence,
                    reason=reason,
                )
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[IntentNode] Failed to parse LLM response: {e}")

        return IntentResult(
            intent="unknown",
            confidence=0.0,
            reason=f"Failed to parse LLM response: {raw[:100]}",
        )
