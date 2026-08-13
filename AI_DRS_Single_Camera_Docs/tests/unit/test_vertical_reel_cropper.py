"""
Unit tests for Vertical 9:16 Short-Form Reel Cropping Engine Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.evaluation.vertical_reel_cropper import VerticalCropResult, VerticalReelCropperEngine


def test_vertical_reel_cropper():
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    cropped, result = VerticalReelCropperEngine.crop_frame_to_vertical(frame, ball_x_px=640.0, ball_y_px=360.0)

    assert isinstance(result, VerticalCropResult)
    assert cropped.shape == (1920, 1080, 3)
    assert result.aspect_ratio == "9:16"
    assert result.is_centered_on_ball is True
