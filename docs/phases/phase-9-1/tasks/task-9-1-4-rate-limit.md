# Task 9-1-4: Rate Limiting

**우선순위**: 4 (Phase 9-1 내 네 번째)
**예상 작업량**: 1일
**의존성**: 없음 (9-1-1과 병렬 진행 가능)
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
API 남용 방지를 위한 요청 제한 (Rate Limiting) 구현

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| Rate Limiting | 없음 | API별 요청 제한 |
| LLM API 제한 | 없음 | 별도 엄격한 제한 |
| 제한 초과 응답 | N/A | 429 Too Many Requests |

### 1.3 Rate Limiting 필요성
```
보호 대상:
1. LLM API - 리소스 집약적, 비용 발생 가능
2. 검색 API - DB/벡터 DB 부하
3. Import API - 대용량 처리
4. 전체 API - DoS 방지
```

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/middleware/rate_limit.py` | Rate Limiting 미들웨어 | 1 |
| `tests/test_rate_limit.py` | Rate Limit 테스트 | 2 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/main.py` | Rate Limit 미들웨어 등록 | 높음 |
| `backend/config.py` | Rate Limit 설정 (9-1-2에서 추가) | 낮음 |
| `requirements.txt` | slowapi 라이브러리 추가 | 낮음 |

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: Rate Limit 정책 설계 (0.1일)

#### 1-1. API별 제한 정책

| API 그룹 | 제한 | 윈도우 | 사유 |
|----------|------|--------|------|
| **일반 API** | 60회 | 분당 | 일반 사용 |
| **LLM API** (/api/ai, /api/reason) | 10회 | 분당 | 리소스 집약적 |
| **검색 API** | 30회 | 분당 | DB 부하 |
| **Import API** | 5회 | 분당 | 대용량 처리 |
| **인증 API** (로그인) | 5회 | 분당 | 브루트포스 방지 |

#### 1-2. 환경변수 설정
```bash
# .env.example

# ============================================
# Rate Limiting Configuration
# ============================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60           # 일반 API
RATE_LIMIT_LLM_PER_MINUTE=10       # LLM API
RATE_LIMIT_SEARCH_PER_MINUTE=30    # 검색 API
RATE_LIMIT_IMPORT_PER_MINUTE=5     # Import API
RATE_LIMIT_AUTH_PER_MINUTE=5       # 인증 API

# Redis 사용 시 (분산 환경)
# REDIS_URL=redis://localhost:6379
```

#### 1-3. config.py 추가
```python
# backend/config.py

# Rate Limiting
RATE_LIMIT_ENABLED = get_env_bool("RATE_LIMIT_ENABLED", True)
RATE_LIMIT_PER_MINUTE = get_env_int("RATE_LIMIT_PER_MINUTE", 60)
RATE_LIMIT_LLM_PER_MINUTE = get_env_int("RATE_LIMIT_LLM_PER_MINUTE", 10)
RATE_LIMIT_SEARCH_PER_MINUTE = get_env_int("RATE_LIMIT_SEARCH_PER_MINUTE", 30)
RATE_LIMIT_IMPORT_PER_MINUTE = get_env_int("RATE_LIMIT_IMPORT_PER_MINUTE", 5)
RATE_LIMIT_AUTH_PER_MINUTE = get_env_int("RATE_LIMIT_AUTH_PER_MINUTE", 5)

# Redis (선택)
REDIS_URL = get_env("REDIS_URL")
```

---

### Step 2: Rate Limiting 미들웨어 구현 (0.5일)

#### 2-1. slowapi 사용 방식 (권장)
```python
# backend/middleware/rate_limit.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request, Response
from typing import Callable, Optional
import logging

from backend.config import (
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_PER_MINUTE,
    RATE_LIMIT_LLM_PER_MINUTE,
    RATE_LIMIT_SEARCH_PER_MINUTE,
    RATE_LIMIT_IMPORT_PER_MINUTE,
    RATE_LIMIT_AUTH_PER_MINUTE,
    REDIS_URL
)

logger = logging.getLogger(__name__)

# ============================================
# Limiter 설정
# ============================================

def get_key_func(request: Request) -> str:
    """
    Rate Limit 키 생성 함수

    인증된 사용자는 사용자 ID로, 아니면 IP로 구분
    """
    # 인증된 사용자 확인
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.username}"

    # IP 기반
    return get_remote_address(request)


# Redis 사용 시 분산 환경 지원
if REDIS_URL:
    from slowapi.middleware import SlowAPIASGIMiddleware
    storage_uri = REDIS_URL
else:
    storage_uri = None  # 인메모리 (단일 인스턴스)

limiter = Limiter(
    key_func=get_key_func,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=storage_uri,
    enabled=RATE_LIMIT_ENABLED
)

# ============================================
# 커스텀 Rate Limit 데코레이터
# ============================================

def limit_llm():
    """LLM API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_LLM_PER_MINUTE}/minute")

def limit_search():
    """검색 API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_SEARCH_PER_MINUTE}/minute")

def limit_import():
    """Import API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_IMPORT_PER_MINUTE}/minute")

def limit_auth():
    """인증 API용 Rate Limit 데코레이터"""
    return limiter.limit(f"{RATE_LIMIT_AUTH_PER_MINUTE}/minute")

# ============================================
# 에러 핸들러
# ============================================

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Rate Limit 초과 시 응답

    429 Too Many Requests + Retry-After 헤더
    """
    response = Response(
        content='{"detail": "Rate limit exceeded. Please try again later."}',
        status_code=429,
        media_type="application/json"
    )

    # Retry-After 헤더 (초 단위)
    response.headers["Retry-After"] = str(60)  # 1분 후 재시도
    response.headers["X-RateLimit-Limit"] = str(exc.detail)

    logger.warning(f"Rate limit exceeded: {get_key_func(request)}")

    return response

# ============================================
# FastAPI 앱에 적용
# ============================================

def setup_rate_limiting(app: FastAPI):
    """Rate Limiting 설정 적용"""

    if not RATE_LIMIT_ENABLED:
        logger.info("Rate limiting is disabled")
        return

    # Limiter를 앱 상태에 저장
    app.state.limiter = limiter

    # 에러 핸들러 등록
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # 미들웨어 추가
    app.add_middleware(SlowAPIMiddleware)

    logger.info(f"Rate limiting enabled: {RATE_LIMIT_PER_MINUTE}/min (default)")
```

---

### Step 3: 라우터에 Rate Limit 적용 (0.2일)

#### 3-1. AI 라우터 (LLM 제한)
```python
# backend/routers/ai/ai.py

from backend.middleware.rate_limit import limiter, limit_llm

router = APIRouter(prefix="/api/ai", tags=["AI"])

@router.post("/ask")
@limit_llm()  # LLM API 제한
async def ask(request: Request, body: AskRequest):
    ...
```

#### 3-2. Reasoning 라우터 (LLM 제한)
```python
# backend/routers/reasoning/reason.py

from backend.middleware.rate_limit import limiter, limit_llm

@router.post("/api/reason")
@limit_llm()  # LLM API 제한
async def reason(request: Request, body: ReasonRequest):
    ...
```

#### 3-3. 검색 라우터
```python
# backend/routers/search/search.py

from backend.middleware.rate_limit import limiter, limit_search

@router.post("/api/search")
@limit_search()  # 검색 API 제한
async def search(request: Request, body: SearchRequest):
    ...
```

#### 3-4. 인증 라우터 (브루트포스 방지)
```python
# backend/routers/auth/auth.py

from backend.middleware.rate_limit import limiter, limit_auth

@router.post("/login")
@limit_auth()  # 로그인 API 제한
async def login(request: Request, body: TokenRequest):
    ...
```

---

### Step 4: main.py 수정 (0.1일)

#### 4-1. Rate Limiting 적용
```python
# backend/main.py

from fastapi import FastAPI
from backend.middleware.rate_limit import setup_rate_limiting, limiter

app = FastAPI(
    title="Personal AI Brain API",
    description="지식 관리 및 AI 추론 시스템",
    version="1.0.0"
)

# Rate Limiting 설정
setup_rate_limiting(app)

# 또는 직접 설정
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

---

### Step 5: 테스트 (0.1일)

#### 5-1. 테스트 케이스
```python
# tests/test_rate_limit.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

client = TestClient(app)

class TestRateLimiting:
    """Rate Limiting 테스트"""

    def test_rate_limit_exceeded(self):
        """제한 초과 시 429 응답"""
        # 제한보다 많은 요청 전송
        for i in range(65):  # 60회 제한 + 5회 초과
            response = client.get("/health")

        # 마지막 요청은 429
        response = client.get("/health")
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_rate_limit_llm_api(self):
        """LLM API 별도 제한"""
        # LLM API는 10회 제한
        for i in range(12):
            response = client.post("/api/ai/ask", json={"question": "test"})

        assert response.status_code == 429

    def test_rate_limit_reset(self):
        """제한 리셋 (1분 후)"""
        # 제한 초과
        for i in range(65):
            client.get("/health")

        # 1분 대기 (테스트 환경에서는 모킹)
        # time.sleep(60)

        # 다시 요청 가능
        # response = client.get("/health")
        # assert response.status_code == 200
        pass

    def test_rate_limit_by_user(self):
        """사용자별 별도 제한"""
        # 사용자 A
        response_a = client.get(
            "/health",
            headers={"X-Forwarded-For": "1.1.1.1"}
        )

        # 사용자 B는 별도 카운트
        response_b = client.get(
            "/health",
            headers={"X-Forwarded-For": "2.2.2.2"}
        )

        # 둘 다 성공
        assert response_a.status_code == 200
        assert response_b.status_code == 200

    def test_rate_limit_headers(self):
        """응답 헤더에 제한 정보 포함"""
        response = client.get("/health")
        # X-RateLimit-Limit, X-RateLimit-Remaining 등
        pass
```

---

## 4. API 응답 형식

### 4.1 정상 응답 (Rate Limit 헤더)
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1706918400
```

### 4.2 Rate Limit 초과 응답
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706918400
Content-Type: application/json

{
    "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 5. Pydantic 모델

### 5.1 응답 모델
```python
# backend/schemas/rate_limit.py

from pydantic import BaseModel, Field

class RateLimitError(BaseModel):
    """Rate Limit 초과 에러"""
    detail: str = Field(default="Rate limit exceeded")
    retry_after: int = Field(description="재시도까지 남은 초")

class RateLimitInfo(BaseModel):
    """Rate Limit 정보 (디버깅용)"""
    limit: int = Field(description="분당 최대 요청 수")
    remaining: int = Field(description="남은 요청 수")
    reset: int = Field(description="리셋 시간 (Unix timestamp)")
```

---

## 6. 개발 주의사항

### 6.1 구현 체크리스트

- [ ] slowapi 라이브러리 설치
- [ ] API별 적절한 제한 설정
- [ ] 429 응답에 Retry-After 헤더 포함
- [ ] 사용자/IP별 별도 카운트
- [ ] 분산 환경 시 Redis 사용

### 6.2 품질 기준

| 항목 | 기준 |
|------|------|
| 제한 초과 | 429 응답 |
| Retry-After | 헤더 포함 |
| 사용자 구분 | IP 또는 인증 토큰 |
| LLM API | 일반보다 엄격한 제한 |

### 6.3 성능 고려사항

```python
# 인메모리 vs Redis
# - 단일 인스턴스: 인메모리 (기본)
# - 다중 인스턴스: Redis 필수

# Redis 사용 시 requirements.txt
# redis>=4.0.0
```

---

## 7. 참고 자료

### 라이브러리
- slowapi: https://github.com/laurentS/slowapi
- Redis: https://redis.io/

### FastAPI Rate Limiting
- https://fastapi.tiangolo.com/advanced/middleware/

### 관련 파일
- `backend/middleware/rate_limit.py` - Rate Limit 로직
- `backend/config.py` - 설정값
- `backend/main.py` - 미들웨어 등록

### requirements.txt 추가
```
slowapi>=0.1.9
redis>=4.0.0  # 분산 환경 시
```
