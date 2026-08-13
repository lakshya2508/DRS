"""
Async Distributed Task Queue & Background Video Processor for AI DRS
"""

import asyncio
from typing import Dict, Optional
import uuid
from pydantic import BaseModel, Field

from ai_drs.api.review_service import ReviewPipelineService
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion.async")


class ProcessingTaskStatus(BaseModel):
    """Schema representing background video processing task status."""
    task_id: str
    status: str = Field(description="'QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED'")
    progress_pct: float = Field(ge=0.0, le=100.0)
    result: Optional[Dict] = None
    error: Optional[str] = None


class AsyncVideoProcessor:
    """Async background worker queue for non-blocking DRS video ingestion and perception processing."""

    def __init__(self, review_service: Optional[ReviewPipelineService] = None):
        self.review_service = review_service or ReviewPipelineService()
        self.tasks: Dict[str, ProcessingTaskStatus] = {}

    def submit_video_job(self, video_path: str, calib_data: Optional[Dict] = None) -> str:
        """Submits video processing job to background queue and returns immediate task_id."""
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        task_status = ProcessingTaskStatus(
            task_id=task_id,
            status="QUEUED",
            progress_pct=0.0
        )
        self.tasks[task_id] = task_status

        # Schedule background asyncio task
        asyncio.create_task(self._process_video_worker(task_id, video_path, calib_data))

        logger.info(f"Submitted async video processing job [{task_id}] for '{video_path}'")
        return task_id

    def get_task_status(self, task_id: str) -> ProcessingTaskStatus:
        """Retrieves status and result of background processing task."""
        if task_id not in self.tasks:
            raise KeyError(f"Task ID '{task_id}' not found.")
        return self.tasks[task_id]

    async def _process_video_worker(self, task_id: str, video_path: str, calib_data: Optional[Dict]):
        """Background async worker processing delivery video."""
        try:
            self.tasks[task_id].status = "PROCESSING"
            self.tasks[task_id].progress_pct = 25.0
            await asyncio.sleep(0.1)  # Simulate non-blocking async execution

            # Process review
            self.tasks[task_id].progress_pct = 75.0
            review_res = self.review_service.process_review(video_path)

            self.tasks[task_id].status = "COMPLETED"
            self.tasks[task_id].progress_pct = 100.0
            self.tasks[task_id].result = review_res.model_dump()
            logger.info(f"Completed async video processing job [{task_id}]: result={review_res.result}")


        except Exception as e:
            logger.error(f"Error in async video processing job [{task_id}]: {e}")
            self.tasks[task_id].status = "FAILED"
            self.tasks[task_id].error = str(e)


# Global async processor instance
async_processor = AsyncVideoProcessor()
