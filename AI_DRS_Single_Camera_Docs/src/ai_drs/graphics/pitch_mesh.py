"""
3D Pitch Wireframe Mesh & Ball Flight Path Generator for Hawk-Eye DRS Visualization
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from ai_drs.calibration.stereo_calibration import Point3D
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.graphics.pitch")


class MeshVertex3D(BaseModel):
    """Schema representing a 3D vertex in the pitch wireframe mesh."""
    x: float
    y: float
    z: float


class Pitch3DMeshScene(BaseModel):
    """Schema representing full 3D Hawk-Eye pitch wireframe scene."""
    pitch_outline: List[MeshVertex3D]
    bowling_crease: List[MeshVertex3D]
    popping_crease: List[MeshVertex3D]
    stumps_bowler: List[MeshVertex3D]
    stumps_batter: List[MeshVertex3D]
    bounce_spot: Optional[MeshVertex3D] = None
    impact_spot: Optional[MeshVertex3D] = None
    tracked_path: List[MeshVertex3D] = Field(default_factory=list)
    projected_path: List[MeshVertex3D] = Field(default_factory=list)


class Pitch3DMeshGenerator:
    """Generates 3D Hawk-Eye pitch scene meshes and trajectory paths."""

    @staticmethod
    def generate_base_pitch_mesh() -> Pitch3DMeshScene:
        """Generates standard 3D metric cricket pitch wireframe geometry (20.12m length x 2.64m width)."""
        w, l = 1.32, 20.12

        outline = [
            MeshVertex3D(x=-w, y=0.0, z=0.0),
            MeshVertex3D(x=w, y=0.0, z=0.0),
            MeshVertex3D(x=w, y=l, z=0.0),
            MeshVertex3D(x=-w, y=l, z=0.0)
        ]

        bowling_crease = [
            MeshVertex3D(x=-1.22, y=0.0, z=0.0),
            MeshVertex3D(x=1.22, y=0.0, z=0.0)
        ]

        popping_crease = [
            MeshVertex3D(x=-1.83, y=18.90, z=0.0),
            MeshVertex3D(x=1.83, y=18.90, z=0.0)
        ]

        stumps_bowler = [
            MeshVertex3D(x=-0.1143, y=0.0, z=0.711),
            MeshVertex3D(x=0.0, y=0.0, z=0.711),
            MeshVertex3D(x=0.1143, y=0.0, z=0.711)
        ]

        stumps_batter = [
            MeshVertex3D(x=-0.1143, y=20.12, z=0.711),
            MeshVertex3D(x=0.0, y=20.12, z=0.711),
            MeshVertex3D(x=0.1143, y=20.12, z=0.711)
        ]

        logger.debug("Generated base 3D Hawk-Eye pitch wireframe mesh scene.")

        return Pitch3DMeshScene(
            pitch_outline=outline,
            bowling_crease=bowling_crease,
            popping_crease=popping_crease,
            stumps_bowler=stumps_bowler,
            stumps_batter=stumps_batter
        )

    def attach_drs_trajectory(
        self,
        scene: Pitch3DMeshScene,
        tracked_points: List[Point3D],
        projected_points: List[Point3D],
        bounce_point: Optional[Point3D] = None,
        impact_point: Optional[Point3D] = None
    ) -> Pitch3DMeshScene:
        """Attaches tracked and projected 3D flight paths and impact markers to scene."""
        scene.tracked_path = [MeshVertex3D(x=pt.x, y=pt.y, z=pt.z) for pt in tracked_points]
        scene.projected_path = [MeshVertex3D(x=pt.x, y=pt.y, z=pt.z) for pt in projected_points]

        if bounce_point:
            scene.bounce_spot = MeshVertex3D(x=bounce_point.x, y=bounce_point.y, z=bounce_point.z)
        if impact_point:
            scene.impact_spot = MeshVertex3D(x=impact_point.x, y=impact_point.y, z=impact_point.z)

        logger.info(
            f"Attached DRS Trajectory to 3D Scene: {len(tracked_points)} tracked pts, "
            f"{len(projected_points)} projected pts."
        )
        return scene
