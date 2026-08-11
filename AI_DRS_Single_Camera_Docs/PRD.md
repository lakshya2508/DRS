# AI DRS — Single-Camera LBW Review System
## Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** 2026-08-11  
**Status:** Ready for Development  
**Product:** AI-assisted cricket LBW review using one fixed smartphone camera positioned behind the bowler.

---

## 1. Product Vision

Build a low-cost, mobile-camera-based AI DRS prototype that analyzes a cricket delivery from a single calibrated camera behind the bowler and produces an evidence-based LBW review.

The system is NOT intended to claim professional Hawk-Eye-level accuracy in V1. It is an AI-assisted experimental/research system whose outputs include detected evidence, estimated trajectory, confidence, and a final recommendation.

## 2. Problem

LBW review requires understanding:
- ball trajectory
- pitching location
- ball/pad impact
- wicket line
- whether the projected trajectory would hit the stumps

Professional systems use specialized multi-camera infrastructure. This project explores how much of the review process can be approximated with one fixed smartphone camera and computer vision.

## 3. Target User

Primary:
- cricket players
- coaches
- amateur/local cricket clubs
- students/researchers working on computer vision

Secondary:
- cricket-tech demonstrators
- academic project evaluators

## 4. V1 Scope

### In scope
- Single smartphone video input
- Fixed behind-bowler camera
- Video upload
- Frame extraction
- Camera/pitch calibration
- Ball detection and tracking
- Stump detection
- Batsman/pad detection
- Pitching-point estimation
- Impact-point estimation
- Ball trajectory estimation
- Trajectory extrapolation toward wicket plane
- LBW recommendation
- Confidence score
- Evidence/replay interface
- Exportable review report

### Out of scope for V1
- Multiple cameras
- Live broadcast-grade DRS
- Real-time streaming
- Hawk-Eye-equivalent 3D reconstruction
- Audio/Snickometer
- UltraEdge
- Hotspot
- Automated no-ball detection
- Official umpiring/legal decision authority

## 5. Core User Flow

1. Mount smartphone behind bowler.
2. Align camera with pitch/stumps.
3. Record delivery.
4. Upload video to application.
5. System validates video and calibration.
6. AI detects ball, batsman/pad and stumps.
7. System tracks ball through frames.
8. System estimates pitching and impact.
9. System extrapolates trajectory.
10. Decision engine evaluates LBW conditions.
11. User sees annotated replay and evidence.
12. User receives OUT / NOT OUT / INCONCLUSIVE.

## 6. Product Output

Example:

AI DRS REVIEW

- Pitching: IN LINE
- Impact: IN LINE
- Wicket: HITTING
- Ball track confidence: 92%
- Impact confidence: 84%
- Decision confidence: 86%
- Recommendation: OUT

The UI must clearly distinguish:
- observed/detected facts
- estimated values
- final AI recommendation

## 7. Decision States

The engine must support:

### OUT
Evidence satisfies the configured LBW rules and confidence exceeds threshold.

### NOT OUT
Evidence indicates the wicket would not be hit or a required condition is not satisfied.

### INCONCLUSIVE
Tracking/calibration/occlusion uncertainty is too high for a reliable recommendation.

**INCONCLUSIVE is mandatory. The system must never force a binary decision when evidence quality is insufficient.**

## 8. Success Metrics

### MVP metrics
- Ball detection precision/recall on project dataset
- Ball-track continuity
- Stump localization accuracy
- Pitch calibration error
- Impact localization error
- Trajectory prediction error
- Correct LBW classification on a labeled test set
- Inference latency per delivery

### Initial engineering targets
These are development targets, not claims of professional accuracy:
- >= 90% ball detection precision on controlled test footage
- >= 85% usable ball-track rate
- >= 90% stump localization success
- <= 5% calibration reprojection error in controlled setup
- >= 80% correct decision rate on a controlled validation set
- >= 95% of low-confidence cases correctly routed to INCONCLUSIVE

Targets should be revised after baseline experiments.

## 9. Dataset Requirements

Create an original controlled dataset using the project smartphone.

Each delivery should have:
- raw video
- camera configuration
- pitch/stump calibration metadata
- delivery ID
- ball coordinates/frame annotations
- pitching point
- impact point
- batsman/pad visibility
- wicket line
- ground-truth LBW outcome

Dataset splits:
- train
- validation
- test

No test video may be used for model tuning.

## 10. Hardware

Minimum:
- one smartphone with stable video recording
- tripod or rigid mount
- cricket pitch/stumps
- laptop/desktop for processing

Recommended recording characteristics:
- fixed camera
- high frame rate when available
- stable exposure/focus
- no digital zoom
- camera aligned to pitch centerline
- consistent camera height and position

## 11. Product Phases

### Phase 0 — Feasibility
Prove ball detection and tracking from the chosen camera position.

### Phase 1 — Calibration
Map image coordinates to a pitch coordinate system.

### Phase 2 — Event Detection
Detect pitching, impact and wicket geometry.

### Phase 3 — Trajectory Engine
Fit and extrapolate ball trajectory.

### Phase 4 — LBW Decision Engine
Combine evidence into OUT / NOT OUT / INCONCLUSIVE.

### Phase 5 — Review UI
Create annotated replay and evidence panel.

### Phase 6 — Validation
Evaluate on unseen controlled deliveries.

### Phase 7 — Optimization
Improve robustness, speed and failure handling.

## 12. Non-Functional Requirements

- Reproducible inference
- Deterministic configuration/versioning
- Clear logging
- No silent failures
- Every decision traceable to evidence
- Model and dataset version recorded
- Privacy-conscious local video handling
- Modular architecture so detectors can be replaced independently

## 13. Risks

### Ball blur/occlusion
Mitigation: high-frame-rate capture, tracking model, temporal filtering.

### Single-view ambiguity
Mitigation: calibrated geometry, uncertainty estimation, INCONCLUSIVE state.

### Lighting variation
Mitigation: controlled dataset followed by varied validation footage.

### Batsman occlusion
Mitigation: temporal evidence and pose/object detection.

### Camera misalignment
Mitigation: mandatory calibration and validation before analysis.

### Dataset bias
Mitigation: multiple bowlers, batters, speeds, lighting conditions and ball colors where practical.

## 14. Definition of Done — V1

V1 is complete when:
- a user can upload a delivery video
- calibration is validated
- ball is detected/tracked
- stumps and relevant player geometry are detected
- pitching/impact/trajectory are estimated
- decision engine returns OUT/NOT OUT/INCONCLUSIVE
- UI shows annotated evidence
- evaluation runs on a held-out test set
- known failure cases are documented
- reproducible setup and execution instructions exist
