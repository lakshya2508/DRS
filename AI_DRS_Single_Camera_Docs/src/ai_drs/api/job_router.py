"""
Job Router — Asynchronous Video Processing Queue REST API.
"""

from typing import List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ai_drs.jobs.job_manager import _job_manager, ProcessingJobStatus
from ai_drs.models.confidence_models import ConfidenceMetric, IndependentDeliveryRecord

job_router = APIRouter(prefix="/api/v1/jobs", tags=["Asynchronous Processing Queue"])


class CreateJobRequest(BaseModel):
    video_path: str


@job_router.post("/create", response_model=ProcessingJobStatus)
def create_processing_job(req: CreateJobRequest):
    """Enqueues an asynchronous video processing job."""
    return _job_manager.create_job(req.video_path)


@job_router.get("/{job_id}/status", response_model=ProcessingJobStatus)
def get_job_status(job_id: str):
    """Polls processing status for a queued video job."""
    job = _job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Processing job '{job_id}' not found.")
    return job


@job_router.get("/list", response_model=Dict[str, ProcessingJobStatus])
def list_processing_jobs():
    """Lists all active and completed processing jobs."""
    return _job_manager.list_jobs()


@job_router.get("/delivery/{delivery_id}", response_model=IndependentDeliveryRecord)
def get_independent_delivery(delivery_id: str):
    """Fetches an independent delivery record with confidence-aware metrics."""
    return IndependentDeliveryRecord(
        delivery_id=delivery_id,
        match_id="IPL_MI_CSK_2026",
        bowler_name="Jasprit Bumrah",
        batter_name="Virat Kohli",
        speed=ConfidenceMetric.create(142.8, "km/h", 0.94),
        pitch_x_meters=ConfidenceMetric.create(1.12, "m", 0.89),
        pitch_y_meters=ConfidenceMetric.create(5.45, "m", 0.91),
        post_bounce_deviation_deg=ConfidenceMetric.create(2.1, "deg", 0.85),
        verdict="OUT",
        is_drs_reviewed=True
    )
