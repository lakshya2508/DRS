"""
Video Ingestion and Frame Extraction Pipeline for AI DRS
"""

import os
from pathlib import Path
from typing import Generator, Optional, Tuple, Union
import cv2
import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion")


class VideoMetadata(BaseModel):
    """Schema representing validated video file properties."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_path: Path
    width: int = Field(ge=0, description="Video width in pixels")
    height: int = Field(ge=0, description="Video height in pixels")
    fps: float = Field(ge=0.0, description="Frames per second")
    total_frames: int = Field(ge=0, description="Total frame count")
    duration_seconds: float = Field(ge=0.0, description="Duration in seconds")
    codec: str = Field(default="", description="Video fourcc codec string")
    is_valid: bool = Field(default=True, description="Whether video passed basic validation")
    validation_error: Optional[str] = Field(default=None, description="Validation failure reason if any")


class Frame(BaseModel):
    """Schema representing an extracted video frame."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    frame_index: int = Field(ge=0, description="Zero-based frame index")
    timestamp_ms: float = Field(ge=0.0, description="Timestamp in milliseconds from start")
    image: np.ndarray = Field(description="OpenCV BGR image array")


class VideoIngestor:
    """Handles video file ingestion, metadata extraction, validation, and frame extraction."""

    def __init__(self, min_fps: float = 24.0, min_width: int = 640, min_height: int = 480):
        self.min_fps = min_fps
        self.min_width = min_width
        self.min_height = min_height

    def extract_metadata(self, video_path: Union[str, Path]) -> VideoMetadata:
        """Extracts metadata from a video file and validates basic constraints."""
        path = Path(video_path).resolve()
        if not path.exists():
            logger.error(f"Video file does not exist: {path}")
            return VideoMetadata(
                file_path=path,
                width=0,
                height=0,
                fps=0.0,
                total_frames=0,
                duration_seconds=0.0,
                is_valid=False,
                validation_error=f"File does not exist: {path}"
            )

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            logger.error(f"Failed to open video file with OpenCV: {path}")
            return VideoMetadata(
                file_path=path,
                width=0,
                height=0,
                fps=0.0,
                total_frames=0,
                duration_seconds=0.0,
                is_valid=False,
                validation_error="Failed to open video container (corrupted or unsupported codec)"
            )

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))

        cap.release()

        # Convert fourcc integer to string codec
        codec = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)]).upper()

        duration = (total_frames / fps) if fps > 0 else 0.0

        is_valid, validation_error = self.validate(width, height, fps, total_frames)

        logger.info(
            f"Ingested video '{path.name}': {width}x{height} @ {fps:.2f}FPS, "
            f"frames={total_frames}, duration={duration:.2f}s, valid={is_valid}"
        )

        return VideoMetadata(
            file_path=path,
            width=width,
            height=height,
            fps=fps,
            total_frames=total_frames,
            duration_seconds=duration,
            codec=codec,
            is_valid=is_valid,
            validation_error=validation_error
        )

    def validate(
        self, width: int, height: int, fps: float, total_frames: int
    ) -> Tuple[bool, Optional[str]]:
        """Validates video properties against project minimum quality constraints."""
        if total_frames <= 0:
            return False, "Video contains 0 frames"
        if fps < self.min_fps:
            return False, f"FPS {fps:.1f} below minimum threshold {self.min_fps}"
        if width < self.min_width or height < self.min_height:
            return False, f"Resolution {width}x{height} below minimum {self.min_width}x{self.min_height}"
        return True, None

    def stream_frames(
        self,
        video_path: Union[str, Path],
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        step: int = 1
    ) -> Generator[Frame, None, None]:
        """Generates frames sequentially from the video file."""
        path = Path(video_path).resolve()
        cap = cv2.VideoCapture(str(path))

        if not cap.isOpened():
            logger.error(f"Cannot stream frames: unable to open video {path}")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if fps <= 0:
            fps = 30.0

        max_frame = total_frames if end_frame is None else min(end_frame, total_frames)

        if start_frame > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        current_frame = start_frame
        while current_frame < max_frame:
            ret, image = cap.read()
            if not ret or image is None:
                logger.warning(f"Failed to read frame at index {current_frame}")
                break

            if (current_frame - start_frame) % step == 0:
                timestamp_ms = (current_frame / fps) * 1000.0
                yield Frame(
                    frame_index=current_frame,
                    timestamp_ms=timestamp_ms,
                    image=image
                )

            current_frame += 1

            if step > 1 and (current_frame - start_frame) % step != 0:
                # Seek if step is large for faster iteration
                skip = step - 1
                next_target = current_frame + skip
                if next_target < max_frame:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, next_target)
                    current_frame = next_target

        cap.release()

    def get_frame_at(self, video_path: Union[str, Path], frame_index: int) -> Optional[Frame]:
        """Retrieves a single frame at a specific zero-based index."""
        path = Path(video_path).resolve()
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_index < 0 or frame_index >= total_frames:
            cap.release()
            return None

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, image = cap.read()
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        cap.release()

        if not ret or image is None:
            return None

        timestamp_ms = (frame_index / fps) * 1000.0 if fps > 0 else 0.0
        return Frame(
            frame_index=frame_index,
            timestamp_ms=timestamp_ms,
            image=image
        )


def create_synthetic_video(
    output_path: Union[str, Path],
    num_frames: int = 60,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0
) -> Path:
    """Helper utility to generate a synthetic test video for deterministic testing."""
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))

    for idx in range(num_frames):
        # Create a synthetic frame with moving circle (ball candidate)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Background color
        frame[:] = (50, 120, 50)
        # Draw moving white circle
        cx = int(100 + (idx * 15) % (width - 200))
        cy = int(200 + (idx * 5) % (height - 300))
        cv2.circle(frame, (cx, cy), 15, (255, 255, 255), -1)

        writer.write(frame)

    writer.release()
    return path
