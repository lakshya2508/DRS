"""
Dataset Model Router — REST API for dataset video classification on archive (1) dataset clips.
"""

import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, Query

from ai_drs.detection.dataset_classifier import (
    DatasetDeliveryClassifier, DatasetClassificationResult
)

dataset_router = APIRouter(prefix="/api/v1/dataset", tags=["Dataset Vision Model"])
_classifier = DatasetDeliveryClassifier()


@dataset_router.get("/clips", response_model=dict)
def get_dataset_clips():
    """Lists available video clips from C:\\Users\\Hello-pc\\Downloads\\archive (1) dataset."""
    clips = _classifier.list_available_clips()
    total = sum(len(v) for v in clips.values())
    return {"status": "ok", "total_clips": total, "clips": clips}


@dataset_router.post("/classify", response_model=dict)
def classify_dataset_clip(video_path: str = Query(..., description="Absolute path to mp4 clip")):
    """Runs AI vision model classification on a video file from the archive (1) dataset."""
    try:
        res = _classifier.classify_video_file(video_path)
        return {"status": "ok", "result": res.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dataset_router.post("/upload-and-classify", response_model=dict)
async def upload_and_classify(file: UploadFile = File(...)):
    """Uploads any MP4/AVI delivery video file and runs AI model inference."""
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        res = _classifier.classify_video_file(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
        return {"status": "ok", "result": res.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
