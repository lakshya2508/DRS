"""
Unit tests for Broadcaster DRS Decision Card & Split-Screen Overlay Renderer Module
"""

import pytest

from ai_drs.api.review_service import ReviewResultResponse
from ai_drs.graphics.overlay_engine import BroadcastDRSOverlayCard, BroadcastOverlayEngine


def test_broadcast_overlay_engine_rendering():
    review = ReviewResultResponse(
        review_id="REV_TV_101",
        result="OUT",
        confidence=0.92,
        recommendation_reason="Pitching in line, Impact in line, Wickets hitting",
        pitching={"zone": "in_line"},
        impact={"zone": "in_line"},
        wicket={"status": "hitting"},
        ball_track={},
        calibration={}
    )


    card = BroadcastOverlayEngine.render_drs_decision_card(review)

    assert isinstance(card, BroadcastDRSOverlayCard)
    assert card.review_id == "REV_TV_101"
    assert card.pitching_badge == "PITCHING: IN_LINE"
    assert card.impact_badge == "IMPACT: IN_LINE"
    assert card.wickets_badge == "WICKETS: HITTING"
    assert card.final_decision_badge == "OUT"
    assert "<svg" in card.svg_overlay_xml
    assert "OUT" in card.svg_overlay_xml
