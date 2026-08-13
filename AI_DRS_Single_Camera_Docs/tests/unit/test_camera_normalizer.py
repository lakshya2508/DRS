"""
Unit tests for Camera White Balance & Auto-Exposure Normalization Engine Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.calibration.camera_normalizer import CameraNormalizationState, CameraNormalizerEngine


def test_camera_normalizer():
    frame = np.full((100, 100, 3), 80, dtype=np.uint8)

    norm_frame, state = CameraNormalizerEngine.normalize_frame(frame)

    assert isinstance(state, CameraNormalizationState)
    assert norm_frame.shape == (100, 100, 3)
    assert state.is_normalized is True
    assert state.mean_luminance >= 0.0
