# Reasoning Scenario Plan — 개발 추가 필요 항목 발췌

**작성일**: 2026-02-06  
**목적**: reasoning-scenario-plan 폴더 문서(00~08, references)와 현재 개발 소스를 비교하여, **추가 개발이 필요한 부분**만 발췌·정리.  
**기준**: [00-08-feature-availability-check.md](00-08-feature-availability-check.md), [01-verification-data-index.md](01-verification-data-index.md), 04~08 검증 문서, references.

---

## 1. 요약

| 구분 | 추가 개발 필요 여부 | 내용 |
|------|---------------------|------|
| **DB** | 선택 | reasoning 전용 버전 마이그레이션·시딩 스크립트 없음 |
| **Backend** | 없음 | API·테스트·서비스 존재 |
| **Frontend** | 없음 | 페이지·스크립트·DOM ID·스크립트 순서 일치 |
| **Qdrant** | 없음 | search_simple, hybrid_search, brain_documents 존재 |
| **Webtest/E2E** | 있음 | 69개 시나리오 실행·결과 기록 절차·자동화 미정비 |
| **기타** | 참고 | 향후 확장 시 개발(문서 §12 등) |

---

## 2. DB (PostgreSQL) — 선택적 추가 개발

### 2.1 문서 요구 (04-verification-database, 01 §2)

- **reasoning_results**, **knowledge_chunks**, **knowledge_relations**, **knowledge_labels** 테이블 존재·검증.
- **Migrations / seed**: `scripts/db/`에 마이그레이션·시딩 스크립트 실행 후 테이블·컬럼 검증.

### 2.2 현재 소스 상태

- **ORM**: `backend/models/models.py`에 ReasoningResult, KnowledgeChunk, KnowledgeRelation, KnowledgeLabel 정의됨.
- **테이블 생성**: `backend/models/database.py`의 `Base.metadata.create_all(bind=engine)`로 생성됨.
- **scripts/db**: `migrate_phase11_1_*.sql`, `seed_phase11_1_*.sql`는 **Admin용**(schemas, templates, rag_profiles, policy_sets, audit_logs). **reasoning_results·knowledge_*** 전용 마이그레이션·시딩 스크립트 없음.

### 2.3 추가 개발 내용 (선택)

| 항목 | 내용 | 산출물 |
|------|------|--------|
| **버전 마이그레이션** | reasoning_results, knowledge_chunks, knowledge_relations, knowledge_labels(또는 기존 공통 마이그레이션에 포함)에 대한 **버전 관리용 SQL 마이그레이션** 추가 | `scripts/db/migrate_reasoning_*.sql` 또는 기존 마이그레이션에 섹션 추가 |
| **시딩 스크립트** | 검증·재현용 **reasoning 시나리오 데이터 시딩** (선택). 예: 샘플 reasoning_results, approved knowledge_chunks | `scripts/db/seed_reasoning_*.sql` 또는 문서화로 “create_all + 기존 시딩으로 충분” 명시 |

**참고**: 현재는 create_all로 테이블이 생성되므로, “재현성·버전 관리”가 필요할 때만 위 항목을 추가하면 됨.

---

## 3. Backend — 추가 개발 없음

### 3.1 문서 요구 (06-verification-backend, 01 §4)

- POST `/api/reason`, reasoning-results CRUD, recommendations, reasoning-chain, reason_stream, reason_store.
- Pytest: test_reasoning_api.py, test_reasoning_recommendations.py.
- 01 §3: hybrid_search — "tests in test_hybrid_search.py **if present**".

### 3.2 현재 소스 상태

- 라우터·서비스·모델 모두 존재. main.py에 라우터 등록됨.
- `tests/test_reasoning_api.py`, `tests/test_reasoning_recommendations.py` 존재.
- `tests/test_hybrid_search.py` 존재.

### 3.3 추가 개발 내용

- **없음.**  
- (선택) pytest 실행 가능 여부·환경(DB·Ollama 등) 문서화 또는 CI에서 skip 조건 명시.

---

## 4. Frontend — 추가 개발 없음

### 4.1 문서 요구 (07-verification-frontend, 01 §5)

- reason.html, reason.js, reason-model.js, reason-common.js, reason-control.js, reason-render.js, reason-viz-loader.js, reason-pdf-export.js, reason.css.
- DOM ID: #question, #progress-stages, #progress-bar, #progress-message, #reasoning-elapsed-text, #eta-display, #eta-text, #cancel-btn, #submit-btn, #results-loading, #results-content, #reasoning-steps 등.
- 스크립트 로드 순서: utils → model → common → render → control → reason.js (설계서 기준; 현재는 viz-loader, pdf-export 포함).

### 4.2 현재 소스 상태

- 위 파일·경로 모두 존재. reason.html에 #progress-bar, #progress-message, #reasoning-elapsed-text, #eta-display, #eta-text, #submit-btn, #cancel-btn, #results-loading, #progress-stages 등 존재.
- 스크립트 순서: model → common → viz-loader → render → control → pdf-export → reason.js.

### 4.3 추가 개발 내용

- **없음.**

---

## 5. Qdrant — 추가 개발 없음

### 5.1 문서 요구 (05-verification-qdrant, 01 §3)

- Collection brain_documents, search_simple, hybrid_search, point_id ↔ chunk 매핑.

### 5.2 현재 소스 상태

- config, search_service, hybrid_search, reason.py에서 사용 확인됨.

### 5.3 추가 개발 내용

- **없음.**

---

## 6. Webtest / E2E — 추가 개발 필요

### 6.1 문서 요구 (08-webtest-mcp-reasoning-scenarios)

- **69개 시나리오** (진입·네비게이션 11, 질문·모드 12, 실행·진행·취소 12, 결과 표시 12, 추천 11, 저장·공유·에러 11).
- 형식: 시나리오 # | 제목 | 조치 | 기대 결과 | 검증 방법.
- Base URL `http://localhost:8000`, MCP cursor-ide-browser 또는 cursor-browser-extension.

### 6.2 현재 소스 상태

- **08-webtest-mcp-reasoning-scenarios.md**: 69개 시나리오 **문서**는 존재.
- **실행·결과 기록**: 수동/MCP 기준; 69개 전체에 대한 **실행 가이드·결과 기록 템플릿·자동화**는 미정비.
- E2E: phase-10-1.spec.js, phase-10-1-mcp-scenarios.spec.js 등 존재하나, 08의 69개 시나리오와 1:1 매핑된 Playwright 스펙은 없음.

### 6.3 추가 개발 내용

| 항목 | 내용 | 산출물 |
|------|------|--------|
| **실행 가이드** | 69개 시나리오를 MCP 또는 수동으로 실행하는 **순서·환경·도구** 안내 | docs/webtest 또는 08 문서 내 §실행 가이드 |
| **결과 기록 템플릿** | 시나리오별 통과/실패·비고를 기록하는 **고정 형식** (예: 표 또는 체크리스트) | 08 문서 하단 또는 docs/webtest/phase-reasoning/ 결과 템플릿 |
| **자동화(선택)** | 08 시나리오와 대응하는 **Playwright(또는 E2E) 스펙** 추가로 69개 또는 대표 시나리오 자동 실행 | e2e/phase-reasoning-mcp-scenarios.spec.js 등 |

---

## 7. references·설계서 — 추가 개발 없음 (참고만)

### 7.1 reason-lab-refactoring-design-ref

- **§6 마이그레이션 순서**: reason-model.js, reason-common.js, reason-render.js, reason-control.js, reason.js, HTML 수정, 회귀 테스트.
- **현재**: 해당 파일 분리·로드 순서 반영 완료. reason-viz-loader.js, reason-pdf-export.js는 설계서의 “reason-mode-viz.js (선택)”에 대응하는 확장으로 보면 됨.

### 7.2 reasoning-lab-feature-report-ref

- **§12 확장 포인트**: 새 추론 모드 추가, 검색 알고리즘 개선, 새 추천 유형 추가.  
- **성격**: “향후 확장 시” 개발 항목이므로, **현재 계획 대비 추가 개발 필수 항목**에는 포함하지 않음. 필요 시 별도 확장 계획에서 다룸.

---

## 8. 정리 (추가 개발 체크리스트)

| # | 구분 | 추가 개발 내용 | 우선순위 | 비고 |
|---|------|----------------|----------|------|
| 1 | DB | reasoning_results·knowledge_* 버전 마이그레이션·시딩 스크립트 (선택) | 낮음 | 재현성·버전 관리 필요 시 |
| 2 | Webtest | 69개 시나리오 실행 가이드·결과 기록 템플릿 | 높음 | 검증 실행·기록용 |
| 3 | Webtest | 08 시나리오 대응 E2E/Playwright 자동화 (선택) | 중간 | 자동 회귀용 |

**문서 위치**: `docs/features/reasoning-scenario-plan/development-gaps-extract.md`
