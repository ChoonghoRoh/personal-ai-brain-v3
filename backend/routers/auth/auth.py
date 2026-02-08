"""인증 API 라우터 (Phase 9-1-1)

JWT 토큰 발급 및 사용자 정보 조회 API
"""
import logging
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from backend.config import JWT_EXPIRE_MINUTES, AUTH_ENABLED, API_SECRET_KEY
from backend.middleware.auth import (
    create_access_token,
    verify_api_key,
    require_auth,
    get_current_user,
    UserInfo,
    TokenResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================
# Pydantic 모델
# ============================================

class TokenRequest(BaseModel):
    """토큰 요청 (간단한 API Key 기반)"""
    api_key: str = Field(..., description="API Key")


class LoginRequest(BaseModel):
    """로그인 요청 (사용자명/비밀번호 방식 - 확장용)"""
    username: str = Field(..., min_length=1, description="사용자명")
    password: str = Field(..., min_length=1, description="비밀번호")


class AuthStatusResponse(BaseModel):
    """인증 상태 응답"""
    auth_enabled: bool
    authenticated: bool
    username: Optional[str] = None
    auth_type: Optional[str] = None


class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str
    success: bool = True


# ============================================
# 인증 API 엔드포인트
# ============================================

@router.post("/token", response_model=TokenResponse, summary="API Key로 JWT 토큰 발급")
async def get_token(request: TokenRequest):
    """
    API Key를 사용하여 JWT 토큰 발급

    - API Key가 유효하면 JWT 액세스 토큰 반환
    - 토큰은 설정된 만료 시간(JWT_EXPIRE_MINUTES) 후 만료

    **요청 예시:**
    ```json
    {
        "api_key": "your-api-key"
    }
    ```

    **응답 예시:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "expires_in": 1800
    }
    ```
    """
    if not API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API Key authentication is not configured"
        )

    if not verify_api_key(request.api_key):
        logger.warning("토큰 발급 실패: 잘못된 API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # JWT 토큰 생성
    access_token = create_access_token(
        data={"sub": "api_user"},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    logger.info("토큰 발급 성공: api_user")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse, summary="로그인 (확장용)")
async def login(request: LoginRequest):
    """
    사용자명/비밀번호로 로그인 (확장용)

    현재는 간단한 검증만 수행하며, 향후 사용자 DB 연동 가능

    **참고:** 현재 구현에서는 모든 로그인 시도가 실패합니다.
    실제 사용자 인증이 필요한 경우 이 엔드포인트를 확장하세요.
    """
    # TODO: 실제 사용자 DB 연동 시 구현
    # 현재는 사용자 DB가 없으므로 항상 실패
    logger.warning(f"로그인 시도: {request.username} (사용자 DB 미구현)")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User authentication is not implemented yet. Use /api/auth/token with API key."
    )


@router.get("/me", response_model=AuthStatusResponse, summary="현재 인증 상태 확인")
async def get_me(
    request: Request,
    user: Optional[UserInfo] = Depends(get_current_user)
):
    """
    현재 인증 상태 및 사용자 정보 확인

    - 인증된 경우: 사용자 정보 반환
    - 인증되지 않은 경우: authenticated=False 반환

    **응답 예시 (인증됨):**
    ```json
    {
        "auth_enabled": true,
        "authenticated": true,
        "username": "api_user",
        "auth_type": "jwt"
    }
    ```

    **응답 예시 (미인증):**
    ```json
    {
        "auth_enabled": false,
        "authenticated": false,
        "username": null,
        "auth_type": null
    }
    ```
    """
    if user:
        return AuthStatusResponse(
            auth_enabled=AUTH_ENABLED,
            authenticated=True,
            username=user.username,
            auth_type=user.auth_type
        )

    return AuthStatusResponse(
        auth_enabled=AUTH_ENABLED,
        authenticated=False,
        username=None,
        auth_type=None
    )


@router.post("/logout", response_model=MessageResponse, summary="로그아웃")
async def logout(user: UserInfo = Depends(require_auth)):
    """
    로그아웃

    JWT는 stateless이므로 서버 측 세션 무효화는 없습니다.
    클라이언트에서 토큰을 삭제하여 로그아웃 처리합니다.

    향후 토큰 블랙리스트 구현 시 서버 측 무효화 가능
    """
    logger.info(f"로그아웃: {user.username}")

    return MessageResponse(
        message="Successfully logged out. Please delete the token on client side.",
        success=True
    )


@router.get("/status", response_model=AuthStatusResponse, summary="인증 시스템 상태")
async def auth_status():
    """
    인증 시스템 활성화 상태 확인

    클라이언트가 인증이 필요한지 확인할 때 사용
    """
    return AuthStatusResponse(
        auth_enabled=AUTH_ENABLED,
        authenticated=False,
        username=None,
        auth_type=None
    )
