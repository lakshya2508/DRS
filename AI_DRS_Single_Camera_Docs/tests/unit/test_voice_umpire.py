"""
Unit tests for Autonomous Third Umpire Voice Assistant Module
"""

import pytest

from ai_drs.api.review_service import (
    DRSEvidencePayload,
    DecisionType,
    HitStumpsStatus,
    PitchingZone,
    ReviewResultResponse,
)
from ai_drs.audio.voice_umpire import VoiceUmpireAssistant, VoiceUmpireCallout


def test_voice_umpire_callout_out():
    review = ReviewResultResponse(
        review_id="REV_VOICE_01",
        video_source="test.mp4",
        decision=DecisionType.OUT,
        confidence_score=0.95,
        evidence=DRSEvidencePayload(
            pitching_zone=PitchingZone.IN_LINE,
            impact_zone=PitchingZone.IN_LINE,
            hit_stumps_status=HitStumpsStatus.HITTING,
            predicted_wicket_y=20.12,
            predicted_wicket_z=0.5
        )
    )

    callout = VoiceUmpireAssistant.generate_drs_voice_callout(review)

    assert isinstance(callout, VoiceUmpireCallout)
    assert callout.review_id == "REV_VOICE_01"
    assert "Pitching in line" in callout.callout_transcript
    assert "Impact in line" in callout.callout_transcript
    assert "Wickets hitting" in callout.callout_transcript
    assert "Signal OUT now" in callout.final_voice_command
