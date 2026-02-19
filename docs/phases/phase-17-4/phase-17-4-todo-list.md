# Phase 17-4 Todo List — AI 질의 고도화: 멀티턴 대화 + 기록 관리

**Phase**: 17-4
**기준**: [phase-17-4-plan.md](phase-17-4-plan.md)

---

- [ ] Task 17-4-1: [BE] 세션 관리 API (Owner: backend-dev)
  - `backend/routers/reasoning/reason_store.py` 수정
  - POST /api/reason/sessions — 세션 생성 (UUID + title 자동 생성)
  - GET /api/reason/sessions — 세션 목록 (page/size + total)
  - GET /api/reason/sessions/{session_id} — 세션 상세 (대화 이력 포함)
  - DELETE /api/reason/sessions/{session_id} — 세션 삭제 (관련 ReasoningResult 포함)
  - Pydantic 스키마 정의
  - 완료 기준: 4개 엔드포인트 정상 동작

- [ ] Task 17-4-2: [BE] 이어서 질문 API (Owner: backend-dev)
  - `backend/routers/reasoning/reason_stream.py` 수정
  - `backend/services/reasoning/stream_executor.py` 수정
  - ReasonStreamRequest에 session_id 필드 추가
  - 이전 턴 조회 (session_id + created_at 정렬)
  - 이전 Q&A 요약을 LLM 프롬프트에 주입 (최근 3턴)
  - 답변 완료 후 ReasoningResult 자동 저장 (session_id 포함)
  - 완료 기준: session_id 전달 시 이전 대화 맥락이 LLM에 반영

- [ ] Task 17-4-3: [BE] 자동 요약 생성 (Owner: backend-dev)
  - `backend/services/reasoning/stream_executor.py` 수정
  - 답변 완료 후 비동기 요약 생성 (asyncio.create_task)
  - LLM에 Q+A 전달 → 200자 이내 한국어 요약
  - ReasoningResult.summary 필드에 저장
  - 완료 기준: 답변 완료 후 summary 자동 생성·저장

- [ ] Task 17-4-4: [BE] 페이지네이션 + 다중 삭제 API (Owner: backend-dev)
  - `backend/routers/reasoning/reason_store.py` 수정
  - GET /api/reason/sessions — page/size 파라미터 + total 응답
  - DELETE /api/reason/sessions/bulk — session_ids 배열로 다중 삭제
  - 완료 기준: 페이지네이션 정상 동작 + 다중 삭제 정상 동작

- [ ] Task 17-4-5: [FE] 대화 스레드 UI + "이어서 질문하기" 버튼 (Owner: frontend-dev)
  - `web/src/pages/reason.html` 수정 — 대화 스레드 패널 추가
  - `web/public/js/reason/reason-control.js` 수정 — session_id 관리
  - `web/public/js/reason/reason.js` 수정 — 세션 초기화
  - 세션 상태 관리 (localStorage에 currentSessionId 저장)
  - 이전 턴 목록 패널 (왼쪽 사이드 또는 상단 탭)
  - "이어서 질문하기" 버튼 → session_id 유지
  - "새 대화 시작" 버튼 → 새 session_id 생성
  - 완료 기준: 멀티턴 대화 UI 정상 동작

- [ ] Task 17-4-6: [FE] 대화 기록 그리드 + 페이지네이션 + 선택 삭제 (Owner: frontend-dev)
  - `web/public/js/reason/reason-render.js` 수정 — 기록 목록 렌더링
  - `web/src/pages/reason.html` 수정 — 기록 탭/영역 추가
  - 세션 목록 카드뷰 (제목, 턴 수, 최근 질문, 생성일)
  - 페이지네이션 컨트롤
  - 체크박스 다중 선택 + "선택 삭제" 버튼
  - 세션 클릭 → 해당 세션 대화 로드
  - 완료 기준: 기록 그리드 + 페이지네이션 + 다중 삭제 정상 동작
