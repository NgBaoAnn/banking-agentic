"""
Input and output schemas used throughout the Banking AI-Agent system.
Includes request/response schemas, node output models, and workflow trace format.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request / Response ──────────────────────────────────────────────

class CustomerRequest(BaseModel):
    """Incoming customer support message."""
    message: str = Field(..., min_length=1, description="Customer message text")


# ── Node output schemas ────────────────────────────────────────────

class IntentResult(BaseModel):
    """Output of the Intent Detection Node."""
    intent: str = Field(..., description="Predicted banking intent label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    reason: str = Field(default="", description="Explanation of the classification")


class PriorityResult(BaseModel):
    """Output of the Priority / Risk Detection Node."""
    level: str = Field(..., description="Priority level: low, medium, or high")
    factors: List[str] = Field(default_factory=list, description="Factors that influenced the priority")


class PolicyResult(BaseModel):
    """Output of the Policy Retrieval Node."""
    policy_title: str = Field(default="", description="Title of the matched policy")
    policy_text: str = Field(default="", description="Relevant policy or FAQ snippet")
    typical_resolution: str = Field(default="", description="Typical resolution for the issue")
    escalation_required: bool = Field(default=False, description="Whether this type of issue typically requires escalation")


class DraftResult(BaseModel):
    """Output of the Response Drafting Node."""
    reply: str = Field(default="", description="Draft reply for the customer")
    missing_info: List[str] = Field(default_factory=list, description="Information still needed from the customer")
    suggested_action: str = Field(default="", description="Next suggested action")


class ValidationResult(BaseModel):
    """Output of the Validation Node."""
    is_valid: bool = Field(default=True, description="Whether the draft passes validation")
    issues: List[str] = Field(default_factory=list, description="List of validation issues found")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quality score of the draft")


class RoutingResult(BaseModel):
    """Output of the Router / Escalation Node."""
    action: str = Field(..., description="Routing decision: reply, ask_more, or escalate")
    reason: str = Field(default="", description="Explanation for the routing decision")


# ── Workflow Trace ──────────────────────────────────────────────────

class WorkflowTrace(BaseModel):
    """Complete trace of all node outputs for observability."""
    intent: Optional[IntentResult] = None
    priority: Optional[PriorityResult] = None
    policy: Optional[PolicyResult] = None
    draft: Optional[DraftResult] = None
    validation: Optional[ValidationResult] = None
    routing: Optional[RoutingResult] = None


# ── Final Agent Response ────────────────────────────────────────────

class AgentResponse(BaseModel):
    """Final response returned to the caller."""
    final_response: str = Field(..., description="The final message to present")
    action: str = Field(..., description="Final action: reply, ask_more, or escalate")
    trace: WorkflowTrace = Field(default_factory=WorkflowTrace, description="Full workflow trace")
