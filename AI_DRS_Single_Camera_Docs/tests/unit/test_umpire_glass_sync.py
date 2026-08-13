"""
Unit tests for Smart Umpire Glass Bluetooth / HUD Sync Protocol Module
"""

import pytest

from ai_drs.wearable.umpire_glass_sync import UmpireGlassSyncEngine, WearableHUDMessage


def test_umpire_glass_sync_out():
    msg = UmpireGlassSyncEngine.transmit_decision_to_glass("GLASS_01", "OUT")
    assert isinstance(msg, WearableHUDMessage)
    assert msg.device_id == "GLASS_01"
    assert msg.decision_text == "OUT"
    assert msg.color_hex == "#FF1744"
    assert msg.ble_gatt_payload_bytes.startswith("0x")


def test_umpire_glass_sync_not_out():
    msg = UmpireGlassSyncEngine.transmit_decision_to_glass("GLASS_02", "NOT OUT")
    assert msg.decision_text == "NOT OUT"
    assert msg.color_hex == "#00E676"
