"""
Unit tests for Autonomous Third Umpire Voice Assistant Module
"""

import pytest

from ai_drs.api.review_service import ReviewResultResponse
from ai_drs.audio.voice_umpire import VoiceUmpireAssistant, VoiceUmpireCallout


def test_voice_umpire_callout_out():
    review = ReviewResultResponse(
        review_id="REV_VOICE_01",
        result="OUT",
        confidence=0.95,
        recommendation_reason="Pitching in line, Impact in line, Wickets hitting",
        pitching={"zone": "in_line"},
        impact={"zone": "in_line"},
        wicket={"status": "hitting"},
        ball_track={},
        calibration={}
    )


    callout = VoiceUmpireAssistant.generate_drs_voice_callout(review)

    assert isinstance(callout, VoiceUmpireCallout)
    assert callout.review_id == "REV_VOICE_01"
    assert "Pitching in line" in callout.callout_transcript
    assert "Impact in line" in callout.callout_transcript
    assert "Wickets hitting" in callout.callout_transcript
    assert "Signal OUT now" in callout.final_voice_command
