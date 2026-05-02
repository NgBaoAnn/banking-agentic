"""
FastAPI application for the Banking AI-Agent backend.
Registers API routes and initializes the main server.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.schemas import CustomerRequest, AgentResponse
from app.agent.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Banking AI-Agent",
    description="AI agentic pipeline for banking customer support",
    version="1.0.0",
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
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "banking-ai-agent"}


@app.post("/api/chat", response_model=AgentResponse)
async def chat(request: CustomerRequest):
    """
    Process a customer support message through the AI agentic pipeline.

    The pipeline runs 6 nodes sequentially:
    1. Intent Detection (fine-tuned ngbaoan/intent-banking model, loaded directly)
    2. Priority / Risk Detection (rule-based)
    3. Policy Retrieval (lookup from policies.py)
    4. Response Drafting (LLM via Ollama gpt-oss:20b)
    5. Validation (quality checks)
    6. Routing (reply / ask_more / escalate)

    Returns the final response, action decision, and full workflow trace.
    """
    logger.info(f"Received chat request: '{request.message[:80]}...'")
    response = await orchestrator.process(request.message)
    return response
