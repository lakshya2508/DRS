"""
Unit tests for Live Stadium Decibel Level & Atmosphere Meter Module
"""

import numpy as np
import pytest

from ai_drs.audio.decibel_meter import StadiumAtmosphereMetrics, StadiumDecibelMeterEngine


def test_decibel_meter_normal():
    audio = np.random.normal(0, 0.05, 44100)
    metrics = StadiumDecibelMeterEngine.measure_stadium_decibels(audio)

    assert isinstance(metrics, StadiumAtmosphereMetrics)
    assert 30.0 <= metrics.spl_decibels_db <= 135.0
    assert metrics.atmosphere_state in ("QUIET", "NORMAL", "LOUD", "ECSTATIC_ROAR")


def test_decibel_meter_ecstatic_roar():
    loud_audio = np.random.normal(0, 1.5, 44100)
    metrics = StadiumDecibelMeterEngine.measure_stadium_decibels(loud_audio)

    assert metrics.spl_decibels_db >= 100.0
    assert metrics.atmosphere_state in ("LOUD", "ECSTATIC_ROAR")
