"""
Live Match REST API Router — Real-time cricket league DRS decisions,
ball-by-ball match tracking, and ICC DRS review budget management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.live_match_engine import (
    CreateLiveMatchRequest,
    DRSReviewRequest,
    LiveDelivery,
    LiveMatchEngine,
    LiveMatchState,
    DRSReviewResult,
)

logger = setup_logger("ai_drs.api.live_match")

live_match_router = APIRouter(prefix="/api/v1/live", tags=["Live Match DRS API"])
router = live_match_router

# Single shared engine instance (in-memory live match state)
_engine = LiveMatchEngine()


class AddDeliveryRequest(BaseModel):
    over_number: int = Field(..., ge=1)
    ball_number: int = Field(..., ge=1, le=6)
    bowler_name: str
    batter_name: str
    runs_scored: int = Field(default=0, ge=0)
    extras: int = Field(default=0, ge=0)
    is_wicket: bool = False
    wicket_type: Optional[str] = None
    ball_speed_kmh: Optional[float] = None


@live_match_router.post("/match/create", response_model=LiveMatchState, status_code=status.HTTP_201_CREATED)
def create_live_match(req: CreateLiveMatchRequest):
    """Create a new live match session for any modern cricket league (IPL, T20I, ODI, Test, SA20, BBL etc.)."""
    try:
        match = _engine.create_match(req)
        logger.info(f"New live match created: {match.match_id}")
        return match
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@live_match_router.get("/match/list", response_model=List[LiveMatchState])
def list_live_matches():
    """List all active live match sessions."""
    return _engine.list_matches()


@live_match_router.get("/match/{match_id}", response_model=LiveMatchState)
def get_live_match(match_id: str):
    """Get current live state, score and DRS log for a match."""
    match = _engine.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")
    return match


@live_match_router.post("/match/{match_id}/delivery", response_model=LiveMatchState)
def add_live_delivery(match_id: str, req: AddDeliveryRequest):
    """Record a live ball delivery for the current over."""
    try:
        from ai_drs.match.live_match_engine import LiveDelivery
        delivery = LiveDelivery(
            over_number=req.over_number,
            ball_number=req.ball_number,
            bowler_name=req.bowler_name,
            batter_name=req.batter_name,
            runs_scored=req.runs_scored,
            extras=req.extras,
            is_wicket=req.is_wicket,
            wicket_type=req.wicket_type,
            ball_speed_kmh=req.ball_speed_kmh,
        )
        return _engine.add_delivery(match_id, delivery)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@live_match_router.post("/match/{match_id}/drs", response_model=DRSReviewResult)
def request_drs_review(match_id: str, req: DRSReviewRequest):
    """
    Submit a live DRS review request for an LBW decision.
    Automatically applies ICC 3-Zone (Pitching / Impact / Wicket-line) logic.
    Deducts from team's DRS review budget if review is unsuccessful.
    """
    try:
        req.match_id = match_id
        result = _engine.process_drs_review(req)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@live_match_router.get("/match/{match_id}/drs/budget")
def get_drs_budget(match_id: str):
    """Returns current DRS review budget remaining for both teams in this match."""
    try:
        return _engine.get_drs_budget(match_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@live_match_router.get("/match/{match_id}/drs/log", response_model=List[DRSReviewResult])
def get_drs_review_log(match_id: str):
    """Returns the complete DRS review history log for the match."""
    match = _engine.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")
    return match.drs_reviews_log


@live_match_router.get("/leagues")
def get_supported_leagues():
    """Returns all supported cricket leagues and their DRS review allocations per ICC rules."""
    from ai_drs.match.live_match_engine import LEAGUE_DRS_REVIEWS
    return {
        "supported_leagues": [
            {"league": k, "drs_reviews_per_team_per_innings": v}
            for k, v in LEAGUE_DRS_REVIEWS.items()
        ]
    }
