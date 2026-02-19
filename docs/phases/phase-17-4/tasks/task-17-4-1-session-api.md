# Task 17-4-1: [BE] 세션 관리 API

**우선순위**: 17-4 내 1순위
**예상 작업량**: 중간
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

멀티턴 대화를 위한 세션 관리 API를 구현한다. 세션은 UUID로 식별되며, 세션 내 모든 ReasoningResult를 그룹핑한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/reasoning/reason_store.py` | 세션 CRUD 엔드포인트 4개 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] Pydantic 스키마: SessionCreateRequest, SessionResponse, SessionListResponse
- [ ] POST /api/reason/sessions — UUID 생성 + 첫 질문을 title로 사용 (또는 자동 생성)
- [ ] GET /api/reason/sessions — page/size 파라미터, total 포함 응답
- [ ] GET /api/reason/sessions/{session_id} — 세션 메타 + ReasoningResult 이력 반환
- [ ] DELETE /api/reason/sessions/{session_id} — 세션 + 관련 ReasoningResult 삭제

## §4. 참조

- 기존 모델: ReasoningResult.session_id (이미 인덱스됨)
- 기존 엔드포인트: /api/reasoning-results?session_id=... (참고용)
