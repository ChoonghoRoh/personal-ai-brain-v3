"""페이지 접근 로그 미들웨어 (Phase 13-4)

HTML 페이지 요청만 비동기로 기록한다.
API 호출(/api/), 정적 파일(/static/), 헬스체크(/health) 등은 제외.
"""
import logging
import time
from typing import Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# 로깅 제외 경로 접두사
_SKIP_PREFIXES: tuple = ("/api/", "/static/", "/health", "/openapi", "/docs", "/redoc")

# HTML 라우트로 간주할 경로 집합 (main.py _HTML_ROUTES에서 추출)
_HTML_PATHS: Set[str] = {
    "/", "/dashboard", "/search", "/ask", "/logs",
    "/knowledge", "/knowledge-detail", "/knowledge-label-matching",
    "/knowledge-relation-matching", "/reason", "/knowledge-admin",
    "/admin/labels", "/admin/groups", "/admin/approval",
    "/admin/chunk-labels", "/admin/chunk-create", "/admin/statistics",
    "/admin/settings/templates", "/admin/settings/presets",
    "/admin/settings/rag-profiles", "/admin/settings/policy-sets",
    "/admin/settings/audit-logs",
}


def _is_html_page_request(path: str) -> bool:
    """HTML 페이지 요청 여부 판별"""
    if any(path.startswith(prefix) for prefix in _SKIP_PREFIXES):
        return False
    # 명시적 HTML 라우트이거나 /document/ 동적 경로
    return path in _HTML_PATHS or path.startswith("/document/")


class PageAccessLogMiddleware(BaseHTTPMiddleware):
    """HTML 페이지 접근을 DB에 기록하는 미들웨어"""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        if not _is_html_page_request(path) or request.method not in ("GET", "HEAD"):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # 백그라운드에서 DB 기록 (응답 지연 방지)
        try:
            _record_access(
                path=path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=elapsed_ms,
                user_agent=request.headers.get("user-agent", "")[:500],
                ip_address=request.client.host if request.client else None,
            )
        except Exception as exc:
            logger.debug("페이지 접근 로그 기록 실패: %s", exc)

        return response


def _record_access(
    path: str,
    method: str,
    status_code: int,
    response_time_ms: int,
    user_agent: str,
    ip_address: str | None,
) -> None:
    """접근 로그를 DB에 동기 삽입 (미들웨어에서 호출)"""
    from backend.models.database import SessionLocal
    from backend.models.admin_models import PageAccessLog

    db = SessionLocal()
    try:
        log_entry = PageAccessLog(
            path=path,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(log_entry)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.debug("page_access_log INSERT 실패: %s", exc)
    finally:
        db.close()
