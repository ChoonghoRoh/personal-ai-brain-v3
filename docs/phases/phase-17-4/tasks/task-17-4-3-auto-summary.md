# Task 17-4-3: [BE] 자동 요약 생성

**우선순위**: 17-4 내 3순위
**예상 작업량**: 중간
**의존성**: 17-4-2 (이어서 질문 API)
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

AI Reasoning 답변 완료 후 비동기로 Q&A 요약을 생성하여 ReasoningResult.summary 필드에 저장한다. 이 요약은 다음 턴에서 컨텍스트 주입 시 활용된다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/reasoning/stream_executor.py` | 요약 생성 비동기 태스크 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] 답변 완료 후 asyncio.create_task로 요약 생성 호출
- [ ] LLM에 질문+답변 전달 → 200자 이내 한국어 요약 생성
- [ ] ReasoningResult.summary 필드에 저장 (DB update)
- [ ] 요약 실패 시 로그만 남기고 에러 전파하지 않음 (사용자 경험 미영향)

## §4. 참조

- ReasoningResult.summary 필드: 이미 모델에 존재 (미활용 상태)
- 요약 프롬프트: "다음 질문과 답변을 200자 이내 한국어로 요약하세요."
