"""
Unit tests for Highlight Reel Generator & Match Summary Exporter Module
"""

import pytest

from ai_drs.evaluation.highlight_generator import (
    HighlightClip,
    HighlightReelGenerator,
    MatchHighlightPackage,
)
from ai_drs.match.models import DeliveryEvent, MatchState


def test_highlight_reel_generation():
    match_state = MatchState(match_id="M_HIGHLIGHT_1", runs=42, wickets=2, overs=3, legal_balls=18)

    deliveries = [
        DeliveryEvent(ball_number=1, over_number=0, runs_batter=0),
        DeliveryEvent(ball_number=2, over_number=0, runs_batter=4),  # Boundary 4
        DeliveryEvent(ball_number=3, over_number=0, runs_batter=6),  # Boundary 6
        DeliveryEvent(ball_number=4, over_number=0, is_wicket=True, dismissal_type="Bowled"),  # Wicket
        DeliveryEvent(ball_number=5, over_number=0, drs_review_requested=True),  # DRS Review
    ]

    package = HighlightReelGenerator.generate_highlight_manifest(match_state, deliveries)

    assert isinstance(package, MatchHighlightPackage)
    assert package.match_id == "M_HIGHLIGHT_1"
    assert package.total_runs == 42
    assert package.total_wickets == 2
    assert len(package.highlights) == 4

    types = [h.event_type for h in package.highlights]
    assert "BOUNDARY_FOUR" in types
    assert "BOUNDARY_SIX" in types
    assert "WICKET" in types
    assert "DRS_REVIEW" in types


def test_empty_deliveries_highlight():
    match_state = MatchState(match_id="M_EMPTY", runs=0, wickets=0)
    package = HighlightReelGenerator.generate_highlight_manifest(match_state, [])
    assert len(package.highlights) == 0
