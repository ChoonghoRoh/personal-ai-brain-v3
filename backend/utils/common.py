"""공통 HTTP 예외·응답 헬퍼 — 라우터 간 일관된 에러 포맷용 (Phase 9-5-1)."""
from fastapi import HTTPException


def http_not_found(detail: str) -> HTTPException:
    """404 Not Found 예외 생성."""
    return HTTPException(status_code=404, detail=detail)


def http_bad_request(detail: str) -> HTTPException:
    """400 Bad Request 예외 생성."""
    return HTTPException(status_code=400, detail=detail)


def http_unprocessable(detail: str) -> HTTPException:
    """422 Unprocessable Entity 예외 생성."""
    return HTTPException(status_code=422, detail=detail)


def http_internal_error(detail: str) -> HTTPException:
    """500 Internal Server Error 예외 생성."""
    return HTTPException(status_code=500, detail=detail)
