"""
Unit tests for WebGL Interactive 3D Camera Free-Orbit Sandbox Component Module
"""

import pytest

from ai_drs.api.sandbox_component import WebGL3DSandboxComponent


def test_sandbox_component_rendering():
    html = WebGL3DSandboxComponent.render_3d_sandbox_html()

    assert "<div id=\"webgl-3d-sandbox\"" in html
    assert "<canvas id=\"sandbox3dCanvas\"" in html
    assert "3D HAWK-EYE CAMERA SANDBOX" in html
