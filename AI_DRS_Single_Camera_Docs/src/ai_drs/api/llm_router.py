"""
FastAPI REST API Router for Protected Open-Source Local LLM Engine
"""

from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Request, status

from ai_drs.common.logging import setup_logger
from ai_drs.enterprise.llm_security_guard import llm_security_guard
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

llm_router = APIRouter(prefix="/api/v1/llm", tags=["Protected Open-Source LLM Engine"])
router = llm_router

llm_engine = OpenSourceLLMEngine()


def _protect_llm_request(
    request_obj: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
) -> str:
    """Helper method to enforce security, rate limiting, and prompt injection checks."""
    client_ip = request_obj.client.host if request_obj.client else "127.0.0.1"
    tier = llm_security_guard.verify_api_key(api_key=x_api_key, auth_header=authorization)
    llm_security_guard.check_rate_limit(client_ip)
    return tier


@llm_router.post("/chat", response_model=LLMChatResponse)
def llm_chat_endpoint(
    req: LLMChatRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """Protected Open-Source LLM Chat Endpoint (API Key & Rate Limit Protected)."""
    try:
        _protect_llm_request(request, x_api_key, authorization)
        req.prompt = llm_security_guard.sanitize_prompt(req.prompt)
        return llm_engine.chat(req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM chat endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/generate", response_model=LLMGenerateResponse)
def llm_generate_endpoint(
    req: LLMGenerateRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """Protected Open-Source LLM Tactical Generation Endpoint."""
    try:
        _protect_llm_request(request, x_api_key, authorization)
        req.task_context = llm_security_guard.sanitize_prompt(req.task_context)
        return llm_engine.generate(req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM generate endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/summarise", response_model=LLMSummariseResponse)
def llm_summarise_endpoint(
    req: LLMSummariseRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """Protected Open-Source LLM Match & Review Summarization Endpoint."""
    try:
        _protect_llm_request(request, x_api_key, authorization)
        req.match_text = llm_security_guard.sanitize_prompt(req.match_text)
        return llm_engine.summarise(req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM summarise endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@llm_router.post("/code", response_model=LLMCodeResponse)
def llm_code_endpoint(
    req: LLMCodeRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """Protected Open-Source LLM Python Code Generation Endpoint."""
    try:
        _protect_llm_request(request, x_api_key, authorization)
        req.instruction = llm_security_guard.sanitize_prompt(req.instruction)
        return llm_engine.code(req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM code endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
