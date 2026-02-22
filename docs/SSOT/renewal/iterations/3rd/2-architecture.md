# SSOT — 아키텍처 (요약)

**버전**: 5.0-renewal  
**최종 수정**: 2026-02-17  
**기반**: 2-architecture-ssot.md (v4.0, 516줄)

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
│  │  :5433   │  │  :6343   │  │ :6379 │  │ (FastAPI) :8001 │  │
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
| `pab-redis-ver3` | redis:7-alpine | 6379:6379 | `redis-data-ver3` (AOF) |
| Ollama | ollama/ollama (호스트) | 11434 | — |

**ver3 전용 포트**:
- PostgreSQL: `5433` (ver2는 5432)
- Qdrant: `6343` (ver2는 6333)
- Backend: `8001` (ver2는 8000)

**공유 포트**:
- Redis: `6379` (ver2와 동일 포트, 충돌 가능)

**환경 격리**: PostgreSQL/Qdrant/Backend는 포트와 볼륨명을 분리했다. Redis는 동일 포트를 사용하므로 동시 실행 시 충돌 위험이 있다.

➜ [상세 인프라 구성](../claude/2-architecture-ssot.md#1-시스템-아키텍처)

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

➜ [상세 백엔드 규칙](../claude/2-architecture-ssot.md#22-백엔드-코드-작성-규칙) 및 [ROLES/backend-dev.md](ROLES/backend-dev.md)

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

```
web/
├── README.md
│
├── src/                              # 소스 / 개발 참조
│   ├── pages/                        # HTML 템플릿 (Jinja2)
│   │   ├── dashboard.html
│   │   ├── search.html
│   │   ├── document.html
│   │   ├── ask.html
│   │   ├── logs.html
│   │   ├── reason.html
│   │   ├── admin/                    # Admin 모듈 페이지
│   │   │   ├── approval.html
│   │   │   ├── chunk-create.html
│   │   │   ├── chunk-labels.html
│   │   │   ├── groups.html
│   │   │   ├── labels.html
│   │   │   ├── statistics.html
│   │   │   └── settings/            # Admin 설정 페이지
│   │   │       ├── templates.html
│   │   │       ├── presets.html
│   │   │       ├── rag-profiles.html
│   │   │       ├── policy-sets.html
│   │   │       └── audit-logs.html
│   │   └── knowledge/               # 지식 관리 페이지
│   │       ├── knowledge.html
│   │       ├── knowledge-admin.html
│   │       ├── knowledge-detail.html
│   │       ├── knowledge-label-matching.html
│   │       └── knowledge-relation-matching.html
│   └── js/                           # 공유 컴포넌트 소스 (3개)
│       ├── header-component.js
│       ├── layout-component.js
│       └── document-utils.js
│
└── public/                           # 정적 파일 (FastAPI → /static 서빙)
    ├── favicon.svg
    ├── css/                          # 스타일시트 (17개)
    │   ├── dashboard.css
    │   ├── search.css
    │   ├── document.css
    │   ├── ask.css
    │   ├── logs.css
    │   ├── reason.css
    │   ├── statistics.css
    │   ├── admin/                    # Admin 스타일 (7개)
    │   │   ├── admin-styles.css
    │   │   ├── admin-approval.css
    │   │   ├── admin-chunk-create.css
    │   │   ├── admin-chunk-labels.css
    │   │   ├── admin-groups.css
    │   │   ├── admin-labels.css
    │   │   └── settings-common.css
    │   └── knowledge/                # 지식 관리 스타일 (3개)
    │       ├── knowledge.css
    │       ├── knowledge-admin.css
    │       └── knowledge-detail.css
    └── js/                           # JavaScript 모듈 (58개)
        ├── components/               # 재사용 컴포넌트 (8개)
        │   ├── header-component.js
        │   ├── layout-component.js
        │   ├── document-utils.js
        │   ├── pagination-component.js
        │   ├── text-formatter.js
        │   ├── ollama-model-options.js
        │   └── utils.js
        ├── dashboard/dashboard.js
        ├── search/search.js
        ├── document/document.js
        ├── ask/ask.js
        ├── logs/logs.js
        ├── reason/                   # Reasoning Lab (9개)
        │   ├── reason.js
        │   ├── reason-common.js
        │   ├── reason-control.js
        │   ├── reason-model.js
        │   ├── reason-render.js
        │   ├── reason-pdf-export.js
        │   └── reason-viz-loader.js
        ├── admin/                    # Admin 모듈 (16개)
        │   ├── admin-common.js
        │   ├── admin-approval.js
        │   ├── admin-chunk-labels.js
        │   ├── admin-groups.js
        │   ├── admin-labels.js
        │   ├── chunk-approval-manager.js
        │   ├── chunk-create.js
        │   ├── knowledge-admin.js
        │   ├── label-manager.js
        │   ├── statistics.js
        │   ├── keyword-group-*.js    # keyword-group 관련 (5개)
        │   └── settings/             # 설정 (6개)
        │       ├── settings-common.js
        │       ├── templates.js
        │       ├── presets.js
        │       ├── rag-profiles.js
        │       ├── policy-sets.js
        │       └── audit-logs.js
        └── knowledge/               # 지식 관리 (4개)
            ├── knowledge.js
            ├── knowledge-detail.js
            ├── knowledge-label-matching.js
            └── knowledge-relation-matching.js
```

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

➜ [상세 프론트엔드 규칙](../claude/2-architecture-ssot.md#32-프론트엔드-코드-작성-규칙) 및 [ROLES/frontend-dev.md](ROLES/frontend-dev.md)

---

### 3.4 프론트엔드 파일 구조 규칙

**신규 페이지 추가 시** 반드시 아래 3개 파일을 함께 생성한다:

```
신규 페이지 예: "monitoring"

1. HTML 템플릿: web/src/pages/monitoring.html
2. JavaScript:   web/public/js/monitoring/monitoring.js
3. CSS:          web/public/css/monitoring.css
```

**HTML 템플릿 필수 구조**:
```html
<!-- layout-component 포함 -->
<script type="module" src="/static/js/components/layout-component.js"></script>
<!-- 페이지별 CSS -->
<link rel="stylesheet" href="/static/css/monitoring.css">
<!-- 페이지별 JS (type="module") -->
<script type="module" src="/static/js/monitoring/monitoring.js"></script>
```

---

## 4. 데이터베이스

### 4.1 PostgreSQL (메타데이터)

**용도**: 문서 메타데이터, 사용자 데이터, 설정, 로그 등

**핵심 테이블**:
- `documents`: 문서 메타데이터
- `chunks`: 문서 청크 (벡터 ID 참조)
- `labels`, `keyword_groups`: 지식 라벨
- `reasoning_results`: Reasoning 결과
- `page_access_log`: 페이지 접근 로그 (Phase 13-4)
- `admin_*`: Admin 설정 (Phase 11)

**ORM 필수**: SQLAlchemy ORM으로만 접근, raw SQL 금지

---

### 4.2 Qdrant (벡터 검색)

**용도**: 문서 청크의 벡터 임베딩 저장 및 의미 검색

**컬렉션**: `document_chunks`

**벡터 크기**: 1024 (nomic-embed-text 기준)

**검색 방식**:
- Semantic Search: 벡터 유사도 검색
- Hybrid Search: 벡터 + 키워드 조합 (Phase 9-3)

---

### 4.3 Redis (캐싱)

**용도**: Rate Limiting, 검색 캐시, AI 작업 진행 상황 등

**현재 사용**:
- Rate Limiting (slowapi) — 5% 정도
- (Phase 15 계획) 검색 캐시, AI 작업 진행, Reasoning 결과 캐싱으로 확장

**지속성**: AOF (Append-Only File) 활성화

---

## 5. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| Backend Charter | Backend Developer 역할 | `docs/rules/role/BACKEND.md` |
| Frontend Charter | Frontend Developer 역할 | `docs/rules/role/FRONTEND.md` |
| 상세 아키텍처 | 전체 아키텍처 상세 | [2-architecture-ssot.md](../claude/2-architecture-ssot.md) |
| Backend 가이드 | Backend 전용 가이드 | [ROLES/backend-dev.md](ROLES/backend-dev.md) |
| Frontend 가이드 | Frontend 전용 가이드 | [ROLES/frontend-dev.md](ROLES/frontend-dev.md) |

---

**문서 관리**:
- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 기반: 2-architecture-ssot.md (v4.0, 516줄 → 350줄 요약)
