# 500줄 초과 파일 인덱스 및 리팩토링 가이드

**작성일**: 2026-02-17  
**범위**: `backend/`, `web/`  
**기준**: 500줄 초과 (해당 라인 수는 포함)

---

## 1. 인덱스 요약

| 구분 | 500줄 초과 파일 수 | 리팩토링 권장 대상 |
|------|-------------------|-------------------|
| Backend | 10 | 10 |
| Web (JS/CSS/HTML) | 17 | 15 (lib·백업 제외) |
| **합계** | **27** | **25** |

- **제외**: `web/public/libs/mermaid/mermaid.min.js` (서드파티), `web/public/js/reason/reason_backup.js` (백업본)

---

## 2. 파일 목록 (줄 수 내림차순)

### 2.1 Backend (Python)

| # | 경로 | 줄 수 | 도메인 | 비고 |
|---|------|:-----:|--------|------|
| 1 | `backend/routers/knowledge/knowledge.py` | 792 | [BE] 지식 | 라우터 |
| 2 | `backend/services/reasoning/recommendation_service.py` | 646 | [BE] 추론 | 서비스 |
| 3 | `backend/routers/reasoning/reason_stream.py` | 642 | [BE] 추론 | 라우터 |
| 4 | `backend/routers/reasoning/reason.py` | 626 | [BE] 추론 | 라우터 |
| 5 | `backend/routers/knowledge/labels.py` | 613 | [BE] 지식 | 라우터 |
| 6 | `backend/main.py` | 558 | [BE] 진입점 | 앱·라우터 등록 |
| 7 | `backend/routers/ai/ai.py` | 543 | [BE] AI | 라우터 |
| 8 | `backend/services/automation/ai_workflow_service.py` | 570 | [BE] 자동화 | 서비스 |
| 9 | `backend/services/system/statistics_service.py` | 503 | [BE] 시스템 | 서비스 |

### 2.2 Web — JavaScript

| # | 경로 | 줄 수 | 도메인 | 비고 |
|---|------|:-----:|--------|------|
| 1 | `web/public/js/reason/reason_backup.js` | 1216 | [FE] Reasoning | **백업본 — 리팩토링 제외** |
| 2 | `web/public/js/admin/knowledge-files.js` | 922 | [FE] Admin | 지식 파일 관리 |
| 3 | `web/public/js/admin/label-manager.js` | 913 | [FE] Admin | 라벨 관리 |
| 4 | `web/public/js/dashboard/dashboard.js` | 749 | [FE] 대시보드 | 대시보드 |
| 5 | `web/public/js/knowledge/knowledge-detail.js` | 691 | [FE] 지식 | 지식 상세 |
| 6 | `web/public/js/admin/ai-automation.js` | 668 | [FE] Admin | AI 자동화 |
| 7 | `web/public/js/reason/reason-render.js` | 652 | [FE] Reasoning | 렌더링 |
| 8 | `web/public/js/knowledge/knowledge-relation-matching.js` | 587 | [FE] 지식 | 관계 매칭 |
| 9 | `web/public/js/admin/chunk-approval-manager.js` | 572 | [FE] Admin | 청크 승인 |
| 10 | `web/public/js/admin/statistics.js` | 519 | [FE] Admin | 통계 |

### 2.3 Web — CSS

| # | 경로 | 줄 수 | 도메인 | 비고 |
|---|------|:-----:|--------|------|
| 1 | `web/public/css/reason.css` | 1586 | [FE] Reasoning | 스타일 |
| 2 | `web/public/css/knowledge/knowledge-detail.css` | 746 | [FE] 지식 | 지식 상세 |
| 3 | `web/public/css/admin/admin-knowledge-files.css` | 704 | [FE] Admin | 지식 파일 |
| 4 | `web/public/css/knowledge/knowledge-admin.css` | 603 | [FE] 지식 | 지식 관리 |
| 5 | `web/public/css/admin/settings-common.css` | 534 | [FE] Admin | 설정 공통 |
| 6 | `web/public/css/admin/admin-ai-automation.css` | 512 | [FE] Admin | AI 자동화 |

### 2.4 제외 (인덱스만, 리팩토링 대상 아님)

| 경로 | 줄 수 | 사유 |
|------|:-----:|------|
| `web/public/libs/mermaid/mermaid.min.js` | 2029 | 서드파티(minified) — 수정 금지 |
| `web/public/js/reason/reason_backup.js` | 1216 | 백업본 — 참조 제거 후 삭제 검토 |

---

## 3. 연관 파일 영향도 분석 항목

리팩토링 전·후에 아래 항목을 채워 영향도를 관리한다.

### 3.1 공통 체크 항목 (파일별)

| 항목 | 설명 | 작성 예시 |
|------|------|----------|
| **직접 의존 (import/참조)** | 해당 파일을 import하거나 직접 참조하는 파일 목록 | `main.py` → `routers/knowledge/knowledge.py` 등록 |
| **역의존 (이 파일이 참조하는 모듈)** | 이 파일이 import·호출하는 모듈/API | `knowledge.py` → `knowledge_integration_service`, `chunk_sync_service` |
| **API 계약** | 변경 시 클라이언트(프론트/외부) 영향 | URL 경로, 요청/응답 스키마 |
| **테스트** | 해당 파일을 검증하는 테스트 경로 | `tests/test_knowledge_api.py` |
| **설정/라우트** | main·설정에 등록된 라우트/앱 바인딩 | `main.py` 내 `include_router(knowledge)` |
| **우선순위** | 리팩토링 순서 (1=높음) | 도메인 의존성·리스크 기준 |

### 3.2 Backend 파일별 영향도 템플릿

아래는 500줄 초과 백엔드 파일에 대해 **영향도 분석 시 채울 항목**이다.

| 파일 | 직접 의존 | 역의존(서비스/모델) | API 계약 | 테스트 | 우선순위 |
|------|----------|---------------------|----------|--------|:--------:|
| `routers/knowledge/knowledge.py` | main.py | knowledge_integration, chunk_sync, labels, … | `/api/knowledge/*` | test_knowledge*.py | 1 |
| `services/reasoning/recommendation_service.py` | reason.py, reason_stream.py, recommendations.py | reasoning_chain, DB | (내부) | test_reasoning*.py | 2 |
| `routers/reasoning/reason_stream.py` | main.py | recommendation_service, reason_store, … | `/api/reason/*` stream | test_reason*.py | 2 |
| `routers/reasoning/reason.py` | main.py | recommendation_service, reason_store, … | `/api/reason/*` | test_reason*.py | 2 |
| `routers/knowledge/labels.py` | main.py | labels 서비스, models | `/api/labels/*` | test_labels*.py | 1 |
| `main.py` | — (진입점) | 모든 라우터·미들웨어 | 전체 앱 | test_main, e2e | 3 |
| `routers/ai/ai.py` | main.py | ollama_client, context_manager | `/api/ai/*` | test_ai*.py | 2 |
| `services/automation/ai_workflow_service.py` | automation 라우터 | workflow_task_service, task_plan_generator | (내부) | test_automation*.py | 2 |
| `services/system/statistics_service.py` | routers/system/statistics.py | DB, models | (내부) | test_statistics*.py | 2 |

### 3.3 Web 파일별 영향도 템플릿

| 파일 | 직접 의존(참조) | 역의존(API/페이지) | 연관 HTML/CSS | 테스트/E2E | 우선순위 |
|------|-----------------|---------------------|---------------|------------|:--------:|
| `admin/knowledge-files.js` | admin 페이지 | `/api/...` 지식·청크 API | knowledge-files 관련 HTML | e2e/admin | 1 |
| `admin/label-manager.js` | admin 페이지 | `/api/labels/*` | labels HTML | e2e/admin | 1 |
| `dashboard/dashboard.js` | dashboard.html | `/api/statistics`, … | dashboard.css | e2e/smoke | 1 |
| `knowledge/knowledge-detail.js` | knowledge-detail.html | `/api/knowledge/*` | knowledge-detail.css | e2e/knowledge | 1 |
| `admin/ai-automation.js` | ai-automation 페이지 | `/api/automation/*` | admin-ai-automation.css | e2e/admin | 2 |
| `reason/reason-render.js` | reason.js, reason.html | `/api/reason/*` | reason.css | e2e/reason | 2 |
| `knowledge/knowledge-relation-matching.js` | relation-matching 페이지 | `/api/knowledge/relations/*` | knowledge CSS | e2e/knowledge | 2 |
| `admin/chunk-approval-manager.js` | approval 페이지 | `/api/chunks/*`, approval | admin-approval.css | e2e/admin | 2 |
| `admin/statistics.js` | statistics 페이지 | `/api/statistics/*` | statistics.css | e2e/admin | 2 |
| `reason.css` | reason.html, reason/*.js | — | reason-*.js | E2E | 2 |
| `knowledge-detail.css` | knowledge-detail.html | — | knowledge-detail.js | E2E | 2 |
| `admin-knowledge-files.css` | 지식 파일 관련 페이지 | — | knowledge-files.js | E2E | 2 |
| `knowledge-admin.css` | knowledge-admin.html | — | knowledge-admin.js | E2E | 2 |
| `settings-common.css` | 설정 공통 (presets, templates, …) | — | settings/*.js | E2E | 2 |
| `admin-ai-automation.css` | ai-automation 페이지 | — | ai-automation.js | E2E | 2 |

---

## 4. 리팩토링 방안 가이드

### 4.1 원칙

1. **한 번에 한 파일(또는 한 도메인)**  
   대규모 동시 변경은 회귀 위험을 높이므로, 500줄 초과 파일을 우선순위대로 하나씩 줄인다.
2. **테스트·E2E 선행**  
   리팩토링 전에 해당 영역 단위/E2E가 있으면 실행해 통과 상태를 확보하고, 리팩토링 후 다시 실행해 회귀 여부를 확인한다.
3. **연관 파일 영향도 먼저 정리**  
   §3의 항목(직접 의존, 역의존, API 계약, 테스트)을 채운 뒤 변경 범위를 정한 다음 리팩토링한다.
4. **기능 동일성 유지**  
   외부 동작(API·UI)은 유지하고, 내부 구조(함수 분리·모듈 분할·스타일 분리)만 변경한다.

### 4.2 Backend 리팩토링 패턴

| 패턴 | 적용 대상 예 | 방법 |
|------|-------------|------|
| **라우터 → 라우터 + 핸들러** | `knowledge.py`, `reason.py`, `labels.py` | 엔드포인트 함수를 별도 모듈(예: `knowledge_handlers.py`)로 이동, 라우터는 등록만 |
| **서비스 → 도메인별 서브 모듈** | `recommendation_service.py`, `ai_workflow_service.py` | 책임별로 `recommendation_*.py` 또는 내부 클래스/함수 그룹으로 분리 |
| **main.py 축소** | `main.py` | 라우터 등록을 `routers/__init__.py` 또는 `routers/registry.py`로 위임, 미들웨어 설정은 `config.py` 또는 전용 모듈로 |

**권장 순서 (의존성 고려)**  
1) 서비스 계층 (`recommendation_service`, `ai_workflow_service`, `statistics_service`)  
2) 라우터 계층 (`knowledge.py`, `labels.py`, `reason.py`, `reason_stream.py`, `ai.py`)  
3) `main.py` (라우터·미들웨어 정리)

### 4.3 Web (JS) 리팩토링 패턴

| 패턴 | 적용 대상 예 | 방법 |
|------|-------------|------|
| **페이지 JS → 기능별 모듈** | `knowledge-files.js`, `label-manager.js`, `dashboard.js` | `fetch·UI·이벤트` 등을 `knowledge-files-api.js`, `knowledge-files-ui.js` 등으로 분리, 메인 JS는 조합만 |
| **공통 유틸 추출** | 여러 Admin JS | 공통 API 호출·에러 처리·테이블 렌더링을 `admin-common.js` 또는 `utils/` 로 이동 |
| **Reason 모듈 정리** | `reason-render.js`, reason_backup 제거 | `reason_backup.js`는 참조 제거 후 삭제 검토, `reason-render.js`는 렌더/이벤트 분리 |

**권장 순서**  
1) 백업/미사용 제거 (`reason_backup.js` 참조 제거)  
2) Admin 대형 JS (`knowledge-files.js`, `label-manager.js`, `ai-automation.js`, `chunk-approval-manager.js`, `statistics.js`)  
3) Knowledge·Dashboard·Reason 메인 JS  
4) CSS는 컴포넌트/페이지 단위로 분할(선택)

### 4.4 Web (CSS) 리팩토링 패턴

| 패턴 | 적용 대상 예 | 방법 |
|------|-------------|------|
| **페이지/기능 단위 분할** | `reason.css`, `knowledge-detail.css` | `reason-control.css`, `reason-render.css` 등 기능별 파일로 분리 후 메인 CSS에서 `@import` 또는 HTML에서 다중 링크 |
| **공통 변수·유틸** | `settings-common.css`, admin 공통 | 변수·믹스인은 `admin-variables.css` 등으로 분리, 나머지는 페이지별로 유지 |
| **중복 제거** | 유사 스타일 반복 | 공통 클래스(.card, .table-actions 등)로 묶고, 페이지별 CSS는 오버라이드만 |

### 4.5 실행 절차 (파일 하나 기준)

1. **§3 영향도**  
   해당 파일 행에 직접 의존·역의존·API·테스트·우선순위를 채운다.
2. **테스트 실행**  
   `pytest tests/` 또는 해당 E2E 스펙 실행 후 통과 확인.
3. **분할/추출 계획**  
   어떤 함수/블록을 어떤 새 파일로 옮길지 목록으로 정리.
4. **작업**  
   새 모듈 생성 → 코드 이동 → 기존 파일은 re-export 또는 import만 유지 → 기존 테스트/E2E 재실행.
5. **정리**  
   이 문서의 해당 파일 줄 수·연관 파일 영향도 행을 갱신.

---

## 5. 문서 갱신

- **파일 추가/제거**: 500줄 기준 재측정 후 §2 테이블 수정.
- **영향도**: 리팩토링 진행 시 §3.2·§3.3 셀을 실제 의존 관계로 업데이트.
- **가이드**: 새로 쓰는 패턴이나 예외는 §4에 항목 추가.

---

## 6. 참조

- SSOT (코드 구조·검증): `docs/SSOT/claude/2-architecture-ssot.md`
- 테스트 전략: `docs/SSOT/claude/1-project-ssot.md` §5
- Phase 워크플로우: `docs/SSOT/claude/3-workflow-ssot.md`
