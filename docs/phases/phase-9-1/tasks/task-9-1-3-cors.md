# Task 9-1-3: CORS 설정

**우선순위**: 3 (Phase 9-1 내 세 번째)
**예상 작업량**: 0.5일
**의존성**: 없음 (9-1-1과 병렬 진행 가능)
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
프로덕션 배포를 위한 CORS(Cross-Origin Resource Sharing) 정책 설정

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| CORS 설정 | 전체 허용 또는 기본값 | 환경별 분리 |
| 허용 오리진 | `*` (모두 허용) | 특정 도메인만 |
| 크레덴셜 | 미설정 | 필요시 허용 |

### 1.3 CORS란?
```
브라우저 보안 정책으로, 다른 오리진(도메인)에서의 요청을 제한
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8001
→ 다른 오리진이므로 CORS 설정 필요
```

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/middleware/cors.py` | CORS 설정 모듈 (선택) | 1 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/main.py` | CORS 미들웨어 설정 | 높음 |
| `backend/config.py` | CORS 관련 환경변수 (9-1-2에서 추가) | 낮음 |

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: CORS 정책 설계 (0.1일)

#### 1-1. 환경별 CORS 정책

| 환경 | 허용 오리진 | 크레덴셜 | 메서드 |
|------|-----------|---------|--------|
| **개발** | `*` 또는 localhost 목록 | 허용 | 전체 |
| **프로덕션** | 특정 도메인만 | 허용 | 전체 |

#### 1-2. 환경변수 설정 (config.py)
```python
# backend/config.py (9-1-2에서 추가됨)

# CORS 설정
CORS_ORIGINS = get_env("CORS_ORIGINS", "http://localhost:3000").split(",")
CORS_ALLOW_CREDENTIALS = get_env_bool("CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOW_METHODS = get_env("CORS_ALLOW_METHODS", "*").split(",")
CORS_ALLOW_HEADERS = get_env("CORS_ALLOW_HEADERS", "*").split(",")
```

#### 1-3. .env.example 추가
```bash
# .env.example

# ============================================
# CORS Configuration
# ============================================
# 개발 환경
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

# 프로덕션 환경 예시
# CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

---

### Step 2: CORS 미들웨어 설정 (0.2일)

#### 2-1. main.py에 CORS 설정
```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import (
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    ENVIRONMENT
)

app = FastAPI(
    title="Personal AI Brain API",
    description="지식 관리 및 AI 추론 시스템",
    version="1.0.0"
)

# ============================================
# CORS 미들웨어 설정
# ============================================

def setup_cors(app: FastAPI):
    """CORS 미들웨어 설정"""

    # 개발 환경에서 더 관대한 설정
    if ENVIRONMENT == "development":
        origins = ["*"]  # 또는 CORS_ORIGINS
        allow_credentials = False  # * 사용 시 credentials=False 필요
    else:
        origins = CORS_ORIGINS
        allow_credentials = CORS_ALLOW_CREDENTIALS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=CORS_ALLOW_METHODS if CORS_ALLOW_METHODS != ["*"] else ["*"],
        allow_headers=CORS_ALLOW_HEADERS if CORS_ALLOW_HEADERS != ["*"] else ["*"],
        expose_headers=["X-Request-ID"],  # 노출할 응답 헤더
        max_age=600,  # 프리플라이트 캐시 시간 (초)
    )

setup_cors(app)
```

#### 2-2. CORS 설정 모듈화 (선택)
```python
# backend/middleware/cors.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

logger = logging.getLogger(__name__)

class CORSConfig:
    """CORS 설정 관리"""

    def __init__(
        self,
        origins: List[str],
        allow_credentials: bool = True,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 600
    ):
        self.origins = origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.max_age = max_age

    def apply(self, app: FastAPI):
        """FastAPI 앱에 CORS 미들웨어 적용"""

        # * 사용 시 credentials 비활성화 필요
        if "*" in self.origins and self.allow_credentials:
            logger.warning(
                "CORS: Cannot use credentials with '*' origins. "
                "Disabling credentials."
            )
            self.allow_credentials = False

        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
            expose_headers=self.expose_headers,
            max_age=self.max_age,
        )

        logger.info(f"CORS configured: origins={self.origins}")


def get_cors_config(environment: str, origins: List[str]) -> CORSConfig:
    """환경별 CORS 설정 생성"""

    if environment == "development":
        return CORSConfig(
            origins=["*"],  # 개발 환경에서 모두 허용
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        return CORSConfig(
            origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
        )
```

---

### Step 3: 테스트 (0.2일)

#### 3-1. CORS 테스트 케이스
```python
# tests/test_cors.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestCORS:
    """CORS 설정 테스트"""

    def test_cors_preflight_request(self):
        """프리플라이트 요청 (OPTIONS) 처리"""
        response = client.options(
            "/api/ai/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            }
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_allowed_origin(self):
        """허용된 오리진에서 요청"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_disallowed_origin_production(self):
        """프로덕션에서 허용되지 않은 오리진 차단"""
        # 프로덕션 환경에서만 테스트
        # 환경 변수 모킹 필요
        pass

    def test_cors_credentials(self):
        """크레덴셜 허용 확인"""
        response = client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        # 개발 환경에서는 credentials 설정에 따라 다름
        pass

    def test_cors_exposed_headers(self):
        """노출 헤더 확인"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # expose_headers 설정 확인
        pass
```

#### 3-2. 수동 테스트 (브라우저)
```javascript
// 브라우저 콘솔에서 테스트
fetch('http://localhost:8001/health', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('CORS Error:', error));
```

---

## 4. CORS 설정 상세

### 4.1 주요 설정 항목

| 항목 | 설명 | 예시 |
|------|------|------|
| `allow_origins` | 허용할 오리진 목록 | `["http://localhost:3000"]` |
| `allow_credentials` | 쿠키/인증 정보 허용 | `True` |
| `allow_methods` | 허용할 HTTP 메서드 | `["GET", "POST", "PUT", "DELETE"]` |
| `allow_headers` | 허용할 요청 헤더 | `["*"]` 또는 명시적 목록 |
| `expose_headers` | 클라이언트에 노출할 응답 헤더 | `["X-Request-ID"]` |
| `max_age` | 프리플라이트 캐시 시간 (초) | `600` |

### 4.2 일반적인 CORS 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| No 'Access-Control-Allow-Origin' | 오리진 미허용 | origins에 추가 |
| Credentials not supported | `*`와 credentials 동시 사용 | 명시적 origins 또는 credentials=False |
| Method not allowed | 메서드 미허용 | methods에 추가 |
| Header not allowed | 헤더 미허용 | headers에 추가 |

---

## 5. 개발 주의사항

### 5.1 보안 체크리스트

- [ ] 프로덕션에서 `*` 사용 금지
- [ ] 허용 오리진 최소화
- [ ] 민감한 헤더 노출 주의
- [ ] 프리플라이트 캐시 적절히 설정

### 5.2 품질 기준

| 항목 | 기준 |
|------|------|
| 개발 환경 | localhost 요청 허용 |
| 프로덕션 | 지정 도메인만 허용 |
| 프리플라이트 | OPTIONS 요청 정상 처리 |

### 5.3 환경별 설정 예시

```bash
# 개발 환경 (.env)
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 프로덕션 환경 (.env)
ENVIRONMENT=production
CORS_ORIGINS=https://your-app.com,https://www.your-app.com
```

---

## 6. 참고 자료

### FastAPI CORS
- https://fastapi.tiangolo.com/tutorial/cors/

### MDN CORS
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

### 관련 파일
- `backend/main.py` - CORS 설정
- `backend/config.py` - 환경변수
