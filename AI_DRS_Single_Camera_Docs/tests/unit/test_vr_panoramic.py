"""
Unit tests for 360-Degree Panoramic Video Sphere Stitcher Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.graphics.vr_panoramic_stitcher import VRPanoramicStitcherEngine, VRSkyboxTextureState


def test_vr_panoramic_stitcher():
    feed_left = np.zeros((720, 1280, 3), dtype=np.uint8)
    feed_right = np.zeros((720, 1280, 3), dtype=np.uint8)

    skybox, state = VRPanoramicStitcherEngine.stitch_equirectangular_skybox([feed_left, feed_right])

    assert isinstance(state, VRSkyboxTextureState)
    assert skybox.shape == (1920, 3840, 3)
    assert state.is_vr_ready is True
    assert state.fov_horizontal_deg == 360.0
