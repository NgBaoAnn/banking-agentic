import logging

from app.core.schemas import (
    RoutingResult,
    IntentResult,
    PriorityResult,
    PolicyResult,
    DraftResult,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class RouterNode:
    """
    Makes the final routing decision for the customer case based on
    the aggregated outputs of the pipeline.
    """

    async def run(
        self,
        intent_result: IntentResult,
        priority_result: PriorityResult,
        policy_result: PolicyResult,
        draft_result: DraftResult,
        validation_result: ValidationResult,
    ) -> RoutingResult:
        """
        Determine the final action for this customer case.

        Args:
            intent_result: Output from Intent Node.
            priority_result: Output from Priority Node.
            policy_result: Output from Policy Node.
            draft_result: Output from Draft Node.
            validation_result: Output from Validation Node.

        Returns:
            RoutingResult with action (reply/ask_more/escalate) and reason.
        """
        logger.info("[RouterNode] Making routing decision...")

        reasons = []

        # ── Rule 1: High priority + validation fail → Escalate ──────
        if (
            priority_result.level == "high"
            and not validation_result.is_valid
        ):
            reasons.append(
                "High-priority case with validation issues — requires human review"
            )
            return RoutingResult(action="escalate", reason="; ".join(reasons))

        # ── Rule 2: Policy requires escalation → Escalate ───────────
        if policy_result.escalation_required:
            reasons.append(
                f"Policy '{policy_result.policy_title}' requires escalation"
            )
            # If priority is also high, definitely escalate
            if priority_result.level == "high":
                return RoutingResult(action="escalate", reason="; ".join(reasons))
            # Otherwise, still escalate but note it could be borderline
            reasons.append("Escalation recommended by policy")
            return RoutingResult(action="escalate", reason="; ".join(reasons))

        # ── Rule 3: Unknown intent or very low confidence → Escalate ─
        if (
            intent_result.intent == "unknown"
            or intent_result.confidence < 0.3
        ):
            reasons.append(
                f"Intent is uncertain ('{intent_result.intent}', "
                f"confidence={intent_result.confidence:.2f}) — needs human judgment"
            )
            return RoutingResult(action="escalate", reason="; ".join(reasons))

        # ── Rule 4: Missing info → Ask for more information ─────────
        if draft_result.missing_info and len(draft_result.missing_info) > 0:
            # If validation passed and priority is not high, ask for more info
            if validation_result.is_valid and priority_result.level != "high":
                reasons.append(
                    f"Additional information needed: {', '.join(draft_result.missing_info)}"
                )
                return RoutingResult(action="ask_more", reason="; ".join(reasons))

        # ── Rule 5: Low confidence but otherwise OK → Ask more ──────
        if intent_result.confidence < 0.5:
            reasons.append(
                "Moderate uncertainty in intent detection — "
                "requesting clarification from customer"
            )
            return RoutingResult(action="ask_more", reason="; ".join(reasons))

        # ── Rule 6: Validation failed → Escalate ────────────────────
        if not validation_result.is_valid:
            reasons.append(
                f"Draft validation failed (score={validation_result.score:.2f}): "
                f"{'; '.join(validation_result.issues)}"
            )
            return RoutingResult(action="escalate", reason="; ".join(reasons))

        # ── Default: Send reply ───────
        reasons.append(
            f"All checks passed (intent confidence={intent_result.confidence:.2f}, "
            f"validation score={validation_result.score:.2f}, "
            f"priority={priority_result.level})"
        )
        return RoutingResult(action="reply", reason="; ".join(reasons))
