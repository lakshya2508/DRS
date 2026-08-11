# AI DRS — Single-Camera LBW Review System
## Technical Requirements Document (TRD)

**Version:** 1.0  
**Date:** 2026-08-11  
**Status:** Ready for Development

---

## 1. Technical Objective

Implement a modular computer-vision pipeline that converts one fixed behind-bowler smartphone video into calibrated image observations, a tracked ball trajectory, LBW evidence and a confidence-aware recommendation.

---

## 2. Reference Architecture

```text
Mobile Video
    |
    v
Ingestion / Validation
    |
    v
Frame Extraction
    |
    +--> Camera/Pitch Calibration
    |
    +--> Ball Detector
    |       |
    |       v
    |   Ball Tracker
    |
    +--> Stump Detector
    |
    +--> Player/Pad Detector
    |
    v
Event Detection
    |
    +--> Pitching Point
    +--> Impact Point
    +--> Wicket Plane
    |
    v
Trajectory Estimation
    |
    v
LBW Decision Engine
    |
    +--> Evidence
    +--> Confidence
    +--> OUT / NOT OUT / INCONCLUSIVE
    |
    v
Review API
    |
    v
Web Review UI
```

## 3. Recommended Stack

### Computer vision / ML
- Python 3.11+
- OpenCV
- PyTorch
- Ultralytics YOLO or equivalent detector
- NumPy
- SciPy
- Pandas for evaluation

### Backend
- FastAPI
- Pydantic
- Uvicorn

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

### Development
- Git
- GitHub
- pytest
- Ruff
- pre-commit
- Docker

PostgreSQL is optional for V1. Local filesystem/SQLite is sufficient for the first prototype. Add PostgreSQL only when persistent multi-user review history is needed.

## 4. Repository Structure

```text
ai-drs/
├── README.md
├── PRD.md
├── TRD.md
├── EXECUTION_PLAN.md
├── pyproject.toml
├── .env.example
├── docker-compose.yml
├── configs/
│   ├── camera.yaml
│   ├── model.yaml
│   └── decision.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── annotations/
│   └── splits/
├── models/
├── notebooks/
├── scripts/
├── src/
│   └── ai_drs/
│       ├── ingestion/
│       ├── calibration/
│       ├── detection/
│       ├── tracking/
│       ├── events/
│       ├── trajectory/
│       ├── decision/
│       ├── evaluation/
│       ├── api/
│       └── common/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── frontend/
    ├── app/
    ├── components/
    └── lib/
```

## 5. Video Ingestion

Input:
- MP4/MOV
- configurable resolution/FPS

Metadata required:
- width
- height
- FPS
- frame count
- duration

Reject or flag:
- corrupted video
- missing frames
- unsupported codec
- extreme blur
- insufficient FPS
- calibration mismatch

## 6. Camera Calibration

V1 uses a fixed-camera setup.

Calibration should identify:
- pitch boundary/reference points
- stumps
- crease
- wicket plane
- camera-to-pitch mapping

Use OpenCV perspective transformation/homography for planar pitch coordinates.

Calibration output:

```text
camera_id
image_size
reference_points
homography_matrix
stump_reference
crease_reference
calibration_error
```

Calibration must be versioned.

## 7. Ball Detection

Detector output:

```python
BallDetection(
    frame_id: int,
    bbox: tuple[float, float, float, float],
    center: tuple[float, float],
    confidence: float
)
```

Because the ball is small and fast, the detector must be evaluated separately from generic object-detection metrics.

Potential approaches:
1. YOLO baseline
2. custom small-object detector
3. temporal detection/tracking
4. detector + optical-flow/trajectory refinement

Do not commit to a final model before baseline evaluation.

## 8. Ball Tracking

Input:
- per-frame ball detections

Output:

```python
BallTrack(
    frame_ids,
    centers,
    confidences,
    visibility,
    interpolated_points
)
```

Requirements:
- temporal continuity
- outlier rejection
- short occlusion handling
- confidence estimation

Track quality metrics:
- track coverage
- missed-frame ratio
- position error
- ID continuity

## 9. Stump / Wicket Detection

Detect:
- three stumps
- bails where visible
- wicket centerline
- wicket plane

The wicket geometry should be transformed into the calibrated coordinate system.

## 10. Player / Pad Detection

At minimum detect:
- batter bounding region
- legs/pads
- relevant impact region

Possible progression:
1. object detection
2. segmentation
3. pose estimation
4. temporal fusion

The system should not depend on perfect segmentation in V1.

## 11. Event Detection

### Pitching
Detect the frame/time and location where the ball contacts the pitch.

Evidence:
- ball trajectory
- vertical/horizontal motion change
- calibrated pitch plane
- temporal neighborhood

### Impact
Detect possible ball-pad contact.

Evidence:
- ball trajectory
- ball proximity to pad
- temporal motion
- visual contact event

### Wicket trajectory
Fit trajectory before/around impact and extrapolate to wicket plane.

## 12. Trajectory Model

Start with a simple calibrated model.

Pipeline:

```text
image coordinates
       |
       v
pitch-coordinate transformation
       |
       v
temporal smoothing
       |
       v
trajectory fit
       |
       v
future trajectory extrapolation
       |
       v
wicket-plane intersection
```

Baseline:
- polynomial/kinematic regression

Later:
- physics-informed model
- learned trajectory model

Do not introduce a complex deep trajectory model until the classical baseline is measured.

## 13. Decision Engine

Input:

```python
DecisionEvidence(
    pitching_zone,
    impact_zone,
    wicket_hit_probability,
    ball_track_confidence,
    calibration_confidence,
    impact_confidence
)
```

Output:

```python
Decision(
    result="OUT|NOT_OUT|INCONCLUSIVE",
    confidence=float,
    evidence=dict,
    pipeline_version=str
)
```

Decision rules must be configuration-driven, not hard-coded throughout the codebase.

Example:

```yaml
thresholds:
  minimum_track_confidence: 0.70
  minimum_calibration_confidence: 0.90
  minimum_decision_confidence: 0.80
  inconclusive_wicket_probability_low: 0.35
  inconclusive_wicket_probability_high: 0.65
```

These are initial engineering values only and must be calibrated using validation data.

## 14. API

### POST /api/v1/reviews
Upload/create a review.

### GET /api/v1/reviews/{review_id}
Return processing status and result.

### GET /api/v1/reviews/{review_id}/evidence
Return trajectory, detections and decision evidence.

### GET /api/v1/reviews/{review_id}/replay
Return annotated replay metadata/video.

### POST /api/v1/calibration
Create/validate calibration.

## 15. Review Result Schema

```json
{
  "review_id": "string",
  "result": "OUT",
  "confidence": 0.86,
  "pitching": {
    "zone": "IN_LINE",
    "confidence": 0.91
  },
  "impact": {
    "zone": "IN_LINE",
    "confidence": 0.84
  },
  "wicket": {
    "hit_probability": 0.88,
    "confidence": 0.89
  },
  "ball_track": {
    "coverage": 0.94
  },
  "calibration": {
    "error": 0.032
  },
  "pipeline_version": "0.1.0"
}
```

## 16. Frontend Requirements

The review page should show:
- original video
- slow-motion replay
- detected ball overlay
- trajectory line
- stump/wicket overlay
- pitching marker
- impact marker
- projected trajectory
- confidence
- final recommendation
- technical evidence
- warnings when evidence is weak

Never visually present an uncertain result as a professional/official decision.

## 17. Evaluation Framework

Maintain a separate test dataset.

Metrics:
- detection precision/recall
- tracking error
- event localization error
- trajectory error
- wicket intersection error
- final classification accuracy
- confusion matrix
- calibration error
- percentage INCONCLUSIVE
- processing time

Every model change must be evaluated against the same test split.

## 18. Testing

Unit tests:
- coordinate transforms
- homography
- trajectory fitting
- decision rules
- confidence aggregation

Integration tests:
- video -> detection
- detection -> tracking
- tracking -> trajectory
- trajectory -> decision
- API upload -> final result

Regression tests:
- fixed benchmark deliveries
- expected trajectory and decision ranges

## 19. Performance

Initial target:
- correctness over real-time speed

Optimization order:
1. correct tracking
2. correct geometry
3. correct decision
4. reduce inference time
5. optimize GPU/CPU execution

Later deployment targets may use ONNX/TensorRT if hardware supports them.

## 20. Security / Privacy

- Store videos locally by default.
- Do not expose uploaded videos publicly.
- Validate file type and size.
- Use generated review IDs.
- Keep model/data versions with every result.
- Delete raw video when configured by retention policy.

## 21. Technical Definition of Done

A module is done only when:
- implementation exists
- unit tests pass
- integration path works
- failure cases are handled
- metrics are recorded
- documentation is updated
- reproducible execution is verified
