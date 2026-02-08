# Phase 8-2-1: 코드 분석 워크플로우 구축 가이드

## 📋 개요

n8n에서 "Code Analysis" 워크플로우를 구축하여 Claude Code CLI를 사용해 코드를 분석하고, 결과를 PostgreSQL에 저장하는 자동화 시스템입니다.

**관련 문서:**

- [phase8-1-0-plan.md](./phase8-1-0-plan.md) - 전체 계획
- [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md) - Docker Compose 통합 관리 가이드

## ✅ 사전 준비 사항

### 1. n8n 컨테이너 설정 확인

n8n은 docker-compose로 통합 관리됩니다. 상세 내용은 [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md) 참조

n8n 컨테이너가 다음 볼륨 마운트로 실행 중인지 확인:

```bash
docker ps | grep n8n
# 또는
docker compose ps
```

볼륨 마운트:

- `n8n_data:/home/node/.n8n` - n8n 데이터 저장
- `/Users/map-rch/WORKS/personal-ai-brain-v2:/workspace` - 프로젝트 경로 (가이드 권장 경로)

### 2. PostgreSQL Credential 확인

n8n에서 PostgreSQL Credential이 등록되어 있어야 합니다:

- Credential Name: `PostgreSQL - PAB Knowledge`
- Host: `postgres` (docker-compose 네트워크 내에서는 컨테이너명 사용)
  - 또는 `host.docker.internal` (Mac/Windows에서 호스트 접근 시)
- Database: `knowledge`
- User: `brain`
- Password: `brain_password`
- Port: `5432`

**참고**: docker-compose로 실행 중인 경우, 같은 네트워크(`pab-network`)에 있으므로 `postgres`를 호스트로 사용할 수 있습니다.

### 3. Claude Code CLI 설치 확인

호스트 시스템에 Claude Code CLI가 설치되어 있고, PATH에 등록되어 있어야 합니다.

## 🔧 워크플로우 구축 단계

### Step 1: 새 워크플로우 생성

1. n8n 웹 인터페이스 접속: `http://localhost:5678`
2. **"Add workflow"** 클릭
3. 워크플로우 이름: `Code Analysis`

### Step 2: Manual Trigger 노드 추가

1. **"+" 버튼** 클릭
2. **"Manual Trigger"** 검색 및 선택
3. 노드 이름: `Manual Trigger`
4. 설정은 기본값 유지

### Step 3: Execute Command 노드 추가

1. Manual Trigger 노드에서 **"+" 버튼** 클릭
2. **"Execute Command"** 검색 및 선택
3. 노드 이름: `Execute Claude Code Analysis`

**⚠️ n8n Execute Command 노드에는 "Command" 필드만 있습니다**

- **Arguments 필드는 없습니다.** 실행할 **명령 전체**(실행 파일 + 인자)를 **Command 필드 한 칸**에 모두 입력합니다..
- [n8n 공식 문서](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/) 기준, 이 노드는 Command 파라미터 하나만 사용합니다.

**호스트 claude 사용:** docker-compose에 `/Users/map-rch/.npm-global:/host-npm-global:ro` 볼륨이 있으면, 컨테이너 안에서는 **`/host-npm-global/bin/claude`** 로 호스트의 claude를 실행할 수 있습니다. (claude는 Node 스크립트이며 `bin` → `../lib/node_modules/...` 심볼릭 링크이므로 `.npm-global` 전체 마운트가 필요합니다.)

**올바른 설정 (Command 필드에 전부 한 번에):**

**방법 1 – 스크립트 호출 (가장 단순):**

Command 필드에 아래 한 줄만 입력:

```
sh /workspace/scripts/run-claude-analysis.sh
```

**방법 2 – 직접 명령:**

Command 필드에 아래를 한 블록으로 입력 (여러 줄 가능):

```
sh -c 'cd /workspace && /host-npm-global/bin/claude "1. backend 폴더 전체 코드 분석
2. 현재 구현 상태 정리
3. current-state.md 파일 생성"'
```

**❌ 잘못된 설정:**

- Command 필드에 `Command`, `Arguments` 같은 레이블 이름을 넣으면 → `Command:: not found`, `Arguments:: not found` 발생.
- 명령과 인자를 다른 필드에 나누어 넣으려 하지 마세요. **모두 Command 필드에** 넣습니다.

**주의사항:**

- 프로젝트 경로는 컨테이너 내부 경로인 `/workspace`를 사용 (가이드 권장 경로)
- Claude Code CLI가 호스트에 설치되어 있으므로, 호스트의 절대 경로를 사용해야 함
- 컨테이너 내부에서 호스트의 실행 파일을 직접 실행할 수 없으므로, 호스트의 절대 경로를 사용하거나 다른 방법을 고려해야 함

**대안 1: 호스트 경로 직접 사용** — 위 "방법 2"처럼 Command 필드에 `sh -c '...'` 형태로 전부 입력하고, claude 경로는 컨테이너 경로 `/host-npm-global/bin/claude`를 사용하세요.

**대안 2: HTTP Request 노드 사용 (권장)**

호스트에 API 서버를 구축하고 HTTP Request 노드로 호출하는 방법이 더 안정적입니다.

### Step 4: Wait 노드 추가 (선택사항)

Claude Code 실행이 완료될 때까지 대기하는 노드를 추가할 수 있습니다.

1. Execute Command 노드에서 **"+" 버튼** 클릭
2. **"Wait"** 검색 및 선택
3. 노드 이름: `Wait for File`
4. 설정:
   - **Wait For**: `Time`
   - **Amount**: `10`
   - **Unit**: `seconds`

### Step 5: Read Binary File 노드 추가

1. Wait 노드(또는 Execute Command 노드)에서 **"+" 버튼** 클릭
2. **"Read Binary File"** 검색 및 선택
3. 노드 이름: `Read current-state.md`

**설정:**

```
File Path: /workspace/current-state.md
```

### Step 6: PostgreSQL 노드 추가

1. Read Binary File 노드에서 **"+" 버튼** 클릭
2. **"Postgres"** 검색 및 선택
3. 노드 이름: `Save to PostgreSQL`

**설정:**

- **Credential**: `PostgreSQL - PAB Knowledge` 선택
- **Operation**: `Execute Query`
- **Query**:

```sql
INSERT INTO workflow_phases (phase_name, status, current_state_md, created_at)
VALUES (
  'Phase-Code-Analysis',
  'draft',
  $1::TEXT,
  NOW()
)
RETURNING id, phase_name, status, created_at;
```

**Parameters:**

- `$1`: `{{ $json.data }}` (Read Binary File 노드의 데이터)

**전체 저장 vs 컨텍스트:** `workflow_phases.current_state_md`는 `TEXT`라 용량 제한 없이 전체를 넣을 수 있습니다. 다만 다음 단계(Gap 분석·Plan 생성)에서 이 값을 LLM 컨텍스트로 넣으면 토큰을 많이 씁니다. 권장:

- **옵션 A**: 생성 시 **요약 위주**로 제한 — 스크립트/프롬프트에서 "A4 2페이지 이내 요약 + 필요 시 상세는 부록" 형태로 요청해, 저장되는 내용 길이를 제한.
- **옵션 B**: **요약 컬럼 추가** — `current_state_summary`(예: 4000자)를 두고, Phase 8-2-2 등에서는 `current_state_summary`만 사용하고 `current_state_md`는 보관용으로만 사용.
- **옵션 C**: **전체 저장 + 읽을 때만 앞부분 사용** — DB에는 전체 저장하고, 다음 단계 워크플로우에서 `LEFT(current_state_md, 8000)` 등으로 잘라서 컨텍스트에 넣기.

### Step 7: 워크플로우 연결 확인

모든 노드가 다음과 같이 연결되어야 합니다:

```
Manual Trigger → Execute Command → Wait → Read Binary File → PostgreSQL
```

### Step 8: 테스트 실행

1. 워크플로우 저장
2. **"Execute Workflow"** 버튼 클릭
3. 각 노드의 실행 결과 확인

## 🔍 문제 해결

### 문제 1: Execute Command 노드 설정 오류

**증상**: `Command:: not found`, `Arguments:: not found` 오류

**원인**: n8n Execute Command 노드에는 **Command 필드만** 있습니다. 레이블 이름("Command", "Arguments")을 값으로 넣거나, 다른 UI를 기대하고 Arguments 필드를 찾는 경우 발생할 수 있습니다.

**해결 방법:**

1. **Command 필드 하나에 명령 전체 입력**
   - 실행 파일과 인자를 모두 Command 필드에 넣습니다. (예: `sh /workspace/scripts/run-claude-analysis.sh`)

2. **올바른 설정 예시 (스크립트 호출):**

   Command 필드에 한 줄만 입력:

   ```
   sh /workspace/scripts/run-claude-analysis.sh
   ```

3. **직접 명령 입력 예시:**

   Command 필드에:

   ```
   sh -c 'cd /workspace && /host-npm-global/bin/claude "1. backend 폴더 전체 코드 분석\n2. 현재 구현 상태 정리\n3. current-state.md 파일 생성"'
   ```

### 문제 2: Execute Command 노드가 작동하지 않음

**증상**: Execute Command 노드에서 권한 오류 또는 명령어 실행 실패

**해결 방법:**

1. **Docker 설정 확인**: `docker-compose.yml`에서 다음 설정이 포함되어 있는지 확인:

   ```yaml
   environment:
     # 노드 차단 해제 (가이드 권장 방법)
     - NODES_EXCLUDE='[]'
   volumes:
     # 프로젝트 폴더 마운트 (가이드 권장 경로)
     - /Users/map-rch/WORKS/personal-ai-brain-v2:/workspace
     # Docker socket 마운트 (필요 시)
     - /var/run/docker.sock:/var/run/docker.sock:ro
   ```

2. **n8n 컨테이너 재시작**:

   ```bash
   docker compose restart n8n
   ```

3. **명령어 실행 테스트**:
   ```bash
   docker exec n8n sh -c "echo 'Test' && ls /workspace | head -5"
   ```

### 문제 3: Claude Code CLI를 찾을 수 없음 (`/host-bin/claude: not found` 등)

**증상**: Execute Command 노드에서 `.../host-bin/claude: not found` 또는 `.../host-npm-global/bin/claude: not found` 오류

**원인**: 호스트의 `claude`는 `bin` → `../lib/node_modules/...` 심볼릭 링크인 Node 스크립트입니다. `.npm-global/bin`만 마운트하면 컨테이너 안에서 링크 대상이 없어 실행할 수 없습니다.

**해결 방법:**

1. **docker-compose 볼륨 확인**: `.npm-global` **전체**를 마운트해야 합니다.

   ```yaml
   - /Users/map-rch/.npm-global:/host-npm-global:ro
   ```

   스크립트·가이드에서는 **`/host-npm-global/bin/claude`** 경로를 사용하세요.

2. **볼륨 변경 후 n8n 재시작**:

   ```bash
   docker compose up -d n8n
   ```

3. **방법 A**: Command 필드에 한 번에 입력

   ```
   sh -c 'cd /workspace && /host-npm-global/bin/claude "1. backend 폴더 전체 코드 분석\n2. 현재 구현 상태 정리\n3. current-state.md 파일 생성"'
   ```

   또는 `sh /workspace/scripts/run-claude-analysis.sh` (스크립트 사용)

4. **방법 B**: HTTP Request 노드 사용 (권장)
   - 호스트에 API 서버 구축
   - n8n에서 HTTP Request로 API 호출

5. **방법 C**: 컨테이너에 Claude CLI 설치 시도

   ```bash
   # n8n 컨테이너에 접속
   docker exec -it n8n sh

   # npm이 있으면 설치 시도 (권한 문제로 실패할 수 있음)
   npm install -g @anthropic-ai/claude-code
   ```

### 문제 4: 파일을 읽을 수 없음

**증상**: Read Binary File 노드에서 파일을 찾을 수 없음

**해결 방법:**

1. 파일 경로 확인: `/workspace/current-state.md`
2. Execute Command 노드가 실제로 파일을 생성했는지 확인
3. Wait 노드의 대기 시간을 늘려보기

### 문제 5: PostgreSQL 연결 실패

**증상**: PostgreSQL 노드에서 연결 오류

**해결 방법:**

1. Credential 설정 확인
2. Host를 `postgres`로 설정 (docker-compose 네트워크 사용 시)
3. 또는 Host를 `host.docker.internal`로 변경 (Mac/Windows)

## 📝 완료 체크리스트

- [ ] n8n 컨테이너가 볼륨 마운트로 실행 중
- [ ] PostgreSQL Credential 등록 완료
- [ ] Manual Trigger 노드 추가
- [ ] Execute Command 노드 추가 및 설정 (Command 필드에 명령 전체 입력)
- [ ] Read Binary File 노드 추가 및 설정
- [ ] PostgreSQL 노드 추가 및 설정
- [ ] 워크플로우 테스트 실행 성공
- [ ] `current-state.md` 파일 생성 확인
- [ ] PostgreSQL에 데이터 저장 확인

## 🎯 다음 단계

워크플로우가 정상 작동하면:

1. **Phase 8-2-2**: Gap 분석 워크플로우 구축
2. **Phase 8-2-3**: Plan 생성 워크플로우 구축
3. **Phase 8-2-4**: Discord 승인 루프 구축

## 📚 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [PostgreSQL 노드 문서](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.postgres/)
- [Execute Command 노드 문서](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
- [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md) - Docker Compose 통합 관리

---

**작성일**: 2026-01-27  
**작성자**: AI Assistant  
**버전**: 1.2 (Execute Command 노드는 Command 필드만 있음 반영)  
**관련 문서**: [phase8-1-0-plan.md](./phase8-1-0-plan.md), [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md)
