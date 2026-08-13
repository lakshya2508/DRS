"""
Wearable Device Telemetry & Battery Monitor Module
"""

from typing import Dict
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.wearable.telemetry")


class WearableDeviceStatus(BaseModel):
    """Schema representing wearable umpire device status and telemetry."""
    device_id: str
    battery_level_pct: float = Field(ge=0.0, le=100.0)
    ble_rssi_dbm: float = Field(le=0.0)
    connection_status: str = Field(description="'CONNECTED', 'DEGRADED', 'DISCONNECTED'")
    is_ready_for_match: bool


class WearableTelemetryMonitor:
    """Monitors battery levels and Bluetooth connectivity RSSI across on-field umpire devices."""

    def __init__(self):
        self.devices: Dict[str, WearableDeviceStatus] = {}

    def update_device_telemetry(
        self,
        device_id: str,
        battery_pct: float,
        rssi_dbm: float = -65.0
    ) -> WearableDeviceStatus:
        """Updates and validates on-field wearable telemetry."""
        if battery_pct < 15.0 or rssi_dbm < -85.0:
            status = "DEGRADED"
        elif battery_pct < 5.0:
            status = "DISCONNECTED"
        else:
            status = "CONNECTED"

        ready = battery_pct >= 20.0 and rssi_dbm >= -80.0

        dev_status = WearableDeviceStatus(
            device_id=device_id,
            battery_level_pct=battery_pct,
            ble_rssi_dbm=rssi_dbm,
            connection_status=status,
            is_ready_for_match=ready
        )

        self.devices[device_id] = dev_status
        logger.info(f"Wearable Telemetry [{device_id}]: Battery={battery_pct}%, RSSI={rssi_dbm}dBm -> Status={status}")

        return dev_status
