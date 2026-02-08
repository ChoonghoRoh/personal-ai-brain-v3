# Phase 9-3: AI 기능 고도화 - Todo List

**상태**: 대기 (Pending)
**우선순위**: 1 (최우선)
**예상 작업량**: 8.5일
**시작일**: -
**완료일**: -

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 9-3
- **Phase 명**: AI 기능 고도화 (AI Enhancement)
- **핵심 목표**: Reasoning 추천, RAG 강화, 지식구조 자동 매칭

### 다음 Phase

- **Next Phase ID**: 9-1
- **Next Phase 명**: 보안 강화 (Security Enhancement)
- **전환 조건**: 9-3 전체 Task 완료 및 테스트 통과

### Phase 우선순위 전체 현황

| 순위  | Phase                  | 상태      | 의존성        |
| ----- | ---------------------- | --------- | ------------- |
| **1** | **9-3 AI 기능 고도화** | 🔄 진행중 | -             |
| 2     | 9-1 보안 강화          | ⏳ 대기   | -             |
| 3     | 9-2 테스트 확대        | ⏳ 대기   | 9-1 부분 의존 |
| 4     | 9-4 기능 확장          | ⏳ 대기   | -             |
| 5     | 9-5 코드 품질          | ⏳ 대기   | -             |

---

## Task 목록

### 9-3-3: RAG 기능 강화 (기반 작업)

**우선순위**: 9-3 내 1순위 (다른 Task의 기반)
**예상 작업량**: 3일
**의존성**: 없음
**상태**: ✅ 1차 구현 완료 (2026-02-01)

- [x] Hybrid Search 구현 (키워드 + 의미 검색)

  - [x] 키워드 검색: PostgreSQL ILIKE 기반 (approved 청크)
  - [x] `backend/services/search/hybrid_search.py` 생성
  - [x] RRF(Reciprocal Rank Fusion) 점수 결합 로직
  - [x] SearchService search_mode 파라미터, search 라우터 hybrid/keyword 옵션

- [x] Reranking 구현

  - [x] Cross-encoder: ms-marco-MiniLM-L-6-v2 (config)
  - [x] `backend/services/search/reranker.py` 생성 (싱글톤 lazy 로딩)
  - [x] AI 라우터 use_reranking 옵션으로 파이프라인 적용

- [x] Context Manager 구현

  - [x] `backend/services/ai/context_manager.py` 생성
  - [x] 질문 복잡도 분석 (simple/complex)
  - [x] 컨텍스트 압축 (문장 단위 추출)
  - [x] 동적 컨텍스트 크기 (CONTEXT_MAX_TOKENS_SIMPLE/COMPLEX)

- [x] Multi-hop RAG 구현

  - [x] `backend/services/search/multi_hop_rag.py` 생성
  - [x] 관계 추적 기반 다단계 검색 (KnowledgeRelation)
  - [x] hop_trace 기록, AI 라우터 use_multihop 옵션

- [x] 기존 AI 라우터 개선

  - [x] `backend/routers/ai/ai.py` 수정 (search_mode, use_reranking, use_multihop)
  - [x] Hybrid Search / Reranking / ContextManager 적용 (옵션 시)
  - [x] 하위 호환 유지 (기본값 = 기존 동작)

- [x] 테스트 및 검증
  - [x] `tests/test_hybrid_search.py` 단위 테스트 (RRF 등)
  - [ ] RAG 품질 비교 테스트 (선택)

---

### 9-3-1: Reasoning AI 추천/샘플 기능 업그레이드

**우선순위**: 9-3 내 2순위
**예상 작업량**: 3일
**의존성**: 9-3-3 (RAG 강화) 완료 후 진행
**상태**: ✅ 1차 구현 완료 (2026-02-01)

- [x] RecommendationService 구현

  - [x] `backend/services/reasoning/recommendation_service.py` 생성
  - [x] `recommend_related_chunks()` (관계·Hybrid·동일 라벨)
  - [x] `recommend_labels()` (키워드·유사 청크 라벨)
  - [x] `generate_sample_questions()` (Ollama)
  - [x] `suggest_exploration()` (프로젝트/라벨 제안)

- [x] Recommendations API 구현

  - [x] `backend/routers/reasoning/recommendations.py` 생성
  - [x] `GET /api/reason/recommendations/chunks`
  - [x] `GET /api/reason/recommendations/labels`
  - [x] `GET /api/reason/recommendations/questions`
  - [x] `GET /api/reason/recommendations/explore`

- [x] LLM 기반 동적 추론 개선

  - [x] `backend/services/reasoning/dynamic_reasoning_service.py` 생성
  - [x] `backend/routers/reasoning/reason.py`: LLM 우선, 실패 시 템플릿 폴백
  - [x] ReasonResponse에 recommendations 필드 추가

- [x] Web UI 업데이트

  - [x] `web/src/pages/reason.html`: 관련 정보 섹션 (추천 청크/라벨/샘플 질문/추가 탐색), utils.js 로드
  - [x] `web/public/js/reason/reason.js`: displayRecommendations, displayRelatedChunks, displaySuggestedLabels, displaySampleQuestions, displayExploreMore, handleSampleQuestionClick, 패널 토글
  - [x] `web/public/css/reason.css`: 추천 카드·태그·샘플 질문·탐색 스타일

- [x] 테스트 및 검증
  - [x] `tests/test_reasoning_recommendations.py` 단위 테스트
  - [ ] UI 기능 테스트 (선택)

---

### 9-3-2: Data Import/CRUD 지식구조 자동 매칭

**우선순위**: 9-3 내 3순위
**예상 작업량**: 2.5일
**의존성**: 9-3-3 (RAG 강화) 완료 후 진행
**상태**: ✅ 1차 구현 완료 (2026-02-01)

- [x] StructureMatcher 구현

  - [x] `backend/services/knowledge/structure_matcher.py` 생성
  - [x] `match_on_chunk_create()` (라벨·유사 청크·카테고리)
  - [x] `suggest_relations_on_approve()` (동일 문서 순서·유사 청크 related_to)
  - [x] `find_similar_documents()` (유사 문서·shared_topics)

- [x] AutoLabeler 구현

  - [x] `backend/services/knowledge/auto_labeler.py` 생성
  - [x] `label_on_import()` (문서/청크별 라벨·카테고리)
  - [x] `suggest_category()` (경로·유사 문서)
  - [x] `apply_suggested_labels()` (추천 라벨 일괄 적용)

- [x] 기존 API 확장

  - [x] `GET /api/knowledge/chunks/{chunk_id}/suggestions` (청크 구조 추천)
  - [x] `GET /api/knowledge/documents/{document_id}/suggestions` (카테고리·유사 문서)
  - [x] `POST /api/approval/chunks/batch/approve` 응답에 suggested_relations 추가 (suggest_relations 쿼리)
  - [x] `POST /api/knowledge/chunks/{chunk_id}/labels/apply` (추천 라벨 적용)

- [x] 자동 매칭 설정 옵션

  - [x] config: AUTO*STRUCTURE_MATCHING_ENABLED, AUTO_LABEL_MIN_CONFIDENCE, MAX*\* 등
  - [x] approval: suggest_relations 쿼리 파라미터

- [x] 테스트 및 검증
  - [x] `tests/test_structure_matching.py` 단위 테스트
  - [ ] Import 시나리오 테스트 (선택)

---

## 완료 기준

### Phase 9-3 완료 조건

- [ ] 9-3-3 RAG 기능 강화 완료
- [ ] 9-3-1 Reasoning 추천 기능 완료
- [ ] 9-3-2 지식구조 자동 매칭 완료
- [ ] 전체 테스트 통과
- [ ] 문서 업데이트

### KPI 달성 기준

| 지표                  | 현재 | 목표 | 달성 |
| --------------------- | ---- | ---- | ---- |
| RAG 검색 정확도       | ~70% | 85%  | [ ]  |
| Reasoning 추천 활용률 | 0%   | 50%  | [ ]  |
| Import 자동 라벨링률  | 30%  | 80%  | [ ]  |

---

## 작업 로그

| 날짜 | Task | 작업 내용 | 상태 |
| ---- | ---- | --------- | ---- |
| -    | -    | -         | -    |

---

## 참고 문서

### Task 수행 결과 보고서 (2026-02-01)

- [Task 9-3-3 수행 결과 보고서](../../../phases/phase-9-3/phase-9-3-task-9-3-3-report.md)
- [Task 9-3-1 수행 결과 보고서](../../../phases/phase-9-3/phase-9-3-task-9-3-1-report.md)
- [Task 9-3-2 수행 결과 보고서](../../../phases/phase-9-3/phase-9-3-task-9-3-2-report.md)
- [Phase 9-3 API 검증 체크리스트](../../../phases/phase-9-3/phase-9-3-api-verification-checklist.md) — Task report 기반 API 2차 점검·샘플 데이터·점검 기록
- [Phase 9-3 Web 사용자 체크리스트](../../../phases/phase-9-3/phase-9-3-web-user-checklist.md) — 브라우저 기능 flow·메뉴(라우터)별 시나리오 점검

### Task 상세 문서

- [Task 9-3-3: RAG 기능 강화](../../../phases/phase-9-3/tasks/task-9-3-3-rag-enhancement.md) ★ 최우선
- [Task 9-3-1: Reasoning 추천](../../../phases/phase-9-3/tasks/task-9-3-1-reasoning-recommendation.md)
- [Task 9-3-2: 지식구조 매칭](../../../phases/phase-9-3/tasks/task-9-3-2-knowledge-structure-matching.md)
- [개발 진행 가이드](../../../phases/phase-9-3/tasks/task-develop-guide.md)

### Phase 문서

- [Phase 9 Master Plan](../../../phases/phase-9-master-plan.md)
- [Phase 9 Navigation](../../../phases/phase-9-navigation.md)
- [작업 지시사항](../../../phases/phase-9-work-instructions.md)
- [프롬프트 템플릿](../../../phases/phase-9-prompt-templates.md)

### 프로젝트 문서

- [프로젝트 분석 보고서](../../../review/2026-02-01-full-project-analysis-report.md)
