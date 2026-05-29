"""Settings for the Intent Classification gRPC microservice."""

import os


class Settings:
    """Configuration loaded from environment variables."""

    # Ollama connection (used to classify intents via LLM)
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    INTENT_MODEL_NAME: str = os.environ.get("INTENT_MODEL_NAME", "gpt-oss:20b")

    # gRPC server port
    GRPC_PORT: int = int(os.environ.get("GRPC_PORT", "50051"))


settings = Settings()
