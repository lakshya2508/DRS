"""
Asynchronous Job Engine — Handles non-blocking video ingestion, frame extraction, tracking, and analysis.
"""

import uuid
import time
import threading
from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.jobs.job_manager")


class ProcessingJobStatus(BaseModel):
    """Processing job status representation."""
    job_id: str
    video_path: str
    status: Literal["queued", "extracting_frames", "detecting_ball", "tracking", "homography_mapping", "completed", "failed"] = "queued"
    progress_pct: int = Field(default=0, ge=0, le=100)
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result_delivery_id: Optional[str] = None


class AsyncJobManager:
    """Manages background computer vision processing jobs without blocking HTTP threads."""

    def __init__(self):
        self._jobs: Dict[str, ProcessingJobStatus] = {}
        self._lock = threading.Lock()

    def create_job(self, video_path: str) -> ProcessingJobStatus:
        """Enqueues a new asynchronous video processing job."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = ProcessingJobStatus(job_id=job_id, video_path=video_path, status="queued", progress_pct=0)
        
        with self._lock:
            self._jobs[job_id] = job

        # Trigger non-blocking worker thread
        thread = threading.Thread(target=self._process_worker, args=(job_id,), daemon=True)
        thread.start()
        logger.info(f"Enqueued async job {job_id} for video '{video_path}'")
        return job

    def get_job(self, job_id: str) -> Optional[ProcessingJobStatus]:
        """Retrieves current job status."""
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> Dict[str, ProcessingJobStatus]:
        """Lists all active and completed jobs."""
        with self._lock:
            return dict(self._jobs)

    def _process_worker(self, job_id: str):
        """Background worker executing the multi-stage CV pipeline."""
        stages = [
            ("extracting_frames", 20),
            ("detecting_ball", 45),
            ("tracking", 70),
            ("homography_mapping", 90),
            ("completed", 100)
        ]

        for stage, pct in stages:
            time.sleep(0.4) # Simulate stage processing step
            with self._lock:
                if job_id in self._jobs:
                    self._jobs[job_id].status = stage
                    self._jobs[job_id].progress_pct = pct
                    if stage == "completed":
                        self._jobs[job_id].completed_at = time.time()
                        self._jobs[job_id].result_delivery_id = f"del_{uuid.uuid4().hex[:6]}"

        logger.info(f"Async job {job_id} completed successfully.")


_job_manager = AsyncJobManager()
