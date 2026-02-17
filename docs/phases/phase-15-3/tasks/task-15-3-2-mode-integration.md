# Task 15-3-2: [BE] Reasoning 모드·템플릿 연동

**우선순위**: 15-3 내 2순위
**의존성**: 15-3-1
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

run-on-documents API에서 4대 추론 모드(design_explain, risk_review, next_steps, history_trace)를 지원하고, 기존 dynamic_reasoning_service를 통해 LLM 추론을 실행한다. 결과를 ReasoningResult 테이블에 document_ids 메타데이터와 함께 저장한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/reasoning/reason_document.py` | 수정 | 모드별 처리 + LLM 연동 + 결과 저장 |

## §3. 작업 체크리스트 (Done Definition)

- [x] 4대 모드 지원: design_explain, risk_review, next_steps, history_trace
- [x] `dynamic_reasoning_service.generate_reasoning()` 호출 (LLM 우선)
- [x] LLM 실패 시 `generate_reasoning_answer()` 템플릿 폴백
- [x] 기존 함수 재사용:
  - `collect_chunks_by_document_ids()` — 문서 전체 청크 수집
  - `collect_chunks_by_question_in_documents()` — 문서 내 의미 검색
  - `expand_chunks_with_relations()` — 관계 확장
  - `build_context_chunks()` — 컨텍스트 구성
  - `collect_relations()` — 관계 정보
- [x] ReasoningResult에 `recommendations.document_ids` 메타데이터 저장
- [x] session_id (share_id) 기반 결과 공유 연동

## §4. 참조

- `backend/services/reasoning/dynamic_reasoning_service.py` — LLM 추론 서비스
- `backend/routers/reasoning/reason.py` — 청크 수집·확장 함수
- `backend/routers/reasoning/reason_store.py` — 결과 공유 패턴
