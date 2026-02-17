# 500줄 초과 파일 인덱스 및 리팩토링 가이드

**작성일**: 2026-02-17
**최종 갱신**: 2026-02-17 (Phase 16-7-2 — 리팩토링 완료 반영)
**범위**: `backend/`, `web/`
**기준**: 500줄 초과 (해당 라인 수는 포함)

---

## 1. 인덱스 요약

### 1.1 리팩토링 전 (Phase 16 착수 시점)

| 구분 | 500줄 초과 파일 수 | 리팩토링 권장 대상 |
|------|-------------------|-------------------|
| Backend | 9 | 9 |
| Web JS | 10 | 9 (백업 제외) |
| Web CSS | 6 | 5 (settings-common 의도적 유지) |
| **합계** | **25** | **23** |

### 1.2 리팩토링 후 (Phase 16-4~16-6 완료)

| 구분 | 500줄 초과 잔존 | 감소율 | 비고 |
|------|:--------------:|:------:|------|
| Backend | 1 (503줄, 경계) | 89% | statistics_service.py |
| Web JS | 0 | 100% | reason_backup.js 삭제 포함 |
| Web CSS | 2 (597, 534줄) | 67% | reason-sections, settings-common |
| **합계** | **3** | **88%** | |

---

## 2. 파일 목록 — 리팩토링 전후 비교

### 2.1 Backend (Python)

| # | 원본 경로 | 전 (줄) | 후 (줄) | 분할 결과 | 상태 |
|---|----------|:-------:|:-------:|----------|:----:|
| 1 | `routers/knowledge/knowledge.py` | 792 | 274 | + knowledge_handlers.py (380), document_handlers.py (266), folder_management.py (452), approval.py (231), graph.py (129), relations.py (249), suggestions.py (259), knowledge_integration.py (78) | DONE |
| 2 | `services/reasoning/recommendation_service.py` | 646 | 248 | + recommendation_llm.py (420), dynamic_reasoning_service.py (197), reasoning_chain_service.py (162) | DONE |
| 3 | `routers/reasoning/reason_stream.py` | 642 | 164 | + stream_executor.py (497) | DONE |
| 4 | `routers/reasoning/reason.py` | 626 | 172 | + reason_helpers.py (484), reason_document.py (284), reason_store.py (187), reasoning_chain.py (52), reasoning_results.py (162), recommendations.py (128) | DONE |
| 5 | `routers/knowledge/labels.py` | 613 | 222 | + labels_handlers.py (494) | DONE |
| 6 | `main.py` | 558 | 450 | + lifecycle.py (116) | DONE |
| 7 | `routers/ai/ai.py` | 543 | 286 | + ai_handlers.py (298), conversations.py (185) | DONE |
| 8 | `services/automation/ai_workflow_service.py` | 570 | 256 | + ai_workflow_state.py (353), workflow_extract.py (409), workflow_finalize.py (323), workflow_task_service.py (238) | DONE |
| 9 | `services/system/statistics_service.py` | 503 | 503 | 현행 유지 (경계선) | KEEP |

**Backend 종합**: 9개 원본 → 43개 모듈, 개별 파일 최대 503줄 (경계)

### 2.2 Web — JavaScript

| # | 원본 경로 | 전 (줄) | 후 (줄) | 분할 결과 | 상태 |
|---|----------|:-------:|:-------:|----------|:----:|
| 1 | `reason/reason_backup.js` | 1216 | — | 참조 0건 확인 → **삭제** | DELETED |
| 2 | `admin/knowledge-files.js` | 922 | 411 | + knowledge-files-api.js (384), knowledge-files-tree.js (140) | DONE |
| 3 | `admin/label-manager.js` | 913 | 469 | + label-manager-api.js (314) | DONE |
| 4 | `dashboard/dashboard.js` | 749 | 321 | + dashboard-api.js (138) | DONE |
| 5 | `knowledge/knowledge-detail.js` | 691 | 258 | + knowledge-label-matching.js (258) | DONE |
| 6 | `admin/ai-automation.js` | 668 | 349 | + ai-automation-api.js (292) | DONE |
| 7 | `reason/reason-render.js` | 652 | 254 | + reason-render-viz.js (261) | DONE |
| 8 | `knowledge/knowledge-relation-matching.js` | 587 | 154 | + knowledge-relation-common.js (446) | DONE |
| 9 | `admin/chunk-approval-manager.js` | 572 | 322 | + chunk-approval-api.js (148) | DONE |
| 10 | `admin/statistics.js` | 519 | 254 | + statistics-charts.js (261) | DONE |

**추가 생성**: `admin-common.js`, `utils.js` (공통 유틸 추출)

**JS 종합**: 500줄 초과 파일 10개 → 0개 (개별 최대 469줄)

### 2.3 Web — CSS

| # | 원본 경로 | 전 (줄) | 후 (줄) | 분할 결과 | 상태 |
|---|----------|:-------:|:-------:|----------|:----:|
| 1 | `reason.css` | 1586 | 502 | + reason-sections.css (597), reason-advanced.css (485) | DONE |
| 2 | `knowledge/knowledge-detail.css` | 746 | 407 | + knowledge-detail-relations.css (339) | DONE |
| 3 | `admin/admin-knowledge-files.css` | 704 | 409 | + admin-knowledge-files-upload.css (295) | DONE |
| 4 | `knowledge/knowledge-admin.css` | 603 | 379 | + knowledge-admin-approval.css (224) | DONE |
| 5 | `admin/admin-ai-automation.css` | 595 | 379 | + admin-ai-automation-results.css (216) | DONE |
| 6 | `admin/settings-common.css` | 534 | 534 | 현행 유지 (5곳 HTML 공유) | KEEP |

**CSS 종합**: 500줄 초과 잔존 2개 (reason-sections 597줄, settings-common 534줄)

### 2.4 제외 (인덱스만, 리팩토링 대상 아님)

| 경로 | 줄 수 | 사유 |
|------|:-----:|------|
| `web/public/libs/mermaid/mermaid.min.js` | 2029 | 서드파티(minified) — 수정 금지 |
| ~~`web/public/js/reason/reason_backup.js`~~ | ~~1216~~ | **Phase 16-5-1에서 삭제 완료** |

---

## 3. 연관 파일 영향도 분석 — 리팩토링 완료 상태

### 3.1 공통 체크 항목 (파일별)

| 항목 | 설명 | 작성 예시 |
|------|------|----------|
| **직접 의존 (import/참조)** | 해당 파일을 import하거나 직접 참조하는 파일 목록 | `main.py` → `routers/knowledge/knowledge.py` 등록 |
| **역의존 (이 파일이 참조하는 모듈)** | 이 파일이 import·호출하는 모듈/API | `knowledge.py` → `knowledge_handlers`, `document_handlers` |
| **API 계약** | 변경 시 클라이언트(프론트/외부) 영향 | URL 경로·스키마 **변경 없음** (내부 분할만) |
| **테스트** | 해당 파일을 검증하는 테스트 경로 | `tests/test_knowledge_api.py` |
| **리팩토링 상태** | 완료 여부 | DONE / KEEP |

### 3.2 Backend 파일별 영향도 (리팩토링 후)

| 원본 파일 | 분할 모듈 | API 계약 변경 | 테스트 | 상태 |
|----------|----------|:------------:|--------|:----:|
| `knowledge.py` (792→274) | knowledge_handlers, document_handlers, folder_management, approval, graph, relations, suggestions, knowledge_integration | 없음 | test_knowledge*.py PASS | DONE |
| `recommendation_service.py` (646→248) | recommendation_llm, dynamic_reasoning_service, reasoning_chain_service | 없음 (내부) | test_reasoning*.py PASS | DONE |
| `reason_stream.py` (642→164) | stream_executor | 없음 | test_reason*.py PASS | DONE |
| `reason.py` (626→172) | reason_helpers, reason_document, reason_store, reasoning_chain, reasoning_results, recommendations | 없음 | test_reason*.py PASS | DONE |
| `labels.py` (613→222) | labels_handlers | 없음 | test_knowledge*.py PASS | DONE |
| `main.py` (558→450) | lifecycle | 없음 | test_api_routers PASS | DONE |
| `ai.py` (543→286) | ai_handlers, conversations | 없음 | test_ai*.py PASS | DONE |
| `ai_workflow_service.py` (570→256) | ai_workflow_state, workflow_extract, workflow_finalize, workflow_task_service | 없음 (내부) | test_ai_automation*.py PASS | DONE |
| `statistics_service.py` (503) | — | 없음 | test_statistics*.py PASS | KEEP |

### 3.3 Web 파일별 영향도 (리팩토링 후)

| 원본 파일 | 분할 모듈 | HTML `<script>` 추가 | 기능 변경 | 상태 |
|----------|----------|:-------------------:|:--------:|:----:|
| `knowledge-files.js` (922→411) | knowledge-files-api, knowledge-files-tree | 예 | 없음 | DONE |
| `label-manager.js` (913→469) | label-manager-api | 예 | 없음 | DONE |
| `dashboard.js` (749→321) | dashboard-api | 예 | 없음 | DONE |
| `knowledge-detail.js` (691→258) | knowledge-label-matching | 예 | 없음 | DONE |
| `ai-automation.js` (668→349) | ai-automation-api | 예 | 없음 | DONE |
| `reason-render.js` (652→254) | reason-render-viz | 예 | 없음 | DONE |
| `knowledge-relation-matching.js` (587→154) | knowledge-relation-common | 예 | 없음 | DONE |
| `chunk-approval-manager.js` (572→322) | chunk-approval-api | 예 | 없음 | DONE |
| `statistics.js` (519→254) | statistics-charts | 예 | 없음 | DONE |
| `reason.css` (1586→502) | reason-sections, reason-advanced | HTML `<link>` 추가 | 없음 | DONE |
| `knowledge-detail.css` (746→407) | knowledge-detail-relations | HTML `<link>` 추가 | 없음 | DONE |
| `knowledge-admin.css` (603→379) | knowledge-admin-approval | HTML `<link>` 추가 | 없음 | DONE |
| `admin-knowledge-files.css` (704→409) | admin-knowledge-files-upload | HTML `<link>` 추가 | 없음 | DONE |
| `admin-ai-automation.css` (595→379) | admin-ai-automation-results | HTML `<link>` 추가 | 없음 | DONE |
| `settings-common.css` (534) | — | — | 없음 | KEEP |

---

## 4. 리팩토링 방안 가이드

### 4.1 원칙

1. **한 번에 한 파일(또는 한 도메인)** — 대규모 동시 변경은 회귀 위험을 높이므로, 500줄 초과 파일을 우선순위대로 하나씩 줄인다.
2. **테스트·E2E 선행** — 리팩토링 전에 해당 영역 단위/E2E가 있으면 실행해 통과 상태를 확보하고, 리팩토링 후 다시 실행해 회귀 여부를 확인한다.
3. **연관 파일 영향도 먼저 정리** — §3의 항목(직접 의존, 역의존, API 계약, 테스트)을 채운 뒤 변경 범위를 정한 다음 리팩토링한다.
4. **기능 동일성 유지** — 외부 동작(API·UI)은 유지하고, 내부 구조(함수 분리·모듈 분할·스타일 분리)만 변경한다.

### 4.2 Backend 리팩토링 패턴 (Phase 16-4 적용)

| 패턴 | 적용 대상 | 방법 | Phase 16 실적 |
|------|----------|------|--------------|
| **라우터 → 라우터 + 핸들러** | knowledge, reason, labels, ai | 엔드포인트 함수를 `*_handlers.py`로 이동 | 5개 라우터 분할 완료 |
| **서비스 → 도메인별 서브 모듈** | recommendation, ai_workflow | 책임별로 서브 모듈 분리 | 2개 서비스 분할 완료 |
| **main.py 축소** | main.py | 이벤트 핸들러를 lifecycle.py로 추출 | 558→450줄 |

### 4.3 Web (JS) 리팩토링 패턴 (Phase 16-5 적용)

| 패턴 | 적용 대상 | 방법 | Phase 16 실적 |
|------|----------|------|--------------|
| **페이지 JS → API + UI** | 모든 Admin·Knowledge JS | API 호출을 `*-api.js`로 분리 | 9개 파일 분할 완료 |
| **공통 유틸 추출** | Admin 공통 | `admin-common.js`, `utils.js` 생성 | 2개 공통 모듈 추출 |
| **미사용 파일 제거** | reason_backup.js | 참조 0건 확인 후 삭제 | 1,216줄 제거 |

### 4.4 Web (CSS) 리팩토링 패턴 (Phase 16-6 적용)

| 패턴 | 적용 대상 | 방법 | Phase 16 실적 |
|------|----------|------|--------------|
| **기능 단위 분할** | reason, knowledge, admin CSS | 섹션별 파일 분리 + HTML `<link>` 추가 | 5개 파일 → 11개 |
| **의도적 유지** | settings-common.css | 5곳 HTML 공유 — 분할 시 수정 범위 과대 | 534줄 유지 |

### 4.5 실행 절차 (파일 하나 기준)

1. **§3 영향도** — 해당 파일 행에 직접 의존·역의존·API·테스트를 채운다.
2. **테스트 실행** — `pytest tests/` 또는 해당 E2E 스펙 실행 후 통과 확인.
3. **분할/추출 계획** — 어떤 함수/블록을 어떤 새 파일로 옮길지 목록으로 정리.
4. **작업** — 새 모듈 생성 → 코드 이동 → 기존 테스트/E2E 재실행.
5. **정리** — 이 문서의 해당 파일 줄 수·영향도 행을 갱신.

---

## 5. 문서 갱신 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-17 (초기) | 500줄 초과 25개 파일 인덱싱, 리팩토링 가이드 초안 |
| 2026-02-17 (16-7-2) | Phase 16-4~16-6 완료 반영: 전후 비교 테이블, 영향도 검증 완료, 잔존 3개 파일 기록 |

---

## 6. 참조

- Phase 16 마스터 플랜: `docs/phases/phase-16-master-plan.md`
- Phase Chain 16: `docs/phases/phase-chain-16.md`
- AI 자동화 리스크 분석: `docs/planning/260217-1600-AI자동화기능-리스크분석.md`
- SSOT 4th: `docs/SSOT/renewal/iterations/4th/0-entrypoint.md`
