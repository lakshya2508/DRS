"""
Unit tests for Pitch Pitching Heatmap & Line-Length Density Generator Module
"""

import pytest

from ai_drs.analytics.heatmap_engine import (
    PitchBouncePoint,
    PitchHeatmapEngine,
    PitchHeatmapSummary,
)


def test_pitch_heatmap_engine():
    engine = PitchHeatmapEngine()

    bounce_pts = [
        PitchBouncePoint(x_m=0.0, y_m=12.0),      # GOOD_LENGTH, STUMPS
        PitchBouncePoint(x_m=-0.5, y_m=16.0),    # FULL, OUTSIDE_OFF
        PitchBouncePoint(x_m=0.5, y_m=8.0),       # SHORT, OUTSIDE_LEG
        PitchBouncePoint(x_m=0.05, y_m=19.0),     # YORKER, STUMPS
    ]

    summary = engine.generate_bowler_heatmap("J. Bumrah", bounce_pts)

    assert isinstance(summary, PitchHeatmapSummary)
    assert summary.bowler_name == "J. Bumrah"
    assert summary.total_deliveries == 4
    assert summary.good_length_pct == 25.0
    assert summary.full_pct == 25.0
    assert summary.short_pct == 25.0
    assert summary.yorker_pct == 25.0
    assert summary.stumps_pct == 50.0


def test_empty_heatmap():
    engine = PitchHeatmapEngine()
    summary = engine.generate_bowler_heatmap("Empty Bowler", [])
    assert summary.total_deliveries == 0
    assert summary.good_length_pct == 0.0
