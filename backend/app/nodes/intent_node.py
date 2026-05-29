"""Intent Detection Node — calls the Intent Service via gRPC."""

import logging

from app.clients.grpc_intent_client import GrpcIntentClient
from app.core.schemas import IntentResult
from app.core.settings import settings

logger = logging.getLogger(__name__)


class IntentNode:
    """
    Receives a customer message and returns the predicted banking intent
    by calling the Intent Service via gRPC.
    """

    def __init__(self):
        self.grpc_client = GrpcIntentClient()
        logger.info(
            f"[IntentNode] Configured to use gRPC Intent Service at "
            f"{settings.INTENT_SERVICE_HOST}:{settings.INTENT_SERVICE_PORT}"
        )

    async def run(self, message: str) -> IntentResult:
        """
        Call the Intent Service via gRPC and return the classification result.

        Args:
            message: Raw customer message.

        Returns:
            IntentResult with intent, confidence, and reason.
        """
        logger.info(
            f"[IntentNode] Calling Intent Service via gRPC for: '{message[:80]}...'"
        )

        result = await self.grpc_client.classify(message)

        logger.info(
            f"[IntentNode] intent='{result.intent}' "
            f"confidence={result.confidence:.3f}"
        )
        return result
