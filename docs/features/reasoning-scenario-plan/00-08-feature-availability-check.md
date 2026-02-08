# 00~08 · references 기능 점검 보고서

**점검일**: 2026-02-06  
**목적**: reasoning-scenario-plan 00~08 및 references 구현에 필요한 기능이 현재 코드베이스에 있는지 점검.  
**결과**: 기능 대부분 존재. 일부는 검증 전 개발(고도화) 목표·Task로 phase 11-6~11-15에 반영.

---

## 1. 점검 결과 요약

| 문서 | 요구 기능 | 현재 상태 | 검증 전 개발 필요 |
|------|-----------|-----------|-------------------|
| **00** Master Plan | 문서·Step 순서 | 존재 | 없음 |
| **01** Verification Data Index | 경로·매핑 문서 | 존재 | 없음 |
| **02** Stories/Scenarios | 스토리·시나리오 문서 | 존재 | 없음 |
| **03** Scenario Creation Guide | references 규칙·템플릿 | 존재 | 없음 |
| **04** DB Verification | reasoning_results, knowledge_* 테이블·스키마·시딩 | ORM create_all로 테이블 존재; scripts/db 전용 마이그레이션·시딩 없음 | **선택**: 버전 마이그레이션·시딩 보강 |
| **05** Qdrant Verification | brain_documents, search_simple, hybrid_search, point_id↔chunk | 존재 | 없음 |
| **06** Backend Verification | /api/reason, reasoning-results, recommendations, pytest | 라우터·테스트 모두 존재 | 없음(실행 가능 확인 Task만) |
| **07** Frontend Verification | reason.html, reason-*.js, DOM ID, 스크립트 순서 | 페이지·스크립트·ID 존재, 순서 일치 | 없음 |
| **08** Webtest MCP | 69개 시나리오 문서·실행·결과 기록 | 문서 있음; 실행은 수동/MCP | **검증 전**: 실행 환경·결과 기록 절차 확보 |
| **references** | ref 복사본·원본 미수정 | references/ 복사본 존재 | 없음 |

---

## 2. 상세 점검

### 2.1 Backend

| 항목 | 경로 | 상태 |
|------|------|------|
| POST /api/reason | backend/routers/reasoning/reason.py | ✅ |
| reason_stream (SSE·진행·취소) | reason_stream.py, main.py include_router | ✅ |
| reason_store (공유·의사결정 저장) | reason_store.py, main.py include_router | ✅ |
| reasoning-results CRUD | reasoning_results.py | ✅ |
| recommendations | recommendations.py | ✅ |
| reasoning-chain | reasoning_chain.py | ✅ |
| ReasoningResult, KnowledgeChunk, KnowledgeRelation, KnowledgeLabel | backend/models/models.py | ✅ |
| reasoning_results 테이블 생성 | database.py create_all | ✅ (전용 migrate 스크립트 없음) |
| search_simple, hybrid_search, brain_documents | search_service.py, hybrid_search.py, config | ✅ |
| test_reasoning_api.py, test_reasoning_recommendations.py | tests/ | ✅ |

### 2.2 Frontend

| 항목 | 경로 | 상태 |
|------|------|------|
| reason.html | web/src/pages/reason.html | ✅ |
| reason.js, reason-model.js, reason-common.js, reason-control.js, reason-render.js, reason-viz-loader.js, reason-pdf-export.js | web/public/js/reason/ | ✅ |
| 스크립트 로드 순서 | model → common → viz-loader → render → control → pdf-export → reason.js | ✅ |
| #question, #mode, #submit-btn, #cancel-btn, #results-loading, #progress-stages | reason.html · reason-control.js | ✅ |
| reason.css | web/public/css/reason.css | ✅ |

### 2.3 DB · Qdrant

| 항목 | 상태 |
|------|------|
| reasoning_results 테이블 (ORM) | ✅ create_all |
| knowledge_chunks, knowledge_relations, knowledge_labels (ORM) | ✅ create_all |
| scripts/db 전용 reasoning 마이그레이션·시딩 | ❌ 없음 (선택적 고도화) |
| Qdrant COLLECTION_NAME, search_simple, hybrid_search | ✅ |

### 2.4 E2E · Webtest

| 항목 | 경로 | 상태 |
|------|------|------|
| phase-10-1.spec.js, phase-10-1-mcp-scenarios.spec.js | e2e/ | ✅ |
| phase-10-2~10-4.spec.js | e2e/ | ✅ |
| phase-10-1 mcp-webtest-scenarios.md, result | docs/webtest/phase-10-1/ | ✅ |
| 08-webtest-mcp-reasoning-scenarios.md (69개 시나리오) | reasoning-scenario-plan/ | ✅ |
| 69개 시나리오 실행·결과 기록 절차 | 수동/MCP | 검증 전 확보 Task (11-14) |

### 2.5 references

| 항목 | 상태 |
|------|------|
| reasoning-lab-feature-report-ref.md, reason-lab-refactoring-design-ref.md | references/ | ✅ |

---

## 3. 검증 전 개발 반영 (phase 11-6 ~ 11-15)

기능이 **없거나 선택적 고도화**가 필요한 항목을 phase plan에 반영함.

| Phase | 검증 전 개발 목표 | Task 요약 |
|-------|-------------------|-----------|
| 11-6 | 없음 (00 문서만 검증) | — |
| 11-7 | 없음 (01 문서만 검증) | — |
| 11-8 | 없음 (02 문서만 검증) | — |
| 11-9 | 없음 (03 문서만 검증) | — |
| 11-10 | DB 검증 가능 상태 확보 | 선택: reasoning_results·knowledge_* 버전 마이그레이션·시딩 보강 또는 문서화 |
| 11-11 | 없음 (Qdrant 기능 존재) | — |
| 11-12 | Backend 검증 실행 가능 확보 | pytest 실행 가능 확인·누락 테스트 보강 |
| 11-13 | 없음 (Frontend 기능 존재) | — |
| 11-14 | Webtest MCP 실행 환경·결과 기록 확보 | 69개 시나리오 실행 가이드·결과 기록 적용 |
| 11-15 | 없음 (README 인덱스만 검증) | — |

상세 목표·Task는 각 `phase-11-Y/phase-11-Y-0-plan.md` §「검증 전 개발」에 기술.

---

**문서 위치**: `docs/features/reasoning-scenario-plan/00-08-feature-availability-check.md`
