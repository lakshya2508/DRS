"""
AI Coach Live Match Tactical Briefing REST Router
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_drs.ai_coach.field_recommender import FieldRecommenderEngine, TacticalFieldSetting
from ai_drs.ai_coach.weakness_detector import BatterVulnerabilityProfile, BatterWeaknessDetector
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.coach")

coach_router = APIRouter(prefix="/api/v1/coach", tags=["AI Coach Engine"])


class TacticalBriefingRequest(BaseModel):
    batter_name: str
    situation_badge: Optional[str] = "STABLE"
    primary_zone: Optional[str] = "COVER"


class TacticalBriefingResponse(BaseModel):
    batter_profile: BatterVulnerabilityProfile
    recommended_field: TacticalFieldSetting


@coach_router.post("/briefing", response_model=TacticalBriefingResponse)
def get_tactical_briefing(req: TacticalBriefingRequest):
    """Retrieves live in-game AI Coach tactical briefing and field recommendations."""
    profile = BatterWeaknessDetector.analyze_batter_vulnerabilities(req.batter_name, [])
    field_setting = FieldRecommenderEngine.recommend_field_setting(
        situation_badge=req.situation_badge,
        batter_primary_zone=req.primary_zone
    )

    logger.info(f"Generated Tactical Briefing for Batter [{req.batter_name}]")
    return TacticalBriefingResponse(
        batter_profile=profile,
        recommended_field=field_setting
    )
