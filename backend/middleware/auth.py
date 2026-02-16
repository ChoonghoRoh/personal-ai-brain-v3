"""인증 미들웨어 (Phase 9-1-1, Phase 14-1 권한 확장)

JWT 토큰 및 API Key 기반 인증을 지원합니다.
역할(role) 기반 접근 제어를 포함합니다.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
    API_SECRET_KEY,
    AUTH_ENABLED,
)

logger = logging.getLogger(__name__)

# ============================================
# 역할(Role) 정의 (Phase 14-1)
# ============================================

ROLE_USER = "user"
ROLE_ADMIN_KNOWLEDGE = "admin_knowledge"
ROLE_ADMIN_SYSTEM = "admin_system"

# 역할 계층: admin_system > admin_knowledge > user
ROLE_HIERARCHY = {
    ROLE_USER: 0,
    ROLE_ADMIN_KNOWLEDGE: 1,
    ROLE_ADMIN_SYSTEM: 2,
}

# ============================================
# Pydantic 모델
# ============================================

class TokenData(BaseModel):
    """토큰 페이로드 데이터"""
    username: Optional[str] = None
    role: str = ROLE_USER
    exp: Optional[datetime] = None


class UserInfo(BaseModel):
    """인증된 사용자 정보"""
    username: str
    auth_type: str  # "jwt" | "api_key" | "none"
    role: str = ROLE_USER


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 초 단위


# ============================================
# 보안 스킴 정의
# ============================================

# JWT Bearer 토큰
bearer_scheme = HTTPBearer(auto_error=False)

# API Key 헤더
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ============================================
# JWT 토큰 함수
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": "username"})
        expires_delta: 만료 시간 (기본: JWT_EXPIRE_MINUTES)

    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[TokenData]:
    """
    JWT 토큰 검증

    Args:
        token: JWT 토큰 문자열

    Returns:
        TokenData 또는 None (검증 실패 시)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", ROLE_USER)
        exp = payload.get("exp")

        if username is None:
            return None

        return TokenData(
            username=username,
            role=role,
            exp=datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None,
        )

    except JWTError as e:
        logger.debug(f"JWT 검증 실패: {e}")
        return None


def verify_api_key(api_key: str) -> bool:
    """
    API Key 검증

    Args:
        api_key: API 키 문자열

    Returns:
        검증 성공 여부
    """
    if not API_SECRET_KEY:
        return False
    return api_key == API_SECRET_KEY


# ============================================
# 인증 의존성 함수
# ============================================

async def get_current_user(
    request: Request,
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header),
) -> Optional[UserInfo]:
    """
    현재 인증된 사용자 정보 가져오기 (선택적 인증)

    인증이 비활성화되어 있으면 None 반환
    인증이 활성화되어 있으면 JWT 또는 API Key로 인증

    Args:
        request: FastAPI Request 객체
        bearer_credentials: JWT Bearer 토큰
        api_key: API Key 헤더

    Returns:
        UserInfo 또는 None
    """
    # 인증 비활성화 시 None 반환 (모든 요청 허용)
    if not AUTH_ENABLED:
        return None

    # JWT Bearer 토큰 확인
    if bearer_credentials:
        token_data = verify_jwt_token(bearer_credentials.credentials)
        if token_data and token_data.username:
            user = UserInfo(username=token_data.username, auth_type="jwt", role=token_data.role)
            request.state.user = user
            return user

    # API Key 확인 (API Key 사용자는 admin_system 권한)
    if api_key and verify_api_key(api_key):
        user = UserInfo(username="api_user", auth_type="api_key", role=ROLE_ADMIN_SYSTEM)
        request.state.user = user
        return user

    return None


async def require_auth(
    request: Request,
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header),
) -> UserInfo:
    """
    인증 필수 의존성 함수

    인증이 비활성화되어 있으면 더미 사용자 반환
    인증이 활성화되어 있으면 인증 필수

    Args:
        request: FastAPI Request 객체
        bearer_credentials: JWT Bearer 토큰
        api_key: API Key 헤더

    Returns:
        UserInfo

    Raises:
        HTTPException: 인증 실패 시 401 Unauthorized
    """
    # 인증 비활성화 시 더미 사용자 반환 (개발 편의: admin_system 권한)
    if not AUTH_ENABLED:
        return UserInfo(username="anonymous", auth_type="none", role=ROLE_ADMIN_SYSTEM)

    user = await get_current_user(request, bearer_credentials, api_key)

    if user is None:
        logger.warning(f"인증 실패: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ============================================
# 역할 기반 권한 검증 의존성 (Phase 14-1)
# ============================================

async def require_admin_knowledge(
    user: UserInfo = Depends(require_auth),
) -> UserInfo:
    """
    지식 관리(Knowledge) 권한 필수 의존성

    admin_knowledge 이상의 역할이 필요합니다.
    (admin_knowledge, admin_system 허용)

    Raises:
        HTTPException: 권한 부족 시 403 Forbidden
    """
    user_level = ROLE_HIERARCHY.get(user.role, 0)
    required_level = ROLE_HIERARCHY[ROLE_ADMIN_KNOWLEDGE]

    if user_level < required_level:
        logger.warning(f"권한 부족: {user.username} (role={user.role}) → admin_knowledge 필요")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Knowledge management permission required. Role 'admin_knowledge' or higher is needed.",
        )

    return user


async def require_admin_system(
    user: UserInfo = Depends(require_auth),
) -> UserInfo:
    """
    시스템 관리(System) 권한 필수 의존성

    admin_system 역할이 필요합니다.

    Raises:
        HTTPException: 권한 부족 시 403 Forbidden
    """
    user_level = ROLE_HIERARCHY.get(user.role, 0)
    required_level = ROLE_HIERARCHY[ROLE_ADMIN_SYSTEM]

    if user_level < required_level:
        logger.warning(f"권한 부족: {user.username} (role={user.role}) → admin_system 필요")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System administration permission required. Role 'admin_system' is needed.",
        )

    return user


# ============================================
# 인증 제외 경로
# ============================================

# 인증이 필요 없는 경로 목록
AUTH_EXCLUDE_PATHS = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/token",
    "/api/auth/status",
    "/api/auth/me",
    # 웹 페이지 (HTML)
    "/login",
    "/dashboard",
    "/search",
    "/ask",
    "/logs",
    "/knowledge",
    "/reason",
]

# 인증 제외 경로 프리픽스
AUTH_EXCLUDE_PREFIXES = [
    "/static",
    "/document/",
    "/admin/",  # 개발 환경에서 편의를 위해 제외 (프로덕션에서는 제거 권장)
]


def is_auth_excluded(path: str) -> bool:
    """
    인증 제외 경로인지 확인

    Args:
        path: 요청 경로

    Returns:
        인증 제외 여부
    """
    # 정확히 일치하는 경로
    if path in AUTH_EXCLUDE_PATHS:
        return True

    # 프리픽스로 시작하는 경로
    for prefix in AUTH_EXCLUDE_PREFIXES:
        if path.startswith(prefix):
            return True

    return False
