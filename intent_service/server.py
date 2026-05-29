"""gRPC server for the Intent Classification microservice."""

import logging
import asyncio
from concurrent import futures

import grpc

from app.core.settings import settings
from app.nodes.intent_node import IntentNode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# These imports will be available after `make` generates them
import intent_service_pb2
import intent_service_pb2_grpc


class IntentServiceServicer(intent_service_pb2_grpc.IntentServiceServicer):
    """gRPC servicer that handles intent classification requests."""

    def __init__(self):
        self.intent_node = IntentNode()
        logger.info("IntentServiceServicer initialized")

    def IntentRecognizer(self, request, context):
        """
        Handle an IntentRecognizer RPC call.

        Args:
            request: IntentRequest with a 'message' field.
            context: gRPC context.

        Returns:
            IntentResponse with intent, confidence, and reason.
        """
        message = request.message
        logger.info(f"Received intent request: '{message[:80]}...'")

        try:
            # Recreate IntentNode per request to avoid httpx loop closed issues
            node = IntentNode()
            result = asyncio.run(node.run(message))

            logger.info(
                f"Intent result: intent='{result.intent}', "
                f"confidence={result.confidence:.3f}"
            )

            return intent_service_pb2.IntentResponse(
                intent=result.intent,
                confidence=result.confidence,
                reason=result.reason,
            )

        except Exception as e:
            logger.error(f"Error processing intent request: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return intent_service_pb2.IntentResponse(
                intent="unknown",
                confidence=0.0,
                reason=f"Error: {str(e)}",
            )


def serve():
    """Start the gRPC server."""
    port = settings.GRPC_PORT
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    intent_service_pb2_grpc.add_IntentServiceServicer_to_server(
        IntentServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info(f"Intent Service gRPC server started on port {port}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"Intent Model: {settings.INTENT_MODEL_NAME}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)


if __name__ == "__main__":
    serve()
