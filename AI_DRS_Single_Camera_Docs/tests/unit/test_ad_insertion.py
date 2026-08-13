"""
Unit tests for Automated Contextual Video Ad Insertion Engine Module
"""

import pytest

from ai_drs.monetization.ad_insertion_engine import ContextualAdCue, ContextualAdInsertionEngine


def test_ad_insertion_engine():
    cue = ContextualAdInsertionEngine.trigger_ad_cue("OVER_BREAK")

    assert isinstance(cue, ContextualAdCue)
    assert cue.trigger_event == "OVER_BREAK"
    assert cue.duration_seconds == 6
    assert cue.cpm_rate_usd > 0.0
