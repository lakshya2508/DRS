"""
FastAPI Application for AI DRS — Single-Camera LBW Review System
"""

import tempfile
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, Query, status
from fastapi.middleware.cors import CORSMiddleware

from ai_drs.api.match_router import router as match_router
from ai_drs.api.review_service import ReviewPipelineService, ReviewResultResponse
from ai_drs.calibration.pitch_calibration import CalibrationData, PitchCalibrator
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api")

app = FastAPI(
    title="AI DRS — Single-Camera LBW Review System & Autonomous Match Engine API",
    description="REST API for single-camera cricket LBW review and autonomous match state engine",
    version="1.7.0"
)

# Enable CORS for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router)


# In-memory stores for reviews and calibrations
reviews_db: Dict[str, ReviewResultResponse] = {}
calibrations_db: Dict[str, CalibrationData] = {}
pipeline_service = ReviewPipelineService()


from fastapi.responses import HTMLResponse
from ai_drs.api.mobile_app import get_mobile_app_html

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the Cricbuzz Mobile App UI."""
    return get_mobile_app_html()



@app.get("/health")
def read_health():
    """Healthcheck endpoint."""
    return {
        "service": "AI DRS — Single-Camera LBW Review & Autonomous Match Engine",
        "status": "online",
        "version": "2.0.0"
    }



@app.post("/api/v1/reviews", response_model=ReviewResultResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    file: UploadFile = File(...),
    batter_stance: str = Query("RHB", description="Batter stance: 'RHB' or 'LHB'"),
    calibration_id: Optional[str] = Query(None, description="Registered camera calibration ID")
):
    """Uploads a delivery MP4/MOV video file and runs the complete AI DRS review pipeline."""
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload an MP4, MOV, or AVI video."
        )

    calib = calibrations_db.get(calibration_id) if calibration_id else None

    # Save uploaded file temporarily
    temp_dir = Path("data/raw")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / f"upload_{file.filename}"

    try:
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)

        response = pipeline_service.process_video(
            video_path=temp_file_path,
            calibration=calib,
            batter_stance=batter_stance
        )
        reviews_db[response.review_id] = response
        return response

    except Exception as e:
        logger.error(f"Error processing review upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal pipeline error: {str(e)}"
        )
    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception:
                pass


@app.get("/api/v1/reviews/{review_id}", response_model=ReviewResultResponse)
def get_review(review_id: str):
    """Retrieves review status and final LBW decision by review ID."""
    if review_id not in reviews_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review ID '{review_id}' not found."
        )
    return reviews_db[review_id]


@app.get("/api/v1/reviews/{review_id}/evidence")
def get_review_evidence(review_id: str):
    """Retrieves structured computer vision evidence details for a review ID."""
    if review_id not in reviews_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review ID '{review_id}' not found."
        )
    rev = reviews_db[review_id]
    return {
        "review_id": rev.review_id,
        "result": rev.result,
        "confidence": rev.confidence,
        "recommendation_reason": rev.recommendation_reason,
        "evidence": {
            "pitching": rev.pitching,
            "impact": rev.impact,
            "wicket": rev.wicket,
            "ball_track": rev.ball_track,
            "calibration": rev.calibration
        }
    }


@app.post("/api/v1/calibration", status_code=status.HTTP_201_CREATED)
def create_calibration(calibration: CalibrationData):
    """Registers and stores a camera pitch calibration profile."""
    if not calibration.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid calibration payload: {calibration.validation_message}"
        )
    calibrations_db[calibration.camera_id] = calibration
    return {
        "status": "success",
        "camera_id": calibration.camera_id,
        "reprojection_error_px": calibration.reprojection_error_px
    }
