"""
Unit tests for Distributed Redis / NATS Real-Time Event Bus Module
"""

import pytest

from ai_drs.api.event_bus import DistributedEventBus, EventBusMessage


def test_distributed_event_bus():
    bus = DistributedEventBus()
    received = []

    def mock_listener(evt_type, payload):
        received.append((evt_type, payload))

    bus.subscribe("match_events", mock_listener)
    msg = bus.publish("match_events", "DELIVERY_COMPLETED", {"ball": 6, "runs": 4})

    assert isinstance(msg, EventBusMessage)
    assert msg.subscribers_notified == 1
    assert len(received) == 1
    assert received[0][0] == "DELIVERY_COMPLETED"
    assert received[0][1]["runs"] == 4
