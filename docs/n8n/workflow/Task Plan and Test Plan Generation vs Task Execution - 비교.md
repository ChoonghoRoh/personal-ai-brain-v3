# Task Plan and Test Plan Generation v1 (test) vs Task Execution v1 — 비교

두 워크플로우는 **역할이 다름**. Generation은 Task·Test Plan을 만들고 `workflow_tasks`에 **INSERT**, Execution은 `workflow_tasks`에서 **pending 조회** 후 Backend로 실행하고 **UPDATE**함.

---

## 1. 목적·Phase

| 항목 | Task Plan and Test Plan Generation v1 (test) | Task Execution v1 |
|------|-----------------------------------------------|-------------------|
| **Phase** | 8-2-6 (Task Plan & Test Plan 생성) | 8-2-7 (Task 실행) |
| **목적** | Todo 항목별로 phaseX-Y-N-task.md, phaseX-Y-N-task-test-result.md 생성 후 `workflow_tasks` INSERT | pending Task 1건 조회 → Backend 실행 → status 갱신 (completed/failed) |
| **입력** | 수동 트리거 + 테스트용 고정 Todo 2건 | 수동 트리거 (DB에서 pending 조회) |
| **출력** | 파일(phaseX-Y-N-task.md, phaseX-Y-N-task-test-result.md) + workflow_tasks INSERT | workflow_tasks UPDATE, (선택) Discord 알림 |

---

## 2. 노드 구성 비교

### Task Plan and Test Plan Generation v1 (test)

| 순서 | 노드 이름 | 타입 | 역할 |
|------|-----------|------|------|
| 0 | Trigger_Manual | Manual Trigger | 수동 실행 |
| 1 | SET_TestTodoList | Set | phase_id=1 등 테스트 입력 |
| 2 | JS_ExpandTodoItems | Code | 테스트용 Todo 2건 배열 생성 |
| 3 | LOOP_TodoItems | Split In Batches | 항목별 1건씩 루프 (batchSize=1) |
| 4 | JS_CreateTaskPlanAndTestPlan | Code | Task Plan/Test Plan 텍스트 + base64 생성 |
| 5 | CMD_WriteTaskFiles | Execute Command | mkdir + base64 디코드로 phaseX-Y-N-task.md, phaseX-Y-N-task-test-result.md 쓰기 (docs/phases/phase-X-Y/tasks/) |
| 6 | DB_InsertWorkflowTask | Postgres | workflow_tasks **INSERT** |
| 7 | DISCORD_SendTaskPlansComplete | Discord | (기본 disabled) 완료 알림 |

**루프:** DB_InsertWorkflowTask → LOOP_TodoItems (다음 항목). LOOP_TodoItems 출력 2(done) → DISCORD.

### Task Execution v1

| 순서 | 노드 이름 | 타입 | 역할 |
|------|-----------|------|------|
| 0 | Trigger_Manual | Manual Trigger | 수동 실행 |
| 1 | DB_SelectPendingTask2 | Postgres | workflow_tasks **SELECT** (status='pending' 1건) |
| 2 | JS_NormalizePendingTaskResult2 | Code | 0/1건 → hasTask 플래그 정규화 |
| 3 | IF_HasPendingTask2 | If | hasTask 분기 |
| 4a | JS_PrepareTaskPayload2 | Code | task_id 등 Backend용 payload 준비 |
| 5a | HTTP_RunTaskExecution2 | HTTP Request | Backend POST /api/workflow/run-task |
| 6a | JS_SetTaskStatusFromResponse1 | Code | 응답에서 success → status (completed/failed) 파생 |
| 7a | DB_UpdateTaskStatus2 | Postgres | workflow_tasks **UPDATE** status, completed_at |
| 8a | Send a message1 | Discord | Task 실행 완료 알림 |
| 9a | LOOP_NextTaskOrTrigger2 | Code | 다음 워크플로우 또는 재실행용 패스스루 |
| 4b | SET_NoPendingTask2 | Set | pending 없을 때 메시지 설정 |

**분기:** IF true → 4a~9a, IF false → 4b.

---

## 3. 다른 부분 요약

| 구분 | Task Plan and Test Plan Generation | Task Execution |
|------|-------------------------------------|----------------|
| **Postgres** | **INSERT** (phase_id, task_name, status='pending', plan_doc, test_plan_doc) | **SELECT** pending 1건 → 후속 **UPDATE** (status, completed_at) |
| **파일 쓰기** | **Execute Command** (mkdir + base64 디코드로 phaseX-Y-N-task.md, phaseX-Y-N-task-test-result.md, 경로: docs/phases/phase-X-Y/tasks/) | 없음 (Backend가 plan_md_path 참조) |
| **Backend 호출** | 없음 | **HTTP Request** POST /api/workflow/run-task |
| **루프** | **Split In Batches** (Todo 항목별 반복) | 없음 (1 Task만 처리, 재실행 시 다시 SELECT) |
| **분기** | 없음 (루프만) | **IF** (hasTask: pending 있음/없음) |
| **Discord** | 완료 시 “Task Plan & Test Plan 생성 완료” (기본 disabled) | Task 실행 완료 시 Task ID·Status (활성) |
| **Credential** | YOUR_POSTGRES_CREDENTIAL_ID, YOUR_DISCORD_* (플레이스홀더) | 실제 credential ID (n8n 다운로드본 반영) |
| **Postgres 옵션** | queryParameters: 단일 표현식 문자열 `={{ [...] }}` | queryReplacement: 배열 `["={{ $json.status }}", "={{ $json.id }}"]` |

---

## 4. 공통점

- 둘 다 **Manual Trigger**로 시작.
- 둘 다 **workflow_tasks** 사용 (Generation은 INSERT, Execution은 SELECT/UPDATE).
- 둘 다 **Discord** 노드 사용 (메시지 내용·활성 여부만 다름).
- **Phase 8-2 흐름**: 8-2-6 Generation으로 task를 DB에 넣으면 → 8-2-7 Execution으로 해당 task를 실행하고 status를 갱신함.

---

## 5. 데이터 흐름 요약

```
[Generation]
  수동 실행 → (고정 Todo 2건) → 루프 → Plan/Test 텍스트 생성 → 파일 쓰기 → workflow_tasks INSERT
  → 루프 끝나면 Discord 알림

[Execution]
  수동 실행 → workflow_tasks에서 pending 1건 SELECT → 있으면 Backend 실행 → 응답으로 status 판단 → workflow_tasks UPDATE → Discord → (다음 Task는 재실행 시)
  pending 없으면 SET_NoPendingTask
```

**다른 부분이 있는가?** → **역할·노드·Postgres 사용(INSERT vs SELECT/UPDATE)·파일 쓰기·Backend 호출·루프/분기·Credential** 모두 다름. 같은 워크플로우가 아니라 **8-2-6용**과 **8-2-7용** 두 개의 별도 워크플로우임.

---

## 6. Task Plan and Test Plan Generation v1 (test) 수정 이력 (n8n 2.2.6 / Docker 반영)

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| **Postgres INSERT** | `queryParameters`: `"={{ [$json.phase_id, $json.task_name, $json.plan_doc, $json.test_plan_doc] }}"` | `queryReplacement`: `["={{ $json.phase_id }}", "={{ $json.task_name }}", "={{ $json.plan_doc }}", "={{ $json.test_plan_doc }}"]` (파라미터 바인딩 오류 방지) |
| **Postgres Credential** | `YOUR_POSTGRES_CREDENTIAL_ID` (플레이스홀더) | Task Execution과 동일 `tbx7tKTwKOdsxhQc` (동일 n8n 인스턴스에서 import 시 그대로 사용) |
| **노드 ID** | `t860-*` 식 단축 ID | UUID 형식 (n8n 2.2.6·다중 워크플로우 환경에서 충돌 방지) |
| **Manual Trigger** | (options 없음) | `executeOnce: false` (Task Execution v1과 동일) |
| **워크플로우 메타** | `meta.templateCredsSetupCompleted` 만 | `versionId`, `meta.instanceId`, `id` 추가 (n8n 2.2.6 형식) |
| **파일 경로** | (구) `/workspace/docs/phases/tasks` | (신) `/workspace/docs/phases/phase-X-Y/tasks/` (phase_dir_id 입력) |
| **파일명** | (구) `task-N-plan.md`, `task-N-test.md` | (신) `phaseX-Y-N-task.md`, `phaseX-Y-N-task-test-result.md` (규정: phase-document-taxonomy, ai-rule-decision) |
| **Discord** | disabled, YOUR_DISCORD_* 플레이스홀더 | 변경 없음 (활성화 시 n8n UI에서 credential·채널 수동 설정) |

**규정 참조**: `docs/n8n/workflow/n8n-workflow-phase-task-convention.md`, `docs/phase-document-taxonomy.md`, `docs/ai/ai-rule-decision.md`
