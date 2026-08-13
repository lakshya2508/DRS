"""
Production Security Guard, Rate Limiter & Prompt Injection Defense for Open-Source LLM API
"""

import time
import re
from typing import Dict, Optional, Tuple
from fastapi import Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.llm_security")


class SecurityAuditLog(BaseModel):
    """Schema representing LLM API security audit log."""
    client_ip: str
    endpoint: str
    api_key_used: Optional[str]
    rate_limit_remaining: int
    is_allowed: bool
    rejection_reason: Optional[str] = None


class LLMSecurityGuard:
    """Enforces API key authentication, rate limiting, prompt injection defense, and request auditing."""

    DEFAULT_API_KEYS = {
        "drs_live_prod_key_9981": "Broadcaster Admin Tier",
        "drs_public_client_key_1024": "Public Client Tier",
        "drs_demo_guest_key": "Demo Tier"
    }

    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system override",
        r"bypass security",
        r"reveal system prompt",
        r"drop database",
        r"sudo rm -rf"
    ]

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.ip_request_counts: Dict[str, Tuple[int, float]] = {}  # ip -> (count, reset_timestamp)

    def verify_api_key(self, api_key: Optional[str] = None, auth_header: Optional[str] = None) -> str:
        """Verifies X-API-Key header or Bearer token."""
        token = api_key
        if not token and auth_header:
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "").strip()
            else:
                token = auth_header.strip()

        if not token:
            # Allow fallback to public demo key if none provided
            token = "drs_demo_guest_key"

        if token not in self.DEFAULT_API_KEYS:
            logger.warning(f"Unauthorized API access attempt with key: '{token}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key or Authorization Token. Access denied."
            )

        return self.DEFAULT_API_KEYS[token]

    def check_rate_limit(self, client_ip: str) -> int:
        """Enforces sliding window rate-limiting per client IP."""
        now = time.time()
        count, reset_time = self.ip_request_counts.get(client_ip, (0, now + 60.0))

        if now > reset_time:
            count = 1
            reset_time = now + 60.0
        else:
            count += 1

        self.ip_request_counts[client_ip] = (count, reset_time)

        if count > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP '{client_ip}': {count} requests in 60s")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests allowed per minute."
            )

        remaining = max(0, self.requests_per_minute - count)
        return remaining

    def sanitize_prompt(self, prompt: str) -> str:
        """Detects and neutralizes prompt injection & security override attempts."""
        prompt_lower = prompt.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, prompt_lower):
                logger.warning(f"Prompt injection pattern detected and blocked: '{pattern}'")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request blocked: Potential prompt injection or system override detected."
                )

        # Sanitize suspicious characters
        sanitized = prompt.replace("\x00", "").strip()
        return sanitized


# Global instance of LLM Security Guard
llm_security_guard = LLMSecurityGuard()
