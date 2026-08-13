"""
Webhook & Cloud Backup REST Router
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_drs.common.logging import setup_logger
from ai_drs.enterprise.cloud_backup import CloudBackupResult, CloudStorageBackupEngine
from ai_drs.enterprise.webhook_dispatcher import ExternalWebhookDispatcher

logger = setup_logger("ai_drs.api.webhook_router")

webhook_router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Webhooks & Cloud Backup"])


class RegisterWebhookRequest(BaseModel):
    webhook_url: str


@webhook_router.post("/webhooks/register")
def register_enterprise_webhook(req: RegisterWebhookRequest):
    """Registers external HTTP POST webhook endpoint URL for match events."""
    dispatcher = ExternalWebhookDispatcher()
    dispatcher.register_webhook(req.webhook_url)
    return {"status": "REGISTERED", "webhook_url": req.webhook_url}


@webhook_router.post("/backup/{match_id}", response_model=CloudBackupResult)
def trigger_cloud_backup(match_id: str, asset_name: str = "match_summary.pdf"):
    """Triggers asynchronous cloud storage backup upload for match replay assets."""
    return CloudStorageBackupEngine.backup_match_assets(match_id=match_id, asset_filepath=asset_name)
