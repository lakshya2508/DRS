"""
Unit tests for Automated MP4 Highlight Video Montage Stitcher Module
"""

from pathlib import Path
import pytest

from ai_drs.evaluation.highlight_generator import HighlightClip
from ai_drs.evaluation.montage_builder import HighlightMontageBuilder, MontageExportResult
from ai_drs.ingestion.video_ingestion import VideoIngestor


def test_montage_builder_synthetic_video(tmp_path: Path):
    in_video = str(tmp_path / "input.mp4")
    out_video = str(tmp_path / "montage.mp4")

    VideoIngestor.create_synthetic_delivery_video(in_video, num_frames=60)

    clips = [
        HighlightClip(
            clip_id="c1",
            event_type="WICKET",
            frame_start=10,
            frame_end=30,
            timestamp_start_s=0.33,
            timestamp_end_s=1.0,
            description="Test Wicket"
        )
    ]

    result = HighlightMontageBuilder.build_highlight_montage(in_video, out_video, clips)

    assert isinstance(result, MontageExportResult)
    assert result.total_clips_stitched == 1
    assert result.duration_seconds > 0.0
