"""보안 미들웨어"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HTTPS 강제 (프로덕션 환경)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
