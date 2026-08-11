"""
Unit tests for Video Ingestion module
"""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from ai_drs.ingestion.video_ingestion import (
    VideoIngestor,
    VideoMetadata,
    Frame,
    create_synthetic_video,
)


@pytest.fixture
def temp_video():
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / "test_delivery.mp4"
        created_path = create_synthetic_video(
            output_path=video_path,
            num_frames=30,
            width=1280,
            height=720,
            fps=30.0,
        )
        yield created_path


def test_synthetic_video_creation(temp_video):
    assert temp_video.exists()
    assert temp_video.stat().st_size > 0


def test_extract_metadata(temp_video):
    ingestor = VideoIngestor(min_fps=24.0, min_width=640, min_height=480)
    meta = ingestor.extract_metadata(temp_video)

    assert isinstance(meta, VideoMetadata)
    assert meta.is_valid is True
    assert meta.width == 1280
    assert meta.height == 720
    assert abs(meta.fps - 30.0) < 1.0
    assert meta.total_frames == 30
    assert abs(meta.duration_seconds - 1.0) < 0.1
    assert meta.validation_error is None


def test_nonexistent_video():
    ingestor = VideoIngestor()
    meta = ingestor.extract_metadata("non_existent_file.mp4")

    assert meta.is_valid is False
    assert "File does not exist" in meta.validation_error


def test_low_quality_validation():
    ingestor = VideoIngestor(min_fps=60.0, min_width=1920, min_height=1080)
    valid_fps, err_fps = ingestor.validate(width=1280, height=720, fps=30.0, total_frames=30)
    assert valid_fps is False
    assert "FPS" in err_fps

    valid_res, err_res = ingestor.validate(width=500, height=400, fps=60.0, total_frames=30)
    assert valid_res is False
    assert "Resolution" in err_res

    valid_zero, err_zero = ingestor.validate(width=1280, height=720, fps=30.0, total_frames=0)
    assert valid_zero is False
    assert "0 frames" in err_zero


def test_stream_frames(temp_video):
    ingestor = VideoIngestor()
    frames = list(ingestor.stream_frames(temp_video))

    assert len(frames) == 30
    for idx, frame in enumerate(frames):
        assert isinstance(frame, Frame)
        assert frame.frame_index == idx
        assert isinstance(frame.image, np.ndarray)
        assert frame.image.shape == (720, 1280, 3)


def test_stream_frames_slice_and_sampling(temp_video):
    ingestor = VideoIngestor()
    sliced = list(ingestor.stream_frames(temp_video, start_frame=5, end_frame=20, step=3))

    assert len(sliced) == 5
    assert sliced[0].frame_index == 5
    assert sliced[1].frame_index == 8


def test_stream_frames_nonexistent():
    ingestor = VideoIngestor()
    frames = list(ingestor.stream_frames("non_existent.mp4"))
    assert len(frames) == 0


def test_get_frame_at(temp_video):
    ingestor = VideoIngestor()
    frame_10 = ingestor.get_frame_at(temp_video, frame_index=10)

    assert frame_10 is not None
    assert frame_10.frame_index == 10
    assert frame_10.image.shape == (720, 1280, 3)

    out_of_bounds = ingestor.get_frame_at(temp_video, frame_index=999)
    assert out_of_bounds is None

    negative = ingestor.get_frame_at(temp_video, frame_index=-1)
    assert negative is None

    non_existent = ingestor.get_frame_at("non_existent.mp4", frame_index=0)
    assert non_existent is None
