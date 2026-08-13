"""
Unit tests for Haptic Feedback Vibration Cue Generator Module
"""

import pytest

from ai_drs.wearable.haptic_cue_generator import HapticCueGenerator, HapticImpulsePattern


def test_haptic_cue_wicket():
    pattern = HapticCueGenerator.generate_haptic_pattern("WICKET")
    assert isinstance(pattern, HapticImpulsePattern)
    assert pattern.intensity_pct == 100
    assert len(pattern.pulse_durations_ms) == 5


def test_haptic_cue_no_ball():
    pattern = HapticCueGenerator.generate_haptic_pattern("NO_BALL")
    assert pattern.intensity_pct == 80
    assert len(pattern.pulse_durations_ms) == 3


def test_haptic_cue_legal():
    pattern = HapticCueGenerator.generate_haptic_pattern("LEGAL")
    assert pattern.intensity_pct == 40
    assert len(pattern.pulse_durations_ms) == 1
