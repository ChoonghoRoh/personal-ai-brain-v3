# SSOT — 아키텍처

**버전**: 6.0-renewal-4th  
**최종 수정**: 2026-02-17  
**특징**: 단독 사용 (다른 SSOT 폴더 참조 불필요)

---

## 1. 인프라 구성

### 1.1 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                       Docker Compose                          │
│                      (pab-network)                            │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌────────────────┐  │
│  │PostgreSQL│  │  Qdrant  │  │ Redis │  │    Backend      │  │
│  │  :5433   │  │  :6343   │  │ :6380 │  │ (FastAPI) :8001 │  │
│  │          │  │          │  │       │  │                  │  │
│  │ 메타데이터│  │ 벡터 검색 │  │ 캐시  │  │ API+Static Files│  │
│  └──────────┘  └──────────┘  └───────┘  └────────────────┘  │
│                                               │               │
└───────────────────────────────────────────────┼───────────────┘
                                                │
                                    ┌───────────▼──────────┐
                                    │   Ollama (호스트)     │
                                    │   :11434              │
                                    │   host.docker.internal│
                                    └──────────────────────┘
```

**서빙 구조**: FastAPI가 정적 파일(`web/public/`)을 `/static` 경로로 서빙하고, HTML 템플릿(`web/src/pages/`)을 Jinja2로 렌더링하는 모놀리식 구조이다. 별도의 프론트엔드 빌드 프로세스는 없다.

**Base URL**: `http://localhost:8001` (ver3 고정)

---

### 1.2 컨테이너 사양

| 컨테이너 | 이미지 | 포트 (호스트:내부) | 볼륨 |
|----------|--------|-------------------|------|
| `pab-backend-ver3` | Dockerfile.backend (Python 3.12-slim) | 8001:8000 | `./:/app` (소스 마운트) |
| `pab-postgres-ver3` | postgres:15 | 5433:5432 | `postgres-data-ver3` |
| `qdrant-ver3` | qdrant/qdrant:latest | 6343:6333, 6344:6334 | `./qdrant-data-ver3` |
| `pab-redis-ver3` | redis:7-alpine | 6380:6379 | `redis-data-ver3` (AOF) |
| Ollama | ollama/ollama (호스트) | 11434 | — |

**ver3 전용 포트**:
- PostgreSQL: `5433` (ver2는 5432)
- Qdrant: `6343` (ver2는 6333)
- Redis: `6380` (ver2는 6379)
- Backend: `8001` (ver2는 8000)

**환경 격리**: ver2와 ver3가 동일 머신에서 독립 실행 가능하도록 포트와 볼륨명을 분리했다.

---

## 2. 백엔드 구조

### 2.1 기술 스택

| 항목 | 기준 |
|------|------|
| **언어** | Python 3.12 |
| **프레임워크** | FastAPI (async) |
| **ORM** | SQLAlchemy 2.0+ (ORM 필수, raw SQL 금지) |
| **DB** | PostgreSQL 15 |
| **벡터 검색** | Qdrant |
| **캐싱** | Redis (AOF 지속성) |
| **스키마 검증** | Pydantic v2 |
| **타입 체크** | mypy |
| **테스트** | pytest |

---

### 2.2 디렉토리 구조

```
backend/
├── main.py                      # FastAPI 앱 진입점 (정적 파일 마운트, 라우터 등록)
├── config.py                    # 환경변수 설정
│
├── models/                      # ORM 모델
│   ├── database.py              # SQLAlchemy 엔진, 세션
│   ├── models.py                # 핵심 ORM 모델
│   ├── admin_models.py          # Admin 설정 모델 (Phase 11) + PageAccessLog (Phase 13-4)
│   └── workflow_common.py       # 워크플로우 공통 모델
│
├── routers/                     # API 라우터 (도메인별)
│   ├── auth/auth.py
│   ├── search/{search,documents}.py
│   ├── ai/{ai,conversations}.py
│   ├── knowledge/{knowledge,labels,relations,approval,suggestions}.py
│   ├── reasoning/{reason,reason_stream,reason_store,reasoning_chain,reasoning_results,recommendations}.py
│   ├── cognitive/{memory,context,learning,personality,metacognition}.py
│   ├── system/{system,backup,integrity,logs,error_logs,statistics}.py
│   ├── automation/{automation,workflow}.py
│   ├── ingest/file_parser.py
│   └── admin/{schema_crud,template_crud,preset_crud,rag_profile_crud,policy_set_crud,audit_log_crud,page_access_log_crud}.py
│
├── services/                    # 비즈니스 로직 (도메인별)
│   ├── search/{search_service,hybrid_search,reranker,multi_hop_rag,document_sync_service}.py
│   ├── ai/{ollama_client,context_manager}.py
│   ├── knowledge/{auto_labeler,structure_matcher,knowledge_integration_service,transaction_manager,chunk_sync_service}.py
│   ├── reasoning/{dynamic_reasoning_service,reasoning_chain_service,recommendation_service}.py
│   ├── cognitive/{memory_service,context_service,learning_service,personality_service,metacognition_service,memory_scheduler}.py
│   ├── system/{system_service,integrity_service,logging_service,statistics_service}.py
│   └── ingest/{file_parser_service,hwp_parser}.py
│
├── middleware/                  # 미들웨어
│   ├── security.py              # 보안 헤더
│   ├── rate_limit.py            # Rate Limiting (slowapi, X-Forwarded-For)
│   ├── request_id.py            # Request ID 미들웨어 (UUID)
│   ├── error_handler.py         # 전역 에러 핸들러 (표준 JSON)
│   ├── page_access_log.py       # 페이지 접근 로그 (Phase 13-4)
│   └── auth.py                  # JWT/API Key 인증
│
└── utils/                       # 유틸리티
    ├── logger.py                # 로깅 설정
    ├── text_processing.py       # 텍스트 처리
    └── ...

tests/                           # 테스트 (pytest)
├── conftest.py                  # pytest 설정
├── test_*.py                    # 테스트 파일
└── integration/                 # 통합 테스트
```

---

### 2.3 백엔드 코드 작성 규칙

| 규칙 | 기준 | 예시 |
|------|------|------|
| **ORM 필수** | raw SQL 절대 금지 | `session.query(Document).filter(...)` (O), `session.execute("SELECT ...")` (X) |
| **타입 힌트 필수** | 모든 함수 시그니처 | `def get_doc(doc_id: int) -> Document:` |
| **Pydantic 검증** | 모든 API 입력 | `@app.post("/api/doc", response_model=DocResponse) def create(req: DocCreate):` |
| **에러 핸들링** | HTTPException | `raise HTTPException(status_code=404, detail="Not found")` |
| **네이밍** | snake_case | `document_service.py`, `def get_document_by_id():` |
| **비동기** | async/await 활용 | `async def get_doc(): await db.execute(...)` |
| **의존성 주입** | Depends 활용 | `def route(db: Session = Depends(get_db)):` |

**금지 사항**:
- raw SQL 쿼리
- 타입 힌트 생략
- 입력 검증 없이 사용자 입력 처리
- 에러 처리 없이 예외 방치

➜ [ROLES/backend-dev.md](ROLES/backend-dev.md)

---

## 3. 프론트엔드 구조

### 3.1 기술 스택

| 항목 | 기준 |
|------|------|
| **언어** | Vanilla JavaScript (ES2020+) |
| **모듈 시스템** | ESM (`<script type="module">`, `import`/`export`) |
| **UI 프레임워크** | Bootstrap 5 (로컬 배치) |
| **아이콘** | Bootstrap Icons (로컬 배치) |
| **템플릿** | Jinja2 (서버 사이드 렌더링) |
| **빌드 도구** | 없음 (빌드리스 구조) |
| **테스트** | Playwright (E2E) |

---

### 3.2 디렉토리 구조

(3rd와 동일한 web/ 구조 — 생략)

---

### 3.3 프론트엔드 코드 작성 규칙

| 규칙 | 기준 | 예시 |
|------|------|------|
| **ESM import/export** | `type="module"` 필수 | `<script type="module" src="/static/js/page.js">` |
| **외부 CDN 금지** | 모든 라이브러리 로컬 배치 | `web/public/libs/` 에 Bootstrap, axios 등 배치 |
| **XSS 방지** | innerHTML 시 esc() 필수 | `elem.innerHTML = esc(userInput)` (O), `elem.innerHTML = userInput` (X) |
| **window 전역 금지** | 새 함수 할당 금지 | `export function fn()` (O), `window.fn = function()` (X) |
| **컴포넌트 재사용** | `layout-component.js` 등 활용 | `import { initLayout } from '/static/js/components/layout-component.js'` |
| **네이밍** | camelCase (변수), kebab-case (파일명) | `myVariable`, `my-page.js` |
| **에러 핸들링** | try-catch + 사용자 메시지 | `try { await api() } catch(e) { alert('오류 발생') }` |

**금지 사항**:
- 외부 CDN 참조 (cdn.jsdelivr.net 등)
- innerHTML에 검증 없는 사용자 입력
- window 전역 객체에 함수 할당 (기존 레거시 제외)

➜ [ROLES/frontend-dev.md](ROLES/frontend-dev.md)

---

### 3.4 프론트엔드 파일 구조 규칙

**신규 페이지 추가 시** 반드시 아래 3개 파일을 함께 생성한다:

```
1. HTML 템플릿: web/src/pages/{페이지명}.html
2. JavaScript:   web/public/js/{페이지명}/{페이지명}.js
3. CSS:          web/public/css/{페이지명}.css
```

**HTML 템플릿 필수**: layout-component 포함, 페이지별 CSS/JS `type="module"` 링크.

---

## 4. 데이터베이스

### 4.1 PostgreSQL (메타데이터)

**용도**: 문서 메타데이터, 사용자 데이터, 설정, 로그 등. **ORM 필수**, raw SQL 금지.

### 4.2 Qdrant (벡터 검색)

**용도**: 문서 청크 벡터 임베딩 저장 및 의미 검색. 컬렉션: `document_chunks`.

### 4.3 Redis (캐싱)

**용도**: Rate Limiting, 검색 캐시, AI 작업 진행 등. AOF 지속성.

---

## 5. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| Backend Charter | Backend Developer 역할 | [PERSONA/BACKEND.md](PERSONA/BACKEND.md) |
| Frontend Charter | Frontend Developer 역할 | [PERSONA/FRONTEND.md](PERSONA/FRONTEND.md) |
| Backend 가이드 | Backend 전용 가이드 | [ROLES/backend-dev.md](ROLES/backend-dev.md) |
| Frontend 가이드 | Frontend 전용 가이드 | [ROLES/frontend-dev.md](ROLES/frontend-dev.md) |

---

**문서 관리**:
- 버전: 6.0-renewal-4th (4th iteration)
- 최종 수정: 2026-02-17
- 단독 사용: 본 iterations/4th 세트만으로 SSOT 완결
