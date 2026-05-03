"""
gRPC server for the Banking Intent Classification Service.
Serves the fine-tuned ngbaoan/intent-banking model via gRPC.
"""
import os
import re
import logging
import torch
from concurrent import futures

import grpc
import intent_service_pb2
import intent_service_pb2_grpc
from model_loader import get_model

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

GRPC_PORT = os.environ.get("GRPC_PORT", "50051")
PROMPT_TEMPLATE = """Instruct: Classify the following banking query into the correct intent.
Query: {query}
Intent: """


class IntentServiceServicer(intent_service_pb2_grpc.IntentServiceServicer):
    def __init__(self):
        self.model, self.tokenizer = get_model()

    def IntentRecognizer(self, request, context):
        message = request.message
        prompt = PROMPT_TEMPLATE.format(query=message)
        device = next(self.model.parameters()).device
        inputs = self.tokenizer([prompt], return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, max_new_tokens=64, use_cache=True,
                temperature=0.1, do_sample=False,
            )

        full_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        intent = "unknown"
        if "Intent:" in full_output:
            raw = full_output.split("Intent:")[-1].strip()
            parsed = re.sub(r'[^\w_].*$', '', raw.split("\n")[0].strip())
            if parsed:
                intent = parsed

        output_len = outputs.shape[1] - inputs["input_ids"].shape[1]
        confidence = 0.92 if output_len <= 5 else 0.80 if output_len <= 10 else 0.65 if output_len <= 20 else 0.50

        return intent_service_pb2.IntentResponse(
            intent=intent, confidence=confidence,
            reason=f"Classified by ngbaoan/intent-banking (Qwen2.5-7B, BANKING77)",
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    intent_service_pb2_grpc.add_IntentServiceServicer_to_server(
        IntentServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    logger.info(f"gRPC Intent Service listening on port {GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
