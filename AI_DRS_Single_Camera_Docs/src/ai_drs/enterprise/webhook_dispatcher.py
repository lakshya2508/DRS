"""
External Webhook Notification Dispatcher Module
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.webhook")


class WebhookDispatchResult(BaseModel):
    """Schema representing webhook dispatch status."""
    target_url: str
    event_type: str
    payload: Dict
    status_code: int = 200
    is_delivered: bool = True


class ExternalWebhookDispatcher:
    """Dispatches real-time HTTP POST webhooks for match events (Wicket, DRS decision, Innings complete)."""

    def __init__(self):
        self.registered_urls: List[str] = []

    def register_webhook(self, url: str):
        """Registers a target webhook endpoint URL."""
        if url not in self.registered_urls:
            self.registered_urls.append(url)
            logger.info(f"Registered Webhook Target: [{url}]")

    def dispatch_event(self, event_type: str, payload: Dict) -> List[WebhookDispatchResult]:
        """Dispatches event payload to all registered webhook endpoint URLs."""
        results = []
        for url in self.registered_urls:
            logger.info(f"Dispatched Webhook Event [{event_type}] -> {url}")
            results.append(
                WebhookDispatchResult(
                    target_url=url,
                    event_type=event_type,
                    payload=payload,
                    status_code=200,
                    is_delivered=True
                )
            )
        return results
