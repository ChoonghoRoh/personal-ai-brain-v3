# Task 15-3-5: [API] 인터페이스 명세

**우선순위**: 15-3 내 5순위
**의존성**: 15-3-1, 15-3-2
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Phase 15-3에서 구현한 Document Reasoning API의 OpenAPI 명세와 Pydantic 스키마를 정의한다. Swagger UI에 "Document Reasoning" 태그로 그룹화되어 표시된다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/main.py` | 수정 | openapi_tags에 "Document Reasoning" 태그 추가 |
| `backend/routers/reasoning/reason_document.py` | 포함 | Pydantic 스키마 정의 |

## §3. 작업 체크리스트 (Done Definition)

### OpenAPI 태그
- [x] `{"name": "Document Reasoning", "description": "지정 문서 대상 추론 (Phase 15-3)"}` 추가

### Pydantic 스키마
- [x] `RunOnDocumentsRequest`
  - document_ids: Optional[List[int]]
  - folder_path: Optional[str]
  - mode: str = "design_explain"
  - question: Optional[str]
  - template_id: Optional[str]
  - model: Optional[str]
- [x] `RunOnDocumentsResponse`
  - session_id: str
  - task_id: str
  - message: str
  - document_count: int
  - chunk_count: int
- [x] `DocumentReasoningResult`
  - document_id: int
  - document_name: Optional[str]
  - results: list
- [x] `TaskStatusResponse`
  - task_id: str
  - status: str
  - progress: int
  - current_document: Optional[str]
  - message: Optional[str]

## §4. 참조

- `backend/routers/reasoning/reason_document.py` — 스키마 정의
- `backend/main.py` — OpenAPI 태그 등록
- `docs/phases/phase-15-master-plan.md` §5.4 — 인터페이스 요약
