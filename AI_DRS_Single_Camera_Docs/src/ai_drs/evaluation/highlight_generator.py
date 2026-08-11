"""
Highlight Reel Generator & Match Summary Exporter for AI DRS & Autonomous Match Engine
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import DeliveryEvent, MatchState

logger = setup_logger("ai_drs.evaluation.highlight")


class HighlightClip(BaseModel):
    """Schema representing a generated highlight clip metadata."""
    clip_id: str
    event_type: str = Field(description="'WICKET', 'BOUNDARY_SIX', 'BOUNDARY_FOUR', 'DRS_REVIEW'")
    frame_start: int
    frame_end: int
    timestamp_start_s: float
    timestamp_end_s: float
    description: str


class MatchHighlightPackage(BaseModel):
    """Schema representing full match highlight package and summary report."""
    match_id: str
    total_deliveries: int
    total_runs: int
    total_wickets: int
    highlights: List[HighlightClip] = Field(default_factory=list)


class HighlightReelGenerator:
    """Generates highlight clip manifests and match summary reports from match delivery history."""

    @staticmethod
    def generate_highlight_manifest(
        match_state: MatchState,
        delivery_history: List[DeliveryEvent],
        fps: float = 30.0,
        pre_padding_s: float = 2.0,
        post_padding_s: float = 3.0
    ) -> MatchHighlightPackage:
        """Parses delivery history and extracts highlight clips for wickets, boundaries, and DRS reviews."""
        highlights: List[HighlightClip] = []
        clip_counter = 1

        for idx, delivery in enumerate(delivery_history):
            # Check if delivery is a highlight worthy event
            is_wicket = delivery.is_wicket
            is_boundary = delivery.runs_batter in (4, 6)
            is_drs = delivery.drs_review_requested

            if is_wicket or is_boundary or is_drs:
                # Classify event type
                if is_wicket:
                    etype = "WICKET"
                    desc = f"WICKET! Batter dismissed: {delivery.dismissal_type or 'Out'}"
                elif delivery.runs_batter == 6:
                    etype = "BOUNDARY_SIX"
                    desc = f"HUGE SIX! {delivery.runs_batter} runs scored off delivery {delivery.over_number}.{delivery.ball_number}"
                elif delivery.runs_batter == 4:
                    etype = "BOUNDARY_FOUR"
                    desc = f"FOUR! Boundary struck off delivery {delivery.over_number}.{delivery.ball_number}"
                else:
                    etype = "DRS_REVIEW"
                    desc = f"AI DRS Review requested on delivery {delivery.over_number}.{delivery.ball_number}"

                # Calculate frame clip boundaries
                est_impact_frame = idx * 60  # Estimated 2-second delivery frame spacing
                frame_start = max(0, int(est_impact_frame - pre_padding_s * fps))
                frame_end = int(est_impact_frame + post_padding_s * fps)

                clip = HighlightClip(
                    clip_id=f"clip_{clip_counter:03d}",
                    event_type=etype,
                    frame_start=frame_start,
                    frame_end=frame_end,
                    timestamp_start_s=float(frame_start / fps),
                    timestamp_end_s=float(frame_end / fps),
                    description=desc
                )
                highlights.append(clip)
                clip_counter += 1

        logger.info(
            f"Generated highlight package for Match [{match_state.match_id}]: "
            f"{len(highlights)} clips extracted across {len(delivery_history)} deliveries."
        )

        return MatchHighlightPackage(
            match_id=match_state.match_id,
            total_deliveries=len(delivery_history),
            total_runs=match_state.runs,
            total_wickets=match_state.wickets,
            highlights=highlights
        )
