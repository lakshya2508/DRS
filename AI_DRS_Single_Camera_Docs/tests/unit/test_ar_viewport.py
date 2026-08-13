"""
Unit tests for AR Mobile Camera Viewport Canvas Overlay Component Module
"""

import pytest

from ai_drs.api.ar_viewport_component import ARMobileViewportComponent


def test_ar_viewport_component():
    html = ARMobileViewportComponent.render_ar_viewport_html()
    assert "<div id=\"ar-mobile-hud\"" in html
    assert "<video id=\"arCameraFeed\"" in html
    assert "<canvas id=\"arOverlayCanvas\"" in html
    assert "AR HUD LIVE CAM STREAM" in html
