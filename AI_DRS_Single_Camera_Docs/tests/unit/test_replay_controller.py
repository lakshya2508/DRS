"""
Unit tests for Match Replay Timeline & DVR Scrubbing Controller Module
"""

import pytest

from ai_drs.api.replay_controller import MatchReplayController, ReplayFrameState


def test_replay_controller_seek():
    ctrl = MatchReplayController("M_REPLAY_01", total_frames=1000)
    state = ctrl.seek_to_frame(500)

    assert isinstance(state, ReplayFrameState)
    assert state.current_frame == 500
    assert state.total_frames == 1000


def test_replay_controller_speed():
    ctrl = MatchReplayController("M_REPLAY_02", total_frames=1000)
    state = ctrl.set_speed(0.5)

    assert state.playback_speed == 0.5
