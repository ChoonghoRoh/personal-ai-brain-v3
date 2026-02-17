# Task 15-3-1: [BE] 지정 폴더/문서 대상 Reasoning API

**우선순위**: 15-3 내 1순위
**의존성**: 15-1 (폴더 관리), 15-2 (자동화)
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

지정 문서(document_ids) 또는 폴더 경로(folder_path)에 대해 기존 Reasoning 엔진을 실행하는 전용 API 3개를 구현한다. 기존 `/api/reason` 과 별도의 `/api/reasoning/run-on-documents` 경로를 사용하여 문서 단위 Reasoning을 명확히 분리한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/reasoning/reason_document.py` | 신규 | 전용 라우터 (3 API) |
| `backend/routers/reasoning/__init__.py` | 수정 | reason_document import/export 추가 |
| `backend/main.py` | 수정 | reason_document.router 등록 |

## §3. 작업 체크리스트 (Done Definition)

- [x] `POST /api/reasoning/run-on-documents` 구현
  - RunOnDocumentsRequest: document_ids, folder_path, mode, question, template_id, model
  - document_ids / folder_path 해석 → 문서 ID 목록 산출
  - 청크 수집 → 관계 확장 → LLM Reasoning → 결과 저장
  - RunOnDocumentsResponse: session_id, task_id, message, document_count, chunk_count
- [x] `GET /api/reasoning/run-on-documents/status/{task_id}` 구현
  - 현재 동기 실행이므로 항상 completed 반환
  - 비동기 확장 시 실제 진행 상태 반환 구조 사전 정의
- [x] `GET /api/reasoning/results-by-documents?document_ids=1,2,3` 구현
  - ReasoningResult의 recommendations.document_ids 매칭으로 문서별 결과 필터링
  - DocumentReasoningResult 응답: document_id, document_name, results[]
- [x] `__init__.py`, `main.py` 등록

## §4. 참조

- `backend/routers/reasoning/reason_document.py` — 산출물
- `backend/routers/reasoning/reason.py` — 청크 수집 함수 재사용
- `docs/phases/phase-15-master-plan.md` §5.2 — API 인터페이스 정의
