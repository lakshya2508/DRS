"""
Unit tests for Async Distributed Task Queue & Video Processor Module
"""

import asyncio
from pathlib import Path
import pytest

from ai_drs.ingestion.async_processor import AsyncVideoProcessor, ProcessingTaskStatus
from ai_drs.ingestion.video_ingestion import VideoIngestor


def test_async_video_processor_e2e(tmp_path: Path):
    async def _runner():
        video_path = str(tmp_path / "async_test.mp4")
        VideoIngestor.create_synthetic_delivery_video(video_path, num_frames=30)

        processor = AsyncVideoProcessor()
        task_id = processor.submit_video_job(video_path)

        assert task_id.startswith("task_")

        # Initial status should be QUEUED or PROCESSING
        status_init = processor.get_task_status(task_id)
        assert isinstance(status_init, ProcessingTaskStatus)

        # Wait for async background worker to complete
        await asyncio.sleep(0.3)

        status_final = processor.get_task_status(task_id)
        assert status_final.status == "COMPLETED"
        assert status_final.progress_pct == 100.0
        assert status_final.result is not None
        assert "decision" in status_final.result

    asyncio.run(_runner())



def test_invalid_task_id():
    processor = AsyncVideoProcessor()
    with pytest.raises(KeyError):
        processor.get_task_status("invalid_task_999")
