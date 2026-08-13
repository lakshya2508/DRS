"""
Unit tests for Multispectral Pitch Moisture & Crack Density Scanner Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.analytics.pitch_curator_scanner import PitchCuratorScannerEngine, PitchHealthReport


def test_pitch_curator_scanner():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Fill green region for grass
    frame[100:300, 100:300] = (34, 139, 34)

    report = PitchCuratorScannerEngine.scan_pitch_surface(frame)

    assert isinstance(report, PitchHealthReport)
    assert 0.0 <= report.moisture_pct <= 100.0
    assert 0.0 <= report.grass_coverage_pct <= 100.0
    assert report.max_crack_width_mm >= 0.0
