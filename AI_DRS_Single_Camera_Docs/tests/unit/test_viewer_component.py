"""
Unit tests for Interactive HTML5 Canvas 3D Review Viewer Component Module
"""

import pytest

from ai_drs.api.viewer_component import HTML5ReviewViewerComponent
from ai_drs.graphics.pitch_mesh import Pitch3DMeshGenerator


def test_viewer_component_rendering():
    scene = Pitch3DMeshGenerator.generate_base_pitch_mesh()
    html = HTML5ReviewViewerComponent.render_viewer_html(scene)

    assert "<div id=\"hawk-eye-3d-viewer\"" in html
    assert "<canvas id=\"hawkEyeCanvas\"" in html
    assert "HAWK-EYE 3D TRAJECTORY VIEWER" in html
