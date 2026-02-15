# Personal AI Brain — 프로젝트 전체·메뉴별 목차 (Cursor Overview)

**작성일**: 2026-02-08  
**버전**: Phase 11 완료 기준  
**대상**: Backend·Frontend·기능 분석 후 메뉴별 목차 (관리자 운영 가이드 포함)  
**Base URL**: http://localhost:8001

---

## 1. 프로젝트 개요

| 구분 | 기술·구조 |
|------|-----------|
| **Backend** | FastAPI, PostgreSQL, Qdrant, Ollama(로컬 LLM) |
| **Frontend** | Vanilla JS + HTML + CSS (SPA 아님, 페이지 단위), `web/` |
| **정적·템플릿** | `web/public/` (CSS·JS·favicon), `web/src/pages/` (HTML) |
| **API 문서** | http://localhost:8001/docs (OpenAPI) |
| **기본 모델** | qwen2.5:7b (docker-compose.yml 기본값, .env 변경 가능) |
| **현재 Phase** | Phase 11 (Admin 설정 관리), Phase 11-5 (Phase 10 고도화) 완료 |

---

## 2. 메뉴별 목차

### 2.1 사용자 메뉴 (좌측 네비게이션)

| 순서 | 메뉴 | 경로 | Frontend (HTML) | 주요 Backend API | 기능 요약 |
|------|------|------|-----------------|------------------|-----------|
| 1 | 대시보드 | `/dashboard` | `dashboard.html` | `/api/system`, `/api/system/statistics` | 시스템 상태·통계·진입 링크 |
| 2 | 검색 | `/search` | `search.html` | `/api/search`, `/api/documents` | 문서·하이브리드 검색 |
| 3 | 지식 구조 | `/knowledge` | `knowledge/knowledge.html` | `/api/knowledge`, `/api/labels`, `/api/relations` | 지식 그래프·청크·라벨·관계 조회 |
| 4 | Reasoning | `/reason` | `reason.html` | `/api/reason` (stream, eta, share, decisions) | 추론 Lab·스트리밍·공유·의사결정 저장 |
| 5 | AI 질의 | `/ask` | `ask.html` | `/api/ask` | AI 기반 질의응답 |
| 6 | 로그 | `/logs` | `logs.html` | `/api/logs` | 대화·로그 조회 |

**보조 경로 (지식·문서)**

| 경로 | HTML | API | 비고 |
|------|------|-----|------|
| `/knowledge-detail` | `knowledge/knowledge-detail.html` | `/api/knowledge` | 청크 상세 |
| `/knowledge-label-matching` | `knowledge/knowledge-label-matching.html` | `/api/knowledge`, `/api/labels` | 라벨 매칭 |
| `/knowledge-relation-matching` | `knowledge/knowledge-relation-matching.html` | `/api/relations` | 관계 매칭 |
| `/document/{path}` | `document.html` | `/api/documents` | 문서 뷰어 |
| `/knowledge-admin` | `knowledge/knowledge-admin.html` | `/api/knowledge`, `/api/approval/chunks` | 지식 관리(승인 연계) |

---

### 2.2 관리자 메뉴 — 지식 관리 (우측)

| 순서 | 메뉴 | 경로 | Frontend (HTML) | 주요 Backend API | 기능 요약 |
|------|------|------|-----------------|------------------|-----------|
| 1 | 키워드 관리 | `/admin/groups` | `admin/groups.html` | `/api/labels` (그룹·키워드) | 키워드 그룹 CRUD |
| 2 | 라벨 관리 | `/admin/labels` | `admin/labels.html` | `/api/labels` | 라벨 CRUD |
| 3 | 청크 생성 | `/admin/chunk-create` | `admin/chunk-create.html` | `/api/knowledge`, ingest | 청크 생성·임베딩 |
| 4 | 청크 승인 | `/admin/approval` | `admin/approval.html` | `/api/approval/chunks` | 승인 대기 청크 승인/반려 |
| 5 | 청크 관리 | `/admin/chunk-labels` | `admin/chunk-labels.html` | `/api/knowledge`, `/api/labels` | 청크·라벨 매핑 |
| 6 | 통계 | `/admin/statistics` | `admin/statistics.html` | `/api/system/statistics` | 프로젝트·청크·통계 |

---

### 2.3 설정 관리 메뉴 (Phase 11-3)

| 순서 | 메뉴 | 경로 | Frontend (HTML) | 주요 Backend API | 기능 요약 |
|------|------|------|-----------------|------------------|-----------|
| 1 | 템플릿 | `/admin/settings/templates` | `admin/settings/templates.html` | `/api/admin/schemas`, `/api/admin/templates` | 스키마·템플릿 CRUD |
| 2 | 프리셋 | `/admin/settings/presets` | `admin/settings/presets.html` | `/api/admin/presets` | 프리셋 CRUD |
| 3 | RAG 프로필 | `/admin/settings/rag-profiles` | `admin/settings/rag-profiles.html` | `/api/admin/rag-profiles` | RAG 프로필 CRUD |
| 4 | 정책 | `/admin/settings/policy-sets` | `admin/settings/policy-sets.html` | `/api/admin/policy-sets` | 정책 세트 CRUD |
| 5 | 변경 이력 | `/admin/settings/audit-logs` | `admin/settings/audit-logs.html` | `/api/admin/audit-logs` | 감사 로그 조회 |

---

## 3. Backend 구조 요약

### 3.1 라우터 (API prefix)

| Prefix | 패키지 | 역할 |
|--------|--------|------|
| `/api/auth` | auth | 인증 (JWT·API Key) |
| `/api/search` | search | 검색 |
| `/api/documents` | search/documents | 문서 조회 |
| `/api/system` | system | 시스템·백업·무결성·통계 |
| `/api/ask` | ai | AI 질의 |
| `/api/conversations` | ai | 대화 기록 |
| `/api/logs` | system/logs | 로그 |
| `/api/labels` | knowledge/labels | 라벨·키워드 그룹 |
| `/api/knowledge` | knowledge | 청크·지식 |
| `/api/approval/chunks` | knowledge/approval | 청크 승인 |
| `/api/relations` | knowledge/relations | 관계 |
| `/api/knowledge-integration` | knowledge | 지식 통합 |
| `/api/reason` | reasoning (reason, reason_stream, reason_store) | 추론·스트리밍·ETA·공유·의사결정 |
| `/api/reason/recommendations` | reasoning/recommendations | 추천 |
| `/api/reasoning-chain` | reasoning | 추론 체인 |
| `/api/reasoning-results` | reasoning | 추론 결과 목록 |
| `/api/context` | cognitive/context | 맥락 |
| `/api/memory` | cognitive/memory | 기억 |
| `/api/learning` | cognitive/learning | 학습 |
| `/api/personality` | cognitive/personality | 성격 |
| `/api/metacognition` | cognitive/metacognition | 메타인지 |
| `/api/automation` | automation | 자동화 |
| `/api/workflow` | automation/workflow | 워크플로우 |
| `/api/file-parser` | ingest | 파일 파싱 |
| `/api/admin/*` | admin | Admin 설정 (schemas, templates, presets, rag-profiles, policy-sets, audit-logs) |

### 3.2 서비스 계층 (backend/services)

| 패키지 | 역할 |
|--------|------|
| ai/ | Ollama 클라이언트·컨텍스트 관리 |
| search/ | 검색·하이브리드·리랭커·문서 동기화 |
| knowledge/ | 구조 매칭·자동 라벨러·지식 통합 |
| reasoning/ | 동적 추론·추론 체인·추천 |
| cognitive/ | 맥락·기억·학습·메타인지·성격 |
| automation/ | 작업 플랜·워크플로우 태스크 |
| ingest/ | 파일 파싱·HWP 파서 |
| system/ | 무결성·로깅·통계 |

### 3.3 모델·DB

| 경로 | 역할 |
|------|------|
| backend/models/models.py | Project, Document, KnowledgeChunk, Label, KnowledgeLabel, ReasoningResult 등 |
| backend/models/admin_models.py | Admin용 (Schema, Template, RAG Profile, Policy Set 등) |
| backend/models/database.py | 세션·DB 초기화 |

---

## 4. Frontend 구조 요약

### 4.1 디렉터리

| 경로 | 역할 |
|------|------|
| `web/src/pages/` | HTML 페이지 (경로별 1:1 대응) |
| `web/public/css/` | 페이지·admin·reason 등 CSS |
| `web/public/js/` | 페이지별 JS, components/, admin/, reason/, knowledge/ 등 |
| `web/public/js/components/` | header-component, layout-component, pagination-component 등 공통 |

### 4.2 페이지 ↔ JS·CSS 대응 (예)

| 페이지 | JS | CSS |
|--------|-----|-----|
| dashboard | dashboard/dashboard.js | dashboard.css |
| search | search/search.js | search.css |
| reason | reason/reason*.js (reason.js, reason-control.js, reason-render.js 등) | reason.css |
| ask | ask/ask.js | ask.css |
| knowledge | knowledge/knowledge.js | knowledge/knowledge.css |
| admin/* | admin/*.js, admin/settings/*.js | admin/*.css, admin/settings-common.css |

---

## 5. 기능·메뉴 매트릭스 (요약)

| 기능 | 사용자 메뉴 | 관리자 메뉴 | 설정 메뉴 | API prefix |
|------|-------------|-------------|-----------|------------|
| 대시보드·통계 | ✅ dashboard | ✅ statistics | - | /api/system, /api/system/statistics |
| 검색 | ✅ search | - | - | /api/search, /api/documents |
| 지식·청크·라벨 | ✅ knowledge, knowledge-* | ✅ groups, labels, chunk-*, approval | - | /api/knowledge, /api/labels, /api/approval, /api/relations |
| Reasoning | ✅ reason | - | - | /api/reason (stream, eta, share, decisions) |
| AI 질의 | ✅ ask | - | - | /api/ask |
| 로그 | ✅ logs | - | - | /api/logs |
| Admin 설정 | - | - | ✅ templates, presets, rag-profiles, policy-sets, audit-logs | /api/admin/* |

---

## 6. Admin 설정 관리 운영 가이드 (Phase 11)

### 6.1 Admin 설정 데이터 흐름

```
schemas (Role 스키마 정의)
    ↓
templates (Role별 시스템 프롬프트 템플릿)
    ↓
presets (사용자 입력 프롬프트 프리셋)
    ↓
rag_profiles (검색 전략·청크 설정)
    ↓
policy_sets (AI 응답 제약·정책)
    ↓
audit_logs (모든 변경 이력 기록)
```

**데이터 흐름 설명**:
1. **schemas**: 6가지 Role(coordinator, searcher, thinker, critic, writer, summarizer) 정의
2. **templates**: 각 Role에 맞는 시스템 프롬프트 템플릿 저장
3. **presets**: 사용자가 자주 사용하는 프롬프트를 템플릿으로 저장
4. **rag_profiles**: 검색 전략(하이브리드·벡터·키워드), 청크 크기, 오버랩 설정
5. **policy_sets**: AI 응답 시 준수해야 할 정책 (금지어, 제약사항 등)
6. **audit_logs**: 모든 Admin 설정 변경을 자동 기록 (사용자, 시간, 변경 전/후)

### 6.2 감사 로그(Audit Logs) 정책

| 항목 | 내용 |
|------|------|
| **추적 범위** | schemas, templates, presets, rag_profiles, policy_sets 전체 CRUD |
| **기록 내용** | 변경 사용자, 변경 시간, 변경 유형(CREATE/UPDATE/DELETE), 변경 전 값, 변경 후 값 |
| **보존 정책** | 무기한 보존 (DB 용량 모니터링 필요) |
| **조회 권한** | Admin 페이지에서 조회 가능 (`/admin/settings/audit-logs`) |
| **롤백 기능** | Phase 11-2-3에서 구현 예정 (현재는 수동 복원) |

**조회 API**:
```
GET /api/admin/audit-logs?table_name=templates&limit=100&offset=0
```

### 6.3 백업/복원 절차 (SOP)

#### 수동 백업

```bash
# 1. PostgreSQL DB 전체 백업
docker exec pab-postgres pg_dump -U brain knowledge > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Qdrant 벡터 DB 백업
tar -czf qdrant_backup_$(date +%Y%m%d_%H%M%S).tar.gz qdrant-data/

# 3. 지식 파일 백업
tar -czf brain_backup_$(date +%Y%m%d_%H%M%S).tar.gz brain/
```

#### API 백업 (Phase 9-4-3)

```bash
# 백업 생성
curl -X POST http://localhost:8001/api/backup/create

# 백업 목록
curl http://localhost:8001/api/backup/list

# 백업 복원 (백업 ID 필요)
curl -X POST http://localhost:8001/api/backup/restore/{backup_id}
```

#### 복원 절차

```bash
# 1. 컨테이너 중지
docker-compose down

# 2. PostgreSQL 복원
cat backup_20260208_120000.sql | docker exec -i pab-postgres psql -U brain knowledge

# 3. Qdrant 복원
rm -rf qdrant-data/
tar -xzf qdrant_backup_20260208_120000.tar.gz

# 4. 재시작
docker-compose up -d
```

### 6.4 Admin 설정 변경 시 영향 범위

| 설정 유형 | 변경 시 영향 | 적용 시점 | 주의사항 |
|----------|-------------|----------|----------|
| **schemas** | Reasoning 실행 시 Role 구조 변경 | 즉시 (다음 실행부터) | 기존 저장된 결과에는 영향 없음 |
| **templates** | 시스템 프롬프트 변경 | 즉시 (다음 API 호출부터) | AI 응답 품질 변화 가능 |
| **presets** | 사용자 프롬프트 기본값 변경 | 즉시 (프리셋 선택 시) | 기존 대화 이력에는 영향 없음 |
| **rag_profiles** | 검색 결과 및 품질 변경 | 즉시 (다음 검색부터) | 청크 크기 변경 시 재임베딩 필요 없음 |
| **policy_sets** | AI 응답 필터링 규칙 변경 | 즉시 (다음 응답부터) | 과도한 제약은 AI 품질 저하 가능 |

**변경 권장 시간**: 사용자가 적은 시간대 (예: 야간, 새벽)

### 6.5 에러 핸들링 및 롤백

#### 설정 변경 실패 시

```bash
# 1. 에러 로그 확인
docker logs pab-backend

# 2. DB 무결성 검사
curl -X POST http://localhost:8001/api/integrity/check

# 3. Audit Log 확인 (최근 변경 이력)
curl "http://localhost:8001/api/admin/audit-logs?limit=10"
```

#### 수동 롤백 (Phase 11-2-3 자동 롤백 구현 전)

```bash
# 1. Audit Log에서 변경 전 값 확인
# 2. Admin UI에서 수동으로 이전 값 입력
# 3. 또는 SQL 직접 수정:
docker exec -it pab-postgres psql -U brain knowledge
# UPDATE templates SET content = '이전 값' WHERE id = 123;
```

### 6.6 권한 관리 (현재 상태)

| 항목 | Phase 11 구현 상태 | Phase 12 계획 |
|------|-------------------|---------------|
| **인증** | JWT/API Key (Phase 9-1) 구현 완료 | 역할 기반 접근 제어(RBAC) |
| **Admin 접근** | 인증된 사용자 모두 접근 가능 | Admin 전용 역할 분리 |
| **감사 로그** | 변경 이력 기록 (사용자 추적) | 승인 워크플로우 (Draft→Review→Publish) |
| **API 보안** | Rate Limiting, CORS (Phase 9-1) | IP 화이트리스트, 2FA |

**현재 접근 제어**:
```
.env 설정:
AUTH_ENABLED=false  # 개발 환경 (인증 비활성화)
AUTH_ENABLED=true   # 프로덕션 환경 (인증 필수)
```

### 6.7 성능 모니터링 및 지표

#### 주요 지표 확인

```bash
# 1. 시스템 통계 대시보드
http://localhost:8001/admin/statistics

# 2. API 통계
curl http://localhost:8001/api/system/statistics/dashboard

# 3. DB 연결 풀 상태
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT * FROM pg_stat_activity;"

# 4. Qdrant 컬렉션 상태
curl http://localhost:6333/collections
```

#### 성능 임계값

| 지표 | 정상 범위 | 경고 | 조치 필요 |
|------|-----------|------|-----------|
| **API 응답 시간** | < 200ms | 200-500ms | > 500ms |
| **DB 연결 수** | < 20 | 20-50 | > 50 |
| **메모리 사용량** | < 2GB | 2-4GB | > 4GB |
| **Qdrant 검색 시간** | < 100ms | 100-300ms | > 300ms |

---

## 7. 개발 워크플로우

### 7.1 로컬 개발 환경 설정

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd personal-ai-brain-v2

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (POSTGRES_PASSWORD, JWT_SECRET_KEY 등)

# 3. Docker 컨테이너 실행
docker-compose up -d

# 4. Ollama 모델 다운로드
docker exec -it ollama ollama pull qwen2.5:7b

# 5. DB 마이그레이션 (최초 1회)
docker exec pab-postgres psql -U brain -d knowledge -f /scripts/db/migrate_phase11_1_1.sql

# 6. 시드 데이터 (선택)
docker exec pab-postgres psql -U brain -d knowledge -f /scripts/db/seed_phase11_1_schemas.sql
```

### 7.2 테스트 실행 방법

#### 통합 테스트 (pytest)

```bash
# 전체 테스트
pytest tests/

# 특정 모듈
pytest tests/test_admin_api.py

# 커버리지 포함
pytest --cov=backend tests/
```

#### E2E 테스트 (Playwright)

```bash
# 전체 E2E 테스트
npx playwright test

# 특정 Phase 테스트
npx playwright test e2e/phase-11-3.spec.js

# UI 모드 (디버깅)
npx playwright test --ui
```

#### 웹 테스트 (webtest.py)

```bash
# Phase 11-3 웹 테스트
python scripts/webtest.py 11-3 start

# MCP-Cursor 시나리오
npx playwright test e2e/phase-10-1-mcp-scenarios.spec.js
```

### 7.3 디버깅 가이드

#### Backend 로그 확인

```bash
# 실시간 로그
docker logs -f pab-backend

# 특정 시간대 로그
docker logs --since 30m pab-backend

# 에러 로그만
docker logs pab-backend 2>&1 | grep ERROR
```

#### Database 디버깅

```bash
# PostgreSQL 콘솔 접속
docker exec -it pab-postgres psql -U brain knowledge

# 테이블 확인
\dt

# Admin 설정 테이블 조회
SELECT * FROM schemas LIMIT 10;
SELECT * FROM templates LIMIT 10;

# Audit Log 조회
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 20;
```

#### Qdrant 디버깅

```bash
# 컬렉션 목록
curl http://localhost:6333/collections

# 컬렉션 상세 정보
curl http://localhost:6333/collections/{collection_name}

# 벡터 검색 테스트
curl -X POST http://localhost:6333/collections/{collection_name}/points/search \
  -H "Content-Type: application/json" \
  -d '{"vector": [...], "limit": 5}'
```

---

## 8. 문제 해결 (Troubleshooting)

### 8.1 컨테이너 관련 문제

#### 컨테이너가 시작되지 않을 때

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs

# 컨테이너 재시작
docker-compose restart backend

# 전체 재시작 (데이터 유지)
docker-compose down
docker-compose up -d

# 완전 초기화 (데이터 삭제 주의!)
docker-compose down -v
docker-compose up -d
```

#### 포트 충돌

```bash
# 포트 사용 확인
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6333  # Qdrant
lsof -i :11434 # Ollama

# 프로세스 종료
kill -9 <PID>
```

### 8.2 DB 관련 문제

#### 마이그레이션 실패

```bash
# 마이그레이션 히스토리 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT * FROM alembic_version;"

# 수동 마이그레이션
docker exec pab-postgres psql -U brain -d knowledge -f /scripts/db/migrate_phase11_1_1.sql
```

#### 데이터 무결성 검사

```bash
# API를 통한 무결성 검사
curl -X POST http://localhost:8001/api/integrity/check

# 수동 검사 (SQL)
docker exec -it pab-postgres psql -U brain knowledge
# SELECT COUNT(*) FROM schemas;
# SELECT COUNT(*) FROM templates;
```

### 8.3 API 관련 문제

#### API 응답 없음

```bash
# Backend 상태 확인
docker ps | grep pab-backend

# 헬스체크
curl http://localhost:8001/api/system/health

# OpenAPI 문서 확인
http://localhost:8001/docs
```

#### 인증 오류

```bash
# 개발 환경에서 인증 비활성화
# .env 파일 수정
AUTH_ENABLED=false

# 컨테이너 재시작
docker-compose restart backend
```

### 8.4 검색 관련 문제

#### 검색 결과 없음

```bash
# Qdrant 컬렉션 확인
curl http://localhost:6333/collections

# 문서 임베딩 상태 확인
curl http://localhost:8001/api/documents

# 재임베딩 (필요 시)
# Admin UI → 청크 생성 페이지에서 재업로드
```

#### Ollama 모델 로딩 실패

```bash
# 모델 목록 확인
docker exec -it ollama ollama list

# 모델 다운로드
docker exec -it ollama ollama pull qwen2.5:7b

# 모델 테스트
docker exec -it ollama ollama run qwen2.5:7b "안녕하세요"
```

---

## 9. 참고 문서

| 문서 | 용도 |
|------|------|
| [README.md](../../README.md) | 프로젝트 진입·요약·빠른 시작 |
| [docs/README/03-development-progress.md](../README/03-development-progress.md) | 개발 진행·Phase별 링크 |
| [docs/phases/phase-11-navigation.md](../phases/phase-11-navigation.md) | Phase 11 작업 순서·현황 |
| [docs/phases/phase-11-master-plan.md](../phases/phase-11-master-plan.md) | Phase 11 계획 (Admin 설정 관리) |
| [backend/routers/README.md](../../backend/routers/README.md) | Backend 라우터 용도별 구조 |
| [docs/devtest/README.md](../devtest/README.md) | 통합 테스트 가이드 |
| [docs/webtest/README.md](../webtest/README.md) | 웹 테스트 수행 가이드 |
| [docs/rules/rules-index.md](../rules/rules-index.md) | 개발 규칙 통합 인덱스 |

---

## 부록

### A. 주요 환경 변수

```env
# Database
POSTGRES_USER=brain
POSTGRES_PASSWORD=brain_password
POSTGRES_DB=knowledge

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b

# Auth (Phase 9-1)
AUTH_ENABLED=false  # 개발: false, 프로덕션: true
JWT_SECRET_KEY=your-secret-key-change-in-production

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### B. Phase별 주요 변경사항

| Phase | 주요 변경 | DB 변경 | API 변경 |
|-------|----------|---------|----------|
| Phase 9 | 보안·테스트·AI 고도화 | - | JWT/API Key, Rate Limit |
| Phase 10 | Reasoning Lab 고도화 | reasoning_results 확장 | SSE 스트리밍, ETA, 공유 |
| Phase 11 | Admin 설정 관리 | schemas, templates, presets, rag_profiles, policy_sets, audit_logs | /api/admin/* (6개 테이블 CRUD) |
| Phase 11-5 | Phase 10 고도화 | - | 성능 개선, 시각화 향상 |

### C. 포트 매핑

| 서비스 | 포트 | 용도 |
|--------|------|------|
| Backend | 8000 | FastAPI API 서버 |
| PostgreSQL | 5432 | 관계형 DB |
| Qdrant | 6333 | Vector DB API |
| Qdrant (gRPC) | 6334 | Vector DB gRPC |
| Ollama | 11434 | 로컬 LLM API |

---

**작성일**: 2026-02-08  
**최종 수정**: 2026-02-08  
**다음 업데이트**: Phase 12 완료 시
