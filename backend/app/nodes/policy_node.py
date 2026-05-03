import logging

from app.core.schemas import PolicyResult
from app.data.policies import get_policy

logger = logging.getLogger(__name__)


class PolicyNode:
    """
    Retrieves a relevant FAQ entry, policy snippet, or support guideline
    based on the detected intent.
    """

    async def run(self, intent: str) -> PolicyResult:
        """
        Look up the policy for the given intent.

        Args:
            intent: Predicted banking intent label.

        Returns:
            PolicyResult with the matched policy details.
        """
        logger.info(f"[PolicyNode] Retrieving policy for intent='{intent}'...")

        policy = get_policy(intent)

        result = PolicyResult(
            policy_title=policy["title"],
            policy_text=policy["policy_text"],
            typical_resolution=policy["typical_resolution"],
            escalation_required=policy.get("escalation_required", False),
        )

        logger.info(f"[PolicyNode] Matched policy: '{result.policy_title}'")
        return result
