# Task 17-4-2: [BE] 이어서 질문 API (session_id + 컨텍스트 주입)

**우선순위**: 17-4 내 2순위
**예상 작업량**: 큰
**의존성**: 17-4-1 (세션 API)
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

POST /api/reason/stream에 session_id 파라미터를 추가하고, 이전 대화 턴의 Q&A 요약을 LLM 프롬프트에 자동 주입한다. 답변 완료 후 결과를 session_id와 함께 자동 저장한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/reasoning/reason_stream.py` | ReasonStreamRequest에 session_id 필드 추가 |
| 수정 | `backend/services/reasoning/stream_executor.py` | 이전 턴 조회 + 컨텍스트 주입 + 자동 저장 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] ReasonStreamRequest에 session_id: Optional[str] 추가
- [ ] session_id 있으면 이전 ReasoningResult 조회 (최근 3턴, created_at 정렬)
- [ ] 이전 턴 요약을 시스템 프롬프트에 주입: "이전 대화 맥락: ..."
- [ ] 답변 완료 후 ReasoningResult 자동 저장 (session_id 포함)
- [ ] session_id 없으면 기존 동작 그대로 (하위 호환)

## §4. 참조

- stream_executor.py: execute_reasoning_with_progress() 함수
- LLM 프롬프트 주입 위치: 4단계 AI Reasoning 직전
