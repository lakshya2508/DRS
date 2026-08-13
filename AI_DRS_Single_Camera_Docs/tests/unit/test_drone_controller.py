"""
Unit tests for Autonomous Umpire Drone Target Tracking Controller Module
"""

import pytest

from ai_drs.ingestion.drone_controller import AutonomousDroneController, DroneControlCommand


def test_drone_controller():
    cmd = AutonomousDroneController.compute_tracking_command(bowler_y_m=0.0, batter_y_m=20.12, current_drone_z_m=18.5)

    assert isinstance(cmd, DroneControlCommand)
    assert cmd.target_waypoint_xyz == (0.0, 10.06, 18.5)
    assert cmd.target_pitch_deg == -65.0
    assert cmd.is_aligned_with_crease is True
