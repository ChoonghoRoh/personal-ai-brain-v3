# Personal AI Brain - 프로젝트 전체 구조 및 메뉴 목차

**작성일**: 2026-02-08
**버전**: Phase 11 완료 기준
**용도**: VSCode에서 프로젝트 전체 탐색 및 개발 시 참조

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [전체 디렉터리 구조](#2-전체-디렉터리-구조)
3. [Backend API 구조](#3-backend-api-구조)
4. [Frontend UI 구조](#4-frontend-ui-구조)
5. [주요 기능별 파일 위치](#5-주요-기능별-파일-위치)
6. [개발 흐름 및 참조 문서](#6-개발-흐름-및-참조-문서)
7. [추가 정보](#7-추가-정보)
8. [다음 단계](#8-다음-단계)
9. [관리자 프로그램 리뷰 체크리스트](#9-관리자-프로그램-리뷰-체크리스트)

---

## 1. 프로젝트 개요

### 1.1 핵심 개념

**Personal AI Brain**은 로컬에서 실행하는 개인 AI 지식 관리 시스템입니다.

- **지식 저장**: Markdown, PDF, DOCX를 벡터 DB에 저장
- **AI 검색**: 의미 기반 하이브리드 검색 (PostgreSQL + Qdrant)
- **Reasoning**: 구조화된 의사결정 추론 (6가지 Role 스키마)
- **Admin 관리**: 템플릿, 프리셋, RAG 프로필, 정책을 UI에서 관리

### 1.2 기술 스택

| 구분          | 기술                                  |
| ------------- | ------------------------------------- |
| **Backend**   | FastAPI (Python 3.11+)                |
| **Frontend**  | Vanilla JavaScript + HTML             |
| **Database**  | PostgreSQL (관계형 데이터)            |
| **Vector DB** | Qdrant (벡터 임베딩)                  |
| **LLM**       | Ollama (로컬 LLM: exaone3.5, qwen2.5) |
| **Container** | Docker Compose                        |
| **테스트**    | Playwright (E2E), pytest (통합)       |

### 1.3 현재 Phase 상태

| Phase      | 상태       | 내용                                            |
| ---------- | ---------- | ----------------------------------------------- |
| Phase 9    | ✅ 완료    | 보안, 테스트, AI 고도화, 기능 확장, 코드 품질   |
| Phase 10   | ✅ 완료    | Reasoning Lab 고도화 (UX, 시각화, 결과물, 공유) |
| Phase 11   | ✅ 완료    | Admin 설정 관리 시스템 (DB, API, UI)            |
| Phase 11-5 | 🔄 진행 중 | Phase 10 고도화 (성능, 시각화, 접근성)          |

---

## 2. 전체 디렉터리 구조

```
personal-ai-brain-v2/
├── backend/                    # FastAPI 백엔드
│   ├── routers/                # API 라우터 (기능별)
│   │   ├── admin/              # Admin 설정 관리 (Phase 11)
│   │   ├── ai/                 # AI 대화 및 추천
│   │   ├── auth/               # 인증 (Phase 9-1)
│   │   ├── automation/         # 자동화 워크플로우
│   │   ├── cognitive/          # 인지 기능 (메모리, 학습)
│   │   ├── ingest/             # 파일 업로드 및 파싱
│   │   ├── knowledge/          # 지식 관리 (CRUD, 승인, 매칭)
│   │   ├── reasoning/          # Reasoning Lab (Phase 10)
│   │   ├── search/             # 검색 (하이브리드, 문서)
│   │   └── system/             # 시스템 (백업, 로그, 통계)
│   ├── models/                 # 데이터 모델 및 DB
│   ├── services/               # 비즈니스 로직
│   ├── middleware/             # 보안, Rate Limit (Phase 9-1)
│   ├── utils/                  # 유틸리티 함수
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   └── config.py               # 환경 설정
│
├── web/                        # 프론트엔드
│   └── src/
│       ├── pages/              # HTML 페이지
│       │   ├── admin/          # Admin 페이지
│       │   │   ├── settings/   # 설정 관리 (Phase 11-3)
│       │   │   ├── approval.html
│       │   │   ├── groups.html
│       │   │   ├── labels.html
│       │   │   └── statistics.html
│       │   ├── knowledge/      # 지식 관리 페이지
│       │   ├── dashboard.html  # 메인 대시보드
│       │   ├── reason.html     # Reasoning Lab (Phase 10)
│       │   ├── search.html     # 검색 페이지
│       │   └── ask.html        # AI 대화 페이지
│       └── public/js/          # JavaScript 모듈 (페이지·컴포넌트)
│
├── docs/                       # 프로젝트 문서
│   ├── README/                 # 개요 및 가이드
│   ├── phases/                 # Phase별 계획 및 요약
│   ├── rules/                  # 개발 규칙 (Phase 11 개선)
│   │   ├── ai/                 # AI 규칙
│   │   ├── backend/            # Backend 규칙
│   │   ├── common/             # 공통 규칙
│   │   ├── prompts/            # Agent 프롬프트 (Phase 11)
│   │   ├── templates/          # 검증 템플릿 (Phase 11)
│   │   └── testing/            # 테스트 가이드 (Phase 11)
│   ├── devtest/                # 통합 테스트 문서
│   ├── webtest/                # 웹 테스트 문서
│   ├── ai/                     # AI 관련 문서
│   ├── db/                     # DB 스키마 문서
│   └── overview/               # 프로젝트 개요 (본 문서 포함)
│
├── scripts/                    # 유틸리티 스크립트
│   ├── db/                     # DB 마이그레이션 및 시딩
│   ├── backup/                 # 백업 스크립트
│   ├── devtool/                # 개발 도구
│   └── webtest.py              # 웹 테스트 실행 스크립트
│
├── tests/                      # pytest 테스트
├── e2e/                        # Playwright E2E 테스트
├── brain/                      # 지식 저장소 (로컬)
├── backups/                    # 백업 파일
├── logs/                       # 로그 파일
├── docker-compose.yml          # Docker Compose 설정
├── requirements.txt            # Python 의존성
├── package.json                # Node.js 의존성 (Playwright)
└── README.md                   # 프로젝트 README
```

---

## 3. Backend API 구조

### 3.1 API 라우터 및 엔드포인트

#### 🔐 인증 (Auth) - Phase 9-1

**파일**: `backend/routers/auth/auth.py`

| 엔드포인트         | 메서드 | 설명           |
| ------------------ | ------ | -------------- |
| `/api/auth/login`  | POST   | 사용자 로그인  |
| `/api/auth/logout` | POST   | 로그아웃       |
| `/api/auth/status` | GET    | 인증 상태 확인 |

---

#### 🔍 검색 (Search)

**파일**:

- `backend/routers/search/search.py` - 메인 검색
- `backend/routers/search/documents.py` - 문서 관리

| 엔드포인트              | 메서드     | 설명                 |
| ----------------------- | ---------- | -------------------- |
| `/api/search`           | GET        | 하이브리드 검색      |
| `/api/search/hybrid`    | POST       | 고급 하이브리드 검색 |
| `/api/documents`        | GET        | 문서 목록            |
| `/api/documents/{id}`   | GET/DELETE | 문서 상세 조회/삭제  |
| `/api/documents/upload` | POST       | 문서 업로드          |

---

#### 🧠 AI 기능 (AI)

**파일**:

- `backend/routers/ai/ai.py` - AI 대화
- `backend/routers/ai/conversations.py` - 대화 기록

| 엔드포인트                   | 메서드     | 설명           |
| ---------------------------- | ---------- | -------------- |
| `/api/ask`                   | POST       | AI에게 질문    |
| `/api/conversations`        | GET        | 대화 기록 목록 |
| `/api/conversations/{id}`    | GET/DELETE | 대화 상세/삭제 |

---

#### 💡 Reasoning Lab - Phase 10

**파일**:

- `backend/routers/reasoning/reason.py` - 메인 Reasoning
- `backend/routers/reasoning/reason_stream.py` - 스트리밍 (Phase 10-1)
- `backend/routers/reasoning/reason_store.py` - 결과 저장/공유 (Phase 10-4)
- `backend/routers/reasoning/reasoning_results.py` - 결과 조회
- `backend/routers/reasoning/recommendations.py` - 추천
- `backend/routers/reasoning/reasoning_chain.py` - 추론 체인

| 엔드포인트                        | 메서드     | 설명                      |
| --------------------------------- | ---------- | ------------------------- |
| `/api/reason`                     | POST       | Reasoning 실행            |
| `/api/reason/stream`             | POST (SSE) | 실시간 진행 상태 스트리밍 (응답에 X-Task-ID) |
| `/api/reason/{task_id}/cancel`   | POST       | Reasoning 취소            |
| `/api/reason/share`              | POST       | 결과 공유(공유 링크 생성) |
| `/api/reason/share/{share_id}`   | GET        | 공유된 결과 조회          |
| `/api/reasoning-results`         | GET        | 결과 목록                 |
| `/api/reasoning-results/{id}`    | GET/DELETE | 결과 상세/삭제            |
| `/api/reason/recommendations`    | GET        | 추천 키워드/질문          |

---

#### 📚 지식 관리 (Knowledge)

**파일**:

- `backend/routers/knowledge/knowledge.py` - 지식 CRUD
- `backend/routers/knowledge/labels.py` - 라벨 관리
- `backend/routers/knowledge/relations.py` - 관계 관리
- `backend/routers/knowledge/approval.py` - 승인 프로세스
- `backend/routers/knowledge/suggestions.py` - 제안
- `backend/routers/knowledge/knowledge_integration.py` - 통합

| 엔드포인트                             | 메서드         | 설명                |
| -------------------------------------- | -------------- | ------------------- |
| `/api/knowledge`                       | GET/POST       | 지식 목록/생성      |
| `/api/knowledge/{id}`                  | GET/PUT/DELETE | 지식 상세/수정/삭제 |
| `/api/labels`                          | GET/POST       | 라벨 목록/생성      |
| `/api/labels/{id}`                     | PUT/DELETE     | 라벨 수정/삭제      |
| `/api/relations`                       | GET/POST       | 관계 목록/생성      |
| `/api/approval/chunks/pending`         | GET            | 승인 대기 목록      |
| `/api/approval/chunks/{chunk_id}/approve` | POST        | 승인                |
| `/api/approval/chunks/{chunk_id}/reject`  | POST        | 거부                |
| `/api/approval/chunks/batch/approve`  | POST           | 일괄 승인           |
| `/api/approval/chunks/batch/reject`   | POST           | 일괄 거부           |
| `/api/suggestions/labels`              | GET            | 라벨 제안           |
| `/api/knowledge/integration/duplicate` | GET            | 중복 지식 탐지      |

---

#### ⚙️ Admin 설정 관리 - Phase 11

**파일**:

- `backend/routers/admin/schema_crud.py` - Role 스키마
- `backend/routers/admin/template_crud.py` - 템플릿
- `backend/routers/admin/preset_crud.py` - 프롬프트 프리셋
- `backend/routers/admin/rag_profile_crud.py` - RAG 프로필
- `backend/routers/admin/policy_set_crud.py` - 정책 세트
- `backend/routers/admin/audit_log_crud.py` - 감사 로그

| 엔드포인트                     | 메서드         | 설명                      |
| ------------------------------ | -------------- | ------------------------- |
| `/api/admin/schemas`           | GET/POST       | Role 스키마 목록/생성     |
| `/api/admin/schemas/{id}`      | GET/PUT/DELETE | 스키마 상세/수정/삭제     |
| `/api/admin/templates`         | GET/POST       | 템플릿 목록/생성          |
| `/api/admin/templates/{id}`    | GET/PUT/DELETE | 템플릿 상세/수정/삭제     |
| `/api/admin/presets`           | GET/POST       | 프리셋 목록/생성          |
| `/api/admin/presets/{id}`      | GET/PUT/DELETE | 프리셋 상세/수정/삭제     |
| `/api/admin/rag-profiles`      | GET/POST       | RAG 프로필 목록/생성      |
| `/api/admin/rag-profiles/{id}` | GET/PUT/DELETE | RAG 프로필 상세/수정/삭제 |
| `/api/admin/policy-sets`       | GET/POST       | 정책 세트 목록/생성       |
| `/api/admin/policy-sets/{id}`  | GET/PUT/DELETE | 정책 세트 상세/수정/삭제  |
| `/api/admin/audit-logs`        | GET            | 감사 로그 조회            |

---

#### 🤖 인지 기능 (Cognitive)

**파일**:

- `backend/routers/cognitive/memory.py` - 메모리 관리
- `backend/routers/cognitive/context.py` - 컨텍스트 관리
- `backend/routers/cognitive/learning.py` - 학습
- `backend/routers/cognitive/personality.py` - 개성
- `backend/routers/cognitive/metacognition.py` - 메타인지

| 엔드포인트               | 메서드 | 설명           |
| ------------------------ | ------ | -------------- |
| `/api/memory`            | GET    | 메모리 조회    |
| `/api/memory/save`       | POST   | 메모리 저장    |
| `/api/context`           | GET    | 컨텍스트 조회  |
| `/api/learning/feedback` | POST   | 학습 피드백    |
| `/api/personality`       | GET    | 개성 설정 조회 |

---

#### 🔧 시스템 (System) - Phase 9-4

**파일**:

- `backend/routers/system/system.py` - 시스템 정보
- `backend/routers/system/backup.py` - 백업 (Phase 9-4-3)
- `backend/routers/system/logs.py` - 로그
- `backend/routers/system/error_logs.py` - 에러 로그
- `backend/routers/system/statistics.py` - 통계 (Phase 9-4-2)
- `backend/routers/system/integrity.py` - 데이터 무결성

| 엔드포인트                  | 메서드 | 설명               |
| --------------------------- | ------ | ------------------ |
| `/api/system/info`          | GET    | 시스템 정보        |
| `/api/system/health`        | GET    | 헬스체크           |
| `/api/system/backup`        | POST   | 백업 생성          |
| `/api/system/backup/s`      | GET    | 백업 목록 (신규; 레거시는 `/api/backup/list`) |
| `/api/system/backup/restore`| POST   | 백업 복원 (body: backup_name, confirm) |
| `/api/logs`                 | GET    | 로그 조회          |
| `/api/error-logs`           | GET    | 에러 로그 조회     |
| `/api/system/statistics`    | GET    | 통계 (루트; /documents, /knowledge 등) |
| `/api/integrity/check`      | POST   | 데이터 무결성 검사 |

---

#### 🚀 자동화 (Automation)

**파일**:

- `backend/routers/automation/automation.py` - 자동화
- `backend/routers/automation/workflow.py` - 워크플로우

| 엔드포인트              | 메서드 | 설명             |
| ----------------------- | ------ | ---------------- |
| `/api/automation/tasks` | GET    | 자동화 작업 목록 |
| `/api/workflow/run`     | POST   | 워크플로우 실행  |

---

#### 📥 파일 업로드 (Ingest)

**파일**: `backend/routers/ingest/file_parser.py`

| 엔드포인트    | 메서드 | 설명                |
| ------------- | ------ | ------------------- |
| `/api/file-parser` | POST | 파일 업로드 및 파싱 |

---

### 3.2 라우터 등록 순서 (main.py)

```python
# backend/main.py 내 라우터 등록 순서

app.include_router(auth.router)                    # 인증
app.include_router(search.router)                  # 검색
app.include_router(system.router)                  # 시스템
app.include_router(documents.router)               # 문서
app.include_router(ai.router)                      # AI 대화
app.include_router(logs.router)                    # 로그
app.include_router(labels.router)                  # 라벨
app.include_router(relations.router)               # 관계
app.include_router(recommendations.router)         # 추천
app.include_router(reason.router)                  # Reasoning
app.include_router(reason_stream.router)           # Reasoning 스트리밍
app.include_router(reason_store.router)            # Reasoning 저장/공유
app.include_router(approval.router)                # 승인
app.include_router(knowledge.router)               # 지식
app.include_router(suggestions.router)             # 제안
app.include_router(context.router)                 # 컨텍스트
app.include_router(memory.router)                  # 메모리
app.include_router(backup.router)                  # 백업
app.include_router(integrity.router)               # 무결성
app.include_router(conversations.router)           # 대화 기록
app.include_router(error_logs.router)              # 에러 로그
app.include_router(reasoning_results.router)       # Reasoning 결과
app.include_router(automation.router)              # 자동화
app.include_router(learning.router)                # 학습
app.include_router(personality.router)             # 개성
app.include_router(metacognition.router)           # 메타인지
app.include_router(reasoning_chain.router)         # 추론 체인
app.include_router(knowledge_integration.router)   # 지식 통합
app.include_router(file_parser.router)             # 파일 파싱
app.include_router(workflow.router)                # 워크플로우
app.include_router(statistics.router)              # 통계
app.include_router(backup_legacy_router)           # 백업 레거시
app.include_router(admin.router)                   # Admin 설정
```

---

## 4. Frontend UI 구조

### 4.1 페이지 구조

```
web/src/pages/
├── dashboard.html              # 메인 대시보드
├── search.html                 # 검색 페이지
├── ask.html                    # AI 대화 페이지
├── reason.html                 # Reasoning Lab (Phase 10)
├── document.html               # 문서 상세
├── logs.html                   # 로그 조회
│
├── admin/                      # Admin 페이지
│   ├── approval.html           # 승인 관리
│   ├── groups.html             # 그룹 관리
│   ├── labels.html             # 라벨 관리
│   ├── statistics.html         # 통계 대시보드
│   ├── chunk-create.html       # 청크 생성
│   ├── chunk-labels.html       # 청크 라벨
│   └── settings/               # 설정 (Phase 11-3)
│       ├── templates.html      # 템플릿 관리
│       ├── presets.html        # 프리셋 관리
│       ├── rag-profiles.html   # RAG 프로필 관리
│       ├── policy-sets.html    # 정책 세트 관리
│       └── audit-logs.html     # 감사 로그
│
└── knowledge/                  # 지식 관리 페이지
    ├── knowledge.html          # 지식 목록
    ├── knowledge-detail.html   # 지식 상세
    ├── knowledge-admin.html    # 지식 관리자
    ├── knowledge-label-matching.html    # 라벨 매칭
    └── knowledge-relation-matching.html # 관계 매칭
```

### 4.2 페이지별 기능

#### 📊 대시보드 (dashboard.html)

- 최근 활동 요약
- 통계 차트
- 빠른 액세스 메뉴

#### 🔍 검색 (search.html)

- 하이브리드 검색 (키워드 + 벡터)
- 필터링 (날짜, 라벨, 타입)
- 검색 결과 목록

#### 💬 AI 대화 (ask.html)

- AI와 자연어 대화
- 대화 기록 저장
- 컨텍스트 유지

#### 💡 Reasoning Lab (reason.html) - Phase 10

**Phase 10-1 (UX/UI 개선)**:

- 진행률 표시 (실시간 진행 상태)
- 취소 기능
- ETA (예상 완료 시간)
- 세션 관리

**Phase 10-2 (모드별 시각화)**:

- 그래프 모드: 관계 시각화
- 타임라인 모드: 시간 순서
- 트리 모드: 계층 구조
- 테이블 모드: 데이터 표

**Phase 10-3 (결과물 형식)**:

- Markdown 내보내기
- JSON 내보내기
- PDF 생성 (선택)
- 템플릿 커스터마이징

**Phase 10-4 (고급 기능)**:

- 스트리밍 (서버 전송 이벤트)
- 결과 공유 (공유 링크)
- 결과 저장 (로컬 DB)
- 히스토리 관리

#### ⚙️ Admin 설정 (admin/settings/) - Phase 11-3

**templates.html**:

- 템플릿 목록 조회
- 템플릿 생성/수정/삭제
- 템플릿 미리보기

**presets.html**:

- 프롬프트 프리셋 관리
- 프리셋 템플릿 적용
- 변수 치환 설정

**rag-profiles.html**:

- RAG 프로필 설정
- 검색 전략 구성
- 청크 크기/오버랩 설정

**policy-sets.html**:

- 정책 세트 관리
- 정책 규칙 정의
- 정책 적용 범위

**audit-logs.html**:

- 설정 변경 이력
- 변경 사용자 추적
- 롤백 기능 (Phase 11-2-3)

#### 📚 지식 관리 (knowledge/)

**knowledge.html**:

- 지식 목록
- 지식 검색
- 지식 필터링

**knowledge-detail.html**:

- 지식 상세 조회
- 지식 수정
- 지식 삭제

**knowledge-admin.html**:

- 지식 관리자 도구
- 일괄 작업
- 승인 프로세스

**knowledge-label-matching.html**:

- 라벨 자동 매칭
- 라벨 제안
- 라벨 승인/거부

**knowledge-relation-matching.html**:

- 관계 자동 매칭
- 관계 제안
- 관계 승인/거부

---

### 4.3 JavaScript 모듈 구조

```
web/public/js/
├── components/                 # 재사용 컴포넌트 (header, layout, pagination 등)
├── dashboard/                 # 대시보드
├── search/                    # 검색
├── reason/                    # Reasoning Lab (reason.js, reason-*.js)
├── admin/                     # Admin (settings/, approval, labels 등)
├── knowledge/                 # 지식 관리
├── ask/                       # AI 대화
├── document/                  # 문서 상세
└── logs/                      # 로그
```

---

## 5. 주요 기능별 파일 위치

### 5.1 Reasoning Lab (Phase 10)

**Backend**:

- `backend/routers/reasoning/reason.py` - 메인 로직
- `backend/routers/reasoning/reason_stream.py` - 스트리밍 (10-1)
- `backend/routers/reasoning/reason_store.py` - 저장/공유 (10-4)
- `backend/routers/reasoning/reasoning_results.py` - 결과 조회
- `backend/routers/reasoning/recommendations.py` - 추천
- `backend/services/reasoning_service.py` - 비즈니스 로직

**Frontend**:

- `web/src/pages/reason.html` - Reasoning Lab UI
- `web/public/js/reason/reason.js` - 클라이언트 로직

**문서**:

- `docs/phases/phase-10-master-plan.md` - Phase 10 계획
- `docs/phases/phase-10-final-summary-report.md` - Phase 10 완료 요약

---

### 5.2 Admin 설정 관리 (Phase 11)

**Backend**:

- `backend/routers/admin/` - Admin API 전체
  - `schema_crud.py` - Role 스키마 CRUD
  - `template_crud.py` - 템플릿 CRUD
  - `preset_crud.py` - 프리셋 CRUD
  - `rag_profile_crud.py` - RAG 프로필 CRUD
  - `policy_set_crud.py` - 정책 세트 CRUD
  - `audit_log_crud.py` - 감사 로그

**Database**:

- `scripts/db/migrate_phase11_1_1.sql` - 스키마 마이그레이션
- `scripts/db/migrate_phase11_1_2.sql` - 추가 테이블
- `scripts/db/seed_phase11_1_*.sql` - 시드 데이터

**Frontend**:

- `web/src/pages/admin/settings/` - Admin UI 전체
  - `templates.html`
  - `presets.html`
  - `rag-profiles.html`
  - `policy-sets.html`
  - `audit-logs.html`

**문서**:

- `docs/phases/phase-11-master-plan.md` - Phase 11 계획
- `docs/phases/phase-11-final-summary-report.md` - Phase 11 완료 요약
- `docs/phases/phase-11-1/` - DB 스키마 (11-1)
- `docs/phases/phase-11-2/` - Backend API (11-2)
- `docs/phases/phase-11-3/` - Admin UI (11-3)

---

### 5.3 검색 (Search)

**Backend**:

- `backend/routers/search/search.py` - 하이브리드 검색
- `backend/routers/search/documents.py` - 문서 관리
- `backend/services/search_service.py` - 검색 로직

**Frontend**:

- `web/src/pages/search.html`
- `web/public/js/search/search.js`

---

### 5.4 지식 관리 (Knowledge)

**Backend**:

- `backend/routers/knowledge/knowledge.py` - 지식 CRUD
- `backend/routers/knowledge/labels.py` - 라벨 관리
- `backend/routers/knowledge/relations.py` - 관계 관리
- `backend/routers/knowledge/approval.py` - 승인 프로세스
- `backend/routers/knowledge/suggestions.py` - 제안
- `backend/routers/knowledge/knowledge_integration.py` - 통합

**Frontend**:

- `web/src/pages/knowledge/` - 지식 관리 UI 전체

---

### 5.5 인증 및 보안 (Phase 9-1)

**Backend**:

- `backend/routers/auth/auth.py` - 인증 API
- `backend/middleware/security.py` - 보안 헤더
- `backend/middleware/rate_limit.py` - Rate Limiting

**문서**:

- `docs/phases/phase-9-1/` - 보안 강화 Task

---

### 5.6 통계 및 백업 (Phase 9-4)

**Backend**:

- `backend/routers/system/statistics.py` - 통계 (9-4-2)
- `backend/routers/system/backup.py` - 백업 (9-4-3)

**Frontend**:

- `web/src/pages/admin/statistics.html`

**Scripts**:

- `scripts/backup/` - 백업 스크립트

---

## 6. 개발 흐름 및 참조 문서

### 6.1 Phase별 개발 순서

```
Phase 1-8  → 기본 기능 구축 (검색, AI, 지식 관리)
Phase 9    → 보안, 테스트, AI 고도화, 기능 확장
Phase 10   → Reasoning Lab 고도화 (UX, 시각화, 결과물)
Phase 11   → Admin 설정 관리 시스템 (DB, API, UI)
Phase 11-5 → Phase 10 추가 고도화 (성능, 시각화, 접근성)
```

### 6.2 핵심 문서 위치

#### 개발 가이드

| 문서                                        | 설명                             |
| ------------------------------------------- | -------------------------------- |
| `README.md`                                 | 프로젝트 개요 및 빠른 시작       |
| `docs/README/01-overview-and-quickstart.md` | 한 줄 설명, 빠른 시작, 기능 요약 |
| `docs/README/02-architecture.md`            | 디렉터리 구조, 기술 스택         |
| `docs/README/03-development-progress.md`    | 개발 진행 단계 및 Phase 링크     |
| `docs/README/04-rules-and-conventions.md`   | 문서 분류, 규칙, AI 룰           |
| `docs/README/05-database.md`                | DB 구조, 마이그레이션            |
| `docs/README/06-reference-docs-index.md`    | 문서 인덱스                      |
| `docs/README/07-issues-and-future.md`       | 이슈, 향후 계획                  |

#### Phase별 문서

| Phase    | 계획 문서                             | 완료 요약                                      |
| -------- | ------------------------------------- | ---------------------------------------------- |
| Phase 9  | `docs/phases/phase-9-master-plan.md`  | `docs/phases/phase-9-final-summary-report.md`  |
| Phase 10 | `docs/phases/phase-10-master-plan.md` | `docs/phases/phase-10-final-summary-report.md` |
| Phase 11 | `docs/phases/phase-11-master-plan.md` | `docs/phases/phase-11-final-summary-report.md` |

#### 개발 규칙 (Phase 11 개선)

| 문서                                                   | 설명                       |
| ------------------------------------------------------ | -------------------------- |
| `docs/rules/rules-index.md`                            | 통합 Rules 인덱스 (SSOT)   |
| `docs/rules/ai-execution-workflow.md`                  | AI 실행 워크플로우 Ver 2.0 |
| `docs/rules/prompts/agent-system-prompts.md`           | Agent 시스템 프롬프트      |
| `docs/rules/templates/verification-report-template.md` | 검증 리포트 템플릿         |
| `docs/rules/testing/integration-test-guide.md`         | 통합 테스트 가이드 (공용)  |
| `docs/rules/testing/phase-unit-user-test-guide.md`     | 웹 테스트 수행 가이드      |

#### 테스트 문서

| 문서                                                        | 설명                      |
| ----------------------------------------------------------- | ------------------------- |
| `docs/devtest/README.md`                                    | 통합 테스트 가이드        |
| `docs/devtest/reports/phase-11-integration-test-summary.md` | Phase 11 통합 테스트 요약 |
| `docs/webtest/README.md`                                    | 웹 테스트 가이드          |
| `docs/webtest/phase-11-webtest-final-summary.md`            | Phase 11 웹 테스트 요약   |

---

### 6.3 개발 시 주의사항

#### 🔐 인증 (Phase 9-1)

- `AUTH_ENABLED=true` 환경 변수 설정 시 인증 활성화
- 모든 보호된 엔드포인트는 `@require_auth` 데코레이터 사용

#### 🧪 테스트

**통합 테스트**:

```bash
pytest tests/
```

**E2E 테스트**:

```bash
npx playwright test
```

**웹 테스트 (특정 Phase)**:

```bash
python scripts/webtest.py 11-1 start
```

#### 📝 문서화

- **Task 문서**: `docs/phases/phase-X-Y/tasks/task-X-Y-Z-*.md`
- **Plan 문서**: `docs/phases/phase-X-Y/phase-X-Y-0-plan.md`
- **Todo 문서**: `docs/phases/phase-X-Y/phase-X-Y-0-todo-list.md`

#### 🗄️ 데이터베이스

**마이그레이션**:

```bash
docker compose exec postgres psql -U brain -d knowledge -f /scripts/db/migrate_*.sql
```

**시딩**:

```bash
docker compose exec postgres psql -U brain -d knowledge -f /scripts/db/seed_*.sql
```

#### 🚀 배포

```bash
docker-compose up -d --build
```

---

### 6.4 디버깅 및 로깅

**Backend 로그**:

```bash
docker compose logs -f backend
```

**Database 접속**:

```bash
docker compose exec postgres psql -U brain -d knowledge
```

**Qdrant 확인**:

```bash
curl http://localhost:6333/collections
```

**Ollama 모델 확인**:

```bash
docker exec -it ollama ollama list
```

---

## 7. 추가 정보

### 7.1 환경 변수 (.env)

```env
# Database
POSTGRES_USER=brain
POSTGRES_PASSWORD=password
POSTGRES_DB=knowledge

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=exaone3.5:2.4b

# Auth (Phase 9-1)
AUTH_ENABLED=false
SECRET_KEY=your-secret-key

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### 7.2 포트 매핑

| 서비스     | 포트  | 설명            |
| ---------- | ----- | --------------- |
| Backend    | 8000  | FastAPI API     |
| PostgreSQL | 5432  | PostgreSQL DB   |
| Qdrant     | 6333  | Vector DB       |
| Ollama     | 11434 | LLM 서버        |
| Web        | 3000  | Frontend (선택) |

### 7.3 추천 개발 도구

- **VSCode Extensions**:
  - Python (Microsoft)
  - Pylance
  - Playwright Test for VSCode
  - Docker
  - ESLint

- **Chrome Extensions**:
  - Vue.js devtools (선택)
  - React Developer Tools (선택)

---

## 8. 다음 단계

### 8.1 Phase 12 권장사항

1. **멀티 테넌시 확장**
   - 회사별 설정 격리
   - 마켓플레이스 기능

2. **고급 Admin 기능**
   - A/B 테스트
   - 품질 리포트 대시보드
   - 설정 변경 이력 분석

3. **외부 연동**
   - Notion, Confluence 연동
   - 설정 동기화

### 8.2 기술 부채 (Technical Debt)

| 항목                    | 우선순위 | 조치 계획         |
| ----------------------- | -------- | ----------------- |
| E2E spec 파일 미존재    | Medium   | Phase 12에서 추가 |
| API 페이지네이션 기본값 | Low      | 다음 개선에 반영  |
| 운영 매뉴얼 미완료      | Low      | 11-4-2에서 완료   |

---

## 9. 관리자 프로그램 리뷰 체크리스트

관리자·운영 관점에서 점검할 항목을 정리한 체크리스트입니다. 배포 전·정기 리뷰 시 참고하세요.

### 9.1 접근 제어·권한

| 항목 | 위치 | 비고 |
|------|------|------|
| Admin API 전용 보호 | `backend/routers/admin/` | Phase 11-2; 현재 인증 미들웨어와 연동 여부 확인 권장 |
| 인증 활성화 | `AUTH_ENABLED`, `backend/routers/auth/` | Phase 9-1; 프로덕션에서는 `true` 권장 |
| Admin UI 진입점 | `web/src/pages/admin/`, 헤더 메뉴 | 설정·승인·통계 등 메뉴 분리 |

### 9.2 감사·변경 이력

| 항목 | 위치 | 비고 |
|------|------|------|
| 감사 로그 API | `/api/admin/audit-logs` | 설정 변경 이력 조회 |
| 감사 로그 UI | `admin/settings/audit-logs.html` | 변경 사용자·시점 추적 |
| 롤백/버전 | Phase 11-2-3 설계 | 필요 시 버전 복원·롤백 절차 문서화 |

### 9.3 백업·복원·무결성

| 항목 | 위치 | 비고 |
|------|------|------|
| 백업 생성/목록/복원 | `/api/system/backup`, `/api/backup/*` (레거시) | Phase 9-4-3 |
| 백업 검증 | `/api/system/backup/{name}/verify` | 복원 전 검증 권장 |
| 데이터 무결성 검사 | `/api/integrity/check` | 정기 점검용 |

### 9.4 운영·모니터링

| 항목 | 위치 | 비고 |
|------|------|------|
| 헬스체크 | `/api/system/health` | LB·배포 검사용 |
| 로그·에러 로그 | `/api/logs`, `/api/error-logs` | 조회·알람 연동 |
| 통계 대시보드 | `/api/system/statistics`, `admin/statistics.html` | 사용량·트렌드 |

### 9.5 보안 설정

| 항목 | 위치 | 비고 |
|------|------|------|
| 보안 헤더 | `backend/middleware/security.py` | Phase 9-1 |
| Rate Limiting | `backend/middleware/rate_limit.py` | DoS 완화 |
| CORS·환경 변수 | `backend/main.py`, `.env` | 프로덕션 오리진·비밀값 점검 |

### 9.6 리뷰 시 확인 권장 사항

- [ ] Admin API에 관리자 전용 인증/역할 적용 여부
- [ ] 감사 로그 보존 기간·용량 정책
- [ ] 백업 스케줄·보관 장소·복원 절차 문서화
- [ ] 에러 로그 알람·대응 절차
- [ ] 비밀키·DB 비밀번호 등 환경 변수 노출 여부

---

## 부록

### A. 빠른 참조 링크

**API 문서**: http://localhost:8000/docs
**대시보드**: http://localhost:8000/dashboard
**Reasoning Lab**: http://localhost:8000/reason
**Admin 설정**: http://localhost:8000/admin/settings/templates

### B. 문제 해결

**컨테이너 재시작**:

```bash
docker-compose restart backend
```

**DB 초기화**:

```bash
docker-compose down -v
docker-compose up -d
```

**로그 확인**:

```bash
docker-compose logs -f
```

---

**작성일**: 2026-02-08
**버전**: Phase 11 완료 기준
**다음 업데이트**: Phase 12 완료 시
