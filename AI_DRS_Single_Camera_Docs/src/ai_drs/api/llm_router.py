"""
FastAPI REST API Router for Open-Source Local LLM Engine (Zero External API Keys)
"""

from fastapi import APIRouter, HTTPException, status

from ai_drs.common.logging import setup_logger
from ai_drs.llm.opensource_llm_engine import (
    LLMChatRequest,
    LLMChatResponse,
    LLMCodeRequest,
    LLMCodeResponse,
    LLMGenerateRequest,
    LLMGenerateResponse,
    LLMSummariseRequest,
    LLMSummariseResponse,
    OpenSourceLLMEngine,
)

logger = setup_logger("ai_drs.api.llm")

llm_router = APIRouter(prefix="/api/v1/llm", tags=["Open-Source LLM Engine"])
router = llm_router

llm_engine = OpenSourceLLMEngine()


@llm_router.post("/chat", response_model=LLMChatResponse)
def llm_chat_endpoint(request: LLMChatRequest):
    """Public Open-Source LLM Chat Endpoint (Zero external API keys required)."""
    try:
        return llm_engine.chat(request)
    except Exception as e:
        logger.error(f"Error in LLM chat endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/generate", response_model=LLMGenerateResponse)
def llm_generate_endpoint(request: LLMGenerateRequest):
    """Public Open-Source LLM Tactical Generation Endpoint."""
    try:
        return llm_engine.generate(request)
    except Exception as e:
        logger.error(f"Error in LLM generate endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/summarise", response_model=LLMSummariseResponse)
def llm_summarise_endpoint(request: LLMSummariseRequest):
    """Public Open-Source LLM Match & Review Summarization Endpoint."""
    try:
        return llm_engine.summarise(request)
    except Exception as e:
        logger.error(f"Error in LLM summarise endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/code", response_model=LLMCodeResponse)
def llm_code_endpoint(request: LLMCodeRequest):
    """Public Open-Source LLM Python Code Generation Endpoint."""
    try:
        return llm_engine.code(request)
    except Exception as e:
        logger.error(f"Error in LLM code endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
