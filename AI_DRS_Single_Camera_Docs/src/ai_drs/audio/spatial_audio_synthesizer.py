"""
Spatial 3D Audio Positional Synthesizer Module
"""

import math
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.spatial")


class SpatialBinauralAudioCoordinates(BaseModel):
    """Schema representing 3D HRTF spatial binaural audio coordinates."""
    azimuth_deg: float = Field(ge=-180.0, le=180.0)
    elevation_deg: float = Field(ge=-90.0, le=90.0)
    distance_m: float = Field(ge=0.0)
    left_ear_gain: float = Field(ge=0.0, le=1.0)
    right_ear_gain: float = Field(ge=0.0, le=1.0)


class SpatialAudioSynthesizerEngine:
    """Computes 3D HRTF spatial binaural audio coordinates (azimuth, elevation, distance) for ball impact and crowd sounds."""

    @staticmethod
    def compute_binaural_coordinates(source_x_m: float, source_y_m: float, source_z_m: float) -> SpatialBinauralAudioCoordinates:
        """Calculates 3D spatial azimuth angle and interaural level differences for VR headphones."""
        dist = math.sqrt(source_x_m**2 + source_y_m**2 + source_z_m**2)
        azimuth = math.degrees(math.atan2(source_x_m, source_y_m))
        elevation = math.degrees(math.atan2(source_z_m, math.sqrt(source_x_m**2 + source_y_m**2)))

        # Interaural level difference (ILD) approximation
        pan = (azimuth + 90.0) / 180.0
        left_gain = max(0.1, min(1.0, 1.0 - pan * 0.5))
        right_gain = max(0.1, min(1.0, pan * 0.5 + 0.5))

        logger.info(f"Spatial 3D Audio HRTF: Azimuth={azimuth:.1f}deg, Elev={elevation:.1f}deg, Dist={dist:.2f}m")

        return SpatialBinauralAudioCoordinates(
            azimuth_deg=round(azimuth, 1),
            elevation_deg=round(elevation, 1),
            distance_m=round(dist, 2),
            left_ear_gain=round(left_gain, 2),
            right_ear_gain=round(right_gain, 2)
        )
