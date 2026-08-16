"""
FastAPI Application for AI DRS — Single-Camera LBW Review System
"""

import tempfile
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, Query, status
from fastapi.middleware.cors import CORSMiddleware

from ai_drs.api.match_router import router as match_router
from ai_drs.api.tournament_router import router as tournament_router
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

from fastapi import FastAPI, File, HTTPException, UploadFile, Query, WebSocket, WebSocketDisconnect, status
from ai_drs.api.websocket_manager import ws_manager, BroadcastEvent
import time

from ai_drs.api.tournament_router import tournament_router
from ai_drs.api.coach_router import coach_router
from ai_drs.api.press_router import press_router
from ai_drs.api.sandbox_router import sandbox_router
from ai_drs.api.reel_router import reel_router
from ai_drs.api.vr_router import vr_router
from ai_drs.api.curator_router import curator_router
from ai_drs.api.ad_router import ad_router
from ai_drs.api.webhook_router import webhook_router
from ai_drs.api.llm_router import llm_router
from ai_drs.api.minimal_api import minimal_drs_router
from ai_drs.api.real_model_router import real_model_router
from ai_drs.api.live_match_router import live_match_router
from ai_drs.api.live_pipeline_router import live_pipeline_router
from ai_drs.api.calibration_router import calibration_router

app.include_router(minimal_drs_router)
app.include_router(real_model_router)
app.include_router(live_match_router)
app.include_router(live_pipeline_router)
app.include_router(calibration_router)
app.include_router(match_router)
app.include_router(tournament_router)
app.include_router(coach_router)
app.include_router(press_router)
app.include_router(sandbox_router)
app.include_router(reel_router)
app.include_router(vr_router)
app.include_router(curator_router)
app.include_router(ad_router)
app.include_router(webhook_router)
app.include_router(llm_router)


from fastapi.responses import HTMLResponse

@app.get("/live", response_class=HTMLResponse, tags=["Live Dashboard"])
def live_dashboard():
    """Serves the full-screen AI DRS Live Operator Dashboard UI."""
    dashboard_path = Path(__file__).parent.parent / "static" / "live_dashboard.html"
    return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))


@app.get("/scoreboard", response_class=HTMLResponse, tags=["Live Dashboard"])
def ground_scoreboard():
    """Serves the full-screen Ground Scoreboard for stadium displays."""
    board_path = Path(__file__).parent.parent / "static" / "ground_scoreboard.html"
    return HTMLResponse(content=board_path.read_text(encoding="utf-8"))


@app.get("/api/v1/leagues", tags=["League Database"])
def get_league_teams():
    """Returns all supported cricket league teams with full player rosters."""
    from ai_drs.match.cricket_league_db import IPL_TEAMS, INDIA_T20I
    teams = {k: v.model_dump() for k, v in IPL_TEAMS.items()}
    teams["IND"] = INDIA_T20I.model_dump()
    return {"total_teams": len(teams), "teams": teams}


@app.get("/setup", response_class=HTMLResponse, tags=["Live Dashboard"])
def match_setup_wizard():
    """Serves the Match Setup Wizard — configure league, teams and camera before going live."""
    setup_path = Path(__file__).parent.parent / "static" / "match_setup.html"
    return HTMLResponse(content=setup_path.read_text(encoding="utf-8"))


@app.websocket("/ws/match/{match_id}")











@app.websocket("/ws/match/{match_id}")
async def websocket_match_endpoint(websocket: WebSocket, match_id: str):
    """Real-time WebSocket endpoint streaming live match events to connected clients."""
    await ws_manager.connect(match_id, websocket)
    try:
        while True:
            # Keep connection alive and receive client heartbeats/messages
            data_text = await websocket.receive_text()
            logger.debug(f"Received WebSocket ping from client on Match [{match_id}]: {data_text}")
    except WebSocketDisconnect:
        ws_manager.disconnect(match_id, websocket)
    except Exception as e:
        ws_manager.disconnect(match_id, websocket)



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
