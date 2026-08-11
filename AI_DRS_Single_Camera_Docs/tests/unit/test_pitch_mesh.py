"""
Unit tests for 3D Pitch Wireframe Mesh & Ball Flight Path Generator Module
"""

import pytest

from ai_drs.calibration.stereo_calibration import Point3D
from ai_drs.graphics.pitch_mesh import Pitch3DMeshGenerator, Pitch3DMeshScene


def test_pitch_3d_mesh_generation():
    scene = Pitch3DMeshGenerator.generate_base_pitch_mesh()

    assert isinstance(scene, Pitch3DMeshScene)
    assert len(scene.pitch_outline) == 4
    assert len(scene.stumps_batter) == 3
    assert scene.stumps_batter[1].z == 0.711
    assert scene.stumps_batter[1].y == 20.12


def test_attach_drs_trajectory():
    generator = Pitch3DMeshGenerator()
    scene = generator.generate_base_pitch_mesh()

    tracked_pts = [Point3D(x=0.0, y=10.0, z=1.5), Point3D(x=0.0, y=14.0, z=0.0)]
    proj_pts = [Point3D(x=0.0, y=18.0, z=0.5), Point3D(x=0.0, y=20.12, z=0.6)]
    bounce_pt = Point3D(x=0.0, y=14.0, z=0.0)
    impact_pt = Point3D(x=0.0, y=18.0, z=0.5)

    updated_scene = generator.attach_drs_trajectory(
        scene, tracked_pts, proj_pts, bounce_point=bounce_pt, impact_point=impact_pt
    )

    assert len(updated_scene.tracked_path) == 2
    assert len(updated_scene.projected_path) == 2
    assert updated_scene.bounce_spot is not None
    assert updated_scene.bounce_spot.y == 14.0
    assert updated_scene.impact_spot is not None
    assert updated_scene.impact_spot.y == 18.0
