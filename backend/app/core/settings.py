"""Application settings and environment-based configuration."""

import os


class Settings:
    # === Ollama LLM (Node 4: Response Drafting) ===
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")

    # === Intent Service gRPC (Node 1: Intent Detection) ===
    INTENT_SERVICE_HOST: str = os.environ.get("INTENT_SERVICE_HOST", "localhost")
    INTENT_SERVICE_PORT: int = int(os.environ.get("INTENT_SERVICE_PORT", "50051"))


settings = Settings()
