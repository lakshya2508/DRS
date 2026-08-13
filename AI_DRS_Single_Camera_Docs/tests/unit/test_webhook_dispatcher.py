"""
Unit tests for External Webhook Notification Dispatcher Module
"""

import pytest

from ai_drs.enterprise.webhook_dispatcher import ExternalWebhookDispatcher, WebhookDispatchResult


def test_webhook_dispatcher():
    dispatcher = ExternalWebhookDispatcher()
    dispatcher.register_webhook("https://api.partner.com/webhooks/drs")

    results = dispatcher.dispatch_event("WICKET_DISMISSAL", {"match_id": "M_WH_01", "batter": "Kohli"})

    assert len(results) == 1
    assert isinstance(results[0], WebhookDispatchResult)
    assert results[0].event_type == "WICKET_DISMISSAL"
    assert results[0].is_delivered is True
