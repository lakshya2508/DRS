# AI DRS — Execution Plan
## Development & Implementation Control File

**Version:** 1.0  
**Date:** 2026-08-11  
**Execution mode:** LOOP Engineering  
**Stop condition:** Production-ready research prototype

---

# 0. Development Rules

1. Build one milestone at a time.
2. Never move forward with a broken foundational module.
3. Every milestone requires:
   - implementation
   - test
   - metric
   - documentation
4. Keep raw data separate from processed data.
5. Never tune on the final test set.
6. Record model/config/data versions.
7. Prefer a simple baseline before advanced AI.
8. If evidence is insufficient, return INCONCLUSIVE.
9. Every completed milestone gets a checkpoint.
10. Do not optimize speed before correctness.

---

# 1. Master Backlog

## P0 — Foundation
- [ ] Repository initialization
- [ ] Python environment
- [ ] project configuration
- [ ] logging
- [ ] test framework
- [ ] video ingestion

## P1 — Camera Setup
- [ ] Define exact camera placement
- [ ] Define camera height/distance
- [ ] Create calibration procedure
- [ ] Implement homography
- [ ] Calibration validation

## P2 — Ball
- [ ] Collect controlled videos
- [ ] Annotate ball
- [ ] Train/evaluate baseline detector
- [ ] Implement tracking
- [ ] Measure track quality

## P3 — Cricket Geometry
- [ ] Detect stumps
- [ ] Detect crease/pitch references
- [ ] Detect batter
- [ ] Detect pad/leg region
- [ ] Convert observations to calibrated coordinates

## P4 — Events
- [ ] Detect bounce/pitching
- [ ] Detect ball-pad impact
- [ ] Detect relevant impact frame
- [ ] Estimate wicket plane

## P5 — Trajectory
- [ ] Implement smoothing
- [ ] Classical trajectory baseline
- [ ] Wicket-plane intersection
- [ ] Uncertainty estimation
- [ ] Trajectory visualization

## P6 — LBW Engine
- [ ] Define configurable rules
- [ ] Implement evidence aggregation
- [ ] Implement OUT
- [ ] Implement NOT OUT
- [ ] Implement INCONCLUSIVE
- [ ] Add confidence scoring

## P7 — Product
- [ ] FastAPI review endpoint
- [ ] Review status
- [ ] Result endpoint
- [ ] Evidence endpoint
- [ ] Next.js review UI
- [ ] Annotated replay

## P8 — Validation
- [x] Build held-out test set
- [x] Run complete benchmark
- [x] Analyze failures
- [x] Fix highest-impact issues
- [x] Re-run benchmark
- [x] Document limitations

## P9 — Match Intelligence Expansion (God Mode)
- [x] M11 — MatchState Engine & Data Models
- [x] M12 — Delivery State Machine
- [x] M13 — Batsman & Bowler Engines
- [x] M14 — Toss Engine
- [x] M15 — Match Condition & Situation Classifier
- [x] M16 — Match Analytics & Projection Engine
- [x] M17 — Match REST API & Live Scoreboard Service

## P10 — V3.0 Advanced Multi-Camera Stereoscopic 3D Fusion & AI
- [x] M18 — Multi-Camera Stereoscopic 3D Calibration & Triangulation Engine
- [x] M19 — Deep Learning Ball & Pose Detector (YOLOv11 & MediaPipe)
- [x] M20 — UltraEdge Snicko Audio Peak Processing

## P11 — V4.0 Enterprise Broadcast & Multi-User Real-Time Streaming
- [x] M21 — Multi-User Real-Time WebSocket Broadcast Manager
- [x] M22 — Async Distributed Task Queue & Video Processor
- [x] M23 — Highlight Reel Generator & Match Summary Exporter

## P12 — V5.0 WebRTC Live Camera & Match Report Exporter
- [x] M24 — WebRTC Smartphone Live Camera Ingestion Gateway
- [x] M25 — Automated Match Report HTML/PDF Exporter

## P13 — V6.0 Wagon Wheel, Pitch Heatmap & Win Probability Engine
- [x] M26 — Wagon Wheel Shot Direction Estimator
- [x] M27 — Pitch Line-Length Density Heatmap Generator
- [x] M28 — Real-Time Win Probability & DLS Momentum Index

## P14 — V7.0 Multi-Match Tournament Operations & Leaderboards
- [x] M29 — Tournament Operations & Net Run Rate (NRR) Engine
- [x] M30 — Tournament Leaderboards (Orange/Purple Cap & Stats)
- [x] M31 — Tournament REST API Router & Standings Service

## P15 — V8.0 Hawk-Eye 3D Pitch Graphics & Broadcast Overlays
- [x] M32 — 3D Pitch Wireframe Mesh & Ball Flight Path Generator
- [x] M33 — Broadcaster DRS Decision Card & Split-Screen Overlay Renderer
- [x] M34 — Interactive HTML5 Canvas 3D Review Viewer Component

## P16 — V9.0 Autonomous Third Umpire & Crease Checker Engine
- [x] M35 — Front-Foot No-Ball & Tramline Wide Detection Engine
- [x] M36 — Autonomous Third Umpire Audio Callout Generator
- [x] M37 — Full System Master Demonstration Suite & E2E Verification

## P17 — V10.0 Enterprise Cloud Multi-Tenancy & Global Match Federation
- [x] M38 — Multi-Tenant Organization & Venue Manager
- [x] M39 — Global Player Passport & Career Records Engine
- [x] M40 — Enterprise Health & Telemetry Metrics Monitor


















---

# 2. Milestone Execution

## M0 — Repository + Environment

### Goal
Create a reproducible development environment.

### Deliverables
- repository
- pyproject.toml
- source structure
- tests
- README
- configs
- .env.example

### Verification
```bash
python --version
pytest
```

### Exit criteria
Clean environment setup and passing starter tests.

---

## M1 — Video Ingestion

### Goal
Reliably load mobile videos and extract frames.

### Tasks
- metadata extraction
- codec validation
- frame iterator
- FPS handling
- frame sampling
- corrupted-video handling

### Output
```python
VideoMetadata(...)
Frame(...)
```

### Test
Use at least 10 recorded deliveries.

### Exit criteria
All valid videos process successfully.

---

## M2 — Camera Calibration

### Goal
Convert image coordinates into a stable pitch coordinate system.

### Tasks
- define reference points
- calibration UI/script
- homography
- reprojection error
- calibration persistence

### Output
```text
configs/calibration/<camera_id>.json
```

### Exit criteria
Calibration error is measured and acceptable for the controlled setup.

---

## M3 — Ball Detection Baseline

### Goal
Find the ball in individual frames.

### Tasks
- collect training data
- annotate
- train baseline
- evaluate
- inspect false positives/negatives

### Exit criteria
Meet the current PRD baseline or document why it is not yet met.

---

## M4 — Ball Tracking

### Goal
Create a continuous ball trajectory.

### Tasks
- detection association
- temporal smoothing
- missed detection recovery
- outlier rejection
- track confidence

### Exit criteria
Most controlled deliveries produce usable continuous tracks.

---

## M5 — Stump + Pitch Geometry

### Goal
Establish wicket and pitch references.

### Tasks
- stump detection
- crease detection/reference
- wicket centerline
- wicket plane
- coordinate transformation

### Exit criteria
Stable geometry across the controlled dataset.

---

## M6 — Pitching Detection

### Goal
Estimate where the ball pitches.

### Tasks
- identify ball/pitch interaction
- detect motion signature
- estimate contact frame
- transform to pitch coordinates

### Output
```text
pitching_frame
pitching_x
pitching_y
confidence
```

---

## M7 — Impact Detection

### Goal
Estimate ball-pad impact.

### Tasks
- pad/leg detection
- ball-pad distance
- temporal contact analysis
- impact frame selection

### Exit criteria
Impact localization is measurable against annotations.

---

## M8 — Trajectory Engine

### Goal
Predict the ball path through the wicket plane.

### Baseline
Use calibrated coordinates + smoothing + polynomial/kinematic fitting.

### Tasks
- fit trajectory
- extrapolate
- intersect wicket plane
- calculate uncertainty

### Exit criteria
Trajectory predictions can be benchmarked on held-out deliveries.

---

## M9 — LBW Decision Engine

### Goal
Combine evidence into a transparent recommendation.

### Decision pipeline
```text
Pitching
   +
Impact
   +
Wicket trajectory
   +
Confidence
   ↓
Rule Engine
   ↓
OUT / NOT OUT / INCONCLUSIVE
```

### Exit criteria
All decisions are reproducible from stored evidence.

---

## M10 — Review Interface

### Goal
Make the system understandable to a human reviewer.

### Screen
```text
┌──────────────────────────────────────┐
│              VIDEO                   │
│                                      │
│      ● Ball                         │
│       \                              │
│        \ trajectory                  │
│         \                            │
│       [STUMPS]                       │
├──────────────────────────────────────┤
│ Pitching     IN LINE       91%       │
│ Impact       IN LINE       84%       │
│ Wicket       HITTING       89%       │
│                                      │
│ Recommendation: OUT                  │
│ Confidence: 86%                      │
└──────────────────────────────────────┘
```

---

# 3. Dataset Execution Plan

## Dataset A — Calibration
At least 20 static scenes.

## Dataset B — Ball Tracking
At least 100 controlled deliveries.

## Dataset C — LBW Events
Progressively collect:
- clear NOT OUT
- clear OUT
- borderline cases
- different speeds
- different bowling angles
- different batter stances
- different lighting

Do not use only successful examples.

---

# 4. Annotation Schema

Each delivery should have:

```json
{
  "delivery_id": "D0001",
  "video": "D0001.mp4",
  "ball": {
    "frames": [],
    "centers": []
  },
  "pitching": {
    "frame": 0,
    "x": 0,
    "y": 0
  },
  "impact": {
    "frame": 0,
    "x": 0,
    "y": 0
  },
  "wicket": {
    "center": [0, 0],
    "plane": {}
  },
  "ground_truth": {
    "result": "OUT"
  }
}
```

---

# 5. Experiment Tracking

For every experiment record:

```text
Experiment ID
Date
Dataset version
Model version
Config version
Training parameters
Validation metrics
Test metrics
Known failure modes
Decision
```

Never overwrite old experiments.

---

# 6. LOOP Engineering Cycle

```text
WHILE project != production_ready:

    ANALYZE current state

    SELECT highest-priority unfinished task

    DEFINE acceptance criteria

    IMPLEMENT

    RUN unit tests

    RUN integration tests

    MEASURE metrics

    FIX failures

    REFACTOR if needed

    UPDATE documentation

    REVIEW requirements

    CREATE next backlog

    MARK task complete

    CREATE checkpoint

END
```

---

# 7. Checkpoint Template

At the end of every session:

```text
AI DRS CHECKPOINT

Completed:
-

In progress:
-

Remaining:
-

Current milestone:
-

Current files/modules:
-

Metrics:
-

Known bugs:
-

Important decisions:
-

Next highest-priority task:
-

Exact next action:
-
```

---

# 8. First 10 Development Tasks

### TASK-001
Initialize repository and Python environment.

### TASK-002
Implement video metadata and frame extraction.

### TASK-003
Record and catalog first controlled mobile dataset.

### TASK-004
Build calibration reference-point tool.

### TASK-005
Implement homography and calibration validation.

### TASK-006
Annotate first ball-detection dataset.

### TASK-007
Train/evaluate ball-detection baseline.

### TASK-008
Implement ball tracker.

### TASK-009
Measure tracking performance.

### TASK-010
Build stump/pitch geometry baseline.

**Do not start LBW decision logic before Tasks 001–009 have produced a reliable ball track.**

---

# 9. Release Plan

## v0.1
Video ingestion + calibration + ball detection.

## v0.2
Ball tracking + stump geometry.

## v0.3
Pitching + impact detection.

## v0.4
Trajectory projection.

## v0.5
LBW decision engine.

## v0.6
Review UI.

## v0.7
Controlled validation.

## v1.0
Research-grade single-camera AI-assisted DRS prototype.

---

# 10. Immediate Next Action

START HERE:

1. Choose the exact smartphone.
2. Fix it on a tripod.
3. Position it behind the bowler and align it with the pitch.
4. Record 20–30 deliveries.
5. Preserve original videos.
6. Record phone model, resolution and FPS.
7. Do not train anything yet.
8. Build the video-ingestion pipeline.
9. Inspect frame quality and ball visibility.
10. Begin M0 → M1.

The first engineering objective is:

**“Can our chosen mobile camera consistently capture enough information to track the cricket ball?”**

If the answer is no, improve the capture setup before adding AI complexity.
