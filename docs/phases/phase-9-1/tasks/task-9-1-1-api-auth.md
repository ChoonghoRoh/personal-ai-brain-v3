# Task 9-1-1: API 인증 시스템 구축

**우선순위**: 2 (Phase 9-1 내 두 번째)
**예상 작업량**: 2일
**의존성**: Task 9-1-2 (환경변수 관리) 완료 후 진행
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
API Key 또는 JWT 기반 인증 시스템을 구축하여 무단 API 접근 차단

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| API 인증 | 없음 (모든 요청 허용) | JWT 또는 API Key 인증 |
| 사용자 관리 | 없음 | 단일 사용자 (간단) 또는 다중 사용자 |
| 토큰 관리 | 없음 | 발급/갱신/폐기 |

### 1.3 인증 방식 비교

| 방식 | 장점 | 단점 | 권장 상황 |
|------|------|------|----------|
| **API Key** | 구현 간단, 상태 없음 | 만료 관리 어려움 | 단일 사용자, 내부 시스템 |
| **JWT** | 상태 없음, 정보 포함 | 토큰 크기, 무효화 어려움 | 다중 사용자, 모바일 |
| **Session** | 서버 제어 용이 | 상태 저장 필요 | 전통적 웹 앱 |

**권장**: 현재 프로젝트는 개인용이므로 **JWT (간단 버전)** 또는 **API Key** 권장

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/middleware/auth.py` | 인증 미들웨어/의존성 | 1 |
| `backend/routers/auth/__init__.py` | 인증 라우터 패키지 | 2 |
| `backend/routers/auth/auth.py` | 인증 API 엔드포인트 | 2 |
| `backend/schemas/auth.py` | 인증 관련 Pydantic 모델 | 3 |
| `tests/test_auth.py` | 인증 테스트 | 4 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/main.py` | 인증 미들웨어/라우터 등록 | 높음 |
| `backend/config.py` | JWT 설정 참조 (9-1-2에서 추가) | 낮음 |
| 기존 라우터들 | 인증 의존성 추가 | 중간 |

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: Pydantic 스키마 정의 (0.2일)

#### 1-1. auth.py 스키마
```python
# backend/schemas/auth.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TokenRequest(BaseModel):
    """로그인 요청"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    """토큰 발급 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="만료까지 남은 초")

class TokenRefreshRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str

class TokenPayload(BaseModel):
    """JWT 페이로드 (내부용)"""
    sub: str = Field(description="사용자 식별자")
    exp: datetime = Field(description="만료 시간")
    iat: datetime = Field(description="발급 시간")
    type: str = Field(default="access", description="토큰 타입")

class UserInfo(BaseModel):
    """현재 사용자 정보"""
    username: str
    is_admin: bool = False

class AuthError(BaseModel):
    """인증 에러 응답"""
    detail: str
    error_code: str
```

---

### Step 2: 인증 미들웨어/의존성 구현 (0.5일)

#### 2-1. auth.py 미들웨어
```python
# backend/middleware/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import logging

from backend.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
    API_SECRET_KEY,
    ENVIRONMENT
)
from backend.schemas.auth import TokenPayload, UserInfo

logger = logging.getLogger(__name__)

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# ============================================
# 토큰 생성/검증 함수
# ============================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        subject: 사용자 식별자 (username)
        expires_delta: 만료 시간 (기본값: JWT_EXPIRE_MINUTES)

    Returns:
        JWT 토큰 문자열
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[TokenPayload]:
    """
    JWT 토큰 검증

    Args:
        token: JWT 토큰 문자열

    Returns:
        TokenPayload 또는 None (검증 실패 시)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def verify_api_key(api_key: str) -> bool:
    """
    API Key 검증

    Args:
        api_key: 요청에서 받은 API Key

    Returns:
        유효 여부
    """
    if not API_SECRET_KEY:
        return False
    return api_key == API_SECRET_KEY


# ============================================
# 의존성 함수 (Dependency)
# ============================================

async def get_current_user(
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> UserInfo:
    """
    현재 인증된 사용자 가져오기 (의존성)

    JWT Bearer 토큰 또는 API Key 중 하나로 인증

    Raises:
        HTTPException: 인증 실패 시 401
    """
    # 개발 환경에서 인증 건너뛰기 (선택적)
    if ENVIRONMENT == "development" and not bearer_credentials and not api_key:
        # 개발 환경에서 인증 없이 접근 허용 (선택)
        # return UserInfo(username="dev_user", is_admin=True)
        pass  # 아래로 진행하여 인증 요구

    # 1. JWT Bearer 토큰 확인
    if bearer_credentials:
        token = bearer_credentials.credentials
        payload = verify_token(token)
        if payload:
            return UserInfo(username=payload.sub, is_admin=True)

    # 2. API Key 확인
    if api_key:
        if verify_api_key(api_key):
            return UserInfo(username="api_user", is_admin=True)

    # 인증 실패
    logger.warning("Authentication failed: No valid credentials")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_optional(
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[UserInfo]:
    """
    현재 사용자 (선택적) - 인증 없어도 None 반환

    공개 API에서 인증된 경우 추가 기능 제공 시 사용
    """
    try:
        return await get_current_user(bearer_credentials, api_key)
    except HTTPException:
        return None


# ============================================
# 인증 제외 경로 설정
# ============================================

# 인증이 필요하지 않은 경로 목록
PUBLIC_PATHS = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/token",
]

def is_public_path(path: str) -> bool:
    """인증이 필요하지 않은 경로인지 확인"""
    return any(path.startswith(p) for p in PUBLIC_PATHS)
```

---

### Step 3: 인증 라우터 구현 (0.5일)

#### 3-1. auth.py 라우터
```python
# backend/routers/auth/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
import hashlib
import logging

from backend.config import JWT_EXPIRE_MINUTES, ENVIRONMENT
from backend.schemas.auth import (
    TokenRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserInfo
)
from backend.middleware.auth import (
    create_access_token,
    get_current_user
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ============================================
# 간단한 사용자 저장소 (개인용)
# 실제 프로덕션에서는 DB 사용 권장
# ============================================

# 환경변수에서 로드하거나 기본값 사용
import os
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

def hash_password(password: str) -> str:
    """비밀번호 해시 (SHA256 + salt)"""
    # 실제 프로덕션에서는 bcrypt 권장
    salt = "personal_ai_brain_salt"  # 환경변수로 관리 권장
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed


# ============================================
# API 엔드포인트
# ============================================

@router.post("/login", response_model=TokenResponse)
@router.post("/token", response_model=TokenResponse)  # OAuth2 호환
async def login(request: TokenRequest):
    """
    로그인하여 액세스 토큰 발급

    - **username**: 사용자 이름
    - **password**: 비밀번호
    """
    # 사용자 검증
    if request.username != ADMIN_USERNAME:
        logger.warning(f"Login failed: Unknown user '{request.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # 비밀번호 검증
    if ADMIN_PASSWORD_HASH:
        if not verify_password(request.password, ADMIN_PASSWORD_HASH):
            logger.warning(f"Login failed: Wrong password for '{request.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
    else:
        # 개발 환경: 비밀번호 해시 미설정 시 기본 비밀번호 허용
        if ENVIRONMENT != "development" or request.password != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

    # 토큰 발급
    access_token = create_access_token(subject=request.username)

    logger.info(f"Login successful: '{request.username}'")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    토큰 갱신

    현재 유효한 토큰으로 새 토큰 발급
    """
    # 새 토큰 발급
    access_token = create_access_token(subject=current_user.username)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(current_user: UserInfo = Depends(get_current_user)):
    """
    로그아웃

    JWT는 상태가 없으므로 클라이언트에서 토큰 삭제 필요
    서버에서는 토큰 블랙리스트 관리 가능 (선택)
    """
    logger.info(f"Logout: '{current_user.username}'")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user


@router.get("/verify")
async def verify_auth(current_user: UserInfo = Depends(get_current_user)):
    """
    인증 상태 확인

    토큰이 유효한지 간단히 확인하는 엔드포인트
    """
    return {"valid": True, "username": current_user.username}
```

#### 3-2. __init__.py
```python
# backend/routers/auth/__init__.py

from .auth import router

__all__ = ["router"]
```

---

### Step 4: 기존 라우터에 인증 적용 (0.5일)

#### 4-1. 인증 적용 방법
```python
# 방법 1: 개별 엔드포인트에 의존성 추가
from backend.middleware.auth import get_current_user

@router.post("/api/ai/ask")
async def ask(
    request: AskRequest,
    current_user: UserInfo = Depends(get_current_user)  # 추가
):
    ...

# 방법 2: 라우터 전체에 의존성 추가
router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
    dependencies=[Depends(get_current_user)]  # 전체 적용
)

# 방법 3: main.py에서 미들웨어로 적용 (권장하지 않음)
```

#### 4-2. 인증 적용 대상 라우터

| 라우터 | 경로 | 인증 필요 | 비고 |
|--------|------|----------|------|
| AI | `/api/ai/*` | ✅ | LLM 사용 |
| Knowledge | `/api/knowledge/*` | ✅ | 데이터 CRUD |
| Reasoning | `/api/reason/*` | ✅ | LLM 사용 |
| Search | `/api/search/*` | ✅ | 검색 |
| Documents | `/api/documents/*` | ✅ | 문서 관리 |
| System | `/api/system/*` | ✅ | 시스템 관리 |
| Auth | `/api/auth/login` | ❌ | 로그인 |
| Health | `/health` | ❌ | 상태 확인 |

---

### Step 5: main.py 수정 (0.2일)

#### 5-1. 라우터 등록
```python
# backend/main.py

from fastapi import FastAPI
from backend.routers.auth import router as auth_router

app = FastAPI(
    title="Personal AI Brain API",
    description="지식 관리 및 AI 추론 시스템",
    version="1.0.0"
)

# 인증 라우터 등록 (공개)
app.include_router(auth_router)

# 기존 라우터들...
```

---

### Step 6: 테스트 (0.3일)

#### 6-1. 테스트 케이스
```python
# tests/test_auth.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestAuthentication:
    """인증 테스트"""

    def test_login_success(self):
        """올바른 자격증명으로 로그인 성공"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin"  # 개발 환경
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """잘못된 비밀번호로 로그인 실패"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrong"
        })
        assert response.status_code == 401

    def test_login_unknown_user(self):
        """존재하지 않는 사용자로 로그인 실패"""
        response = client.post("/api/auth/login", json={
            "username": "unknown",
            "password": "any"
        })
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self):
        """토큰 없이 보호된 엔드포인트 접근 실패"""
        response = client.get("/api/ai/models")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self):
        """토큰으로 보호된 엔드포인트 접근 성공"""
        # 로그인
        login_response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        token = login_response.json()["access_token"]

        # 보호된 엔드포인트 접근
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_expired_token(self):
        """만료된 토큰으로 접근 실패"""
        # 만료된 토큰 생성 (테스트용)
        pass

    def test_invalid_token(self):
        """유효하지 않은 토큰으로 접근 실패"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_api_key_auth(self):
        """API Key로 인증 성공"""
        # API_SECRET_KEY 설정 필요
        pass
```

---

## 4. API 엔드포인트 상세 스펙

### 4.1 POST /api/auth/login
**용도**: 로그인하여 액세스 토큰 발급

**Request**
```json
{
    "username": "admin",
    "password": "your_password"
}
```

**Response 200**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

**Response 401**
```json
{
    "detail": "Incorrect username or password"
}
```

---

### 4.2 GET /api/auth/me
**용도**: 현재 사용자 정보 조회

**Headers**
```
Authorization: Bearer {access_token}
```

**Response 200**
```json
{
    "username": "admin",
    "is_admin": true
}
```

---

### 4.3 POST /api/auth/logout
**용도**: 로그아웃

**Headers**
```
Authorization: Bearer {access_token}
```

**Response 200**
```json
{
    "message": "Successfully logged out"
}
```

---

## 5. 개발 주의사항

### 5.1 보안 체크리스트

- [ ] JWT 시크릿 키 환경변수로 관리
- [ ] 비밀번호 평문 저장 금지 (해시 사용)
- [ ] 토큰 만료 시간 적절히 설정 (30분 권장)
- [ ] 민감한 정보 토큰에 포함 금지
- [ ] HTTPS 사용 (프로덕션)
- [ ] 로그인 실패 로깅

### 5.2 품질 기준

| 항목 | 기준 |
|------|------|
| 단위 테스트 | 100% 통과 |
| 인증 실패 | 401 응답 |
| 토큰 만료 | 401 응답 + 명확한 메시지 |
| 공개 경로 | 인증 없이 접근 가능 |

---

## 6. 참고 자료

### 라이브러리
- python-jose: https://github.com/mpdavis/python-jose
- passlib: https://passlib.readthedocs.io/ (bcrypt 해시 권장)
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

### 관련 파일
- `backend/config.py` - JWT 설정
- `backend/main.py` - 라우터 등록
- `backend/middleware/auth.py` - 인증 로직
