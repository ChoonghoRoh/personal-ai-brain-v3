# Phase 15-3 Todo List: 지정 폴더 파일 Reasoning

**Phase**: 15-3
**G1 판정**: PASS
**작성일**: 2026-02-17

---

- [x] Task 15-3-1: [BE] 지정 폴더/문서 대상 Reasoning API (Owner: backend-dev)
  - `POST /api/reasoning/run-on-documents` — document_ids 또는 folder_path 기반 Reasoning 실행
  - `GET /api/reasoning/run-on-documents/status/{task_id}` — 진행 상황 조회 (동기→completed)
  - `GET /api/reasoning/results-by-documents` — 문서별 결과 목록 조회
  - `reason_document.py` 라우터 신규 생성, `__init__.py` 및 `main.py` 등록

- [x] Task 15-3-2: [BE] Reasoning 모드·템플릿 연동 (Owner: backend-dev)
  - 4대 모드 (design_explain, risk_review, next_steps, history_trace) 지원
  - `dynamic_reasoning_service.generate_reasoning()` 연동
  - 기존 `collect_chunks_by_document_ids`, `collect_chunks_by_question_in_documents` 재활용
  - ReasoningResult에 document_ids 메타데이터 저장

- [x] Task 15-3-3: [FE] "이 폴더로 Reasoning" 진입점 (Owner: frontend-dev)
  - 파일관리 테이블에 체크박스 열 추가 (전체 선택 + 개별 선택)
  - "선택 문서 Reasoning" 벌크 액션 버튼
  - 선택 개수에 따른 버튼 활성/비활성 동적 업데이트

- [x] Task 15-3-4: [FE] Reasoning 실행·진행·결과 표시 (Owner: frontend-dev)
  - 모드 선택 모달 (4대 모드 라디오 + 질문 입력 필드)
  - `POST /api/reasoning/run-on-documents` 호출 → 결과 페이지 이동
  - 모달 CSS 스타일 (admin-knowledge-files.css)
  - 성공/실패 토스트 메시지

- [x] Task 15-3-5: [API] 인터페이스 명세 (Owner: backend-dev)
  - OpenAPI 태그 "Document Reasoning" 추가
  - RunOnDocumentsRequest/Response Pydantic 스키마 정의
  - DocumentReasoningResult, TaskStatusResponse 스키마 정의
