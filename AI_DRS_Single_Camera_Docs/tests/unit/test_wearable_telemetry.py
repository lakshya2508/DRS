"""
Unit tests for Wearable Device Telemetry & Battery Monitor Module
"""

import pytest

from ai_drs.wearable.wearable_telemetry import WearableDeviceStatus, WearableTelemetryMonitor


def test_wearable_telemetry_normal():
    monitor = WearableTelemetryMonitor()
    status = monitor.update_device_telemetry("DEV_GLASS_1", battery_pct=85.0, rssi_dbm=-55.0)

    assert isinstance(status, WearableDeviceStatus)
    assert status.connection_status == "CONNECTED"
    assert status.is_ready_for_match is True


def test_wearable_telemetry_degraded():
    monitor = WearableTelemetryMonitor()
    status = monitor.update_device_telemetry("DEV_GLASS_2", battery_pct=10.0, rssi_dbm=-90.0)

    assert status.connection_status == "DEGRADED"
    assert status.is_ready_for_match is False
