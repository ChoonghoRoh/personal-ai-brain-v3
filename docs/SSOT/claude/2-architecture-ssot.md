# AI Team — Architecture SSOT

**버전**: 4.0
**최종 수정**: 2026-02-16

---

## 1. 시스템 아키텍처

### 1.1 인프라 구성

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

### 1.2 컨테이너 사양

| 컨테이너 | 이미지 | 포트 (호스트:내부) | 볼륨 |
|----------|--------|-------------------|------|
| `pab-backend-ver3` | Dockerfile.backend (Python 3.12-slim) | 8001:8000 | `./:/app` |
| `pab-postgres-ver3` | postgres:15 | 5433:5432 | `postgres-data-ver3` |
| `qdrant-ver3` | qdrant/qdrant:latest | 6343:6333, 6344:6334 | `./qdrant-data-ver3` |
| `pab-redis-ver3` | redis:7-alpine | 6379:6379 | `redis-data-ver3` (AOF) |
| Ollama | ollama/ollama (호스트) | 11434 | — |

**Base URL**: `http://localhost:8001` (ver3 고정)

---

## 2. 백엔드 코드 구조

### 2.1 디렉토리 맵

```
backend/
├── main.py                      # FastAPI 앱 진입점 (정적 파일 마운트, 라우터 등록)
├── config.py                    # 환경변수 설정
├── models/
│   ├── database.py              # SQLAlchemy 엔진, 세션
│   ├── models.py                # 핵심 ORM 모델
│   ├── admin_models.py          # Admin 설정 모델 (Phase 11) + PageAccessLog (Phase 13-4)
│   └── workflow_common.py       # 워크플로우 공통 모델
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
├── services/                    # 비즈니스 로직 (도메인별)
│   ├── search/{search_service,hybrid_search,reranker,multi_hop_rag,document_sync_service}.py
│   ├── ai/{ollama_client,context_manager}.py
│   ├── knowledge/{auto_labeler,structure_matcher,knowledge_integration_service}.py
│   ├── reasoning/{dynamic_reasoning_service,reasoning_chain_service,recommendation_service}.py
│   ├── cognitive/{memory_service,context_service,learning_service,personality_service,metacognition_service,memory_scheduler}.py
│   ├── knowledge/{...,transaction_manager,chunk_sync_service}.py
│   ├── system/{system_service,integrity_service,logging_service,statistics_service}.py
│   └── ingest/{file_parser_service,hwp_parser}.py
└── middleware/
    ├── security.py              # 보안 헤더
    ├── rate_limit.py            # Rate Limiting (slowapi, X-Forwarded-For)
    ├── request_id.py            # Request ID 미들웨어 (UUID)
    ├── error_handler.py         # 전역 에러 핸들러 (표준 JSON)
    ├── page_access_log.py       # 페이지 접근 로그 (Phase 13-4)
    └── auth.py                  # JWT/API Key 인증
```

### 2.2 백엔드 코드 작성 규칙

| 규칙 | 기준 |
|------|------|
| **언어** | Python 3.12 |
| **프레임워크** | FastAPI (async) |
| **ORM** | SQLAlchemy 2.0+ (ORM 필수, raw SQL 금지) |
| **타입 힌트** | 모든 함수 시그니처에 필수 |
| **입력 검증** | Pydantic 모델 사용 |
| **에러 핸들링** | HTTPException with 적절한 status code |
| **네이밍** | snake_case |
| **새 파일 생성** | 기존 패턴 참조 후 동일 구조로 생성 |
| **참조 Charter** | `docs/rules/role/BACKEND.md` |

---

## 3. 프론트엔드 코드 구조

### 3.1 디렉토리 맵

```
web/
├── README.md
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

### 3.2 프론트엔드 코드 작성 규칙

| 규칙 | 기준 |
|------|------|
| **언어** | Vanilla JavaScript (ES2020+) |
| **모듈 시스템** | ESM (`<script type="module">`, `import`/`export`) |
| **UI 프레임워크** | Bootstrap (로컬 배치, CDN 금지) |
| **빌드 도구** | 없음 (빌드리스 구조) |
| **외부 CDN** | **절대 금지** — 모든 라이브러리는 `web/public/libs/`에 로컬 배치 |
| **네이밍** | camelCase (변수/함수), kebab-case (파일명) |
| **XSS 방지** | `innerHTML` 사용 시 반드시 `esc()` 적용, 가능하면 `textContent` 사용 |
| **전역 객체** | `window`에 함수 할당 금지 (기존 레거시 제외) |
| **컴포넌트 재사용** | `layout-component.js`, `header-component.js` 등 기존 컴포넌트 활용 |
| **참조 Charter** | `docs/rules/role/FRONTEND.md` |

### 3.3 프론트엔드 파일 구조 규칙

새 페이지 추가 시 반드시 아래 3개 파일을 함께 생성한다:

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

### 3.4 로컬 배치 라이브러리 (Phase 12-1-1 완료)

기존 CDN 참조를 On-Premise 원칙에 따라 로컬 배치로 전환 완료하였다:

| 라이브러리 | 사용 위치 | 용도 | 상태 |
|-----------|----------|------|------|
| Mermaid 10 | reason.html | 다이어그램 시각화 | ✅ 로컬 전환 완료 (`web/public/libs/`) Phase 12-1-1 |
| Marked | document.html, logs.html | Markdown 파싱 | ✅ 로컬 전환 완료 (`web/public/libs/`) Phase 12-1-1 |
| Chart.js 4 | 여러 페이지 | 데이터 시각화 | ✅ 로컬 전환 완료 (`web/public/libs/`) Phase 12-1-1 |
| html2canvas 1.4.1 | PDF 내보내기 | 스크린샷 | ✅ 로컬 전환 완료 (`web/public/libs/`) Phase 12-1-1 |
| jsPDF 2.5.1 | PDF 내보내기 | PDF 생성 | ✅ 로컬 전환 완료 (`web/public/libs/`) Phase 12-1-1 |

---

## 4. 데이터베이스 스키마

### 4.1 핵심 테이블

| 테이블 | PK 타입 | 주요 관계 | 용도 |
|--------|---------|----------|------|
| `projects` | serial | 1:N → documents | 프로젝트 정보 |
| `documents` | serial | FK: project_id, category_label_id | 문서 메타데이터 |
| `knowledge_chunks` | serial | FK: document_id | 지식 청크 (status: draft/approved/rejected) |
| `labels` | serial | 자기참조: parent_label_id | 계층형 라벨 |
| `knowledge_labels` | serial | FK: chunk_id, label_id | 청크-라벨 다대다 |
| `knowledge_relations` | serial | FK: source_chunk_id, target_chunk_id | 청크 간 관계 |
| `memories` | serial | — | 기억 시스템 (장기/단기/작업) |
| `conversations` | serial | — | 대화 기록 |
| `reasoning_results` | serial | share_id (공유) | 추론 결과 |

### 4.2 Admin 테이블 (Phase 11)

| 테이블 | PK 타입 | 특징 |
|--------|---------|------|
| `schemas` | UUID | role_key unique, JSONB fields |
| `templates` | UUID | 버전 관리, Draft/Published |
| `prompt_presets` | UUID | task_type, model_name |
| `rag_profiles` | UUID | chunk_size, top_k, score_threshold |
| `context_rules` | UUID | JSONB classification_logic |
| `policy_sets` | UUID | FK: projects, templates, presets, profiles |
| `audit_logs` | UUID | JSONB old/new_values |

### 4.2.1 운영 테이블 (Phase 13-4)

| 테이블 | PK 타입 | 특징 |
|--------|---------|------|
| `page_access_logs` | SERIAL | path, status_code, response_time_ms, accessed_at |

### 4.3 DB 변경 규칙

| 규칙 | 기준 |
|------|------|
| **마이그레이션 (레거시)** | Phase 11 이전: `scripts/db/migrate_*.sql` |
| **마이그레이션 (현행)** | Phase 12 이후: `scripts/migrations/NNN_*.sql` (순번제, README 관리) |
| **시드 데이터** | `scripts/db/seed_*.sql`에 저장 |
| **인덱스** | FK 컬럼, 자주 조회되는 컬럼에 반드시 생성 |
| **제약조건** | FK, NOT NULL, UNIQUE 적극 활용 |
| **ORM 동기화** | SQL 변경 시 반드시 `models.py` 또는 `admin_models.py` 동기화 |
| **롤백 SQL** | 마이그레이션 작성 시 롤백 SQL도 함께 작성 |

---

## 5. API 설계 규칙

### 5.1 엔드포인트 규칙

| 규칙 | 기준 |
|------|------|
| **Prefix** | `/api/` (향후 `/api/v1/` 전환 예정) |
| **리소스 명명** | 복수형 명사 (`/api/templates`, `/api/chunks`) |
| **HTTP 메소드** | GET(조회), POST(생성), PUT(수정), DELETE(삭제) |
| **응답 코드** | 200(성공), 201(생성), 400(잘못된 요청), 404(없음), 500(서버 오류) |
| **페이지네이션** | `limit`, `offset` 쿼리 파라미터 |
| **문서화** | FastAPI 자동 생성 (Swagger `/docs`, ReDoc `/redoc`) |

### 5.2 API 응답 형식

```json
// 성공 (단일)
{
  "id": 1,
  "name": "example",
  "created_at": "2026-02-09T10:00:00Z"
}

// 성공 (목록)
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}

// 에러
{
  "detail": "Resource not found"
}
```

### 5.3 프론트엔드-API 연동 패턴

프론트엔드에서 API를 호출할 때의 표준 패턴:

```javascript
// 표준 API 호출 패턴 (ESM 모듈 내)
async function fetchData(endpoint) {
    try {
        const response = await fetch(`/api/${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API 호출 실패: ${endpoint}`, error);
        // 사용자에게 에러 메시지 표시
    }
}
```

---

## 6. 보안 기준

### 6.1 현재 적용 사항

| 영역 | 기술 | 상태 |
|------|------|------|
| 인증 | JWT Bearer + API Key | ✅ 구현 (AUTH_ENABLED 토글) |
| CORS | 환경별 분리 | ✅ 구현 |
| Rate Limiting | slowapi (메모리 기반, X-Forwarded-For 지원) | ✅ 구현 (Phase 12-3-2 IP 파싱 강화) |
| 보안 헤더 | X-Content-Type-Options, X-Frame-Options, XSS Protection | ✅ 구현 |
| SQL Injection | SQLAlchemy ORM | ✅ 방지 |
| 입력 검증 | Pydantic | ✅ 구현 |
| HSTS | 환경변수 기반 활성화 (ENABLE_HSTS) | ✅ Phase 12-1-3 구현 |

### 6.2 백엔드 보안 체크리스트

새 API 엔드포인트 또는 서비스 로직 작성 시:

- [ ] SQLAlchemy ORM 사용 (raw SQL 금지)
- [ ] Pydantic 모델로 입력 검증
- [ ] 적절한 HTTP status code 반환
- [ ] 인증 데코레이터 적용 (필요한 경우)
- [ ] Rate Limit 적용 (LLM/Import 관련 엔드포인트)
- [ ] 에러 메시지에 내부 정보 미포함
- [ ] 파일 업로드 시 타입/크기 검증

### 6.3 프론트엔드 보안 체크리스트

HTML/JS/CSS 작성 시:

- [ ] `innerHTML` 사용 시 `esc()` 적용 (XSS 방지)
- [ ] 사용자 입력값 렌더링 시 `textContent` 우선 사용
- [ ] API 응답 데이터를 DOM에 삽입할 때 이스케이프 처리
- [ ] `eval()`, `Function()` 등 동적 코드 실행 금지
- [ ] 외부 CDN 미사용 (공급망 공격 방지)
- [ ] `window` 전역 오염 최소화
- [ ] 인라인 이벤트 핸들러 (`onclick` 등) 지양, ESM 내 바인딩 권장

---

## 7. 환경 변수 기준

### 7.1 필수 환경 변수

```bash
# Database
DATABASE_URL=postgresql://brain:password@postgres:5432/knowledge
POSTGRES_USER=brain
POSTGRES_PASSWORD=brain_password  # 프로덕션 시 변경 필수
POSTGRES_DB=knowledge

# Qdrant
QDRANT_HOST=qdrant      # Docker 내부: qdrant, 호스트: localhost
QDRANT_PORT=6333        # Docker 내부: 6333, 호스트: 6343

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b

# Auth
AUTH_ENABLED=false      # 개발: false, 프로덕션: true
JWT_SECRET_KEY=change-in-production
API_SECRET_KEY=change-in-production

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_LLM_PER_MINUTE=10
```

### 7.2 환경 변수 변경 규칙

- `.env` 파일은 Git에 커밋하지 않음 (`.gitignore` 포함)
- `.env.example`에 키 이름과 기본값만 기재
- 프로덕션 환경에서는 `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`를 반드시 변경

---

## 8. 검증 기준 요약

코드 리뷰 시 적용하는 기준 체크리스트. `verifier` 팀원(Agent Teams, subagent_type: "Explore")이 사용한다.

### 8.1 백엔드 검증 기준

#### Critical (필수 통과)

- [ ] 구문 오류 없음 (Python import, 문법)
- [ ] ORM 사용 (raw SQL 없음)
- [ ] 입력 검증 존재 (Pydantic)
- [ ] FK 제약조건 정합성 (DB 변경 시)
- [ ] 기존 테스트 깨지지 않음

#### High (권장 통과)

- [ ] 타입 힌트 완전
- [ ] 에러 핸들링 존재 (try-except + HTTPException)
- [ ] 새 기능에 대한 테스트 파일 존재
- [ ] API 응답 형식 일관성

#### Low (개선 권장)

- [ ] docstring 존재
- [ ] 로깅 적절
- [ ] 변수/함수 명명 일관성

### 8.2 프론트엔드 검증 기준

#### Critical (필수 통과)

- [ ] 외부 CDN 참조 없음
- [ ] `innerHTML` 사용 시 `esc()` 적용
- [ ] ESM `import`/`export` 패턴 사용 (`type="module"`)
- [ ] 페이지 로드 시 콘솔 에러 없음
- [ ] 기존 페이지 동작 깨지지 않음

#### High (권장 통과)

- [ ] `window` 전역 객체에 새 함수 할당 없음
- [ ] 기존 컴포넌트 재사용 (`layout-component.js`, `header-component.js`)
- [ ] API 호출 시 에러 핸들링 (try-catch + 사용자 메시지)
- [ ] 반응형 레이아웃 (Bootstrap grid 사용)

#### Low (개선 권장)

- [ ] JSDoc 주석 존재
- [ ] CSS 클래스 네이밍 일관성
- [ ] 접근성 (aria-label, alt 속성)

---

## 9. 버전 히스토리

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초안 작성 (백엔드 전용) | Claude Code (Backend & Logic Expert) |
| 2.0 | 2026-02-09 | 프론트엔드 구조 추가, 보안/검증 기준 분리, 공통 AI 팀 언어로 전환 | Claude Code (Backend & Logic Expert) |
| 3.0 | 2026-02-15 | Claude Code 내부 에이전트 팀 전환: 검증 기준 문구를 Verifier 서브에이전트(Task tool) 기반으로 수정 | Claude Code (Backend & Logic Expert) |
| 3.1 | 2026-02-16 | Phase 12 반영: Redis 컨테이너 추가, CDN 5개 로컬 전환 완료, HSTS 환경변수 활성화, middleware(request_id, error_handler) 추가, Rate Limit X-Forwarded-For, memory_scheduler/transaction_manager/chunk_sync_service 추가 | Claude Code (Backend & Logic Expert) |
| 3.2 | 2026-02-16 | Phase 13-4 반영: page_access_log 미들웨어·page_access_log_crud 라우터·page_access_logs 테이블 추가, 마이그레이션 경로 이원화(레거시 scripts/db/ + 현행 scripts/migrations/) 반영 | Claude Code (Backend & Logic Expert) |
| 4.0 | 2026-02-16 | Agent Teams 전환: Verifier 참조를 팀원 기반으로 변경 | Claude Code (Backend & Logic Expert) |
