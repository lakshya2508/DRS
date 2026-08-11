"""
Unit tests for Batter Weakness & Pitch Zone Exploit Finder Module
"""

import pytest

from ai_drs.ai_coach.weakness_detector import (
    BatterVulnerabilityProfile,
    BatterWeaknessDetector,
)
from ai_drs.match.models import DeliveryEvent


def test_batter_weakness_detector():
    deliveries = [
        DeliveryEvent(ball_number=1, over_number=0, runs_batter=0),
        DeliveryEvent(ball_number=2, over_number=0, runs_batter=0),
        DeliveryEvent(ball_number=3, over_number=0, runs_batter=0),
        DeliveryEvent(ball_number=4, over_number=0, is_wicket=True, dismissal_type="Caught"),
    ]

    profile = BatterWeaknessDetector.analyze_batter_vulnerabilities("Batter X", deliveries)

    assert isinstance(profile, BatterVulnerabilityProfile)
    assert profile.batter_name == "Batter X"
    assert profile.total_deliveries_analyzed == 4
    assert profile.dot_ball_rate_pct == 75.0
    assert profile.dismissal_rate_pct == 25.0
    assert "slip cordon" in profile.tactical_recommendation.lower()


def test_empty_deliveries_weakness():
    profile = BatterWeaknessDetector.analyze_batter_vulnerabilities("New Batter", [])
    assert profile.total_deliveries_analyzed == 0
    assert profile.dot_ball_rate_pct == 0.0
