"""
FastAPI Production REST API Router for Real Model Weight Loading & Tensor Inference
"""

import tempfile
from typing import Dict, List, Optional
import cv2
import numpy as np
from fastapi import APIRouter, File, Header, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.detection.real_model_inference import (
    ModelPredictionResult,
    RealModelInferenceEngine,
)
from ai_drs.enterprise.llm_security_guard import llm_security_guard

logger = setup_logger("ai_drs.api.real_model")

real_model_router = APIRouter(prefix="/api/v1/model", tags=["Real Model Inference API"])
router = real_model_router

# Initialize active model engine instance
active_model_engine = RealModelInferenceEngine()


class LoadModelRequest(BaseModel):
    """Schema for loading custom model weights."""
    weights_path: str = Field(
        default="C:\\Users\\Hello-pc\\Downloads\\archive (1)\\weights\\best_cricket_ball_model.pt",
        description="Path to trained PyTorch / ONNX model weights"
    )


class LoadModelResponse(BaseModel):
    """Schema for model loading response."""
    status: str
    weights_path: str
    model_backend: str
    is_loaded: bool


class TensorPredictionRequest(BaseModel):
    """Schema for prediction on synthetic/matrix tensor."""
    width: int = Field(default=1280, ge=100)
    height: int = Field(default=720, ge=100)
    confidence_threshold: float = Field(default=0.35, ge=0.0, le=1.0)


@real_model_router.get("/status", response_model=LoadModelResponse)
def get_model_status():
    """Returns currently loaded model weights, status, and backend details."""
    return LoadModelResponse(
        status="ACTIVE" if active_model_engine.is_loaded else "UNINITIALIZED",
        weights_path=active_model_engine.weights_path,
        model_backend=active_model_engine.model_backend,
        is_loaded=active_model_engine.is_loaded
    )


@real_model_router.post("/load", response_model=LoadModelResponse)
def load_custom_model_weights(
    req: LoadModelRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """Loads custom trained model weights from specified path (e.g. from archive dataset)."""
    global active_model_engine
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        logger.info(f"Loading custom model weights request: '{req.weights_path}'")

        active_model_engine = RealModelInferenceEngine(weights_path=req.weights_path)

        return LoadModelResponse(
            status="SUCCESS",
            weights_path=active_model_engine.weights_path,
            model_backend=active_model_engine.model_backend,
            is_loaded=active_model_engine.is_loaded
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading model weights: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@real_model_router.post("/predict", response_model=ModelPredictionResult)
def predict_uploaded_image(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.35,
    x_api_key: Optional[str] = Header(default=None)
):
    """Executes real model inference on an uploaded image file (PNG/JPG)."""
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        contents = file.file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format.")

        result = active_model_engine.predict_image(img, confidence_threshold=confidence_threshold)
        logger.info(f"Predicted uploaded image '{file.filename}': {len(result.detections)} detections in {result.inference_time_ms}ms")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting uploaded image: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@real_model_router.post("/predict_tensor", response_model=ModelPredictionResult)
def predict_synthetic_tensor(
    req: TensorPredictionRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """Executes real model forward pass inference on a frame matrix."""
    try:
        llm_security_guard.verify_api_key(api_key=x_api_key)
        # Create synthetic frame matrix
        img = np.zeros((req.height, req.width, 3), dtype=np.uint8)
        cv2.circle(img, (int(req.width * 0.5), int(req.height * 0.6)), 12, (0, 0, 255), -1)

        result = active_model_engine.predict_image(img, confidence_threshold=req.confidence_threshold)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predict_tensor endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
