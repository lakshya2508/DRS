"""
Viral Short-Form Video Exporter REST Router
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.reel")

reel_router = APIRouter(prefix="/api/v1/reels", tags=["Short-Form Video Suite"])


class ShortFormReelResponse(BaseModel):
    reel_id: str
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"
    download_url: str
    share_text: str


@reel_router.get("/export/{delivery_id}", response_model=ShortFormReelResponse)
def export_viral_reel(delivery_id: str):
    """Exports vertical 9:16 short-form video clip packaged with social media share text."""
    download_url = f"https://cdn.aidrs.io/reels/{delivery_id}_9x16.mp4"
    share_text = f"🔥 Watch this insane delivery from ball {delivery_id}! #AIDRS #CricketReels"

    logger.info(f"Exported Viral Short-Form Reel [{delivery_id}]")
    return ShortFormReelResponse(
        reel_id=f"reel_{delivery_id}",
        aspect_ratio="9:16",
        resolution="1080x1920",
        download_url=download_url,
        share_text=share_text
    )
