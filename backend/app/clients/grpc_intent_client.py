"""gRPC client for communicating with the Intent Classification microservice."""

import logging

import grpc

from app.core.schemas import IntentResult
from app.core.settings import settings
from app.intent_grpc import intent_service_pb2
from app.intent_grpc import intent_service_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcIntentClient:
    """gRPC client that connects to the Intent Service."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
    ):
        self.host = host or settings.INTENT_SERVICE_HOST
        self.port = port or settings.INTENT_SERVICE_PORT
        self._channel = None
        self._stub = None

    @property
    def target(self) -> str:
        return f"{self.host}:{self.port}"

    def _get_stub(self) -> intent_service_pb2_grpc.IntentServiceStub:
        """Get or create the gRPC stub."""
        if self._channel is None:
            self._channel = grpc.insecure_channel(self.target)
            self._stub = intent_service_pb2_grpc.IntentServiceStub(self._channel)
            logger.info(f"Connected to Intent Service at {self.target}")
        return self._stub

    async def classify(self, message: str) -> IntentResult:
        """
        Classify a customer message by calling the Intent Service via gRPC.

        Args:
            message: The customer message to classify.

        Returns:
            IntentResult with intent, confidence, and reason.
        """
        logger.info(f"[GrpcIntentClient] Calling Intent Service at {self.target}...")

        try:
            stub = self._get_stub()
            request = intent_service_pb2.IntentRequest(message=message)
            response = stub.IntentRecognizer(request, timeout=60)

            result = IntentResult(
                intent=response.intent,
                confidence=response.confidence,
                reason=response.reason,
            )
            logger.info(
                f"[GrpcIntentClient] intent='{result.intent}' "
                f"confidence={result.confidence:.3f}"
            )
            return result

        except grpc.RpcError as e:
            logger.error(
                f"[GrpcIntentClient] gRPC error: "
                f"code={e.code()}, details={e.details()}"
            )
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                reason=f"gRPC error: {e.details()}",
            )
        except Exception as e:
            logger.error(f"[GrpcIntentClient] Unexpected error: {e}")
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                reason=f"Intent service unavailable: {str(e)}",
            )

    def close(self):
        """Close the gRPC channel."""
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
            logger.info("Closed gRPC channel to Intent Service")
