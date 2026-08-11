"""
LBW Decision Engine Module for AI DRS (Evidence Aggregation & MCC Law 36 Rules)
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import CalibrationData
from ai_drs.common.config import load_yaml_config
from ai_drs.common.logging import setup_logger
from ai_drs.events.event_detector import ImpactEvent, PitchingEvent
from ai_drs.tracking.ball_tracker import BallTrack
from ai_drs.trajectory.trajectory_engine import TrajectoryPrediction, WicketProjection

logger = setup_logger("ai_drs.decision")


class DecisionEvidence(BaseModel):
    """Schema representing structured technical evidence gathered for an LBW review."""
    pitching_zone: str = Field(description="'IN_LINE', 'OUTSIDE_OFF', 'OUTSIDE_LEG'")
    pitching_confidence: float = Field(ge=0.0, le=1.0)
    impact_zone: str = Field(description="'IN_LINE', 'OUTSIDE_OFF', 'OUTSIDE_LEG'")
    impact_confidence: float = Field(ge=0.0, le=1.0)
    wicket_hit_result: str = Field(description="'HITTING', 'MISSING', 'CLIPPING'")
    wicket_hit_probability: float = Field(ge=0.0, le=1.0)
    wicket_confidence: float = Field(ge=0.0, le=1.0)
    ball_track_coverage: float = Field(ge=0.0, le=1.0)
    calibration_reprojection_error_px: float = Field(ge=0.0)
    shot_offered: bool = Field(default=True)


class LBWDecision(BaseModel):
    """Schema representing final LBW review decision output."""
    result: str = Field(description="'OUT', 'NOT_OUT', or 'INCONCLUSIVE'")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall decision confidence score")
    recommendation_reason: str = Field(description="Human-readable decision explanation")
    evidence: DecisionEvidence = Field(description="Structured evidence supporting decision")
    pipeline_version: str = Field(default="0.8.0")


class LBWDecisionEngine:
    """Configurable Rule Engine evaluating LBW evidence against MCC Law 36 and confidence thresholds."""

    def __init__(self, config_path: str = "configs/decision.yaml"):
        raw_config = load_yaml_config(config_path)
        thresholds = raw_config.get("thresholds", {})

        self.min_track_confidence = float(thresholds.get("minimum_track_confidence", 0.70))
        self.min_calibration_confidence = float(thresholds.get("minimum_calibration_confidence", 0.90))
        self.min_decision_confidence = float(thresholds.get("minimum_decision_confidence", 0.80))
        self.max_reprojection_error_px = 5.0

    def evaluate(
        self,
        pitching_event: Optional[PitchingEvent],
        impact_event: Optional[ImpactEvent],
        trajectory_prediction: Optional[TrajectoryPrediction],
        ball_track: Optional[BallTrack],
        calibration: Optional[CalibrationData],
        shot_offered: bool = True
    ) -> LBWDecision:
        """Evaluates delivery evidence and returns OUT, NOT_OUT, or INCONCLUSIVE."""
        # 1. Inspect evidence availability & calibration quality
        calib_error = calibration.reprojection_error_px if (calibration and calibration.is_valid) else 999.0
        track_coverage = ball_track.coverage_ratio if ball_track else 0.0

        # Construct evidence object (default fallback values if events missing)
        evidence = DecisionEvidence(
            pitching_zone=pitching_event.zone if pitching_event else "UNKNOWN",
            pitching_confidence=pitching_event.confidence if pitching_event else 0.0,
            impact_zone=impact_event.zone if impact_event else "UNKNOWN",
            impact_confidence=impact_event.confidence if impact_event else 0.0,
            wicket_hit_result=trajectory_prediction.wicket_projection.hit_result if trajectory_prediction else "UNKNOWN",
            wicket_hit_probability=trajectory_prediction.wicket_projection.hit_probability if trajectory_prediction else 0.0,
            wicket_confidence=trajectory_prediction.wicket_projection.confidence if trajectory_prediction else 0.0,
            ball_track_coverage=track_coverage,
            calibration_reprojection_error_px=calib_error,
            shot_offered=shot_offered
        )

        # 2. Mandatory INCONCLUSIVE gating checks
        if calibration is None or not calibration.is_valid or calib_error > self.max_reprojection_error_px:
            return LBWDecision(
                result="INCONCLUSIVE",
                confidence=0.0,
                recommendation_reason="INCONCLUSIVE: Camera calibration is missing or exceeds error threshold.",
                evidence=evidence
            )

        if ball_track is None or track_coverage < self.min_track_confidence:
            return LBWDecision(
                result="INCONCLUSIVE",
                confidence=float(track_coverage),
                recommendation_reason=f"INCONCLUSIVE: Ball tracking coverage ({track_coverage:.0%}) below minimum required ({self.min_track_confidence:.0%}).",
                evidence=evidence
            )

        if pitching_event is None or impact_event is None or trajectory_prediction is None:
            return LBWDecision(
                result="INCONCLUSIVE",
                confidence=0.0,
                recommendation_reason="INCONCLUSIVE: Incomplete event or trajectory detection.",
                evidence=evidence
            )

        # Calculate combined decision confidence
        combined_conf = float(
            pitching_event.confidence * 0.25 +
            impact_event.confidence * 0.25 +
            trajectory_prediction.wicket_projection.confidence * 0.35 +
            track_coverage * 0.15
        )

        if combined_conf < self.min_decision_confidence * 0.7:
            return LBWDecision(
                result="INCONCLUSIVE",
                confidence=combined_conf,
                recommendation_reason=f"INCONCLUSIVE: Combined evidence confidence ({combined_conf:.2f}) is too low for reliable review.",
                evidence=evidence
            )

        # 3. MCC Law 36 Rule Evaluation
        # Rule A: Pitching
        if pitching_event.zone == "OUTSIDE_LEG":
            return LBWDecision(
                result="NOT_OUT",
                confidence=combined_conf,
                recommendation_reason="NOT OUT: Pitching outside leg stump.",
                evidence=evidence
            )

        # Rule B: Impact
        if impact_event.zone == "OUTSIDE_LEG":
            return LBWDecision(
                result="NOT_OUT",
                confidence=combined_conf,
                recommendation_reason="NOT OUT: Impact outside leg stump.",
                evidence=evidence
            )

        if impact_event.zone == "OUTSIDE_OFF" and shot_offered:
            return LBWDecision(
                result="NOT_OUT",
                confidence=combined_conf,
                recommendation_reason="NOT OUT: Impact outside off stump with shot offered.",
                evidence=evidence
            )

        # Rule C: Wicket Projection
        hit_res = trajectory_prediction.wicket_projection.hit_result

        if hit_res == "MISSING":
            return LBWDecision(
                result="NOT_OUT",
                confidence=combined_conf,
                recommendation_reason="NOT OUT: Ball trajectory projected to miss stumps.",
                evidence=evidence
            )

        if hit_res == "HITTING":
            return LBWDecision(
                result="OUT",
                confidence=combined_conf,
                recommendation_reason="OUT: Pitching in-line/outside-off, impact in-line, projected to hit stumps.",
                evidence=evidence
            )

        if hit_res == "CLIPPING":
            if combined_conf >= self.min_decision_confidence:
                return LBWDecision(
                    result="OUT",
                    confidence=combined_conf,
                    recommendation_reason="OUT: Ball projected to clip stumps (Umpire's Call - hitting).",
                    evidence=evidence
                )
            else:
                return LBWDecision(
                    result="INCONCLUSIVE",
                    confidence=combined_conf,
                    recommendation_reason="INCONCLUSIVE: Marginal clipping trajectory with insufficient confidence.",
                    evidence=evidence
                )

        return LBWDecision(
            result="INCONCLUSIVE",
            confidence=combined_conf,
            recommendation_reason="INCONCLUSIVE: Undefined decision state.",
            evidence=evidence
        )
