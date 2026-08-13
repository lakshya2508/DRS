"""
Unit tests for Automated Press Release & Social Media Copy Generator Module
"""

import pytest

from ai_drs.analytics.press_release_generator import PressReleaseGenerator, PressReleaseKit
from ai_drs.match.models import MatchState


def test_press_release_generator():
    match_state = MatchState(match_id="M_PRESS_01", runs=195, wickets=4, overs=20, legal_balls=0)

    kit = PressReleaseGenerator.generate_press_kit(match_state, "V. Kohli")

    assert isinstance(kit, PressReleaseKit)
    assert "MATCH REPORT" in kit.headline
    assert "195/4" in kit.official_press_release_body
    assert len(kit.twitter_thread_posts) == 3
    assert "#Cricket" in kit.hashtags
