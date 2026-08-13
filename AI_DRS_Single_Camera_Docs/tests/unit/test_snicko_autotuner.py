"""
Unit tests for Acoustic Calibration & Snicko Threshold Auto-Tuner Module
"""

import pytest

from ai_drs.audio.snicko_autotuner import SnickoAutoTunerConfig, SnickoAutoTunerEngine


def test_snicko_autotuner_loud():
    cfg = SnickoAutoTunerEngine.tune_snicko_threshold(background_db_spl=100.0, base_ratio=3.5)
    assert isinstance(cfg, SnickoAutoTunerConfig)
    assert cfg.noise_environment == "LOUD_STADIUM"
    assert cfg.tuned_peak_threshold_ratio > 3.5


def test_snicko_autotuner_quiet():
    cfg = SnickoAutoTunerEngine.tune_snicko_threshold(background_db_spl=60.0, base_ratio=3.5)
    assert cfg.noise_environment == "QUIET_GROUND"
    assert cfg.tuned_peak_threshold_ratio == 3.5
