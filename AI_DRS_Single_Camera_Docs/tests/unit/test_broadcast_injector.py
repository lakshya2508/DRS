"""
Unit tests for Broadcast Lower-Third & Scoreboard Graphic Overlay Injector Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.graphics.broadcast_injector import BroadcastFrameInjector
from ai_drs.match.models import MatchState


def test_broadcast_frame_injector():
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    match_state = MatchState(match_id="M_OVERLAY", runs=145, wickets=3, overs=14, legal_balls=2)

    annotated = BroadcastFrameInjector.inject_scoreboard_overlay(frame, match_state)

    assert annotated is not None
    assert annotated.shape == (720, 1280, 3)
    assert not np.array_equal(frame, annotated)  # Graphic elements drawn
