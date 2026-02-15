"""보안 미들웨어"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import HSTS_ENABLED, HSTS_MAX_AGE, HSTS_INCLUDE_SUBDOMAINS, HSTS_PRELOAD


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (HTTP Strict Transport Security) — 환경변수 기반 활성화 (Phase 12-1-3)
        if HSTS_ENABLED:
            hsts_value = f"max-age={HSTS_MAX_AGE}"
            if HSTS_INCLUDE_SUBDOMAINS:
                hsts_value += "; includeSubDomains"
            if HSTS_PRELOAD:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        return response
