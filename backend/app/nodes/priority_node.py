"""
Priority / Risk Detection Node.
Uses rule-based logic (keywords + intent mapping) to classify whether a
customer case is low, medium, or high priority.
"""

import logging
from typing import List

from app.core.schemas import PriorityResult, IntentResult

logger = logging.getLogger(__name__)

# Intents that are inherently high-priority
HIGH_PRIORITY_INTENTS = {
    "lost_or_stolen_card",
    "compromised_card",
    "card_payment_not_recognised",
    "blocked_account",
    "unauthorized_transaction",
    "fraud",
    "identity_theft",
}

# Intents that are inherently medium-priority
MEDIUM_PRIORITY_INTENTS = {
    "failed_transfer",
    "transfer_not_received_by_recipient",
    "request_refund",
    "card_not_received",
    "top_up_failed",
    "balance_not_updated_after_bank_transfer",
    "wrong_amount_of_cash_received",
    "card_payment_fee_charged",
    "card_swallowed",
}

# Urgent keywords that bump priority up
URGENT_KEYWORDS = [
    "urgent", "emergency", "immediately", "stolen", "hack", "hacked",
    "fraud", "unauthorized", "suspicious", "lost", "missing money",
    "help me", "asap", "right now", "critical",
]


class PriorityNode:
    """
    Determines the priority level of a customer issue based on the
    detected intent and keywords found in the original message.
    """

    async def run(
        self, message: str, intent_result: IntentResult
    ) -> PriorityResult:
        """
        Classify the priority of the customer case.

        Args:
            message: Original customer message.
            intent_result: Output from the Intent Detection Node.

        Returns:
            PriorityResult with level (low/medium/high) and contributing factors.
        """
        logger.info("[PriorityNode] Evaluating priority...")
        factors: List[str] = []
        intent = intent_result.intent.lower()

        # --- Intent-based priority ---
        if intent in HIGH_PRIORITY_INTENTS:
            base_level = "high"
            factors.append(f"Intent '{intent}' is classified as high-risk")
        elif intent in MEDIUM_PRIORITY_INTENTS:
            base_level = "medium"
            factors.append(f"Intent '{intent}' is classified as medium-risk")
        else:
            base_level = "low"
            factors.append(f"Intent '{intent}' is classified as low-risk")

        # --- Keyword-based escalation ---
        message_lower = message.lower()
        found_keywords = [kw for kw in URGENT_KEYWORDS if kw in message_lower]
        if found_keywords:
            factors.append(f"Urgent keywords detected: {', '.join(found_keywords)}")
            if base_level == "low":
                base_level = "medium"
            elif base_level == "medium":
                base_level = "high"

        # --- Low confidence may increase priority ---
        if intent_result.confidence < 0.5:
            factors.append(
                f"Low intent confidence ({intent_result.confidence:.2f}) — "
                "may need human review"
            )
            if base_level == "low":
                base_level = "medium"

        logger.info(f"[PriorityNode] Priority: {base_level} | Factors: {factors}")

        return PriorityResult(level=base_level, factors=factors)
