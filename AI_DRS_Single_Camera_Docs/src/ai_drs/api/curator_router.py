"""
AI Pitch Curator REST Router
"""

from fastapi import APIRouter, HTTPException, status

from ai_drs.analytics.pitch_curator_scanner import PitchCuratorScannerEngine, PitchHealthReport
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.curator")

curator_router = APIRouter(prefix="/api/v1/curator", tags=["AI Pitch Curator Engine"])


@curator_router.get("/report", response_model=PitchHealthReport)
def get_pitch_curator_report():
    """Returns AI Pitch Curator ground health analysis, moisture %, and crack density metrics."""
    report = PitchCuratorScannerEngine.scan_pitch_surface(None)
    logger.info("Served AI Pitch Curator Health Report.")
    return report
