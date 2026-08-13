"""
Unit tests for AI Match Commentary Voice Generator Module
"""

import pytest

from ai_drs.audio.voice_commentary import CommentaryAudioScript, VoiceCommentaryGenerator
from ai_drs.match.models import DeliveryEvent


def test_voice_commentary_generator():
    # 1. Wicket Commentary
    del_w = DeliveryEvent(ball_number=4, over_number=2, is_wicket=True, dismissal_type="Bowled")
    comm_w = VoiceCommentaryGenerator.generate_delivery_commentary(del_w, "V. Kohli", "J. Bumrah")

    assert isinstance(comm_w, CommentaryAudioScript)
    assert comm_w.excitement_level == "HIGH"
    assert "OUT!" in comm_w.commentary_text
    assert "J. Bumrah strikes!" in comm_w.commentary_text

    # 2. Six Commentary
    del_6 = DeliveryEvent(ball_number=5, over_number=2, runs_batter=6)
    comm_6 = VoiceCommentaryGenerator.generate_delivery_commentary(del_6, "V. Kohli", "J. Bumrah")
    assert comm_6.excitement_level == "HIGH"
    assert "SIX!" in comm_6.commentary_text
