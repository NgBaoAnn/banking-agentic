"""
FastAPI application for the Banking AI-Agent API Gateway.
Registers API routes and initializes the main server.
"""

import logging

from typing import Annotated

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.schemas import CustomerRequest, AgentResponse
from app.core.settings import settings
from app.agent.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Banking AI-Agent API Gateway",
    description="API Gateway for the Banking AI agentic pipeline with gRPC-based intent detection",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()


@app.get("/health")
def health_check() -> dict:
    """Check whether the system is running."""
    return {"status": "ok", "service": "banking-ai-agent-gateway"}


@app.get("/config")
def get_config() -> dict:
    """Return the current system configuration."""
    return {
        "service": "banking-ai-agent-gateway",
        "version": "2.0.0",
        "intent_service": {
            "type": "gRPC",
            "host": settings.INTENT_SERVICE_HOST,
            "port": settings.INTENT_SERVICE_PORT,
        },
        "ollama": {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
        },
    }


@app.post("/run-agent")
async def run_agent(request: Annotated[CustomerRequest, Body()]) -> AgentResponse:
    """
    Execute the full agentic workflow.

    The pipeline runs 6 nodes sequentially:
    1. Intent Detection (via gRPC Intent Service)
    2. Priority / Risk Detection (rule-based)
    3. Policy Retrieval (lookup from policies.py)
    4. Response Drafting (LLM via Ollama gpt-oss:20b)
    5. Validation (quality checks)
    6. Routing (reply / ask_more / escalate)

    Returns the final response, action decision, and full workflow trace.
    """
    logger.info(f"Received run-agent request: '{request.message[:80]}...'")
    response = await orchestrator.process(request.message)
    return response


@app.post("/api/chat")
async def chat(request: Annotated[CustomerRequest, Body()]) -> AgentResponse:
    """
    Alias for /run-agent — kept for backward compatibility with frontend.
    """
    logger.info(f"Received chat request: '{request.message[:80]}...'")
    response = await orchestrator.process(request.message)
    return response
