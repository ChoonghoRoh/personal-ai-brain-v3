"""Rate Limiting 미들웨어 (Phase 9-1-4)

slowapi를 사용한 API 요청 제한
"""
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.config import (
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_PER_MINUTE,
    RATE_LIMIT_LLM_PER_MINUTE,
    RATE_LIMIT_SEARCH_PER_MINUTE,
    RATE_LIMIT_IMPORT_PER_MINUTE,
    RATE_LIMIT_AUTH_PER_MINUTE,
    REDIS_URL,
)

logger = logging.getLogger(__name__)


# ============================================
# Rate Limit 키 생성 함수
# ============================================

def _get_client_ip(request: Request) -> str:
    """클라이언트 실제 IP 추출 (Phase 12-3-2)

    리버스 프록시(Nginx, Docker 등) 뒤에서 X-Forwarded-For 헤더를 파싱하여
    실제 클라이언트 IP를 반환한다. 헤더가 없으면 기존 방식(request.client.host)을 사용.

    X-Forwarded-For 형식: "client, proxy1, proxy2"
    첫 번째 IP가 원본 클라이언트 IP.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # 첫 번째 IP = 원본 클라이언트
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip
    return get_remote_address(request)


def get_key_func(request: Request) -> str:
    """
    Rate Limit 키 생성 함수

    인증된 사용자는 사용자 ID로, 아니면 IP로 구분
    """
    # 인증된 사용자 확인
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.username}"

    # IP 기반 (X-Forwarded-For 우선, Phase 12-3-2)
    return _get_client_ip(request)


# ============================================
# Limiter 설정
# ============================================

# Redis 사용 시 분산 환경 지원
storage_uri = REDIS_URL if REDIS_URL else None

limiter = Limiter(
    key_func=get_key_func,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=storage_uri,
    enabled=RATE_LIMIT_ENABLED,
)


# ============================================
# 커스텀 Rate Limit 데코레이터
# ============================================

def limit_llm() -> Callable:
    """LLM API용 Rate Limit 데코레이터 (엄격한 제한)"""
    return limiter.limit(f"{RATE_LIMIT_LLM_PER_MINUTE}/minute")


def limit_search() -> Callable:
    """검색 API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_SEARCH_PER_MINUTE}/minute")


def limit_import() -> Callable:
    """Import API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_IMPORT_PER_MINUTE}/minute")


def limit_auth() -> Callable:
    """인증 API용 Rate Limit 데코레이터 (브루트포스 방지)"""
    return limiter.limit(f"{RATE_LIMIT_AUTH_PER_MINUTE}/minute")


def limit_default() -> Callable:
    """기본 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")


# ============================================
# 에러 핸들러
# ============================================

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Rate Limit 초과 시 응답

    429 Too Many Requests + Retry-After 헤더
    """
    response = Response(
        content='{"detail": "Rate limit exceeded. Please try again later.", "error_code": "RATE_LIMIT_EXCEEDED"}',
        status_code=429,
        media_type="application/json"
    )

    # Retry-After 헤더 (초 단위)
    response.headers["Retry-After"] = str(60)  # 1분 후 재시도
    response.headers["X-RateLimit-Limit"] = str(exc.detail) if exc.detail else str(RATE_LIMIT_PER_MINUTE)

    logger.warning(f"Rate limit exceeded: {get_key_func(request)} - {request.url.path}")

    return response


# ============================================
# FastAPI 앱에 적용
# ============================================

def setup_rate_limiting(app: FastAPI) -> None:
    """
    Rate Limiting 설정 적용

    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    if not RATE_LIMIT_ENABLED:
        logger.info("Rate limiting is disabled")
        return

    # Limiter를 앱 상태에 저장 (라우터에서 접근 가능)
    app.state.limiter = limiter

    # 에러 핸들러 등록
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # 미들웨어 추가
    app.add_middleware(SlowAPIMiddleware)

    storage_info = f"Redis: {REDIS_URL}" if REDIS_URL else "In-Memory"
    logger.info(f"Rate limiting enabled: {RATE_LIMIT_PER_MINUTE}/min (default), Storage: {storage_info}")


# ============================================
# Rate Limit 정보 조회
# ============================================

def get_rate_limit_info() -> dict:
    """현재 Rate Limit 설정 정보 반환"""
    return {
        "enabled": RATE_LIMIT_ENABLED,
        "default_limit": f"{RATE_LIMIT_PER_MINUTE}/minute",
        "llm_limit": f"{RATE_LIMIT_LLM_PER_MINUTE}/minute",
        "search_limit": f"{RATE_LIMIT_SEARCH_PER_MINUTE}/minute",
        "import_limit": f"{RATE_LIMIT_IMPORT_PER_MINUTE}/minute",
        "auth_limit": f"{RATE_LIMIT_AUTH_PER_MINUTE}/minute",
        "storage": "redis" if REDIS_URL else "memory",
    }
