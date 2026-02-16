"""인증 API 라우터 (Phase 9-1-1, Phase 14-5-2, Phase 15-5-2)

JWT 토큰 발급, 사용자 로그인/로그아웃/회원가입/프로필 API
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import JWT_EXPIRE_MINUTES, AUTH_ENABLED, API_SECRET_KEY
from backend.models.database import get_db
from backend.models.user_models import User
from backend.middleware.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_api_key,
    require_auth,
    get_current_user,
    blacklist_token,
    UserInfo,
    TokenResponse,
    ROLE_ADMIN_SYSTEM,
    ROLE_USER,
)

# 비밀번호 해싱 컨텍스트 (Phase 14-5-2)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    role: Optional[str] = None


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

    # JWT 토큰 생성 (API Key 사용자는 admin_system 권한)
    access_token = create_access_token(
        data={"sub": "api_user", "role": ROLE_ADMIN_SYSTEM},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    logger.info("토큰 발급 성공: api_user")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse, summary="사용자 로그인")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    사용자명/비밀번호로 로그인 (Phase 14-5-2)

    - users 테이블에서 사용자 조회
    - bcrypt 비밀번호 검증
    - 성공 시 JWT 액세스 토큰 반환
    """
    user = db.query(User).filter(
        User.username == request.username,
        User.is_active == True,
    ).first()

    if not user or not pwd_context.verify(request.password, user.hashed_password):
        logger.warning(f"로그인 실패: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES),
    )

    # Phase 15-6-1: Refresh Token 생성
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role}
    )

    # last_login_at 갱신
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"로그인 성공: {user.username} (role={user.role})")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
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
            auth_type=user.auth_type,
            role=user.role,
        )

    # 인증 비활성화 시 admin_system 권한 반환 (개발 편의)
    if not AUTH_ENABLED:
        return AuthStatusResponse(
            auth_enabled=False,
            authenticated=False,
            username=None,
            auth_type=None,
            role=ROLE_ADMIN_SYSTEM,
        )

    return AuthStatusResponse(
        auth_enabled=AUTH_ENABLED,
        authenticated=False,
        username=None,
        auth_type=None,
        role=None,
    )


@router.post("/logout", response_model=MessageResponse, summary="로그아웃")
async def logout(
    request: Request,
    user: UserInfo = Depends(require_auth),
):
    """
    로그아웃 (Phase 15-6-2: 서버 측 토큰 블랙리스트)

    - Authorization 헤더의 토큰을 블랙리스트에 추가
    - Redis 사용 가능 시 Redis, 아니면 메모리 폴백
    - 클라이언트에서도 토큰 삭제 권장
    """
    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        blacklist_token(token, expires_in_seconds=JWT_EXPIRE_MINUTES * 60)

    logger.info(f"로그아웃 (블랙리스트 등록): {user.username}")

    return MessageResponse(
        message="Successfully logged out. Token has been invalidated.",
        success=True
    )


@router.get("/status", response_model=AuthStatusResponse, summary="인증 시스템 상태")
async def auth_status():
    """
    인증 시스템 활성화 상태 확인

    클라이언트가 인증이 필요한지 확인할 때 사용.
    AUTH_ENABLED=false 시 role=admin_system 반환 (개발 환경에서 전체 메뉴 노출).
    """
    # 인증 비활성화 시 admin_system 권한 반환
    if not AUTH_ENABLED:
        return AuthStatusResponse(
            auth_enabled=False,
            authenticated=False,
            username=None,
            auth_type=None,
            role=ROLE_ADMIN_SYSTEM,
        )

    return AuthStatusResponse(
        auth_enabled=AUTH_ENABLED,
        authenticated=False,
        username=None,
        auth_type=None,
        role=None,
    )


# ============================================
# Refresh Token API (Phase 15-6-1)
# ============================================

class RefreshRequest(BaseModel):
    """Refresh Token 갱신 요청"""
    refresh_token: str = Field(..., description="Refresh Token")


@router.post("/refresh", response_model=TokenResponse, summary="토큰 갱신")
async def refresh_token(request: RefreshRequest):
    """
    Refresh Token으로 새 Access Token 발급 (Phase 15-6-1)

    - Refresh Token 검증
    - 새 Access Token + (선택) 새 Refresh Token 발급
    """
    token_data = verify_refresh_token(request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # 새 Access Token 생성
    new_access_token = create_access_token(
        data={"sub": token_data.username, "role": token_data.role},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES),
    )

    logger.info(f"토큰 갱신: {token_data.username}")

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60,
    )


# ============================================
# 셀프 서비스 API (Phase 15-5-2)
# ============================================

class RegisterRequest(BaseModel):
    """회원 가입 요청"""
    username: str = Field(..., min_length=3, max_length=100, description="사용자명 (3자 이상)")
    password: str = Field(..., min_length=8, max_length=72, description="비밀번호 (8자 이상)")
    display_name: Optional[str] = Field(None, max_length=200, description="표시 이름")
    email: Optional[str] = Field(None, max_length=255, description="이메일")


class ProfileResponse(BaseModel):
    """프로필 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ProfileUpdateRequest(BaseModel):
    """프로필 수정 요청"""
    display_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, max_length=72, description="새 비밀번호 (8자 이상)")


@router.post("/register", response_model=ProfileResponse, status_code=201, summary="회원 가입")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    새 사용자 회원 가입 (Phase 15-5-2)

    - 기본 역할: user
    - username 중복 시 409 Conflict
    - 비밀번호: bcrypt 해싱
    """
    user = User(
        username=request.username,
        hashed_password=pwd_context.hash(request.password),
        display_name=request.display_name,
        email=request.email,
        role=ROLE_USER,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    logger.info(f"회원 가입: {user.username} (id={user.id})")
    return user


@router.get("/profile", response_model=ProfileResponse, summary="내 프로필 조회")
async def get_profile(
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """현재 로그인한 사용자의 프로필 조회 (Phase 15-5-2)"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/profile", response_model=ProfileResponse, summary="내 프로필 수정")
async def update_profile(
    data: ProfileUpdateRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """현재 로그인한 사용자의 프로필 수정 (Phase 15-5-2)"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.display_name is not None:
        db_user.display_name = data.display_name
    if data.email is not None:
        db_user.email = data.email

    db_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_user)

    logger.info(f"프로필 수정: {user.username}")
    return db_user


@router.post("/change-password", response_model=MessageResponse, summary="비밀번호 변경")
async def change_password(
    data: ChangePasswordRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """현재 로그인한 사용자의 비밀번호 변경 (Phase 15-5-2)"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 현재 비밀번호 검증
    if not pwd_context.verify(data.current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    db_user.hashed_password = pwd_context.hash(data.new_password)
    db_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"비밀번호 변경: {user.username}")
    return MessageResponse(message="Password changed successfully")
