# Task 9-1-2: 환경변수 비밀번호 관리

**우선순위**: 1 (Phase 9-1 내 최우선, 기반 작업)
**예상 작업량**: 0.5일
**의존성**: 없음
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
하드코딩된 비밀번호 및 민감 정보를 환경변수로 이동하여 보안 강화

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| DB 비밀번호 | config.py 또는 docker-compose.yml | 환경변수 (.env) |
| API 키 | 코드 내 하드코딩 가능성 | 환경변수 |
| 시크릿 키 | 없음 또는 하드코딩 | 환경변수 (JWT용) |

### 1.3 보안 위험
```
현재 위험:
1. 코드에 비밀번호 노출 → Git 이력에 남음
2. 환경별 설정 분리 어려움
3. 비밀번호 변경 시 코드 수정 필요
```

---

## 2. 파일 변경 계획

### 2.1 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/config.py` | 환경변수 로딩 추가/수정 | 높음 |
| `.env.example` | 환경변수 항목 추가 | 낮음 |
| `docker-compose.yml` | 환경변수 전달 확인 | 중간 |
| `README.md` | 환경 설정 가이드 추가 | 낮음 |

### 2.2 신규 생성 파일
- 없음 (기존 파일 수정)

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: 현재 하드코딩된 비밀번호 식별 (0.1일)

#### 1-1. 검색 대상 파일
```bash
# 검색 명령어 예시
grep -r "password" backend/
grep -r "secret" backend/
grep -r "api_key" backend/
grep -r "POSTGRES" backend/
```

#### 1-2. 확인할 항목

| 항목 | 파일 위치 (예상) | 변수명 |
|------|-----------------|--------|
| PostgreSQL 비밀번호 | config.py, docker-compose.yml | POSTGRES_PASSWORD |
| PostgreSQL 사용자 | config.py, docker-compose.yml | POSTGRES_USER |
| PostgreSQL DB명 | config.py, docker-compose.yml | POSTGRES_DB |
| Qdrant API Key | config.py | QDRANT_API_KEY (있는 경우) |
| Ollama URL | config.py | OLLAMA_BASE_URL |
| JWT 시크릿 | 없음 (신규) | JWT_SECRET_KEY |
| API 키 | 없음 (신규) | API_SECRET_KEY |

---

### Step 2: .env.example 업데이트 (0.1일)

#### 2-1. 추가할 환경변수
```bash
# .env.example

# ============================================
# Database Configuration
# ============================================
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=personal_ai_brain

# ============================================
# Qdrant Configuration
# ============================================
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=           # 선택: Qdrant API 키 (설정한 경우)

# ============================================
# Ollama Configuration
# ============================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=eeve-korean:latest

# ============================================
# Security Configuration (Phase 9-1)
# ============================================
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

API_SECRET_KEY=your_api_secret_key_for_simple_auth

# ============================================
# Application Configuration
# ============================================
DEBUG=false
ENVIRONMENT=development    # development | production
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# ============================================
# Rate Limiting (Phase 9-1)
# ============================================
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_LLM_PER_MINUTE=10
```

---

### Step 3: config.py 수정 (0.2일)

#### 3-1. 환경변수 로딩 구조
```python
# backend/config.py

import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    환경변수를 안전하게 가져오는 헬퍼 함수

    Args:
        key: 환경변수 키
        default: 기본값
        required: 필수 여부 (True이고 없으면 에러)

    Returns:
        환경변수 값

    Raises:
        ValueError: required=True이고 환경변수가 없을 때
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value

def get_env_int(key: str, default: int) -> int:
    """정수형 환경변수 가져오기"""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def get_env_bool(key: str, default: bool = False) -> bool:
    """불리언 환경변수 가져오기"""
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes"):
        return True
    elif value in ("false", "0", "no"):
        return False
    return default

# ============================================
# Database Configuration
# ============================================
POSTGRES_HOST = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT = get_env_int("POSTGRES_PORT", 5432)
POSTGRES_USER = get_env("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", required=True)  # 필수
POSTGRES_DB = get_env("POSTGRES_DB", "personal_ai_brain")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============================================
# Qdrant Configuration
# ============================================
QDRANT_HOST = get_env("QDRANT_HOST", "localhost")
QDRANT_PORT = get_env_int("QDRANT_PORT", 6333)
QDRANT_API_KEY = get_env("QDRANT_API_KEY")  # 선택

# ============================================
# Ollama Configuration
# ============================================
OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "eeve-korean:latest")

# ============================================
# Security Configuration
# ============================================
JWT_SECRET_KEY = get_env("JWT_SECRET_KEY", required=True)  # 필수
JWT_ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = get_env_int("JWT_EXPIRE_MINUTES", 30)

API_SECRET_KEY = get_env("API_SECRET_KEY")  # 선택 (간단한 API 키 인증용)

# ============================================
# Application Configuration
# ============================================
DEBUG = get_env_bool("DEBUG", False)
ENVIRONMENT = get_env("ENVIRONMENT", "development")
CORS_ORIGINS = get_env("CORS_ORIGINS", "http://localhost:3000").split(",")

# ============================================
# Rate Limiting
# ============================================
RATE_LIMIT_PER_MINUTE = get_env_int("RATE_LIMIT_PER_MINUTE", 60)
RATE_LIMIT_LLM_PER_MINUTE = get_env_int("RATE_LIMIT_LLM_PER_MINUTE", 10)

# ============================================
# 기존 설정 유지 (RAG 관련 등)
# ============================================
# ... 기존 설정들 ...
```

---

### Step 4: docker-compose.yml 확인 및 수정 (0.05일)

#### 4-1. 환경변수 전달 확인
```yaml
# docker-compose.yml

services:
  backend:
    build: ./backend
    env_file:
      - .env    # .env 파일에서 환경변수 로드
    environment:
      # 또는 직접 지정 (docker-compose에서 오버라이드)
      - POSTGRES_HOST=postgres
      - QDRANT_HOST=qdrant
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - qdrant
      - ollama

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    # ...

  # ... 다른 서비스들 ...
```

---

### Step 5: 문서 업데이트 (0.05일)

#### 5-1. README.md에 환경 설정 가이드 추가
```markdown
## 환경 설정

### 1. 환경변수 파일 생성
\`\`\`bash
cp .env.example .env
\`\`\`

### 2. 필수 환경변수 설정
\`\`\`bash
# .env 파일 편집
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_super_secret_jwt_key
\`\`\`

### 3. JWT 시크릿 키 생성 (권장)
\`\`\`bash
# Python으로 랜덤 키 생성
python -c "import secrets; print(secrets.token_hex(32))"
\`\`\`

### 4. 환경별 설정
- 개발 환경: `ENVIRONMENT=development`, `DEBUG=true`
- 프로덕션: `ENVIRONMENT=production`, `DEBUG=false`
```

---

## 4. Pydantic 설정 모델 (선택)

### 4.1 Settings 클래스 활용 (권장)
```python
# backend/config.py (Pydantic 방식)

from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str
    postgres_db: str = "personal_ai_brain"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "eeve-korean:latest"

    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    api_secret_key: Optional[str] = None

    # Application
    debug: bool = False
    environment: str = "development"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_llm_per_minute: int = 10

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 싱글톤 인스턴스
settings = Settings()
```

---

## 5. 개발 주의사항

### 5.1 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] 커밋 전 코드에 비밀번호 하드코딩 없는지 확인
- [ ] `.env.example`에는 실제 값 대신 예시만 포함
- [ ] 프로덕션 비밀번호는 별도 안전한 곳에 보관

### 5.2 품질 기준

| 항목 | 기준 |
|------|------|
| 하드코딩 비밀번호 | 코드 내 0건 |
| 환경변수 검증 | 필수 항목 누락 시 시작 실패 |
| 문서화 | .env.example에 모든 항목 설명 |

### 5.3 테스트 케이스

```python
# tests/test_config.py

def test_required_env_vars():
    """필수 환경변수 누락 시 에러"""
    # JWT_SECRET_KEY 없이 시작 시도 → ValueError
    pass

def test_database_url_construction():
    """DATABASE_URL 올바르게 구성되는지"""
    pass

def test_env_type_conversion():
    """환경변수 타입 변환 (int, bool)"""
    pass
```

---

## 6. 참고 자료

### 관련 파일
- `backend/config.py` - 현재 설정 파일
- `.env.example` - 환경변수 예시
- `docker-compose.yml` - Docker 설정

### 라이브러리
- python-dotenv: https://github.com/theskumar/python-dotenv
- pydantic-settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

### 보안 가이드
- OWASP Secrets Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
