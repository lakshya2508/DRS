"""
Analytics Router — REST API endpoints for fulltrack.ai performance graphics.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from ai_drs.analytics.analytics_engine import AnalyticsEngine, DeliveryRecord

analytics_router = APIRouter(prefix="/api/v1/analytics", tags=["Performance Analytics"])
_engine = AnalyticsEngine()


@analytics_router.get("/pitch-map", response_model=dict)
def get_pitch_map(
    bowler_name: Optional[str] = Query(None),
    match_id: Optional[str] = Query(None),
):
    """Returns pitch landing coordinates and length distribution metrics."""
    data = _engine.get_pitch_map(bowler_name=bowler_name, match_id=match_id)
    return {"status": "ok", "pitch_map": data.__dict__}


@analytics_router.get("/wagon-wheel", response_model=dict)
def get_wagon_wheel(
    batter_name: Optional[str] = Query(None),
    match_id: Optional[str] = Query(None),
):
    """Returns shot sector vectors and boundary counts for batting analysis."""
    data = _engine.get_wagon_wheel(batter_name=batter_name, match_id=match_id)
    return {"status": "ok", "wagon_wheel": data.__dict__}


@analytics_router.get("/beehive", response_model=dict)
def get_beehive(
    bowler_name: Optional[str] = Query(None),
    match_id: Optional[str] = Query(None),
):
    """Returns stump-level impact coordinates and target hit accuracy."""
    data = _engine.get_beehive(bowler_name=bowler_name, match_id=match_id)
    return {"status": "ok", "beehive": data.__dict__}


@analytics_router.get("/player/{player_name}", response_model=dict)
def get_player_stats(player_name: str):
    """Returns cumulative batting & bowling performance statistics."""
    stats = _engine.get_player_stats(player_name)
    return {"status": "ok", "stats": stats}


@analytics_router.post("/record-delivery", response_model=dict)
def record_delivery(delivery: DeliveryRecord):
    """Ingests a new ball delivery record into the analytics engine."""
    _engine.add_delivery(delivery)
    return {"status": "recorded", "delivery_id": delivery.delivery_id}
