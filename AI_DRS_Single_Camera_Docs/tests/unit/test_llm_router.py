"""
Unit tests for Open-Source Local LLM Engine & REST API Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
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

client = TestClient(app)


def test_llm_engine_chat():
    engine = OpenSourceLLMEngine()
    res = engine.chat(LLMChatRequest(prompt="What is the LBW decision?"))

    assert isinstance(res, LLMChatResponse)
    assert "OUT" in res.response or "AI DRS" in res.response
    assert res.tokens_generated > 0


def test_llm_engine_generate():
    engine = OpenSourceLLMEngine()
    res = engine.generate(LLMGenerateRequest(task_context="Analyze V. Kohli batting against seam"))

    assert isinstance(res, LLMGenerateResponse)
    assert "TACTICAL INSIGHT" in res.generated_text


def test_llm_engine_summarise():
    engine = OpenSourceLLMEngine()
    res = engine.summarise(LLMSummariseRequest(match_text="Over 14.1 LBW review requested"))

    assert isinstance(res, LLMSummariseResponse)
    assert len(res.key_points) > 0


def test_llm_engine_code():
    engine = OpenSourceLLMEngine()
    res = engine.code(LLMCodeRequest(instruction="Generate wagon wheel analysis script"))

    assert isinstance(res, LLMCodeResponse)
    assert "WagonWheelEngine" in res.code


def test_llm_chat_api_endpoint():
    response = client.post("/api/v1/llm/chat", json={"prompt": "Explain pitch seam deviation"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "model_name" in data


def test_llm_generate_api_endpoint():
    response = client.post("/api/v1/llm/generate", json={"task_context": "Match preview India vs Australia"})
    assert response.status_code == 200
    data = response.json()
    assert "generated_text" in data


def test_llm_summarise_api_endpoint():
    response = client.post("/api/v1/llm/summarise", json={"match_text": "Delivery 1: 4 runs. Delivery 2: Wicket."})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "key_points" in data


def test_llm_code_api_endpoint():
    response = client.post("/api/v1/llm/code", json={"instruction": "Filter ball tracking data"})
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "explanation" in data
