"""Schemas used by the Intent Service."""

from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    """Output of intent classification."""
    intent: str = Field(..., description="Predicted banking intent label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    reason: str = Field(default="", description="Explanation of the classification")
