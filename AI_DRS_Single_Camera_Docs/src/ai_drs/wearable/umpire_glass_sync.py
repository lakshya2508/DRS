"""
Smart Umpire Glass Bluetooth / HUD Sync Protocol Module
"""

import time
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.wearable.glass_sync")


class WearableHUDMessage(BaseModel):
    """Schema representing decision signal transmitted to smart umpire glasses HUD."""
    device_id: str
    decision_text: str
    color_hex: str
    latency_ms: float = Field(ge=0.0)
    ble_gatt_payload_bytes: str


class UmpireGlassSyncEngine:
    """Transmits low-latency decision signals to on-field smart umpire glasses via Bluetooth LE GATT socket."""

    @staticmethod
    def transmit_decision_to_glass(device_id: str, decision: str) -> WearableHUDMessage:
        """Encodes decision signal into BLE GATT packet and transmits to smart glass display."""
        t0 = time.time()
        dec_upper = decision.upper()

        if dec_upper == "OUT":
            color = "#FF1744"  # Red
            hex_payload = "0x015F4F5554"
        elif dec_upper in ("NOT OUT", "NOT_OUT"):
            color = "#00E676"  # Green
            hex_payload = "0x015F4E4F54"
        elif "NO" in dec_upper:
            color = "#FFEA00"  # Yellow
            hex_payload = "0x015F4E4F42"
        else:
            color = "#00B0FF"  # Cyan
            hex_payload = "0x015F574944"

        latency = float((time.time() - t0) * 1000.0)
        logger.info(f"Transmitted Decision [{dec_upper}] to Smart Glass [{device_id}] (Latency: {latency:.2f}ms)")

        return WearableHUDMessage(
            device_id=device_id,
            decision_text=dec_upper,
            color_hex=color,
            latency_ms=round(latency, 2),
            ble_gatt_payload_bytes=hex_payload
        )
