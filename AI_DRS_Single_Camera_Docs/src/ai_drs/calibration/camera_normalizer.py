"""
Camera White Balance & Auto-Exposure Normalization Engine
"""

import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.calibration.normalizer")


class CameraNormalizationState(BaseModel):
    """Schema representing image normalization metrics."""
    mean_luminance: float = Field(ge=0.0, le=255.0)
    contrast_std: float = Field(ge=0.0)
    is_normalized: bool = True


class CameraNormalizerEngine:
    """Normalizes lighting histogram intensity, white balance, and contrast across multi-angle broadcast feeds."""

    @staticmethod
    def normalize_frame(frame: np.ndarray, target_mean_luminance: float = 128.0) -> Tuple[np.ndarray, CameraNormalizationState]:
        """Applies CLAHE histogram equalization and Gray World white balance normalization."""
        if frame is None or frame.size == 0:
            return frame, CameraNormalizationState(mean_luminance=0.0, contrast_std=0.0, is_normalized=False)

        # Gray World White Balance
        b, g, r = cv2.split(frame)
        b_avg, g_avg, r_avg = np.mean(b), np.mean(g), np.mean(r)
        k_avg = (b_avg + g_avg + r_avg) / 3.0

        b_norm = cv2.scaleAdd(b, k_avg / max(1.0, b_avg), np.zeros_like(b))
        g_norm = cv2.scaleAdd(g, k_avg / max(1.0, g_avg), np.zeros_like(g))
        r_norm = cv2.scaleAdd(r, k_avg / max(1.0, r_avg), np.zeros_like(r))

        wb_frame = cv2.merge([b_norm, g_norm, r_norm])

        # CLAHE Contrast Adjustment on LAB L-channel
        lab = cv2.cvtColor(wb_frame, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_norm = clahe.apply(l)

        lab_norm = cv2.merge([l_norm, a, b_ch])
        normalized = cv2.cvtColor(lab_norm, cv2.COLOR_LAB2BGR)

        mean_lum = float(np.mean(l_norm))
        std_cont = float(np.std(l_norm))

        logger.debug(f"Normalized Camera Frame: mean_lum={mean_lum:.1f}, contrast={std_cont:.1f}")

        return normalized, CameraNormalizationState(
            mean_luminance=round(mean_lum, 1),
            contrast_std=round(std_cont, 1),
            is_normalized=True
        )
