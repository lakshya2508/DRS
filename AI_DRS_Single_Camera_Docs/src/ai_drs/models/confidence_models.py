"""
Confidence-Aware Data Models — Encapsulates metric value, unit, confidence score, and status.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ConfidenceMetric(BaseModel):
    """Encapsulates a computer vision measurement with explicit confidence bounds."""
    value: float = Field(..., description="Measured numerical value")
    unit: str = Field(..., description="Measurement unit (e.g. km/h, m, deg)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    status: Literal["high", "medium", "estimated", "uncertain"] = Field(
        default="high", description="Measurement status"
    )

    @classmethod
    def create(cls, value: float, unit: str, confidence: float) -> "ConfidenceMetric":
        status: Literal["high", "medium", "estimated", "uncertain"] = "high"
        if confidence < 0.5:
            status = "uncertain"
        elif confidence < 0.75:
            status = "estimated"
        elif confidence < 0.90:
            status = "medium"
        return cls(value=round(value, 2), unit=unit, confidence=round(confidence, 2), status=status)


class IndependentDeliveryRecord(BaseModel):
    """Independently queryable delivery record with confidence metrics."""
    delivery_id: str
    match_id: str
    bowler_name: str
    batter_name: str
    speed: ConfidenceMetric
    pitch_x_meters: ConfidenceMetric
    pitch_y_meters: ConfidenceMetric
    post_bounce_deviation_deg: ConfidenceMetric
    verdict: str
    is_drs_reviewed: bool = False
