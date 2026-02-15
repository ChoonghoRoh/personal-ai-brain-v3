"""Request ID 미들웨어 (Phase 12-2-4)

모든 요청에 고유 Request ID를 부여하여 로깅·에러 추적에 활용.
클라이언트가 X-Request-ID 헤더를 전달하면 해당 값을 사용하고,
없으면 UUID v4를 자동 생성한다.
"""
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Request ID 미들웨어"""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or f"req_{uuid.uuid4().hex[:12]}"
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
