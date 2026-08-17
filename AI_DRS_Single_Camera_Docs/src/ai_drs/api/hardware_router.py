"""
Hardware Router — Discovers connected USB webcams, capture cards, OpenCV backends, and CUDA/CPU acceleration.
"""

from typing import Dict, List
import cv2
from fastapi import APIRouter

hardware_router = APIRouter(prefix="/api/v1/hardware", tags=["Hardware Diagnostics"])


@hardware_router.get("/devices", response_model=dict)
def get_hardware_diagnostics():
    """Detects available camera devices and hardware acceleration capabilities."""
    available_cameras: List[Dict] = []

    # Check indices 0, 1, 2 for video devices
    for idx in range(3):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            available_cameras.append({
                "device_id": idx,
                "name": f"USB Camera / Device {idx}",
                "resolution": f"{w}x{h}",
                "fps": fps,
                "status": "ONLINE"
            })
            cap.release()

    cuda_available = False
    device_name = "CPU (OpenCV DNN / NumPy)"
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
    except ImportError:
        pass

    return {
        "status": "ok",
        "opencv_version": cv2.__version__,
        "cuda_accelerated": cuda_available,
        "compute_device": device_name,
        "detected_cameras": available_cameras,
        "synthetic_mode_available": True
    }
