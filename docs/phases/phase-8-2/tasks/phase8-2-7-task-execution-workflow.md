# Phase 8-2-7: Task 실행 워크플로우 (Claude-Code 실행 자동화)

**작성일**: 2026-01-28  
**기준 워크플로우**: Phase Auto Checker v1 (문서 구조·노드 명명 규칙 적용)  
**개선안**: `docs/n8n/workflow/Task Execution v1 Workflow Improvement Plan.md`  
**관련 문서**: phase8-2-6-task-test-plan-generation.md, phase8-master-plan.md, `docs/n8n/rules/n8n node nameing Rules.md`

---

## 1. Workflow 목적

이 workflow의 목적은 다음을 자동으로 수행하는 것이다.

1. **workflow_tasks** 테이블에서 status='pending'인 Task 1건 조회  
2. 해당 Task의 **task-N-plan.md**(plan_doc) 내용을 Claude API(또는 동등 에이전트)에 전달  
3. **실제 코드/파일 작업 수행** (Backend API `POST /api/workflow/run-task` 호출)  
4. 완료 시 **workflow_tasks.status** 갱신 (HTTP 응답 기반 → completed / failed)  
5. (선택) Discord 알림 전송  
6. 다음 Task 반복 또는 **Phase 8-2-8(테스트·결과 저장)** 트리거

즉,

**Todo-list로 정의된 Task .md를 문서가 아닌 실행 단위로 다루고,  
문서(Plan) = 입력, 상태(DB) = 다음 행동 트리거**

로 동작하는 Task 실행 엔진이다.

---

## 2. 참조 파일 구조

### 2.1 Task 산출물 디렉토리

**경로**

```
docs/phases/tasks/
```

**검사/입력 대상 파일**

- `task-{N}-plan.md` — 실행할 Task Plan (또는 DB의 plan_doc)
- `task-{N}-test.md` — (8-2-8에서 사용) Test Plan

**출력**

- 스크립트가 워크스페이스에서 코드/파일 변경 수행
- (8-2-8에서) `task-{N}-result.md` 생성

이 디렉토리와 DB의 **workflow_tasks** 조합으로 Task 상태를 판단한다.

---

### 2.2 규칙 / 판단 문서 (AI·워크플로우 기준)

| 문서 | 역할 |
|------|------|
| docs/n8n/rules/n8n node nameing Rules.md | 노드 명명 규칙 (PREFIX_VerbObject) |
| docs/n8n/workflow/Task Execution v1 Workflow Improvement Plan.md | 본 워크플로우 개선안·STEP 구성 |
| (선택) docs/ai/ | Task Plan 형식, 완료 기준 등 AI 판단 규칙 |

---

### 2.3 시스템 컨텍스트 문서

| 문서/리소스 | 역할 |
|-------------|------|
| README.md | 프로젝트 개요 (참고용, 직접 판단 로직에는 미사용) |
| PostgreSQL workflow_tasks | task_id, phase_id, task_name, status, plan_doc, test_plan_doc, completed_at |
| Backend API `POST /api/workflow/run-task` | Task 실행 핵심 (n8n에서 HTTP Request로 호출) |
| scripts/n8n/run_task_execution.py | CLI용 Task 실행 스크립트 (선택, 동일 로직은 Backend 서비스에 구현) |

---

### 2.4 Workflow Node Naming 규칙 문서

**docs/n8n/rules/n8n node nameing Rules.md**

- 워크플로우 생성 시 노드 이름 규칙: **PREFIX_VerbObject**
- 노드 이름만으로 역할·책임 파악 가능
- Phase, 자동화, 로그, 오류 추적 시 일관된 기준점으로 사용

---

## 3. 전체 실행 흐름

**STEP 0. Manual Trigger**

- 수동 실행 트리거 (개발/테스트용)
- 향후 Phase 8-2-6 완료 Webhook 트리거로 대체 가능

---

**STEP 1. Pending Task 조회**

**DB_SelectPendingTask**

- PostgreSQL: `SELECT * FROM workflow_tasks WHERE status = 'pending' ORDER BY id LIMIT 1`
- 모든 실행의 기준점이 되는 Task 1건 선택

---

**STEP 2. 실행 여부 분기**

**IF_HasPendingTask**

- 조회 결과가 있음 → 실행 분기
- 없음 → 종료 또는 8-2-8 트리거

---

**STEP 3. 실행 payload 정리**

**JS_PrepareTaskPayload**

- task_id, task_name, plan_doc(또는 plan 파일 경로), workspace root 등 정리
- HTTP_RunTaskExecution 노드에 전달할 요청 body 구성 (`task_id` 등)

---

**STEP 4. Task 실행 (핵심)**

**HTTP_RunTaskExecution**

- HTTP Request: `POST {{ BACKEND_URL }}/api/workflow/run-task`
- Body: `{ "task_id": {{ $json.id }} }`
- Backend에서 Task 조회 → plan_doc 기반 Claude API 호출 → 워크스페이스에서 작업 수행 → 응답으로 success/실패 반환
- n8n 실행 환경에 Python/venv가 없어도 동작 (실행은 Backend 서버에서 수행)

---

**STEP 5. Task 상태 갱신**

**JS_SetTaskStatusFromResponse** → **DB_UpdateTaskStatus**

- HTTP 응답(statusCode, body.success)으로 성공/실패 판단 → `status`: `completed` 또는 `failed`
- DB_UpdateTaskStatus: `UPDATE workflow_tasks SET status = $1, completed_at = NOW() WHERE id = $2`
- (선택) result_doc 또는 로그는 Backend 응답에서 저장하거나 별도 노드로 보강

---

**STEP 6. 알림 (선택)**

**DISCORD_SendTaskComplete**

- "Task-N 실행 완료" 메시지 전송
- 실패 시: **DISCORD_SendTaskFailure** (선택)

---

**STEP 7. 다음 Task 또는 8-2-8 트리거**

**LOOP_NextTaskOrTrigger**

- 남은 pending Task가 있으면 STEP 1로 반복
- 없으면 Phase 8-2-8(테스트·결과 저장) 워크플로우 트리거

---

## 4. 구현 상세

### 4.1 Backend API (n8n 기본 경로)

**엔드포인트**: `POST /api/workflow/run-task`  
**구현**: `backend/routers/workflow.py`, `backend/services/workflow_task_service.py`

**역할**

- Body: `{ "task_id": N }`
- DB에서 Task(plan_doc 등) 조회 → Claude API로 Task Plan 수행 → 워크스페이스에서 코드/파일 작업
- 응답: `{ "success": true/false, ... }` → n8n의 JS_SetTaskStatusFromResponse에서 status 결정

**n8n에서 Python/venv 없이 동작**: 실행은 Backend 서버에서 하므로, n8n은 HTTP 호출만 담당.

### 4.2 CLI 스크립트 (선택)

**파일**: `scripts/n8n/run_task_execution.py`

- 인자: `--task-id N` 등
- 동일 로직을 CLI에서 실행할 때 사용 (필요 시 Backend API를 호출하도록 연동 가능)

**Claude 호출 방식 (Backend 서비스 기준)**

| 옵션 | 설명 |
|------|------|
| A. Anthropic API | Backend 서비스에서 Python SDK 사용 (권장) |
| B. 백엔드 /run-task | n8n HTTP Request로 호출 (현재 방식) |
| C. CLI 스크립트 | run_task_execution.py (로컬/CI용) |

**Task Plan .md 권장 형식**

- 목표 (한 문장)
- 단계별 작업 목록 (번호/체크리스트)
- 작업 디렉토리/파일
- 완료 기준

---

## 5. Workflow 성격 요약

이 workflow는 다음 철학을 따른다.

- **DB(workflow_tasks)를 상태 머신으로 사용**
- **문서(plan_doc / task-N-plan.md) = 실행 입력**
- **상태(status) = 다음 행동 트리거** (pending → 실행 → completed → 8-2-8)
- **AI(Claude)는 규칙 집행자** — Task Plan대로 수행

즉, Phase Auto Checker v1과 동일하게

**문서 = 상태, 상태 = 다음 행동 트리거**

구조를 유지한다.

---

## 6. 향후 리팩토링 분리 기준 (가이드)

권장 분리 단위:

1. **Pending Task 조회·분기** (DB_SelectPendingTask, IF_HasPendingTask)
2. **Task 실행** (JS_PrepareTaskPayload, HTTP_RunTaskExecution, JS_SetTaskStatusFromResponse)
3. **상태 갱신·알림** (DB_UpdateTaskStatus, DISCORD_SendTaskComplete)
4. **반복·다음 워크플로우** (LOOP_NextTaskOrTrigger → 8-2-8)

이 문서는 위 분리를 위한 기준 문서로 사용한다.

---

## 7. 완료 기준

- [ ] Backend `POST /api/workflow/run-task` 구현 및 단일 Task 실행 검증
- [ ] Claude API로 Task Plan 1건 실제 수행 가능 (파일 변경 또는 명확한 출력)
- [ ] n8n 워크플로우에서 위 **노드 이름(PREFIX_VerbObject)** 적용하여 구성 (HTTP_RunTaskExecution, JS_SetTaskStatusFromResponse)
- [ ] DB_SelectPendingTask → HTTP_RunTaskExecution → JS_SetTaskStatusFromResponse → DB_UpdateTaskStatus 흐름 동작
- [ ] (선택) DISCORD_SendTaskComplete
- [ ] 문서: 실행 방법 및 실패 시 확인 사항

---

## 8. 리스크 및 대응

| 리스크 | 대응 |
|--------|------|
| Claude가 코드 변경 없이 설명만 함 | system 프롬프트에 "반드시 파일 수정/생성", "코드 블록은 적용 가능 형태" 명시 |
| 장시간 실행으로 n8n 타임아웃 | 스크립트 백그라운드 실행 + 폴링/Webhook 완료 감지 |
| 동시 실행 충돌 | pending 1건만 조회, 한 번에 1 Task만 실행 |

---

## 9. 다음 단계

**Phase 8-2-8**: Task 실행(8-2-7) 완료 시 **결과물 테스트 및 결과 저장** 워크플로우.

- 입력: 8-2-7 완료 Task (workflow_tasks.id, task-N-test.md)
- 출력: 테스트 실행, workflow_test_results 저장, task-N-result.md

---

## 10. 관련 문서

- `docs/n8n/workflow/Phase Auto Checker v1 Workflow.md` — 동일 문서 구조·철학 참조
- `docs/n8n/rules/n8n node nameing Rules.md` — 노드 명명 규칙
- `docs/n8n/workflow/Task Execution v1 Workflow Improvement Plan.md` — 개선안
- `phase8-2-6-task-test-plan-generation.md` — Task Plan/Test Plan 생성
- `phase8-2-8-task-test-and-store-workflow.md` — 테스트 및 결과 저장 플랜
- `phase8-1-1-database-schema-n8n-setting.md` — workflow_tasks 스키마

---

**문서 버전**: 2.1  
**최종 업데이트**: 2026-01-28 — CMD → HTTP(Backend API) 방식 반영, HTTP_RunTaskExecution·JS_SetTaskStatusFromResponse 문서화
