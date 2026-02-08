# workflow_task_service.py 설명

Phase 8-2-7 **Task 실행** 로직. n8n HTTP 호출(`POST /api/workflow/run-task`) 및 로컬 스크립트(`run_task_execution.py`)에서 공통 사용.

---

## 1. 전체 흐름

```
[호출] task_id
    ↓
can_claude_access_workspace(workspace_root)  →  CLI 존재·워크스페이스 접근 가능 여부 검사 (실패 시 즉 반환)
    ↓
get_task(db, task_id)  →  workflow_tasks에서 1건 조회 (id, phase_id, task_name, status, plan_doc, test_plan_doc, plan_md_path)
    ↓
update_status(db, task_id, "in_progress")
    ↓
run_with_claude(workspace_root, plan_doc=..., plan_md_path=...)
    ├─ plan_md_path 있음  →  CLI에 "해당 .md 파일을 읽고 실행하라" 경로만 전달 (PROMPT_BY_PLAN_PATH)
    └─ plan_md_path 없음  →  plan_doc 텍스트를 그대로 프롬프트에 넣음 (기존 동작)
    ├─ CLI 경로 있음  →  run_with_claude_cli(...)  →  node cli.js -p "..."
    └─ CLI 없음      →  Anthropic API (messages.create) 로 동일 프롬프트 전송
    ↓
성공 시 update_status(db, task_id, "completed") / 실패 시 "failed"
    ↓
(success, message) 반환
```

---

## 2. Claude가 프로젝트 폴더에 접근 가능한지 검사 (`can_claude_access_workspace`)

Python에서 **Claude Code CLI가 프로젝트 폴더에 접근 가능한지** 다음 순서로 검사한다.

| 단계 | 검사 내용 |
|------|-----------|
| 1 | `workspace_root` 경로가 존재하고 디렉터리인지 |
| 2 | 해당 디렉터리에 **읽기·쓰기** 권한이 있는지 (`os.R_OK`, `os.W_OK`) |
| 3 | Claude CLI 실행 파일이 있는지 (`_resolve_claude_cli_js()` 또는 `CLAUDE_CLI_PATH`) |
| 4 | **프로브**: CLI를 `cwd=workspace_root`로 짧게 실행 (프롬프트 "Reply with only: OK", 타임아웃 15초). 성공하면 실제로 해당 폴더에서 CLI가 동작함을 확인 |

실패 시 `run_task`는 **Claude 실행 없이** `(False, "Claude CLI가 프로젝트 폴더에 접근할 수 없음: ...")` 를 반환한다.

---

## 3. DB에서 쓰는 컬럼

| 컬럼 | 용도 |
|------|------|
| `id` | 조회/갱신 대상 |
| `phase_id` | 조회만 (현재 로직에서 미사용) |
| `task_name` | 실패/완료 메시지에 사용 |
| `status` | `in_progress` → `completed` / `failed` |
| `plan_doc` | **plan_md_path 없을 때** CLI/API에 넘기는 Task Plan 전문(마크다운 텍스트) |
| `test_plan_doc` | 조회만 (현재 실행 로직에서 미사용) |
| `plan_md_path` | **있으면** CLI에 **파일 경로만** 전달. workspace 기준 상대 경로 (예: `docs/phases/tasks/task-1-plan.md`). CLI가 해당 .md를 읽고 Task 실행. |

- **plan_md_path가 있는 경우**: DB에서는 **파일 경로만** 전달하고, Claude Code CLI가 그 경로의 .md 파일을 찾아 읽은 뒤 Task를 실행한다.
- **plan_md_path가 없거나 NULL**: 기존처럼 `plan_doc` 텍스트를 그대로 프롬프트에 넣는다.
- `plan_md_path` 컬럼 추가: `scripts/db/migrate_workflow_tasks_plan_md_path.sql` 참고.

---

## 4. Claude CLI에 넘기는 것 (경로 기반 vs 텍스트 기반)

### plan_md_path가 있을 때 (경로 기반)

- **프롬프트** (`PROMPT_BY_PLAN_PATH`):
  - `"Workspace root: {workspace_root}\n\nTask plan file (relative to workspace): {plan_md_path}\n\nRead this .md file and execute the task described in it. You may read, create, modify, or delete files under the project folder as needed. Reply with a short summary of what you did."`
- CLI는 `cwd=workspace_root`에서 실행되므로, 해당 경로의 .md 파일을 읽고 내용에 따라 프로젝트 폴더 내 파일을 읽기/쓰기/수정/삭제할 수 있다.

### plan_md_path가 없을 때 (기존)

- **프롬프트**: `"Workspace root: {workspace_root}\n\nTask Plan:\n{plan_doc}\n\nSummarize the steps to execute this plan (short summary)."`

---

## 5. 함수별 역할

| 함수 | 역할 |
|------|------|
| `get_task(db, task_id)` | `workflow_tasks` 에서 해당 id 1건 조회. `plan_md_path` 컬럼 없으면 fallback으로 6컬럼만 조회. |
| `update_status(db, task_id, status)` | `workflow_tasks.status` (및 `completed_at`) 갱신. |
| `_resolve_claude_cli_js()` | `CLAUDE_CLI_JS` / `CLAUDE_CLI_PATH` 환경 변수 또는 기본값으로 cli.js 경로 결정. |
| `can_claude_access_workspace(workspace_root)` | CLI 존재·워크스페이스 디렉터리·권한·프로브 실행으로 “Claude가 프로젝트 폴더 접근 가능” 여부 검사. |
| `run_with_claude_cli(workspace_root, plan_doc=..., plan_md_path=...)` | `node cli.js -p "..."` 로 CLI 실행. `plan_md_path` 있으면 경로 기반 프롬프트, 없으면 plan_doc 텍스트. |
| `run_with_claude(workspace_root, plan_doc=..., plan_md_path=...)` | CLI 경로가 있으면 CLI만 사용. 없으면 Anthropic API로 동일 프롬프트 전송. |
| `run_task(db, task_id, workspace_root=None)` | 접근 검사 → 조회 → in_progress → run_with_claude → completed/failed 갱신. 진입점. |

---

## 6. n8n Task Plan and Test Plan Generation 워크플로우

- **JS_CreateTaskPlanAndTestPlan**: `plan_md_path` = `docs/phases/tasks/task-{index}-plan.md` (및 `test_plan_md_path`) 출력.
- **DB_InsertWorkflowTask**: INSERT 시 `plan_md_path` 컬럼에 위 경로 저장.
- Task Execution 시 Backend는 `plan_md_path`를 읽어 CLI에 **경로만** 넘기고, CLI가 해당 .md를 찾아 Task를 실행한다.

**DB 마이그레이션**: `plan_md_path` 컬럼이 없으면 먼저 `scripts/db/migrate_workflow_tasks_plan_md_path.sql` 를 실행한 뒤 n8n 워크플로우를 사용한다.
