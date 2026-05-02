"""
Intent Detection Node — the core node of the agentic workflow.

Calls the Intent Classification Service API (running on Google Colab)
to classify the customer's banking intent using the fine-tuned
ngbaoan/intent-banking model (LoRA adapter on Qwen2.5-7B).

Set INTENT_SERVICE_URL to the public URL exposed by the Colab notebook
(e.g., https://xxx.ngrok-free.app or https://xxx.a.pinggy.io).
"""

import logging

import httpx

from app.core.schemas import IntentResult
from app.core.settings import settings

logger = logging.getLogger(__name__)


class IntentNode:
    """
    Receives a customer message and returns the predicted banking intent
    by calling the remote Intent Classification API (hosted on Colab).
    """

    def __init__(self):
        self.service_url = settings.INTENT_SERVICE_URL.rstrip("/")
        self.timeout = 60.0

    async def run(self, message: str) -> IntentResult:
        """
        Call the Intent Classification API and return the result.

        Args:
            message: Raw customer message text.

        Returns:
            IntentResult with predicted intent, confidence, and reason.
        """
        logger.info(
            f"[IntentNode] Calling intent service at {self.service_url}/classify ..."
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}/classify",
                    json={"message": message},
                )
                response.raise_for_status()
                data = response.json()

            result = IntentResult(
                intent=data.get("intent", "unknown"),
                confidence=data.get("confidence", 0.0),
                reason=data.get(
                    "reason",
                    f"Classified by {settings.INTENT_MODEL_NAME} (fine-tuned Qwen2.5-7B on BANKING77)",
                ),
            )
            logger.info(
                f"[IntentNode] intent='{result.intent}' "
                f"confidence={result.confidence:.3f}"
            )
            return result

        except httpx.TimeoutException:
            logger.error("[IntentNode] Request to intent service timed out.")
            return self._fallback("Intent service timed out")

        except httpx.HTTPStatusError as e:
            logger.error(f"[IntentNode] HTTP error from intent service: {e.response.status_code}")
            return self._fallback(f"HTTP error: {e.response.status_code}")

        except Exception as e:
            logger.error(f"[IntentNode] Failed to call intent service: {e}")
            return self._fallback(str(e))

    def _fallback(self, reason: str) -> IntentResult:
        """Return a safe fallback when the intent service is unreachable."""
        logger.warning(f"[IntentNode] Using fallback intent. Reason: {reason}")
        return IntentResult(
            intent="unknown",
            confidence=0.0,
            reason=f"Intent service unavailable: {reason}",
        )
