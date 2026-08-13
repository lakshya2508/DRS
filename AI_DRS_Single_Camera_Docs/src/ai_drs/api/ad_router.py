"""
Virtual Sponsorship & Commercial Ad REST Router
"""

from fastapi import APIRouter, HTTPException, status

from ai_drs.common.logging import setup_logger
from ai_drs.monetization.ad_insertion_engine import ContextualAdCue, ContextualAdInsertionEngine

logger = setup_logger("ai_drs.api.ads")

ad_router = APIRouter(prefix="/api/v1/ads", tags=["Monetization & Ad Insertion Engine"])


@ad_router.get("/trigger/{event_type}", response_model=ContextualAdCue)
def get_commercial_ad_cue(event_type: str):
    """Returns contextual 6-second video ad cue for DRS review delays and over breaks."""
    cue = ContextualAdInsertionEngine.trigger_ad_cue(trigger_event=event_type)
    logger.info(f"Served Commercial Ad Cue [{cue.ad_id}].")
    return cue
