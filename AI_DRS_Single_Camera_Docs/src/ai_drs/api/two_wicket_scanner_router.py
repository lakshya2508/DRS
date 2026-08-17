"""
Two-Wicket Pitch Scanner Router — REST API Endpoints for Dual Wicket Axis Calibration & Pitch Coordinates.
"""

from typing import Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_drs.calibration.two_wicket_scanner import (
    two_wicket_scanner,
    TwoWicketCalibrationState,
    LineLengthClassification,
    WicketAnchor
)

two_wicket_router = APIRouter(prefix="/api/v1/two-wicket-scanner", tags=["Two-Wicket Pitch Scanner"])


class UpdateWicketsRequest(BaseModel):
    wicket_a_x: float = Field(..., description="Wicket A center X pixel")
    wicket_a_y: float = Field(..., description="Wicket A center Y pixel")
    wicket_b_x: float = Field(..., description="Wicket B center X pixel")
    wicket_b_y: float = Field(..., description="Wicket B center Y pixel")
    confidence_a: float = Field(default=0.96, ge=0.0, le=1.0)
    confidence_b: float = Field(default=0.94, ge=0.0, le=1.0)


class TransformPointRequest(BaseModel):
    pixel_x: float
    pixel_y: float


class ClassifyDeliveryRequest(BaseModel):
    pitch_x_meters: float
    pitch_y_meters: float
    batter_hand: str = Field(default="RIGHT", description="RIGHT or LEFT")


@two_wicket_router.get("/status", response_model=TwoWicketCalibrationState)
@two_wicket_router.get("/two-wicket-scanner/status", response_model=TwoWicketCalibrationState)
def get_scanner_status():
    """Returns the current 2-Wicket scanner calibration status and pitch axis parameters."""
    return two_wicket_scanner.update_calibration()


@two_wicket_router.post("/update-anchors", response_model=TwoWicketCalibrationState)
def update_wicket_anchors(req: UpdateWicketsRequest):
    """Updates Wicket A and Wicket B anchor coordinates and recalculates the primary pitch axis."""
    two_wicket_scanner.wicket_a = WicketAnchor(
        wicket_id="WICKET_A",
        center_pixel=(req.wicket_a_x, req.wicket_a_y),
        stump_centers=[(req.wicket_a_x - 20, req.wicket_a_y), (req.wicket_a_x, req.wicket_a_y), (req.wicket_a_x + 20, req.wicket_a_y)],
        confidence=req.confidence_a
    )
    two_wicket_scanner.wicket_b = WicketAnchor(
        wicket_id="WICKET_B",
        center_pixel=(req.wicket_b_x, req.wicket_b_y),
        stump_centers=[(req.wicket_b_x - 10, req.wicket_b_y), (req.wicket_b_x, req.wicket_b_y), (req.wicket_b_x + 10, req.wicket_b_y)],
        confidence=req.confidence_b
    )
    return two_wicket_scanner.update_calibration()


@two_wicket_router.post("/transform-point")
def transform_pixel_to_pitch(req: TransformPointRequest):
    """Transforms a 2D camera pixel coordinate to Pitch World Coordinates (x_meters, y_meters)."""
    x_m, y_m = two_wicket_scanner.pixel_to_pitch_coords(req.pixel_x, req.pixel_y)
    return {
        "pixel_x": req.pixel_x,
        "pixel_y": req.pixel_y,
        "pitch_x_meters": x_m,
        "pitch_y_meters": y_m,
        "unit": "meters"
    }


@two_wicket_router.post("/classify-delivery", response_model=LineLengthClassification)
def classify_delivery_coords(req: ClassifyDeliveryRequest):
    """Classifies delivery line and length from pitch coordinates relative to the 2-wicket pitch axis."""
    return two_wicket_scanner.classify_line_and_length(
        pitch_x_meters=req.pitch_x_meters,
        pitch_y_meters=req.pitch_y_meters,
        batter_hand=req.batter_hand
    )
