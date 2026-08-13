"""
Unit tests for Virtual Turf Sponsor Logo Overlay Generator Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.graphics.virtual_sponsor_overlay import (
    VirtualSponsorOverlayConfig,
    VirtualTurfSponsorOverlayEngine,
)


def test_virtual_sponsor_overlay():
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    cfg = VirtualSponsorOverlayConfig(sponsor_name="ARAMCO", opacity=0.9)

    annotated = VirtualTurfSponsorOverlayEngine.draw_virtual_sponsor_logo(frame, cfg)

    assert annotated is not None
    assert annotated.shape == (720, 1280, 3)
    assert not np.array_equal(frame, annotated)
