import json
import logging

from app.clients.ollama_client import OllamaClient
from app.core.schemas import (
    DraftResult,
    IntentResult,
    PriorityResult,
    PolicyResult,
)

logger = logging.getLogger(__name__)

DRAFT_SYSTEM_PROMPT = """You are a professional banking customer support agent. \
Your task is to draft a helpful, empathetic, and accurate response to the customer.

Rules:
- Be polite, clear, and concise.
- Reference the relevant policy when applicable.
- If information is missing from the customer, note what is needed.
- Suggest a clear next action.
- Do NOT make promises the bank cannot keep.
- Keep the response under 200 words."""

DRAFT_USER_TEMPLATE = """Customer Message: {message}

Detected Intent: {intent} (Confidence: {confidence:.0%})
Priority Level: {priority}
Relevant Policy: {policy_title}
Policy Details: {policy_text}
Typical Resolution: {typical_resolution}

Please draft a professional reply to the customer. Also indicate:
1. Any missing information needed from the customer (as a JSON list of strings).
2. The suggested next action (as a short string).

Respond in this exact JSON format:
{{
    "reply": "<your draft reply to the customer>",
    "missing_info": ["<info1>", "<info2>"],
    "suggested_action": "<next action>"
}}"""


class DraftNode:
    """
    Generates a draft reply using the Ollama LLM, considering the full
    context from previous nodes.
    """

    def __init__(self):
        self.client = OllamaClient()

    async def run(
        self,
        message: str,
        intent_result: IntentResult,
        priority_result: PriorityResult,
        policy_result: PolicyResult,
    ) -> DraftResult:
        """
        Generate a draft customer response via the LLM.

        Args:
            message: Original customer message.
            intent_result: Output from Intent Node.
            priority_result: Output from Priority Node.
            policy_result: Output from Policy Node.

        Returns:
            DraftResult with reply, missing_info, and suggested_action.
        """
        logger.info("[DraftNode] Generating draft response via Ollama...")

        prompt = DRAFT_USER_TEMPLATE.format(
            message=message,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            priority=priority_result.level,
            policy_title=policy_result.policy_title,
            policy_text=policy_result.policy_text,
            typical_resolution=policy_result.typical_resolution,
        )

        try:
            raw_response = await self.client.generate(
                prompt=prompt,
                system=DRAFT_SYSTEM_PROMPT,
            )
            result = self._parse_response(raw_response)
            logger.info(f"[DraftNode] Draft generated ({len(result.reply)} chars)")
            return result

        except Exception as e:
            logger.error(f"[DraftNode] LLM call failed: {e}")
            return self._fallback_draft(
                message, intent_result, priority_result, policy_result
            )

    def _parse_response(self, raw: str) -> DraftResult:
        """Try to parse the LLM output as JSON, fall back to plain text."""
        # Try to extract JSON from the response
        try:
            # Find JSON block in the response
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(raw[start:end])
                return DraftResult(
                    reply=data.get("reply", raw),
                    missing_info=data.get("missing_info", []),
                    suggested_action=data.get("suggested_action", ""),
                )
        except json.JSONDecodeError:
            pass

        # Fallback: use raw text as the reply
        return DraftResult(
            reply=raw.strip(),
            missing_info=[],
            suggested_action="Review and send the response",
        )

    def _fallback_draft(
        self,
        message: str,
        intent_result: IntentResult,
        priority_result: PriorityResult,
        policy_result: PolicyResult,
    ) -> DraftResult:
        """Generate a basic fallback draft when the LLM is unavailable."""
        reply = (
            f"Thank you for contacting us regarding your {intent_result.intent.replace('_', ' ')} issue. "
            f"We understand this is a {priority_result.level}-priority matter for you.\n\n"
            f"According to our policy: {policy_result.policy_text}\n\n"
            f"Recommended steps: {policy_result.typical_resolution}\n\n"
            f"Please don't hesitate to reach out if you need further assistance."
        )
        return DraftResult(
            reply=reply,
            missing_info=["Account number or customer ID for verification"],
            suggested_action="Send reply after verification",
        )
