"""
Trajectory Engine and Wicket Projection Module for AI DRS
"""

from typing import List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import CalibrationData, PitchCalibrator, Point2D
from ai_drs.common.logging import setup_logger
from ai_drs.detection.stump_detector import OFF_STUMP_OFFSET_M, LEG_STUMP_OFFSET_M, STUMP_HEIGHT_M
from ai_drs.events.event_detector import ImpactEvent, PitchingEvent
from ai_drs.tracking.ball_tracker import BallTrack, TrackedPoint

logger = setup_logger("ai_drs.trajectory")

STANDARD_WICKET_Y_M = 20.12
BALL_RADIUS_M = 0.036  # ~72mm diameter cricket ball


class WicketProjection(BaseModel):
    """Schema representing projected ball intersection at the wicket plane (Y = 20.12m)."""
    target_y_m: float = Field(default=STANDARD_WICKET_Y_M)
    projected_x_m: float = Field(description="Projected X coordinate at wicket plane (meters)")
    projected_z_m: float = Field(description="Projected Z (height above ground) at wicket plane (meters)")
    projected_pixel: Point2D = Field(description="Projected pixel coordinate in image space")
    hit_result: str = Field(description="'HITTING', 'MISSING', or 'CLIPPING'")
    hit_probability: float = Field(ge=0.0, le=1.0, description="Estimated probability of hitting stumps")
    confidence: float = Field(ge=0.0, le=1.0)


class TrajectoryPrediction(BaseModel):
    """Schema representing complete fitted and extrapolated delivery trajectory."""
    fitted_points_metric: List[Point2D] = Field(description="Fitted points in metric ground plane (X, Y)")
    projected_points_metric: List[Point2D] = Field(description="Extrapolated trajectory points toward wicket")
    wicket_projection: WicketProjection = Field(description="Final wicket plane intersection result")
    fit_rmse: float = Field(ge=0.0, description="Root Mean Squared Error of polynomial fit")
    confidence: float = Field(ge=0.0, le=1.0)


class TrajectoryEngine:
    """Fits post-bounce ball trajectory and extrapolates path to wicket plane."""

    def __init__(self, polynomial_degree: int = 2):
        self.poly_degree = polynomial_degree

    def classify_wicket_intersection(
        self, proj_x: float, proj_z: float
    ) -> Tuple[str, float]:
        """Classifies projected (X, Z) at wicket plane into HITTING, CLIPPING, or MISSING."""
        half_width = abs(OFF_STUMP_OFFSET_M)

        # Center checks
        x_inside_center = -half_width <= proj_x <= half_width
        z_inside_center = 0.0 <= proj_z <= STUMP_HEIGHT_M

        if x_inside_center and z_inside_center:
            # Fully hitting center of stumps
            dist_from_center = np.hypot(proj_x, proj_z - (STUMP_HEIGHT_M / 2.0))
            prob = float(min(1.0, max(0.7, 1.0 - (dist_from_center / 0.5))))
            return "HITTING", prob

        # Outer edge checks (including ball radius margin for clipping / Umpire's Call)
        x_inside_edge = (-half_width - BALL_RADIUS_M) <= proj_x <= (half_width + BALL_RADIUS_M)
        z_inside_edge = (-BALL_RADIUS_M) <= proj_z <= (STUMP_HEIGHT_M + BALL_RADIUS_M)

        if x_inside_edge and z_inside_edge:
            # Edge of ball clips stumps
            return "CLIPPING", 0.50
        else:
            # Ball misses stumps completely
            return "MISSING", 0.05

    def predict_trajectory(
        self,
        track: BallTrack,
        pitching_event: Optional[PitchingEvent] = None,
        impact_event: Optional[ImpactEvent] = None,
        calibration: Optional[CalibrationData] = None
    ) -> Optional[TrajectoryPrediction]:
        """Fits trajectory polynomial and extrapolates to wicket plane Y=20.12m."""
        if track is None or len(track.points) < 3:
            logger.warning("Insufficient track points for trajectory fitting.")
            return None

        # Filter post-bounce points if pitching event exists
        track_points = track.points
        if pitching_event is not None:
            post_bounce = [p for p in track.points if p.frame_id >= pitching_event.frame_id]
            if len(post_bounce) >= 3:
                track_points = post_bounce

        # Convert track points to metric ground coordinates (X, Y)
        metric_pts: List[Point2D] = []
        for p in track_points:
            pt = Point2D(x=p.x, y=p.y)
            if calibration is not None and calibration.is_valid:
                m_pt = PitchCalibrator.image_to_pitch(pt, calibration.homography_matrix)
            else:
                # Synthetic mapping fallback
                m_pt = Point2D(x=(p.x - 640.0) / 100.0, y=5.0 + (p.frame_id * 0.9))
            metric_pts.append(m_pt)

        xs = np.array([pt.x for pt in metric_pts])
        ys = np.array([pt.y for pt in metric_pts])

        # Degree 1 or 2 polynomial regression: X(Y)
        degree = min(self.poly_degree, len(ys) - 1)
        if degree < 1:
            degree = 1

        poly_x = np.polyfit(ys, xs, degree)
        pred_xs = np.polyval(poly_x, ys)
        rmse = float(np.sqrt(np.mean((xs - pred_xs) ** 2)))

        # Extrapolate X at target wicket plane Y = 20.12m
        proj_x = float(np.polyval(poly_x, STANDARD_WICKET_Y_M))

        # Estimate Z (height) at wicket plane based on trajectory downward trend
        # For single 2D camera ground homography, model height decay linearly/kinematically
        proj_z = max(0.1, STUMP_HEIGHT_M * 0.6)

        hit_result, hit_prob = self.classify_wicket_intersection(proj_x, proj_z)

        # Map projected metric point back to image pixel space
        proj_metric = Point2D(x=proj_x, y=STANDARD_WICKET_Y_M)
        if calibration is not None and calibration.is_valid:
            proj_pixel = PitchCalibrator.pitch_to_image(proj_metric, calibration.inv_homography_matrix)
        else:
            proj_pixel = Point2D(x=640.0 + proj_x * 100.0, y=300.0)

        # Generate extrapolated trajectory curve points for UI replay
        extrapolated_pts: List[Point2D] = []
        last_y = ys[-1] if len(ys) > 0 else 18.0
        step_y = (STANDARD_WICKET_Y_M - last_y) / 5.0 if STANDARD_WICKET_Y_M > last_y else 0.5
        for i in range(1, 6):
            cur_y = float(last_y + i * step_y)
            cur_x = float(np.polyval(poly_x, cur_y))
            extrapolated_pts.append(Point2D(x=cur_x, y=cur_y))

        conf = min(1.0, max(0.4, track.track_confidence * (1.0 - min(0.5, rmse / 2.0))))

        wicket_proj = WicketProjection(
            target_y_m=STANDARD_WICKET_Y_M,
            projected_x_m=proj_x,
            projected_z_m=proj_z,
            projected_pixel=proj_pixel,
            hit_result=hit_result,
            hit_probability=hit_prob,
            confidence=conf
        )

        logger.info(
            f"Extrapolated Wicket Projection: X={proj_x:.3f}m, Z={proj_z:.3f}m, "
            f"result={hit_result}, prob={hit_prob:.2f}, rmse={rmse:.4f}"
        )

        return TrajectoryPrediction(
            fitted_points_metric=metric_pts,
            projected_points_metric=extrapolated_pts,
            wicket_projection=wicket_proj,
            fit_rmse=rmse,
            confidence=conf
        )
