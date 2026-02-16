# Task 15-2-1: AI 자동화 API 엔드포인트 + SSE + 상태 관리

**우선순위**: 15-2 내 1순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

AI 자동화 워크플로우를 실행·관리하는 5개 API 엔드포인트와 SSE 진행 상황 스트리밍, 태스크 상태 관리를 구현한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/automation/automation.py` | 수정 | 5개 엔드포인트 추가 |
| `backend/services/automation/ai_workflow_state.py` | 신규 | 태스크 상태 관리 + SSE 유틸 |
| `tests/test_ai_automation_api.py` | 신규 | API 테스트 |

## §3. 작업 체크리스트 (Done Definition)

### API 엔드포인트
- [ ] `POST /api/automation/run-full` — 전체 워크플로우 실행
  - 요청: `{ document_ids: int[], auto_approve: bool = false }`
  - 응답: `{ task_id: str, message: str }`
  - BackgroundTasks로 비동기 실행
- [ ] `GET /api/automation/progress/{task_id}` — SSE 진행 상황
  - `StreamingResponse(media_type="text/event-stream")`
  - 이벤트: stage_name, progress_pct, message, status
- [ ] `POST /api/automation/cancel/{task_id}` — 실행 취소
  - cancel 플래그 설정 → 워크플로우에서 체크
- [ ] `GET /api/automation/tasks` — 태스크 목록
  - 최근 태스크 목록 (status, progress, created_at)
- [ ] `POST /api/automation/approve-pending` — 대기 항목 승인
  - 요청: `{ task_id: str }` 또는 `{ chunk_ids: int[] }`
  - 해당 태스크에서 생성된 draft 청크/라벨 일괄 승인

### 상태 관리 (ai_workflow_state.py)
- [ ] `active_tasks: Dict[str, TaskState]` 메모리 저장소
- [ ] TaskState: task_id, status(running/completed/failed/cancelled), progress_pct, current_stage, stages[], document_ids, created_at, results
- [ ] `create_task()`, `update_progress()`, `cancel_task()`, `get_task()`, `list_tasks()` 메서드
- [ ] SSE 이벤트 포맷: `format_sse_event(event, data)` (reason_stream.py 패턴)

### 공통
- [ ] `Depends(require_admin_knowledge)` 적용
- [ ] Pydantic 요청/응답 스키마 정의
- [ ] 테스트 추가

## §4. 참조

- `backend/routers/reasoning/reason_stream.py` — SSE + active_tasks 패턴
- `backend/routers/automation/automation.py` — 기존 라우터 구조
