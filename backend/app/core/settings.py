"""
Application settings and environment-based configuration.
"""

import os


class Settings:
    # === Ollama LLM (Node 4: Response Drafting) ===
    # - Local:  http://localhost:11434
    # - Docker: http://host.docker.internal:11434
    # - Colab:  https://xxx.a.pinggy.io  (from Ollama-Pinggy.ipynb)
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")

    # === Intent Classification Service (Node 1: Intent Detection) ===
    # - Colab:  https://xxx.ngrok-free.app  (from Intent-Service-Colab.ipynb)
    INTENT_SERVICE_URL: str = os.environ.get("INTENT_SERVICE_URL", "http://localhost:8001")
    INTENT_MODEL_NAME: str = os.environ.get("INTENT_MODEL_NAME", "ngbaoan/intent-banking")


settings = Settings()
