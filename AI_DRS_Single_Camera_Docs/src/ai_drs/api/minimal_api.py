"""
Minimum AI DRS Production API — Lightweight, Core-Focused Single-Camera LBW Review API
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from ai_drs.api.review_service import ReviewPipelineService
from ai_drs.audio.snicko_detector import SnickoAudioDetector
from ai_drs.calibration.pitch_calibration import PitchCalibrator, Point2D
from ai_drs.common.logging import setup_logger
from ai_drs.enterprise.llm_security_guard import llm_security_guard

logger = setup_logger("ai_drs.api.minimal")

minimal_drs_router = APIRouter(prefix="/api/v1/drs", tags=["Minimum AI DRS API"])
router = minimal_drs_router

pipeline_service = ReviewPipelineService()
snicko_detector = SnickoAudioDetector()



# --- REQUEST & RESPONSE SCHEMAS ---

class MinimalReviewRequest(BaseModel):
    """Minimal LBW decision review request."""
    video_path: str = Field(description="Path to delivery video file")
    batter_stance: str = Field(default="RHB", description="'RHB' or 'LHB'")


class MinimalReviewResponse(BaseModel):
    """Minimal LBW decision review response."""
    review_id: str
    decision: str = Field(description="'OUT', 'NOT_OUT', 'INCONCLUSIVE'")
    confidence_pct: float
    pitching: str
    impact: str
    wickets: str
    recommendation_reason: str
    voice_callout: str


class MinimalCalibrationRequest(BaseModel):
    """Minimal camera calibration request."""
    image_points: List[List[float]] = Field(description="4 image points [[x1, y1], [x2, y2], ...]")
    width: int = Field(default=1280)
    height: int = Field(default=720)


class MinimalCalibrationResponse(BaseModel):
    """Minimal camera calibration response."""
    camera_id: str
    is_valid: bool
    reprojection_error_px: float


class MinimalSnickoRequest(BaseModel):
    """Minimal UltraEdge audio Snicko check request."""
    audio_amplitudes: List[float] = Field(description="PCM audio waveform samples")
    sample_rate_hz: int = Field(default=44100)


class MinimalSnickoResponse(BaseModel):
    """Minimal UltraEdge audio Snicko response."""
    spike_detected: bool
    confidence_pct: float
    frequency_hz: float
    verdict: str


# --- MINIMAL ENDPOINTS ---

@minimal_drs_router.get("/health")
def drs_health_check():
    """Minimal system health check endpoint."""
    return {
        "status": "ONLINE",
        "system": "AI DRS Minimum Production API",
        "version": "30.0.0"
    }


@minimal_drs_router.post("/review", response_model=MinimalReviewResponse)
def execute_minimal_drs_review(
    req: MinimalReviewRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """Core Single-Camera LBW Decision Review Endpoint."""
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        logger.info(f"Minimum AI DRS Review request for video: '{req.video_path}'")

        review_res = pipeline_service.process_video(req.video_path, batter_stance=req.batter_stance)

        pitch_str = review_res.pitching.get("zone", "in_line")
        impact_str = review_res.impact.get("zone", "in_line")
        wicket_str = review_res.wicket.get("status", "hitting")

        callout = (
            f"Checking pitching: {pitch_str}. Checking impact: {impact_str}. "
            f"Checking wickets: {wicket_str}. Final decision: {review_res.result}."
        )

        return MinimalReviewResponse(
            review_id=review_res.review_id,
            decision=review_res.result,
            confidence_pct=round(review_res.confidence * 100.0, 1),
            pitching=pitch_str.upper(),
            impact=impact_str.upper(),
            wickets=wicket_str.upper(),
            recommendation_reason=review_res.recommendation_reason,
            voice_callout=callout
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in minimal DRS review endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@minimal_drs_router.post("/calibrate", response_model=MinimalCalibrationResponse)
def execute_minimal_calibration(
    req: MinimalCalibrationRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """Core Pitch Homography Camera Calibration Endpoint."""
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        if len(req.image_points) != 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactly 4 image points required.")

        img_pts = [Point2D(x=p[0], y=p[1]) for p in req.image_points]
        pitch_pts = [
            Point2D(x=-1.32, y=1.22),
            Point2D(x=1.32, y=1.22),
            Point2D(x=1.32, y=20.12),
            Point2D(x=-1.32, y=20.12),
        ]

        calibrator = PitchCalibrator()
        calib = calibrator.calibrate(img_pts, pitch_pts, image_size=(req.width, req.height))

        return MinimalCalibrationResponse(
            camera_id=calib.camera_id,
            is_valid=calib.is_valid,
            reprojection_error_px=round(calib.reprojection_error_px, 3)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in minimal calibration endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@minimal_drs_router.post("/snicko", response_model=MinimalSnickoResponse)
def execute_minimal_snicko(
    req: MinimalSnickoRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """Core UltraEdge Audio Snicko Contact Detection Endpoint."""
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        import numpy as np
        samples = np.array(req.audio_amplitudes, dtype=np.float32)

        events = snicko_detector.analyze_audio_waveform(samples)
        spike_found = len(events) > 0
        best_event = events[0] if spike_found else None

        return MinimalSnickoResponse(
            spike_detected=spike_found,
            confidence_pct=round(best_event.confidence * 100.0, 1) if best_event else 0.0,
            frequency_hz=round(best_event.peak_frequency_hz, 1) if best_event else 0.0,
            verdict="OUTSIDE_EDGE_DETECTED" if spike_found else "NO_EDGE_CONTACT"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in minimal Snicko endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
