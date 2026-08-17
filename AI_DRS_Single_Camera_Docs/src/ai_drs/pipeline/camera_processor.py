"""
Live Camera Processor — Captures frames from webcam / RTSP stream / video file
and feeds them through the real-time LBW decision pipeline.
"""

import threading
import time
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.pipeline.camera_processor")


class CameraSource(str, Enum):
    WEBCAM    = "WEBCAM"     # USB / built-in camera
    RTSP      = "RTSP"       # IP camera / broadcast feed
    VIDEO     = "VIDEO"      # Pre-recorded delivery video file
    SYNTHETIC = "SYNTHETIC"  # Simulated frames (for testing without camera)


class CameraFrame:
    """Single captured frame with metadata."""
    def __init__(self, frame: np.ndarray, frame_id: int, timestamp: float, source: str):
        self.frame      = frame
        self.frame_id   = frame_id
        self.timestamp  = timestamp
        self.source     = source
        self.height, self.width = frame.shape[:2]


class LiveCameraProcessor:
    """
    Real-time frame capture engine.
    Supports: webcam (0), RTSP URL, video file path, or synthetic frames.
    """

    def __init__(
        self,
        source: CameraSource = CameraSource.WEBCAM,
        source_path: str = "0",
        target_fps: int = 30,
        on_frame: Optional[Callable[[CameraFrame], None]] = None,
    ):
        self.source      = source
        self.source_path = source_path
        self.target_fps  = target_fps
        self.on_frame    = on_frame

        self._lock = threading.Lock()
        self._cap: Optional[cv2.VideoCapture] = None
        self._running    = False
        self._thread: Optional[threading.Thread] = None
        self._frame_id   = 0
        self._last_frame: Optional[CameraFrame] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Start capturing frames in a background thread."""
        if self._running:
            logger.warning("Camera processor is already running.")
            return

        if self.source == CameraSource.SYNTHETIC:
            logger.info("Starting synthetic frame generator (no physical camera needed).")
        else:
            if self.source == CameraSource.WEBCAM:
                try:
                    path = int(self.source_path)
                except ValueError:
                    path = 0
            else:
                path = self.source_path

            self._cap = cv2.VideoCapture(path)
            if not self._cap or not self._cap.isOpened():
                logger.warning(f"Could not open camera source '{path}'. Falling back to synthetic mode.")
                self.source = CameraSource.SYNTHETIC
                self._cap = None

        self._running = True
        self._thread  = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"LiveCameraProcessor started — source={self.source.value}, fps={self.target_fps}")

    def stop(self):
        """Stop capturing and release camera resources."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
        if self._cap:
            self._cap.release()
            self._cap = None
        logger.info("LiveCameraProcessor stopped.")

    def get_last_frame(self) -> Optional[CameraFrame]:
        with self._lock:
            return self._last_frame

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Internal capture loop
    # ------------------------------------------------------------------

    def _capture_loop(self):
        interval = 1.0 / self.target_fps
        while self._running:
            t_start = time.time()

            if self.source == CameraSource.SYNTHETIC or self._cap is None:
                frame_array = self._generate_synthetic_frame()
            else:
                ret, frame_array = self._cap.read()
                if not ret:
                    logger.info("End of video stream reached — restarting from beginning.")
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

            self._frame_id += 1
            cam_frame = CameraFrame(
                frame     = frame_array,
                frame_id  = self._frame_id,
                timestamp = time.time(),
                source    = self.source.value,
            )
            with self._lock:
                self._last_frame = cam_frame

            if self.on_frame:
                try:
                    self.on_frame(cam_frame)
                except Exception as e:
                    logger.error(f"Error in on_frame callback: {e}")

            elapsed = time.time() - t_start
            sleep_time = max(0.0, interval - elapsed)
            time.sleep(sleep_time)

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generate a realistic synthetic cricket pitch frame for testing."""
        h, w = 720, 1280
        # Pitch background (green field)
        frame = np.full((h, w, 3), (34, 139, 34), dtype=np.uint8)

        # Draw pitch strip (light brown)
        cv2.rectangle(frame, (w//2 - 55, 100), (w//2 + 55, h - 100), (210, 180, 140), -1)
        cv2.rectangle(frame, (w//2 - 55, 100), (w//2 + 55, h - 100), (139, 90, 43), 3)

        # Draw crease lines
        cv2.line(frame, (w//2 - 70, h - 200), (w//2 + 70, h - 200), (255, 255, 255), 3)
        cv2.line(frame, (w//2 - 70, 280), (w//2 + 70, 280), (255, 255, 255), 3)

        # Draw stumps
        for i, x in enumerate([w//2 - 12, w//2, w//2 + 12]):
            cv2.line(frame, (x, h - 200), (x, h - 200 - 75), (255, 255, 255), 4)

        # Animate ball position (oscillate across frame for demo)
        t = time.time()
        ball_x = int(w // 2 + 40 * np.sin(t * 2.0))
        ball_y = int(h * 0.55 + 80 * np.sin(t * 1.5))
        cv2.circle(frame, (ball_x, ball_y), 14, (0, 0, 200), -1)
        cv2.circle(frame, (ball_x, ball_y), 14, (255, 255, 255), 1)

        # HUD overlay
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
        cv2.putText(frame, f"AI DRS LIVE  |  Frame {self._frame_id}  |  {time.strftime('%H:%M:%S')}",
                    (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2)

        return frame
