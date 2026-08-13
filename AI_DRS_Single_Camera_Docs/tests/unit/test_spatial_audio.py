"""
Unit tests for Spatial 3D Audio Positional Synthesizer Module
"""

import pytest

from ai_drs.audio.spatial_audio_synthesizer import (
    SpatialAudioSynthesizerEngine,
    SpatialBinauralAudioCoordinates,
)


def test_spatial_audio_synthesizer():
    coords = SpatialAudioSynthesizerEngine.compute_binaural_coordinates(source_x_m=2.0, source_y_m=10.0, source_z_m=1.5)

    assert isinstance(coords, SpatialBinauralAudioCoordinates)
    assert coords.distance_m > 10.0
    assert -180.0 <= coords.azimuth_deg <= 180.0
    assert 0.0 <= coords.left_ear_gain <= 1.0
    assert 0.0 <= coords.right_ear_gain <= 1.0
