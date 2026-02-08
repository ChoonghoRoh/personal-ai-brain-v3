# Task Execution v1 워크플로우 실행 결과 확인 방법

## 1. n8n UI에서 실행 로그 확인

### 1.1 실행 이력 확인
1. n8n UI → **Executions** 메뉴
2. **Task Execution v1** 워크플로우 실행 이력 확인
3. 각 실행 클릭 → 노드별 입력/출력 데이터 확인

### 1.2 노드별 출력 확인
워크플로우 편집 화면에서 각 노드 클릭 → **OUTPUT** 탭에서 확인:

| 노드 | 확인 내용 |
|------|----------|
| **DB_SelectPendingTask** | `status='pending'` Task 조회 결과 (id, task_name, plan_doc 등) |
| **JS_PrepareTaskPayload** | Backend로 전송할 payload (id, task_name, plan_doc, workspace_root) |
| **HTTP_RunTaskExecution** | Backend 응답 (`success`, `message`, `task_id`) |
| **JS_SetTaskStatusFromResponse** | 파생된 status (`completed` 또는 `failed`) 및 task id |
| **DB_UpdateTaskStatus** | UPDATE 쿼리 실행 결과 (affected rows) |

### 1.3 오류 확인
- 노드에 **빨간색 표시** → 클릭하여 에러 메시지 확인
- **HTTP_RunTaskExecution** 오류 시: Backend 연결/응답 확인
- **DB_UpdateTaskStatus** 오류 시: Query Parameters 및 DB 연결 확인

---

## 2. PostgreSQL에서 workflow_tasks 테이블 확인

### 2.1 Docker Compose 환경
```bash
# PostgreSQL 컨테이너 접속
docker exec -it pab-postgres psql -U brain -d postgres

# 또는 직접 쿼리 실행
docker exec -it pab-postgres psql -U brain -d postgres -c "SELECT * FROM workflow_tasks ORDER BY id DESC LIMIT 5;"
```

### 2.2 확인할 쿼리

#### 최근 실행된 Task 확인
```sql
SELECT 
  id,
  phase_id,
  task_name,
  status,
  created_at,
  completed_at
FROM workflow_tasks
ORDER BY id DESC
LIMIT 10;
```

#### 특정 Task 상세 확인
```sql
SELECT * FROM workflow_tasks WHERE id = 2;
```

#### 상태별 Task 개수
```sql
SELECT 
  status,
  COUNT(*) as count
FROM workflow_tasks
GROUP BY status;
```

#### Pending Task 확인 (다음 실행 대상)
```sql
SELECT * FROM workflow_tasks 
WHERE status = 'pending' 
ORDER BY id 
LIMIT 1;
```

#### 완료된 Task 확인
```sql
SELECT 
  id,
  task_name,
  status,
  completed_at,
  LEFT(plan_doc, 100) as plan_preview
FROM workflow_tasks
WHERE status = 'completed'
ORDER BY completed_at DESC
LIMIT 10;
```

#### 실패한 Task 확인
```sql
SELECT 
  id,
  task_name,
  status,
  created_at,
  completed_at
FROM workflow_tasks
WHERE status = 'failed'
ORDER BY id DESC;
```

---

## 3. Backend 로그 확인

### 3.1 Docker Compose 환경
```bash
# Backend 컨테이너 로그 실시간 확인
docker compose logs -f backend

# 최근 100줄만 확인
docker compose logs --tail=100 backend

# 특정 시간 이후 로그
docker compose logs --since=10m backend
```

### 3.2 확인할 로그 패턴
- `POST /api/workflow/run-task` 요청 로그
- Task 실행 시작/완료 메시지
- Claude Code CLI 실행 로그 (`claude -p ...`)
- 에러 메시지 (traceback 등)

### 3.3 예시 로그
```
INFO:     POST /api/workflow/run-task HTTP/1.1 200 OK
Task execution started: task_id=2
Running Claude Code CLI...
Task completed successfully: task_id=2
```

---

## 4. Discord 알림 확인 (활성화 시)

**DISCORD_SendTaskComplete** 노드가 **disabled: false**인 경우:

1. Discord 채널에서 메시지 확인
2. 메시지 형식:
   ```
   Task 실행 완료
   Task ID: 2
   Status: completed
   ```

**참고:** 기본적으로 `disabled: true`로 설정되어 있음. 활성화하려면 n8n UI에서 노드 설정 → **disabled** 체크 해제.

---

## 5. 생성된 파일 확인

Task 실행 결과로 생성된 파일 확인:

### 5.1 Task Plan/Test Plan 파일
```bash
# Task Plan 파일 확인
ls -lh docs/phases/tasks/task-*-plan.md

# Test Plan 파일 확인
ls -lh docs/phases/tasks/task-*-test.md

# 최근 생성된 파일 확인
ls -lth docs/phases/tasks/ | head -10
```

### 5.2 파일 내용 확인
```bash
# 특정 Task Plan 확인
cat docs/phases/tasks/task-2-plan.md

# 특정 Test Plan 확인
cat docs/phases/tasks/task-2-test.md
```

---

## 6. 종합 확인 체크리스트

워크플로우 실행 후 다음을 순서대로 확인:

- [ ] **n8n Executions**: 실행 이력에 성공/실패 표시 확인
- [ ] **HTTP_RunTaskExecution 노드**: Backend 응답 `success: true` 확인
- [ ] **DB_UpdateTaskStatus 노드**: UPDATE 쿼리 성공 확인
- [ ] **PostgreSQL**: `workflow_tasks.status = 'completed'` 및 `completed_at` 갱신 확인
- [ ] **Backend 로그**: Task 실행 완료 메시지 확인
- [ ] **생성된 파일**: `docs/phases/tasks/task-{id}-plan.md` 존재 확인 (해당 Task가 파일 생성하는 경우)

---

## 7. 문제 해결

### 7.1 Task가 실행되지 않는 경우
```sql
-- Pending Task가 있는지 확인
SELECT * FROM workflow_tasks WHERE status = 'pending' ORDER BY id LIMIT 1;
```
- 결과가 없으면 → Task Plan and Test Plan Generation 워크플로우를 먼저 실행하여 Task 생성

### 7.2 Task가 'failed' 상태인 경우
1. **n8n Executions**에서 실패한 실행 확인
2. **HTTP_RunTaskExecution** 노드 출력에서 Backend 에러 메시지 확인
3. **Backend 로그**에서 상세 에러 확인
4. 필요 시 Task를 다시 pending으로 변경:
   ```sql
   UPDATE workflow_tasks SET status = 'pending', completed_at = NULL WHERE id = 2;
   ```

### 7.3 Backend 연결 오류
- `ECONNREFUSED` → Backend 컨테이너 실행 상태 확인: `docker compose ps backend`
- `http://backend:8000` 접근 불가 → Docker 네트워크 확인

---

## 8. 빠른 확인 명령어 (요약)

```bash
# 1. 최근 실행된 Task 확인
docker exec -it pab-postgres psql -U brain -d postgres -c \
  "SELECT id, task_name, status, completed_at FROM workflow_tasks ORDER BY id DESC LIMIT 5;"

# 2. Pending Task 확인
docker exec -it pab-postgres psql -U brain -d postgres -c \
  "SELECT * FROM workflow_tasks WHERE status = 'pending' ORDER BY id LIMIT 1;"

# 3. Backend 로그 확인
docker compose logs --tail=50 backend | grep -i "task\|workflow"

# 4. 생성된 파일 확인
ls -lth docs/phases/tasks/ | head -5
```
