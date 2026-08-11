# 🏏 AI DRS — Single-Camera LBW Review & Autonomous Cricket Match Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green.svg)](https://opencv.org/)
[![Pytest](https://img.shields.io/badge/tests-80%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-94%25-success.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Python package and artificial intelligence engine combining **Single-Camera Computer Vision LBW Decision Review System (DRS)** with an **Autonomous Cricbuzz-Style Live Cricket Match Engine (God Mode)**.

---

## 📖 About `ai-drs`

`ai-drs` is designed to solve a fundamental problem in grassroots and amateur cricket: bringing professional-grade Hawk-Eye style LBW review capabilities and live Cricbuzz match intelligence to any cricket match using **just one smartphone camera positioned behind the bowler**.

The package operates across two unified intelligence layers:

### 1. Single-Camera AI DRS Perception Engine (V1.0)
Processes smartphone delivery video behind the bowler, calibrates the 2D/3D ground pitch plane, tracks the ball trajectory, localizes stumps, detects pitching (bounce) and pad impact events, projects 3D flight paths to the wicket plane, and produces explainable `OUT`, `NOT_OUT`, or `INCONCLUSIVE` decisions compliant with MCC Law 36.

### 2. Cricbuzz-Style Autonomous Match Engine — God Mode (V2.0)
Maintains the single authoritative `MatchState`, enforces a strict 9-stage delivery finite state machine (FSM), tracks live batter and bowler cards, conducts cryptographic coin tosses, classifies live match situations (`COMFORTABLE`, `STABLE`, `PRESSURE`, `HIGH_PRESSURE`, `CRITICAL`), computes over-by-over pressure trends & score projections, and serves a live mobile web application.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                               ONE CAMERA                                │
│                                   │                                     │
│                                   ▼                                     │
│                       CRICKET PERCEPTION ENGINE                         │
│                                   │                                     │
│            ┌──────────────────────┼──────────────────────┐              │
│            ▼                      ▼                      ▼              │
│      BALL DETECTOR         STUMP DETECTOR         EVENT DETECTOR        │
│       & TRACKER             & PITCH GEOM           (PITCH & IMPACT)     │
│            │                      │                      │              │
│            └──────────────────────┼──────────────────────┘              │
│                                   ▼                                     │
│                           TRAJECTORY ENGINE                             │
│                           & WICKET PROJECTION                           │
│                                   │                                     │
│            ┌──────────────────────┴──────────────────────┐              │
│            ▼                                             ▼              │
│    LBW DECISION ENGINE                         DELIVERY FSM ENGINE      │
│   (OUT/NOT OUT/INCONCL)                                  │              │
│                                                          ▼              │
│                                                 AUTHORITATIVE MATCHSTATE│
│                                                          │              │
│            ┌──────────────────────┬──────────────────────┤              │
│            ▼                      ▼                      ▼              │
│     CRICBUZZ CARDS         MATCH CONDITIONS       MATCH ANALYTICS       │
│    (BATTER & BOWLER)      & SITUATION BADGE     & PRESSURE TRENDS       │
│            │                      │                      │              │
│            └──────────────────────┼──────────────────────┘              │
│                                   ▼                                     │
│                        FASTAPI REST API ENGINE                          │
│                         & MOBILE WEB APP UI                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Package Modules & Structure

| Module | Source Directory | Primary Purpose |
| :--- | :--- | :--- |
| `ai_drs.ingestion` | `src/ai_drs/ingestion/` | Video frame streaming, metadata extraction, and synthetic test video generation. |
| `ai_drs.calibration` | `src/ai_drs/calibration/` | 2D/3D ground pitch homography transform mapping and reprojection error measurement. |
| `ai_drs.detection` | `src/ai_drs/detection/` | Classical HSV/contour/motion ball detector, YOLOv11 interface, and stump detector. |
| `ai_drs.tracking` | `src/ai_drs/tracking/` | 2D Constant-Velocity Kalman Filter, gating distance association, and occlusion interpolation. |
| `ai_drs.events` | `src/ai_drs/events/` | Bounce (pitching) and pad impact localization with MCC Law 36 zone classification. |
| `ai_drs.trajectory` | `src/ai_drs/trajectory/` | Polynomial $X(Y)$ trajectory fitting, $Y=20.12\text{m}$ extrapolation, and wicket hit classification. |
| `ai_drs.decision` | `src/ai_drs/decision/` | LBW rule aggregation, evidence confidence scoring, and `INCONCLUSIVE` state routing. |
| `ai_drs.match` | `src/ai_drs/match/` | Authoritative `MatchState`, 9-stage delivery FSM, Cricbuzz player cards, toss, and analytics. |
| `ai_drs.api` | `src/ai_drs/api/` | FastAPI REST endpoints (`review_service.py`, `match_router.py`) and Cricbuzz Mobile App UI. |
| `ai_drs.evaluation` | `src/ai_drs/evaluation/` | Benchmark evaluator for held-out delivery dataset catalog validation. |

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install the package in editable mode:
```bash
git clone https://github.com/lakshya2508/DRS.git
cd DRS
pip install -e .
```

### 2. Run Master Terminal Demonstration
Execute the end-to-end live terminal demonstration:
```bash
python demo.py
```

### 3. Launch Local Web Application & API
Start the local FastAPI development server:
```bash
python -m uvicorn ai_drs.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Access the interfaces in your browser:
- **Cricbuzz Mobile Web App UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Pytest Suite
Run the 80 unit & integration tests with code coverage report:
```bash
python -m pytest --cov=ai_drs --cov-report=term-missing
```

---

## 📡 REST API Reference

### AI DRS Review Endpoints
- `POST /api/v1/reviews` — Upload delivery video (`.mp4`, `.mov`, `.avi`) and execute full DRS pipeline.
- `GET /api/v1/reviews/{review_id}` — Retrieve review decision (`OUT`, `NOT_OUT`, `INCONCLUSIVE`).
- `GET /api/v1/reviews/{review_id}/evidence` — Retrieve full computer vision evidence payload.
- `POST /api/v1/calibration` — Register camera pitch calibration profile.

### Autonomous Match Engine Endpoints
- `POST /api/v1/match/create` — Initialize new match.
- `POST /api/v1/match/{match_id}/toss` — Conduct official cryptographic coin toss.
- `POST /api/v1/match/{match_id}/delivery` — Process delivery through 9-stage FSM.
- `GET /api/v1/match/{match_id}/scoreboard` — Retrieve authoritative Cricbuzz live scoreboard.
- `GET /api/v1/match/{match_id}/cards` — Retrieve Cricbuzz live striker, non-striker, and bowler cards.
- `GET /api/v1/match/{match_id}/condition-panel` — Retrieve live match condition panel & situation badge.
- `GET /api/v1/match/{match_id}/analytics` — Retrieve run rate trends, pressure indexes, and score projection ranges.

---

## ⚖️ Uncertainty Law & MCC Law 36 Compliance

The system strictly adheres to the **Uncertainty Law**:
> *If tracking coverage $< 70\%$, pitch calibration reprojection error $> 5.0\text{px}$, or combined evidence confidence $< 0.56$, the engine MUST return `INCONCLUSIVE`. The system never fabricates confidence.*

---

## 📄 Key Project Documentation

- `PRD.md` — Product Requirements Document
- `TRD.md` — Technical Architecture & Reference Schema Document
- `EXECUTION_PLAN.md` — Master Backlog & Milestone Control Plan
- `PROJECT_STATE.md` — Component Status Matrix & Verified Features Log
- `project_report.md` — Comprehensive Technical Evaluation & Expansion Report

---

## 📜 License & Citation

Distributed under the **MIT License**. Created by **Lakshya Kucheriya** (`lakshya2508`) under the **L99 Loop Engineering Protocol**.

If you use `ai-drs` in research or sports analytics, please cite:
```text
@software{kucheriya2026aidrs,
  author = {Lakshya Kucheriya},
  title = {AI DRS: Single-Camera LBW System & Autonomous Cricket Match Engine},
  year = {2026},
  url = {https://github.com/lakshya2508/DRS}
}
```
