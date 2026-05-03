import logging
from typing import List

from app.core.schemas import (
    ValidationResult,
    DraftResult,
    IntentResult,
    PolicyResult,
)

logger = logging.getLogger(__name__)

# Minimum acceptable reply length (characters)
MIN_REPLY_LENGTH = 50

# Minimum acceptable intent confidence
MIN_CONFIDENCE = 0.5

# Phrases that should NOT appear in a professional banking response
PROHIBITED_PHRASES = [
    "i don't know",
    "i'm not sure",
    "i cannot help",
    "as an ai",
    "as a language model",
    "i apologize for any inconvenience this may cause, but i am unable",
]


class ValidationNode:
    """
    Validates the generated draft reply for quality, consistency
    with policy, and completeness.
    """

    async def run(
        self,
        draft_result: DraftResult,
        intent_result: IntentResult,
        policy_result: PolicyResult,
    ) -> ValidationResult:
        """
        Validate the draft response.

        Args:
            draft_result: Output from the Draft Node.
            intent_result: Output from the Intent Node.
            policy_result: Output from the Policy Node.

        Returns:
            ValidationResult with is_valid, issues list, and quality score.
        """
        logger.info("[ValidationNode] Validating draft response...")

        issues: List[str] = []
        score = 1.0

        # --- Check 1: Reply length ---
        if len(draft_result.reply) < MIN_REPLY_LENGTH:
            issues.append(
                f"Reply is too short ({len(draft_result.reply)} chars, "
                f"minimum {MIN_REPLY_LENGTH})"
            )
            score -= 0.3

        # --- Check 2: Intent confidence ---
        if intent_result.confidence < MIN_CONFIDENCE:
            issues.append(
                f"Intent confidence is low ({intent_result.confidence:.2f}), "
                "response may not address the correct issue"
            )
            score -= 0.2

        # --- Check 3: Policy reference ---
        reply_lower = draft_result.reply.lower()
        # Check if the reply mentions something related to the policy
        policy_keywords = policy_result.policy_title.lower().split()
        has_policy_ref = any(kw in reply_lower for kw in policy_keywords if len(kw) > 3)
        if not has_policy_ref and policy_result.policy_title != "General Customer Support Policy":
            issues.append(
                "Reply does not appear to reference the relevant policy"
            )
            score -= 0.1

        # --- Check 4: Prohibited phrases ---
        for phrase in PROHIBITED_PHRASES:
            if phrase in reply_lower:
                issues.append(f"Reply contains prohibited phrase: '{phrase}'")
                score -= 0.2
                break

        # --- Check 5: Missing information noted ---
        if draft_result.missing_info and len(draft_result.missing_info) > 3:
            issues.append(
                "Too many items flagged as missing — the reply may be too vague"
            )
            score -= 0.1

        # --- Check 6: Reply is not empty ---
        if not draft_result.reply.strip():
            issues.append("Reply is empty")
            score = 0.0

        # Clamp score
        score = max(0.0, min(1.0, score))
        is_valid = len(issues) == 0 and score >= 0.6

        logger.info(
            f"[ValidationNode] Valid={is_valid}, Score={score:.2f}, "
            f"Issues={len(issues)}"
        )

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=score,
        )
