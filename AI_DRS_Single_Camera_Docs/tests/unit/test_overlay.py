"""
Unit tests for Broadcaster DRS Decision Card & Split-Screen Overlay Renderer Module
"""

import pytest

from ai_drs.api.review_service import (
    DRSEvidencePayload,
    DecisionType,
    HitStumpsStatus,
    PitchingZone,
    ReviewResultResponse,
)
from ai_drs.graphics.overlay_engine import BroadcastDRSOverlayCard, BroadcastOverlayEngine


def test_broadcast_overlay_engine_rendering():
    review = ReviewResultResponse(
        review_id="REV_TV_101",
        video_source="test.mp4",
        decision=DecisionType.OUT,
        confidence_score=0.92,
        evidence=DRSEvidencePayload(
            pitching_zone=PitchingZone.IN_LINE,
            impact_zone=PitchingZone.IN_LINE,
            hit_stumps_status=HitStumpsStatus.HITTING,
            predicted_wicket_y=20.12,
            predicted_wicket_z=0.5
        )
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
