# Task Plan and Test Plan Generation v2 (phase-folder)

**기준**: `Task Plan and Test Plan Generation v1 (test).json`  
**규정**: `docs/phase-document-taxonomy.md`, `docs/ai/ai-rule-decision.md`, `docs/n8n/workflow/n8n-workflow-phase-task-convention.md`

실제 **phase 폴더**의 todo-list를 읽어, 항목별로 Task Plan·Test Plan을 생성하고 `docs/phases/phase-X-Y/tasks/`에 저장한 뒤 `workflow_tasks`에 INSERT하는 **루프 워크플로우**이다.

---

## 1. 목적

- **입력**: `phase_dir_id`(예: `phase-8-0`, `Testphase1-1`)만 설정. DB에는 **task_num**(고유 Task 번호, 예: 8-1-1, 1-1-2)과 **phase_slug**로 저장.
- **동작**: 해당 Phase의 `phaseX-Y-todo-list.md`를 읽어 파싱 → 항목별 루프 → Task Plan/Test Plan 생성 → 파일 쓰기 → DB INSERT
- **출력**: `docs/phases/phase-X-Y/tasks/phaseX-Y-N-task.md`, `phaseX-Y-N-task-test-result.md` 및 `workflow_tasks` 행

---

## 2. 노드 구성

| 순서 | 노드 이름 | 타입 | 역할 |
|------|-----------|------|------|
| 0 | Trigger_Manual | Manual Trigger | 수동 실행 |
| 1 | SET_PhaseContext | Set | phase_dir_id만 설정 (예: Testphase1-1, phase-8-0). DB INSERT는 phase_slug 사용, workflow_phases 불필요 |
| 2 | JS_PhaseContext | Code | phase_slug 계산 (phase-8-0 → 8-0) |
| 3 | CMD_ReadTodoList | Execute Command | phase todo-list 파일 읽기 (`cat /workspace/docs/phases/{phase_dir_id}/phase{phase_slug}-todo-list.md`) |
| 4 | JS_ParseTodoList | Code | todo-list 파싱 (### 8.0.N: Title 또는 - [ ] 항목) → 항목 배열 출력 |
| 5 | LOOP_TodoItems | Split In Batches | 항목별 1건씩 루프 (batchSize=1). **Reset: false** 필수 — 루프백 시 원본 N개 유지, true면 루프백 입력(1건)으로 초기화되어 1번만 돔 |
| 6 | JS_CreateTaskPlanAndTestPlan | Code | Task Plan/Test Plan 텍스트 + plan_md_path 등 생성 |
| 7 | CMD_WriteTaskFiles | Execute Command | mkdir + base64 디코드로 phaseX-Y-N-task.md, phaseX-Y-N-task-test-result.md 쓰기 |
| 8 | JS_PassPlanToDb | Code | CMD_WriteTaskFiles 출력(exitCode/stdout) 대신 JS_CreateTaskPlanAndTestPlan의 plan 데이터를 다음 노드로 전달 |
| 9 | DB_InsertWorkflowTask | Postgres | workflow_tasks INSERT (5개 파라미터만: task_num, phase_slug, task_name, plan_doc, test_plan_doc. plan_md_path는 빈 문자열로 INSERT) |
| 10 | JS_MergeIdAndPlanMdPath | Code | INSERT 반환 id + JS_PassPlanToDb의 plan_md_path 합쳐서 다음 노드로 전달 |
| 11 | DB_UpdatePlanMdPath | Postgres | workflow_tasks.plan_md_path UPDATE (2개 파라미터: plan_md_path, id) |
| 12 | (루프) | — | DB_UpdatePlanMdPath → LOOP_TodoItems (다음 항목) |
| 10 | JS_OnceForDiscord | Code | done 출력 N items → 루프 항목 수(total_items)·phase_dir_id를 담은 **요약 1건**만 Discord로 전달. 메시지 1번만 전송. |
| 11 | DISCORD_SendTaskPlansComplete | Discord | 루프 종료 시 완료 알림 (기본 disabled) |

---

## 3. 데이터 흐름

```
Trigger → SET_PhaseContext(phase_dir_id)
       → JS_PhaseContext(phase_slug 추가)
       → CMD_ReadTodoList(todo-list 파일 내용 → stdout)
       → JS_ParseTodoList(stdout 파싱 → [{ index, task_num, content, phase_id, phase_dir_id, phase_slug }, ...])
       → LOOP_TodoItems(항목별 1건)
         → JS_CreateTaskPlanAndTestPlan
         → CMD_WriteTaskFiles
         → JS_PassPlanToDb → DB_InsertWorkflowTask → JS_MergeIdAndPlanMdPath → DB_UpdatePlanMdPath
         → LOOP_TodoItems(다음 항목)
       → (루프 끝) JS_OnceForDiscord → DISCORD_SendTaskPlansComplete
```

---

## 4. todo-list 파싱 규칙

- **우선**: `### X-Y-N: 제목` 형식의 헤더에서 **task_num**(X-Y-N, 예: 1-1-1)과 **제목**(콜론 뒤)을 추출. task_num·task_name은 이 값 사용.
- **폴백**: `- [ ] 내용` 체크리스트 형식이면 task_num = phase_slug + '-' + index, content = 내용.
- **결과**: 각 항목당 `{ index, task_num, content, phase_id, phase_dir_id, phase_slug }` 를 LOOP에 전달. **task_num**(1-1-1)과 **task_name**(제목)은 todo-list 헤더 `### 1-1-1: 실데이터 성능 리그레션 검증...` 에서 그대로 사용.

---

## 5. 경로·파일명 (규정 준수)

- **Phase todo-list**: `docs/phases/{phase_dir_id}/phase{phase_slug}-todo-list.md` (예: `docs/phases/phase-8-0/phase8-0-todo-list.md`)
- **Task 저장**: `docs/phases/{phase_dir_id}/tasks/`
- **파일명**: `phase{task_num}-task.md`, `phase{task_num}-task-test-result.md` (예: `phase1-1-1-task.md`. task_num은 todo-list 헤더 `### 1-1-1: 제목` 에서 추출)

---

## 6. v1 (test) 대비 차이

| 항목 | v1 (test) | v2 (phase-folder) |
|------|------------|--------------------|
| Todo 항목 | 고정 2건 (JS_ExpandTodoItems 하드코딩) | 실제 phase 폴더의 todo-list 파일에서 파싱 |
| 입력 | SET_TestTodoList(phase_id, phase_dir_id) | SET_PhaseContext(phase_id, phase_dir_id) + JS_PhaseContext(phase_slug) |
| Todo 읽기 | 없음 | CMD_ReadTodoList + JS_ParseTodoList |
| 루프 이전 | JS_ExpandTodoItems → LOOP | CMD_ReadTodoList → JS_ParseTodoList → LOOP |

나머지(LOOP, JS_CreateTaskPlanAndTestPlan, CMD_WriteTaskFiles, **JS_PassPlanToDb**, DB_InsertWorkflowTask, Discord)는 v1과 동일한 역할·규정 경로·파일명을 사용한다. JS_PassPlanToDb는 Execute Command 출력 대신 plan 데이터를 DB 노드로 넘기기 위한 Code 노드이다.

---

## 7. 수동 설정

- **SET_PhaseContext**: 실행할 Phase에 맞게 **`phase_dir_id`**만 설정 (예: `Testphase1-1`, `phase-8-0`). DB에는 **task_num**(고유 Task 번호, 예: 8-1-1, 1-1-2)과 **phase_slug**로 저장. **workflow_phases 사전 INSERT 불필요.** 마이그레이션 `scripts/db/migrate_workflow_tasks_phase_slug.sql`, `migrate_workflow_tasks_task_num.sql` 실행 후 사용.
- **CMD_ReadTodoList**: 워크스페이스 루트가 `/workspace`가 아니면 경로 수정 (또는 환경 변수로 루트 지정).
- **Postgres/Discord**: credential ID를 실제 n8n 환경에 맞게 설정.

## 8. 파싱이 안 될 때 확인

- **CMD_ReadTodoList 출력**: n8n에서 해당 노드 실행 후 출력을 확인. `stdout`에 todo-list 본문이 들어와야 함. (없으면 `/workspace/docs/phases/{phase_dir_id}/phase{phase_slug}-todo-list.md` 경로·파일 존재 여부 확인.)
- **todo-list 형식**: 항목은 `### X-Y-N: 제목` 한 줄 형식 (task-X-Y-N, Phase별 X-Y에 맞춤. 예: Testphase1-1 → 1-1-1~1-1-6, phase-8-0 → 8-0-1~8-0-N). 공백·전각문자 사용 여부 확인.
- **SET_PhaseContext**: `phase_dir_id`가 폴더명과 동일한지 (예: `Testphase1-1`), 해당 폴더에 `phaseTestphase1-1-todo-list.md` 파일이 있는지 확인.
- **DB_InsertWorkflowTask Query Parameters가 모두 `[undefined]`**: Execute Command(CMD_WriteTaskFiles) 노드는 출력으로 `{ exitCode, stdout, stderr }`만 넘기므로, DB 노드의 `$json`에는 `phase_id` 등이 없음. **JS_PassPlanToDb** 노드가 JS_CreateTaskPlanAndTestPlan 출력을 그대로 넘기도록 추가되어 있음. import 후에도 undefined면 JS_PassPlanToDb가 CMD_WriteTaskFiles와 DB_InsertWorkflowTask 사이에 있는지 확인.
- **Discord가 항목 수만큼 실행됨**: done 출력이 **N items**를 넘기면 Discord는 항목당 1번 실행됨. **JS_OnceForDiscord**에서 `$input.all().length`로 **루프 항목 수**를 저장하고, `{ total_items, phase_dir_id }` 요약 1건만 Discord로 넘기면 메시지 1번만 전송·메시지에 "N개 Task Plan 생성됨" 표시 가능.
- **Discord "Send a message" / phase_dir_id [undefined]**: 루프 done 분기에서는 `.item(0)` 이 undefined가 나올 수 있음. **`$('SET_PhaseContext').first().json.phase_dir_id`** 사용. 노드 이름이 바뀌었으면 `$('SET_PhaseContext2').first().json.phase_dir_id` 도 시도. 그래도 undefined면 메시지에 fallback `|| 'phase-folder'` 넣었으므로 'phase-folder'로 표시됨.
- **DB_InsertWorkflowTask `there is no parameter $4` / task_num·phase_slug가 `[undefined]`**: **JS_PassPlanToDb**가 넘기는 데이터에 `task_num`, `phase_slug`가 없을 때 발생. 1) **JS_CreateTaskPlanAndTestPlan** 노드 Code에 **return 문에 `task_num`, `phase_slug` 포함**돼 있는지 확인. 2) n8n에서 노드가 **JS_CreateTaskPlanAndTestPlan2** 등으로 이름이 바뀌었으면 **JS_PassPlanToDb** Code 안의 `$('JS_CreateTaskPlanAndTestPlan')` 를 실제 노드 이름으로 수정하거나, 최신 워크플로우 JSON을 다시 import(최신은 노드 이름 2도 시도·LOOP에서 task_num/phase_slug 보정).
- **DB_InsertWorkflowTask `there is no parameter $6`**: n8n Postgres 노드는 5개 초과 파라미터에서 오류가 나는 경우가 있음. 그래서 INSERT는 **5개**만 사용하고, plan_md_path는 **DB_UpdatePlanMdPath** 노드에서 별도 UPDATE함. INSERT Query Parameters: `$json.task_num`, `$json.phase_slug`, `$json.task_name`, `$json.plan_doc`, `$json.test_plan_doc` (5개).
- **DB_InsertWorkflowTask FK 오류** (과거 `workflow_tasks_phase_id_fkey`): 현재는 INSERT 시 **phase_slug**만 사용하므로 **workflow_phases 불필요.** `scripts/db/migrate_workflow_tasks_phase_slug.sql` 실행 후 워크플로우 사용. (phase_id 컬럼은 nullable로 유지되며 INSERT에서 생략됨.)

---

## 9. 파일 위치

- 워크플로우 JSON: `docs/n8n/workflow/Task Plan and Test Plan Generation v2 (phase-folder).json`
- 본 설명: `docs/n8n/workflow/Task Plan and Test Plan Generation v2 (phase-folder) - Workflow.md`
