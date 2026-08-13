"""
Duckworth-Lewis-Stern (DLS 4.0) Resource Percentage Engine
"""

import math
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.match.dls")


class DLSResourceState(BaseModel):
    """Schema representing DLS resource percentage remaining for team."""
    overs_remaining: float = Field(ge=0.0, le=50.0)
    wickets_lost: int = Field(ge=0, le=10)
    resource_pct: float = Field(ge=0.0, le=100.0)


class DLSEngine:
    """Computes DLS 4.0 resource percentages based on exponential decay curves R(u, w)."""

    # Lambda exponential decay constants per wickets lost w (0..9)
    LAMBDA_DECAY = [0.0367, 0.0369, 0.0374, 0.0385, 0.0402, 0.0428, 0.0468, 0.0531, 0.0638, 0.0864]

    @classmethod
    def get_resource_percentage(cls, overs_remaining: float, wickets_lost: int) -> float:
        """Calculates DLS resource percentage remaining R(u, w) for u overs and w wickets."""
        if overs_remaining <= 0.0 or wickets_lost >= 10:
            return 0.0
        if overs_remaining >= 50.0 and wickets_lost == 0:
            return 100.0

        w_idx = min(9, max(0, wickets_lost))
        lam = cls.LAMBDA_DECAY[w_idx]

        # R(u, w) = R_0 * (1 - exp(-lambda * u))
        # Standardized R_0 scale where 50 overs, 0 wickets = 100%
        r_pct = 100.0 * (1.0 - math.exp(-lam * overs_remaining)) / (1.0 - math.exp(-cls.LAMBDA_DECAY[0] * 50.0))
        r_pct = min(100.0, max(0.0, r_pct))

        logger.debug(f"DLS Resource R({overs_remaining:.1f} ov, {wickets_lost} wkts) = {r_pct:.1f}%")
        return round(r_pct, 1)
