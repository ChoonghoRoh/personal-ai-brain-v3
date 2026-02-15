"""전역 에러 핸들러 (Phase 12-2-4)

모든 예외를 표준 JSON 형식으로 변환한다.
RateLimitExceeded는 rate_limit.py에서 별도 처리하므로 여기서 제외.

표준 에러 응답 형식:
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "status": 404,
    "timestamp": "2026-02-15T18:00:00Z",
    "request_id": "req_abc123",
    "path": "/api/knowledge/chunks/123"
  }
}
"""
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config import DEBUG

logger = logging.getLogger(__name__)

# HTTP 상태 코드 → 에러 코드 매핑
_STATUS_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_SERVER_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


def _get_request_id(request: Request) -> str:
    """request.state에서 request_id 추출 (RequestIDMiddleware가 설정)"""
    return getattr(request.state, "request_id", "unknown")


def _build_error_response(
    status: int,
    message: str,
    request: Request,
    code: str | None = None,
) -> JSONResponse:
    """표준 에러 응답 생성"""
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code or _STATUS_CODE_MAP.get(status, "UNKNOWN_ERROR"),
                "message": message,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": _get_request_id(request),
                "path": str(request.url.path),
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTPException 전역 핸들러"""
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _build_error_response(
        status=exc.status_code,
        message=message,
        request=request,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """RequestValidationError 핸들러 (422)"""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    loc = " → ".join(str(l) for l in first_error.get("loc", []))
    msg = first_error.get("msg", "Validation error")
    message = f"{loc}: {msg}" if loc else msg

    return _build_error_response(
        status=422,
        message=message,
        request=request,
        code="VALIDATION_ERROR",
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """미처리 예외 핸들러 (500)"""
    request_id = _get_request_id(request)
    logger.error(
        "Unhandled exception [%s] %s: %s",
        request_id,
        type(exc).__name__,
        str(exc),
        exc_info=True,
    )

    message = f"{type(exc).__name__}: {exc}" if DEBUG else "Internal server error"
    return _build_error_response(
        status=500,
        message=message,
        request=request,
        code="INTERNAL_SERVER_ERROR",
    )


def setup_error_handlers(app: FastAPI) -> None:
    """에러 핸들러를 앱에 등록한다.

    주의: RateLimitExceeded 핸들러는 rate_limit.py에서 별도 등록하므로 여기서 제외.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    logger.info("Global error handlers registered (Phase 12-2-4)")
