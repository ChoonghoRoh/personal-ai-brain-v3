# Task 17-4-4: [BE] 페이지네이션 + 다중 삭제 API

**우선순위**: 17-4 내 4순위
**예상 작업량**: 작음
**의존성**: 17-4-1 (세션 API)
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

세션 목록 조회에 페이지네이션을 적용하고, 다중 세션 일괄 삭제 API를 추가한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/reasoning/reason_store.py` | 페이지네이션 응답 + bulk delete 엔드포인트 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] GET /api/reason/sessions 응답에 total, page, size, total_pages 포함
- [ ] DELETE /api/reason/sessions/bulk — { session_ids: [...] } 배열로 다중 삭제
- [ ] Pydantic: BulkDeleteRequest, PaginatedSessionResponse 스키마
- [ ] 삭제 시 관련 ReasoningResult도 cascade 삭제

## §4. 참조

- 17-4-1에서 구현한 세션 API 기반 확장
