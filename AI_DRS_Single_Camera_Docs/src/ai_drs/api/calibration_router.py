"""
Calibration REST API — exposes auto-calibration endpoints
so the operator can calibrate the camera from the live dashboard.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np
import cv2
import tempfile
from pathlib import Path

from ai_drs.calibration.auto_calibrator import AutoCalibrator, CalibrationPoints, CalibrationResult
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.calibration")

calibration_router = APIRouter(prefix="/api/v1/calibration", tags=["Camera Calibration"])

_calibrator = AutoCalibrator()


@calibration_router.post("/auto", response_model=dict)
async def auto_calibrate(file: UploadFile = File(...)):
    """
    Auto-calibrate camera geometry by uploading a single frame image.
    Detects crease lines and stump positions automatically via Hough lines.
    """
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")
        result = _calibrator.auto_calibrate_from_frame(frame)
        return {"status": "ok", "calibration": result.__dict__}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@calibration_router.post("/manual", response_model=dict)
def manual_calibrate(
    batter_crease_left_x:  float = 560.0,
    batter_crease_left_y:  float = 520.0,
    batter_crease_right_x: float = 720.0,
    batter_crease_right_y: float = 520.0,
    off_stump_x:           float = 672.0,
    off_stump_y:           float = 510.0,
    leg_stump_x:           float = 608.0,
    leg_stump_y:           float = 510.0,
    frame_w:               int   = 1280,
    frame_h:               int   = 720,
):
    """
    Manual calibration — provide pixel coordinates of four reference points.
    Use this when you know exactly where the crease and stumps appear in the frame.
    """
    points = CalibrationPoints(
        batter_crease_left  = (batter_crease_left_x,  batter_crease_left_y),
        batter_crease_right = (batter_crease_right_x, batter_crease_right_y),
        off_stump_base      = (off_stump_x, off_stump_y),
        leg_stump_base      = (leg_stump_x, leg_stump_y),
    )
    result = _calibrator.calibrate_from_points(points, frame_w, frame_h)
    return {"status": "ok", "calibration": result.__dict__}


@calibration_router.get("/current", response_model=dict)
def get_current_calibration():
    """Returns the current active calibration parameters."""
    return {"calibration": _calibrator.result.__dict__,
            "pitch_geometry": _calibrator.get_pitch_geometry()}


@calibration_router.post("/reset")
def reset_calibration():
    """Resets calibration to default 1280×720 geometry."""
    from ai_drs.calibration.auto_calibrator import CalibrationResult
    _calibrator._result = CalibrationResult()
    return {"status": "reset", "calibration": _calibrator.result.__dict__}
