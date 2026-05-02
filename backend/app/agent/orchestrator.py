"""
Main workflow controller — the AI Agentic Pipeline orchestrator.
Calls all nodes in the correct order and collects intermediate outputs
so the workflow trace can be observed during testing.
"""

import logging
import time

from app.core.schemas import (
    AgentResponse,
    WorkflowTrace,
)
from app.nodes.intent_node import IntentNode
from app.nodes.priority_node import PriorityNode
from app.nodes.policy_node import PolicyNode
from app.nodes.draft_node import DraftNode
from app.nodes.validation_node import ValidationNode
from app.nodes.router_node import RouterNode

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrates the full AI agentic pipeline:
        1. Intent Detection
        2. Priority Detection
        3. Policy Retrieval
        4. Response Drafting
        5. Validation
        6. Routing
    """

    def __init__(self):
        self.intent_node = IntentNode()
        self.priority_node = PriorityNode()
        self.policy_node = PolicyNode()
        self.draft_node = DraftNode()
        self.validation_node = ValidationNode()
        self.router_node = RouterNode()

    async def process(self, message: str) -> AgentResponse:
        """
        Run the complete agentic pipeline on a customer message.

        Args:
            message: Raw customer message.

        Returns:
            AgentResponse with the final response, action, and full trace.
        """
        logger.info("=" * 60)
        logger.info(f"[Orchestrator] Processing message: '{message[:80]}...'")
        start_time = time.time()

        trace = WorkflowTrace()

        # ── Step 1: Intent Detection ──────────────────────────────
        logger.info("[Orchestrator] Step 1/6: Intent Detection")
        intent_result = await self.intent_node.run(message)
        trace.intent = intent_result

        # ── Step 2: Priority Detection ────────────────────────────
        logger.info("[Orchestrator] Step 2/6: Priority Detection")
        priority_result = await self.priority_node.run(message, intent_result)
        trace.priority = priority_result

        # ── Step 3: Policy Retrieval ──────────────────────────────
        logger.info("[Orchestrator] Step 3/6: Policy Retrieval")
        policy_result = await self.policy_node.run(intent_result.intent)
        trace.policy = policy_result

        # ── Step 4: Response Drafting ─────────────────────────────
        logger.info("[Orchestrator] Step 4/6: Response Drafting")
        draft_result = await self.draft_node.run(
            message, intent_result, priority_result, policy_result
        )
        trace.draft = draft_result

        # ── Step 5: Validation ────────────────────────────────────
        logger.info("[Orchestrator] Step 5/6: Validation")
        validation_result = await self.validation_node.run(
            draft_result, intent_result, policy_result
        )
        trace.validation = validation_result

        # ── Step 6: Routing ───────────────────────────────────────
        logger.info("[Orchestrator] Step 6/6: Routing")
        routing_result = await self.router_node.run(
            intent_result, priority_result, policy_result,
            draft_result, validation_result,
        )
        trace.routing = routing_result

        # ── Build final response ──────────────────────────────────
        final_response = self._build_final_response(
            draft_result.reply, routing_result.action, routing_result.reason
        )

        elapsed = time.time() - start_time
        logger.info(
            f"[Orchestrator] Pipeline complete in {elapsed:.2f}s | "
            f"Action: {routing_result.action}"
        )
        logger.info("=" * 60)

        return AgentResponse(
            final_response=final_response,
            action=routing_result.action,
            trace=trace,
        )

    def _build_final_response(
        self, draft_reply: str, action: str, reason: str
    ) -> str:
        """Compose the final response based on the routing decision."""
        if action == "reply":
            return draft_reply
        elif action == "ask_more":
            return (
                f"{draft_reply}\n\n"
                "---\n"
                "⚠️ We need additional information to fully resolve your issue. "
                "Please provide the details mentioned above so we can assist you "
                "more effectively."
            )
        elif action == "escalate":
            return (
                "Thank you for reaching out. Your case has been identified as "
                "requiring specialized attention.\n\n"
                f"**Reason for escalation:** {reason}\n\n"
                "A member of our support team will contact you shortly. "
                "If this is urgent, please call our priority support line "
                "at 1-800-BANK-HELP."
            )
        else:
            return draft_reply
