"""
Post-Match Press Conference REST Router
"""

from fastapi import APIRouter, HTTPException, status

from ai_drs.analytics.press_release_generator import PressReleaseGenerator, PressReleaseKit
from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.api.press")

press_router = APIRouter(prefix="/api/v1/press", tags=["Media Press Kit Engine"])


@press_router.get("/release/{match_id}", response_model=PressReleaseKit)
def get_press_release(match_id: str, player_of_match: str = "V. Kohli"):
    """Returns automated post-match media press release kit and social media thread."""
    match_state = MatchState(match_id=match_id, runs=188, wickets=4, overs=20, legal_balls=0)
    kit = PressReleaseGenerator.generate_press_kit(match_state, player_of_match=player_of_match)

    logger.info(f"Served Media Press Kit for Match [{match_id}]")
    return kit
