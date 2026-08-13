"""
Broadcast Lower-Third & Scoreboard Graphic Overlay Injector Module
"""

import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.graphics.injector")


class BroadcastFrameInjector:
    """Injects broadcast lower-third scoreboards and TV banners directly onto video frames."""

    @staticmethod
    def inject_scoreboard_overlay(frame: np.ndarray, match_state: MatchState) -> np.ndarray:
        """Draws professional TV broadcast lower-third score bar at bottom of frame."""
        if frame is None or frame.size == 0:
            return frame

        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw dark lower-third background bar
        bar_h = 45
        y_start = h - bar_h - 15
        y_end = h - 15
        x_start = 30
        x_end = w - 30

        # Semi-transparent dark bar
        overlay = annotated.copy()
        cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), (16, 16, 22), -1)
        cv2.addWeighted(overlay, 0.85, annotated, 0.15, 0, annotated)

        # Draw green border line
        cv2.line(annotated, (x_start, y_start), (x_end, y_start), (118, 230, 0), 2)

        # Score text formatting
        team_str = f"{match_state.team_b} {match_state.runs}/{match_state.wickets}"
        overs_str = f"({match_state.overs}.{match_state.legal_balls} ov)"
        vs_str = f"vs {match_state.team_a}"

        text = f"{team_str} {overs_str} | {vs_str}"
        cv2.putText(annotated, text, (x_start + 20, y_start + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        logger.debug(f"Injected Broadcast Lower-Third Overlay onto frame ({w}x{h}).")
        return annotated
