"""
Unit tests for Dynamic Motion Tracking Subtitle & Badge Overlay Engine Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.graphics.motion_subtitle_overlay import (
    MotionSubtitleOverlayConfig,
    MotionSubtitleOverlayEngine,
)


def test_motion_subtitle_overlay():
    frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
    cfg = MotionSubtitleOverlayConfig(speed_text="148.5 KM/H", subtitle_text="MASSIVE SIX!")

    annotated = MotionSubtitleOverlayEngine.draw_motion_overlays(frame, cfg)

    assert annotated is not None
    assert annotated.shape == (1920, 1080, 3)
    assert not np.array_equal(frame, annotated)
