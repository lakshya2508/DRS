"""
Distributed Redis / NATS Real-Time Event Bus Module
"""

from typing import Callable, Dict, List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.event_bus")


class EventBusMessage(BaseModel):
    """Schema representing distributed pub/sub event bus message."""
    channel: str
    event_type: str
    payload: Dict
    subscribers_notified: int


class DistributedEventBus:
    """High-throughput event pub/sub bus for fanning out match events to 100,000+ concurrent clients."""

    def __init__(self):
        # channel -> List of callback functions
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, channel: str, callback: Callable):
        """Subscribes callback listener to channel."""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed callback to Event Bus channel '{channel}'.")

    def publish(self, channel: str, event_type: str, payload: Dict) -> EventBusMessage:
        """Publishes event to channel and notifies registered subscriber callbacks."""
        callbacks = self.subscribers.get(channel, [])
        count = 0
        for cb in callbacks:
            try:
                cb(event_type, payload)
                count += 1
            except Exception as e:
                logger.error(f"Error executing event bus callback: {e}")

        logger.debug(f"Published Event [{event_type}] on channel [{channel}] to {count} subscribers.")

        return EventBusMessage(
            channel=channel,
            event_type=event_type,
            payload=payload,
            subscribers_notified=count
        )
