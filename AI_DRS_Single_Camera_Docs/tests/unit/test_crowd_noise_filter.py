"""
Unit tests for Stadium Crowd Noise Spectral Subtraction Filter Module
"""

import numpy as np
import pytest

from ai_drs.audio.crowd_noise_filter import CrowdNoiseFilterEngine, CrowdNoiseFilterResult


def test_crowd_noise_filter():
    # Synthetic noisy audio: background noise + sharp impulse spike
    t = np.linspace(0, 1.0, 44100)
    noise = np.random.normal(0, 0.1, 44100)
    spike = np.zeros(44100)
    spike[20000:20100] = 1.0  # Ball edge spike
    audio = noise + spike

    clean_audio, res = CrowdNoiseFilterEngine.filter_crowd_noise(audio)

    assert isinstance(res, CrowdNoiseFilterResult)
    assert len(clean_audio) == 44100
    assert res.clean_audio_samples_count == 44100
    assert res.filtered_snr_db != res.original_snr_db
