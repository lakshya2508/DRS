"""
Unit tests for UltraEdge Snicko Audio Peak Processing Engine
"""

import numpy as np
import pytest

from ai_drs.audio.snicko_detector import AudioEdgeEvent, SnickoAudioDetector


def test_snicko_audio_spike_detection():
    sample_rate = 44100
    duration_s = 1.0  # 1 second of audio
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)

    # Low frequency ambient noise (100 Hz)
    audio = 0.1 * np.sin(2 * np.pi * 100 * t)

    # Inject sharp 4 kHz high-frequency click spike at t = 0.5s (Frame 15 at 30 FPS)
    spike_idx = int(0.5 * sample_rate)
    spike_window = 200
    audio[spike_idx: spike_idx + spike_window] += 2.5 * np.sin(2 * np.pi * 4000 * t[spike_idx: spike_idx + spike_window])

    detector = SnickoAudioDetector(sample_rate=sample_rate, spike_threshold_ratio=3.0)
    events = detector.analyze_audio_waveform(audio, fps=30.0)

    assert len(events) == 30  # 30 frames in 1 second
    assert isinstance(events[15], AudioEdgeEvent)
    # Frame 15 should detect edge
    assert events[15].is_edge_detected is True
    assert events[15].snicko_spike_ratio > 3.0


def test_empty_audio_waveform():
    detector = SnickoAudioDetector()
    events = detector.analyze_audio_waveform(np.array([]))
    assert len(events) == 0
