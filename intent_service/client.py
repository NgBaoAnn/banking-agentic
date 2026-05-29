"""gRPC client for testing the Intent Service."""

import sys
import grpc

import intent_service_pb2
import intent_service_pb2_grpc


def classify_intent(message: str, host: str = "localhost", port: int = 50051):
    """Send a message to the Intent Service and print the result."""
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = intent_service_pb2_grpc.IntentServiceStub(channel)

    request = intent_service_pb2.IntentRequest(message=message)
    response = stub.IntentRecognizer(request)

    print(f"Intent:     {response.intent}")
    print(f"Confidence: {response.confidence:.3f}")
    print(f"Reason:     {response.reason}")

    return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py '<message>'")
        print("Example: python client.py 'I lost my card yesterday'")
        sys.exit(1)

    msg = " ".join(sys.argv[1:])
    classify_intent(msg)
