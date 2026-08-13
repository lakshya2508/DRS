"""
Unit tests for Aerial Drone Camera 3D Pose & Flight Telemetry Ingester Module
"""

import pytest

from ai_drs.ingestion.drone_ingester import DroneTelemetryIngester, DroneTelemetryState


def test_drone_telemetry_ingester():
    state = DroneTelemetryIngester.ingest_drone_telemetry("DRONE_01", altitude_m=22.0, pitch_deg=-30.0)

    assert isinstance(state, DroneTelemetryState)
    assert state.drone_id == "DRONE_01"
    assert state.altitude_z_m == 22.0
    assert state.gimbal_pitch_deg == -30.0
    assert state.fps == 60.0
