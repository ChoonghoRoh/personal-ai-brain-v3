# n8n → Backend 호출 시 수동 수정 항목

n8n 워크플로우에서 **Backend API**를 호출하는 노드는 JSON으로 import한 뒤에도 **n8n UI에서 직접 수정**해야 합니다.  
(환경별 URL·호스트가 다르기 때문)

**Phase·Task 경로 규정**: Task 파일 경로는 `docs/phase-document-taxonomy.md`, `docs/ai/ai-rule-decision.md`를 따른다.  
- Phase 폴더: `docs/phases/phase-X-Y/`  
- Task 문서: `docs/phases/phase-X-Y/tasks/phaseX-Y-N-task.md`, `phaseX-Y-N-task-test-result.md`  
- 상세: `docs/n8n/workflow/n8n-workflow-phase-task-convention.md`

---

## 1. Task Execution v1

### 1-A. HTTP_RunTaskExecution (Backend URL)

| 항목 | 값 |
|------|-----|
| **워크플로우** | Task Execution v1 |
| **노드 이름** | **HTTP_RunTaskExecution** |
| **노드 타입** | HTTP Request |

#### 수동 수정 필드

| 필드 | JSON 기본값 (참고용) | 수동 수정 예시 |
|------|----------------------|----------------|
| **URL** | `http://localhost:8000/api/workflow/run-task` | 아래 표 참고 |

---

### 1-B. JS_PrepareTaskPayload (Code 노드)

| 항목 | 값 |
|------|-----|
| **워크플로우** | Task Execution v1 |
| **노드 이름** | **JS_PrepareTaskPayload** |
| **노드 타입** | Code (JavaScript) |

#### 바꿔야 하는 부분 (수동 수정)

| 위치 | 변경 전 | 변경 후 |
|------|---------|---------|
| **주석** | `// Prepare payload for CMD_RunTaskExecution: ...` | `// Prepare payload for HTTP_RunTaskExecution: task_id, workspace root` |
| **workspace_root 값** | `const workspaceRoot = '/workspace';` | `const workspaceRoot = process.env.WORKSPACE_ROOT \|\| '/workspace';` |

**이유:** Backend 호출 방식이 Execute Command → HTTP Request로 바뀌었고, `WORKSPACE_ROOT`는 Docker Compose에서 n8n에 `WORKSPACE_ROOT=/workspace` 등으로 넘기므로 환경 변수 사용 시 환경별로 맞출 수 있습니다.

#### 수동 입력할 전체 코드 (복사용)

n8n UI에서 **JS_PrepareTaskPayload** 노드 → **Code** 필드에 아래 전체를 넣으면 됩니다.

```javascript
// Prepare payload for HTTP_RunTaskExecution: task_id, workspace root
const item = $input.first().json;
const taskId = item.id;
const workspaceRoot = process.env.WORKSPACE_ROOT || '/workspace';
return [{
  json: {
    id: taskId,
    task_name: item.task_name,
    plan_doc: item.plan_doc,
    workspace_root: workspaceRoot
  }
}];
```

**참고:** n8n Code 노드에서는 환경 변수를 `process.env.WORKSPACE_ROOT`로 읽습니다. (`$env`는 파라미터 표현식용)

### URL 설정 (환경별)

| 실행 환경 | 수동 입력할 URL |
|-----------|------------------|
| **n8n·Backend 모두 Docker Compose** (같은 네트워크) | `http://backend:8000/api/workflow/run-task` |
| n8n만 Docker, Backend는 호스트에서 실행 | `http://host.docker.internal:8000/api/workflow/run-task` (Mac/Win) 또는 호스트 IP |
| n8n·Backend 모두 호스트에서 실행 | `http://localhost:8000/api/workflow/run-task` |

**참고:** Docker Compose에는 `BACKEND_URL=http://backend:8000` 이 설정되어 있으나, n8n HTTP Request 노드에서 **환경 변수**를 쓰려면 n8n 표현식(예: `{{ $env.BACKEND_URL }}`) 지원 여부를 확인한 뒤 사용하세요. 지원되지 않으면 위 표처럼 URL을 **직접 입력**합니다.

---

## 1.1 "The service refused the connection" / ECONNREFUSED ::1:8000 오류 해결

**증상:** HTTP_RunTaskExecution(또는 HTTP_RunTaskExecution2) 노드 실행 시  
- `Problem in node 'HTTP Request' - The service refused the connection - perhaps it is offline`  
- 또는 **Error code: ECONNREFUSED**, **Full message: connect ECONNREFUSED ::1:8000**

**원인 (Docker 사용 시):**  
URL이 `http://localhost:8000` 이면, n8n 컨테이너 안에서 **localhost**(또는 ::1) = n8n 자신이라 Backend 컨테이너에 연결되지 않습니다.

**해결:**

1. n8n UI에서 **HTTP_RunTaskExecution** / **HTTP_RunTaskExecution2** 등 Backend를 호출하는 HTTP Request 노드를 모두 열기
2. **URL** 을 아래처럼 **반드시** 변경  
   - **n8n·Backend 모두 Docker Compose로 실행 중이면**  
     → `http://backend:8000/api/workflow/run-task`  
   - n8n만 Docker, Backend는 호스트면  
     → `http://host.docker.internal:8000/api/workflow/run-task` (Mac/Windows)
3. 저장 후 워크플로우 다시 실행

**주의:** 복제한 노드(예: HTTP_RunTaskExecution2)가 있으면 그 노드의 URL도 동일하게 `http://backend:8000/...` 로 바꿔야 합니다.

**Backend 동작 확인:**

- 호스트에서: `curl -s http://localhost:8000/health` → `{"status":"ok"}` 이면 Backend 정상
- Docker 내부(n8n 컨테이너)에서 Backend 도달 확인:  
  `docker exec -it n8n wget -qO- http://backend:8000/health`  
  → `{"status":"ok"}` 이면 같은 네트워크에서 Backend 접근 가능

---

## 1.2 "Your request is invalid" / "Field required" 오류 해결

**증상:** HTTP_RunTaskExecution 노드 실행 시  
`Your request is invalid or could not be processed by the service` · `Field required`

**원인:** Backend API(`POST /api/workflow/run-task`)는 **Request Body**에 `{ "task_id": 숫자 }` 가 필요합니다.  
n8n에서 Body를 잘못 설정하면(예: "Using Fields Below"에서 **Name**에 전체 JSON을 넣고 **Value**를 비움) body가 비거나 잘못 전달되어 "Field required"가 납니다.

**해결 (둘 중 하나로 설정):**

### 방법 A — JSON으로 한 번에 보내기 (권장)

1. **HTTP_RunTaskExecution** 노드에서 **Specify Body** 를 **"JSON"** (또는 "Using JSON")으로 선택
2. **JSON** 필드(본문 한 칸)에 아래만 입력:
   ```json
   { "task_id": {{ $json.id }} }
   ```
3. 저장 후 다시 실행

### 방법 B — Using Fields Below 사용 시

1. **Specify Body** = **"Using Fields Below"** 인 경우, **필드를 키 하나씩** 넣습니다.
2. **Body Parameters** 에 행을 **한 개** 추가:
   - **Name:** `task_id`
   - **Value:** `{{ $json.id }}`
3. ❌ **Name**에 `{ "task_id": {{ $json.id }} }` 처럼 전체 JSON을 넣거나, **Value**를 비우지 마세요.

**Backend가 기대하는 body:** `{ "task_id": 1 }` 형태 (task_id는 숫자).

---

## 1.3 Task 실행 시 "anthropic 패키지 없음" / "ANTHROPIC_API_KEY 미설정"

**증상:** HTTP_RunTaskExecution 호출은 성공하지만, 응답 메시지에  
`anthropic 패키지 없음 (pip install anthropic)` 또는 `ANTHROPIC_API_KEY 미설정` 이 나옴.

**왜 나오나:** Backend는 **먼저 로컬 Claude CLI**를 시도하고, CLI가 없거나 실패하면 **anthropic 패키지(API)** 를 시도합니다.  
CLI 볼륨을 추가했는데도 이 메시지가 나오면 → **CLI 설정 후 backend 컨테이너를 다시 띄우지 않아서** 새 볼륨이 적용되지 않은 경우가 많습니다. (컨테이너는 기동 시점의 볼륨만 보므로, docker-compose 수정 후 **재시작/재생성**이 필요합니다.)

**해결 (CLI 사용 시):**

1. **docker-compose.yml** 에서 backend 서비스의 CLI 볼륨 주석 해제:
   ```yaml
   - ${HOME}/.npm-global:/host-npm-global:ro
   ```
   (경로를 본인 호스트에 맞게 수정, 예: `/Users/본인계정/.npm-global`)
2. **Backend 컨테이너 재생성(재시작)** — 여기서 반드시 해야 함:
   ```bash
   docker compose up -d backend
   ```
   또는 볼륨만 바뀌었으면:
   ```bash
   docker compose up -d --force-recreate backend
   ```
3. 호스트에서 `claude login` 이 완료된 상태인지 확인한 뒤, n8n에서 Task 다시 실행.

**해결 (API 키 사용 시):**

1. **Backend 환경에 anthropic 설치**  
   - 로컬: `pip install anthropic` 또는 `pip install -r requirements.txt`  
   - Docker: `requirements-docker.txt`에 `anthropic>=0.39.0` 포함 후  
     `docker compose build backend && docker compose up -d backend`
2. **ANTHROPIC_API_KEY 설정**  
   - Backend 컨테이너(또는 실행 환경)에 환경 변수 `ANTHROPIC_API_KEY` 설정  
   - Docker Compose: `backend` 서비스의 `environment`에  
     `ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}` 추가 후 `.env`에 값 설정

위가 반영되면 Task 실행 시 Backend가 CLI 또는 Claude API를 사용해 Plan을 수행하고, 실패 시에는 응답이 `success: false`로 오며 n8n에서 `failed`로 처리됩니다.

---

### (대안) 로컬 Claude Code CLI에 전달하는 방법

API 키 대신 **이미 인증된 로컬 Claude Code CLI**를 쓰고 싶다면 아래 두 가지 중 하나를 쓰면 됩니다.

| 방법 | 설명 | n8n 연동 |
|------|------|----------|
| **A. Backend에서 CLI 실행** | Backend 컨테이너에 호스트의 `claude` CLI를 마운트하고, Backend가 그 CLI를 subprocess로 실행. CLI가 사용하는 인증(호스트에서 `claude login` 한 상태)을 그대로 사용. | n8n은 그대로 **HTTP_RunTaskExecution** → Backend 호출. Backend가 CLI 실행. |
| **B. 호스트에서 스크립트 실행** | n8n/Backend를 거치지 않고, 호스트에서 `python scripts/n8n/run_task_execution.py --task-id 1` 실행. 호스트에 Claude CLI 설치·인증돼 있으면 CLI로 Task 수행. | n8n 워크플로우와는 별도. 수동 실행 또는 호스트용 cron/스케줄러로 트리거. |
| **C. n8n에서 직접 CLI 실행** ⭐ | n8n 컨테이너에 이미 마운트된 `/host-npm-global/bin/claude`를 **Execute Command** 노드로 직접 실행. Backend HTTP 호출 없이 n8n에서 Task 실행. | **HTTP_RunTaskExecution** 대신 **CMD_RunClaudeCLI** (Execute Command) 사용. |

**방법 A 설정 요약**

1. **docker-compose.yml** — backend 서비스에 호스트 Claude CLI 경로 + **인증 디렉터리** 마운트:
   ```yaml
   volumes:
     - ${PAB_PROJECT_ROOT:-.}:/app
     # CLI 바이너리 (n8n과 동일 경로)
     - /Users/본인경로/.npm-global:/host-npm-global:ro
     # CLI 인증 + 쓰기: 로컬에서 claude login 한 ~/.claude. CLI가 debug/cache 등 쓰기 필요 → :ro 사용 시 EROFS
     - /Users/본인경로/.claude:/root/.claude
   ```
2. **인증은 별도로 안 해도 됨**  
   로컬(iTerm 등)에서 **한 번만** `claude login` 해 두면 인증이 `~/.claude/` 에 저장됩니다.  
   위처럼 `~/.claude` 를 컨테이너의 `/root/.claude` 로 마운트하면, Backend가 컨테이너 안에서 CLI를 실행할 때 **같은 인증**을 사용합니다. 컨테이너 안에서 다시 로그인할 필요 없습니다.
3. **Backend 환경 변수** (선택): `CLAUDE_CLI_PATH=/host-npm-global/bin/claude`  
   설정하지 않으면 Backend가 `/host-npm-global/bin/claude` 를 기본으로 찾습니다.
4. **동작**: `ANTHROPIC_API_KEY`가 없어도 CLI 실행 파일 + `~/.claude` 마운트가 있으면 Backend가 CLI로 Plan을 실행합니다.

5. **Backend 컨테이너에 Node.js 필요**  
   Claude Code CLI는 Node.js 앱이므로, Backend Docker 이미지에 `nodejs`가 설치되어 있어야 합니다. `Dockerfile.backend`에 `apt-get install -y nodejs`가 포함되어 있으면 재빌드 후 컨테이너 안에서 `claude` 실행이 가능합니다.

**도커 재시작 후 Claude 마운트 체크 (backend 컨테이너):**

| 확인 항목 | 명령 | 기대 결과 |
|-----------|------|-----------|
| CLI 바이너리 | `docker exec pab-backend ls -la /host-npm-global/bin/claude` | `claude` 심볼릭 링크 또는 실행 파일 존재 |
| 인증 디렉터리 | `docker exec pab-backend ls -la /root/.claude` | `cache`, `history.jsonl` 등 디렉터리/파일 존재 |
| Node.js (CLI 실행용) | `docker exec pab-backend node --version` | 버전 출력 (Node 미설치 시 `claude` 실행 불가 → Backend 이미지 재빌드 필요) |

**`env: '/host-npm-global/bin/claude': Invalid argument` 가 나올 때:**  
Backend는 `bin/claude` 대신 **`node` + `cli.js`** 로 직접 실행합니다. `CLAUDE_CLI_JS` 미설정 시 기본값은 `/host-npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js` 입니다.

**동작:** CLI 경로가 있으면 **API로 fallback 하지 않습니다.** CLI만 사용하고, CLI 실패 시 그 메시지만 반환합니다. API는 **CLI 경로가 없을 때만** 사용됩니다.

**`Claude CLI 실패 (exit 1): Invalid API key · Please run /login` 가 나올 때:**  
CLI는 **`ANTHROPIC_API_KEY` 환경 변수를 지원**합니다. macOS에서는 호스트에서 `claude login` 해도 토큰이 **키체인**에 들어가서, 컨테이너가 마운트된 `~/.claude`만으로는 인증이 안 될 수 있습니다.

**해결:** Backend 컨테이너에 **API 키를 환경 변수로** 넘기면, CLI 실행 시 그 키를 사용합니다. (호스트 키체인 불필요)

1. 프로젝트 루트 `.env` 에 추가:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```
2. `docker-compose.yml` 의 backend 서비스에는 이미 `ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}` 가 있으므로, backend만 재시작:
   ```bash
   docker compose up -d backend
   ```
3. CLI는 subprocess 실행 시 컨테이너의 `os.environ`을 그대로 받으므로, `ANTHROPIC_API_KEY`가 설정돼 있으면 **로그인 없이** API 키로 동작합니다.

**`Claude CLI 실패 (exit 1): ...` (그 외):**  
Backend가 **stdout**도 실패 메시지에 포함하므로, CLI가 출력한 안내를 확인할 수 있습니다. 호스트에서 `claude login` 후 `~/.claude` 를 쓰기 가능하게 마운트해 두었는지 확인하세요.

**방법 B**  
호스트 터미널에서 `claude` 가 PATH에 있고 인증돼 있으면,  
`python scripts/n8n/run_task_execution.py --task-id 1`  
만 실행하면 됩니다. DB의 `workflow_tasks`를 직접 갱신하므로 n8n HTTP 호출 없이 Task만 실행할 때 적합합니다.

**방법 C 설정 요약 (n8n에서 직접 CLI 실행)** ⭐

1. **docker-compose.yml** — n8n 서비스에 이미 Claude CLI 마운트가 있음:
   ```yaml
   volumes:
     - /Users/본인경로/.npm-global:/host-npm-global:ro
   ```
   (이미 설정되어 있으면 추가 불필요)

2. **n8n 워크플로우 수정** — `HTTP_RunTaskExecution` 대신 **Execute Command** 노드 사용:
   - 노드 이름: **CMD_RunClaudeCLI** (또는 원하는 이름)
   - **Command:** `sh`
   - **Arguments:** `-c "cd /workspace && /host-npm-global/bin/claude -p \"Workspace root: /workspace\n\nTask Plan:\n{{ $json.plan_doc }}\n\nSummarize the steps to execute this plan (short summary).\""`
   - 또는 더 간단하게:
     - **Command:** `/host-npm-global/bin/claude`
     - **Arguments:** `-p "Workspace root: /workspace\n\nTask Plan:\n{{ $json.plan_doc }}\n\nSummarize the steps to execute this plan (short summary)."`

3. **응답 처리** — Execute Command의 stdout을 받아서:
   - **JS_SetTaskStatusFromResponse** 노드에서:
     ```javascript
     const taskId = $node["JS_PrepareTaskPayload"].json.id;
     const stdout = $input.first().json.stdout || "";
     const stderr = $input.first().json.stderr || "";
     const exitCode = $input.first().json.exitCode || 0;
     const success = exitCode === 0 && !stderr;
     const status = success ? 'completed' : 'failed';
     return [{ json: { id: taskId, status, message: stdout || stderr } }];
     ```

4. **장점:**
   - Backend HTTP 호출 불필요 (Backend가 다운되어도 Task 실행 가능)
   - API 키(`ANTHROPIC_API_KEY`) 불필요 (CLI 인증 사용)
   - n8n에서 직접 실행하므로 응답 지연 감소

5. **주의사항:**
   - n8n 컨테이너에 `/host-npm-global/bin/claude`가 접근 가능해야 함
   - 호스트에서 `claude login` 완료 상태여야 함
   - Execute Command 노드가 활성화되어 있어야 함 (`NODES_EXCLUDE='[]'` 확인)

**방법 C 워크플로우 예시 구조:**
```
JS_PrepareTaskPayload → CMD_RunClaudeCLI (Execute Command) → JS_SetTaskStatusFromResponse → DB_UpdateTaskStatus
```

**조건부 분기 (CLI 우선, 없으면 HTTP):**
- **IF_CheckClaudeCLI** (Code): `/host-npm-global/bin/claude` 존재 여부 확인
- **True 분기:** CMD_RunClaudeCLI (Execute Command)
- **False 분기:** HTTP_RunTaskExecution (HTTP Request)

### 1.3-A. DB_UpdateTaskStatus — Query Parameters (`there is no parameter $2`)

**증상:** DB_UpdateTaskStatus 노드 실행 시  
`there is no parameter $2` / `Failed query: UPDATE workflow_tasks SET status = $1, completed_at = NOW() WHERE id = $2`

**원인:** n8n Postgres 노드가 Query Parameters를 **배열 한 개의 표현식** `={{ [$json.status, $json.id] }}`으로 받을 때, 버전/해석에 따라 `$2`에 해당하는 값이 전달되지 않는 경우가 있음.

**해결 (n8n UI에서 수동 설정):**

1. **DB_UpdateTaskStatus** 노드 열기
2. **Options** → **Query Parameters**에서:
   - **항목을 2개**로 두고,
   - 첫 번째: `{{ $json.status }}`
   - 두 번째: `{{ $json.id }}`
3. 또는 표현식 한 줄인 경우: `{{ [$json.status, $json.id] }}` 가 **실제로 두 값**을 넘기도록, 이전 노드(JS_SetTaskStatusFromResponse) 출력에 `id`, `status`가 모두 있는지 확인

**참고:** 워크플로우 JSON에서는 **Options**에 `queryReplacement` 배열(`["={{ $json.status }}", "={{ $json.id }}"]`)을 사용해 `$1`, `$2`에 각각 바인딩되도록 수정해 둠. import 후에도 오류가 나면 위처럼 UI에서 항목 2개로 직접 입력.

### 1.3-B. Task Plan and Test Plan Generation v1 — DB_InsertWorkflowTask (`queryReplacement`)

**워크플로우:** Task Plan and Test Plan Generation v1 (test)

**증상:** DB_InsertWorkflowTask 노드 실행 시 `there is no parameter $2` (또는 $3, $4) / INSERT 실패.

**원인:** Task Execution의 DB_UpdateTaskStatus와 동일. Postgres 노드에서 `queryParameters: "={{ [$json.phase_id, ...] }}"`처럼 배열 한 개의 표현식으로 넘기면 n8n 2.2.x에서 파라미터가 제대로 분리되지 않을 수 있음.

**해결:**

1. **Query Parameters가 모두 `[undefined]`인 경우**: Execute Command(CMD_WriteTaskFiles) 노드는 출력으로 `{ exitCode, stdout, stderr }`만 넘기므로, DB 노드의 `$json`에 `phase_id` 등이 없음. 워크플로우에 **JS_PassPlanToDb** Code 노드를 CMD_WriteTaskFiles와 DB_InsertWorkflowTask **사이**에 두고, `$('JS_CreateTaskPlanAndTestPlan').item.json`을 그대로 다음 노드로 넘기도록 설정함.
2. **`$1` 인식 오류**: 워크플로우 JSON에서 **Options**에 `queryReplacement`를 **쉼표로 구분한 한 줄**로 설정 (6개):
   - `={{ $json.task_num }},={{ $json.phase_slug }},={{ $json.task_name }},={{ $json.plan_doc }},={{ $json.test_plan_doc }},={{ $json.plan_md_path }}`
3. **FK 오류** (과거 `workflow_tasks_phase_id_fkey`): 현재는 INSERT 시 **phase_slug**만 사용하므로 **workflow_phases 사전 INSERT 불필요.** `scripts/db/migrate_workflow_tasks_phase_slug.sql` 실행 후 사용.

**DB 마이그레이션:** `plan_md_path` 컬럼이 없으면 먼저 `scripts/db/migrate_workflow_tasks_plan_md_path.sql` 실행 필요.  
Backend는 `plan_md_path`가 있으면 해당 .md **파일 경로만** Claude CLI에 전달해, CLI가 프로젝트 폴더에서 해당 파일을 읽고 Task를 실행함.

**n8n UI에서 수동 설정 시:** DB_InsertWorkflowTask 노드 → **Options** → Query Parameters(또는 Query Replacement)를 **5개**로 두고, 위 다섯 표현식을 각각 입력.

---

## 1.4 DISCORD_SendTaskComplete — Discord Message > Send (V2)

**워크플로우:** Task Execution v1 (및 Task Plan and Test Plan Generation v1)

**변경:** 기존 Discord 노드(V1, `channelId`/`content`)는 현재 n8n 버전에서 사용하지 않음. **Discord > Message > Send** (V2)로 적용함.

| 항목 | 변경 전 (V1) | 변경 후 (V2) |
|------|--------------|--------------|
| **Resource / Operation** | (단일 노드) | **Resource:** Message, **Operation:** Send |
| **Credentials** | `discordApi` | `discordBotApi` (Bot Token) |
| **채널 지정** | `channelId`: 문자열 | **Send To:** Channel, **Channel:** Resource Locator (By ID: `YOUR_DISCORD_CHANNEL_ID`) |
| **서버 지정** | 없음 | **Server (guildId):** Resource Locator (By ID: `YOUR_DISCORD_GUILD_ID`) |
| **메시지** | `content` | `content` (동일) |

**n8n UI에서 수동 설정:**

1. **DISCORD_SendTaskComplete** 노드 열기
2. **Connection Type:** Bot Token (또는 OAuth2) 선택 후 **Credential**에서 Discord Bot credential 선택
3. **Resource:** Message, **Operation:** Send
4. **Server:** By ID → 서버(Guild) ID 입력
5. **Send To:** Channel → **Channel:** By ID → 채널 ID 입력
6. **Message:** `Task 실행 완료\nTask ID: {{ $node["JS_PrepareTaskPayload"].json.id }}\nStatus: {{ $node["JS_SetTaskStatusFromResponse"].json.status }}` (또는 표현식 유지)
7. 사용 시 **disabled** 해제

**참고:** Task Plan and Test Plan Generation v1의 **DISCORD_SendTaskPlansComplete** 노드도 동일하게 Message > Send (V2)로 적용되어 있음.

---

## 2. 변경 사항 요약 (코드/문서 기준)

Backend 호출로 **기존 대비 변경된 부분**만 정리합니다.

| 구분 | 변경 전 | 변경 후 |
|------|---------|---------|
| Task 실행 방식 | n8n **Execute Command** 노드에서 `run_task_execution.py` 실행 (Python/Claude CLI 필요) | n8n **HTTP Request** 노드에서 Backend `POST /api/workflow/run-task` 호출 (또는 **Execute Command**로 `/host-npm-global/bin/claude` 직접 실행) |
| 노드 이름 | CMD_RunTaskExecution | **HTTP_RunTaskExecution** (또는 **CMD_RunClaudeCLI** - 방법 C) |
| n8n 컨테이너 요구사항 | Python, Claude CLI 등 | **HTTP 방식:** 불필요 (Backend에서 실행) / **CLI 방식:** `/host-npm-global/bin/claude` 접근 가능 (이미 마운트됨) |
| 수동 설정 | Execute Command의 Command/Arguments | **HTTP 방식:** HTTP Request의 URL (§1-A) + JS_PrepareTaskPayload Code (§1-B) / **CLI 방식:** Execute Command의 Command/Arguments (§1.3 방법 C) |

---

## 3. n8n UI에서 수정 절차

1. n8n 워크플로우 편집기에서 **Task Execution v1** 열기
2. **HTTP_RunTaskExecution** 노드 클릭 → **URL** 필드에 사용 중인 환경에 맞는 URL 입력 (§1-A 표 참고)
3. **JS_PrepareTaskPayload** 노드 클릭 → **Code** 필드에 §1-B의 전체 코드 붙여넣기 (또는 주석·`workspaceRoot` 한 줄만 위 표대로 수정)
4. **HTTP_RunTaskExecution** Body 확인: **Specify Body** = **JSON**, 본문에 `{ "task_id": {{ $json.id }} }` 만 입력 (§1.2 참고)
5. 저장 후 테스트 실행

---

## 4. 추후 Backend 호출 추가 시

다른 워크플로우에서 Backend를 호출하는 **HTTP Request** 노드를 추가할 때마다:

- 이 문서의 **§1** 형식으로 **워크플로우명 / 노드명 / 수정 필드(URL 등)** 를 추가하고
- **§2** 에 “변경 전·후”가 있으면 요약해 두면, 수동 수정 시 찾기 쉽습니다.

---

**문서 버전**: 1.5  
**최종 업데이트**: 2026-01-28 — Discord 노드 V2 (Message > Send) 적용, DISCORD_SendTaskComplete 수동 설정 (§1.4) 추가
