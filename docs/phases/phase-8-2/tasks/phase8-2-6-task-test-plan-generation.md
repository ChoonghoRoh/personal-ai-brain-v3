# Phase 8-2-6: Todo-List 기반 Task Plan 생성 워크플로우

**작성일**: 2026-01-28  
**최종 변경**: 2026-02-01 — todo-list 기반 Task Plan만 생성, test-report 완전 삭제  
**기반 문서**: phase8-1-0-plan.md  
**관련 문서**: phase8-2-5-todo-list-generation.md, `docs/n8n/rules/n8n node nameing Rules.md`

---

## 📋 개요

Phase 8-2-6는 **todo-list만 작성**하는 단계로 정리하며, Backend API는 **Task Plan(또는 todo용 산출물)만 생성**합니다.

- **Test Plan / Test Report**: 완전 삭제. 본 워크플로우에서는 생성하지 않음.
- **Claude 사용 토큰 표기**: CLI 경로에서는 구현 불가 시 **보류**.

**우선순위**: High  
**예상 소요 시간**: 2시간  
**의존성**: Phase 8-2-5 완료 (Todo-List 승인 완료 후)

---

## 🔄 워크플로우 방향

- **n8n 등**: "todo-list만 작성" 단계로 정리.
- **API `POST /api/workflow/generate-task-plan`**: Task Plan(또는 todo용 산출물)만 생성. test_plan 필드 없음.

**출력**: Task Plan 마크다운, `plan_md_path`(또는 plan_doc), workflow_tasks INSERT 시 test_plan_doc 은 사용하지 않거나 빈 값.

---

## 📋 n8n 2.2.6 워크플로우 (테스트용)

**대상 버전**: n8n 2.2.6  
**Import 파일**: `docs/n8n/workflow/Task Plan and Test Plan Generation v1 (test).json` (기존 파일; Task Plan만 사용하도록 노드 수정)

### 노드 구성 (PREFIX_VerbObject)

| STEP | 노드 이름 | 노드 유형 | 설명 |
|------|-----------|-----------|------|
| 0 | Trigger_Manual | Manual Trigger | 수동 실행 |
| 1 | SET_TestTodoList | Set | phase_id=1 등 테스트 입력 설정 |
| 2 | JS_ExpandTodoItems | Code | Todo 항목 배열 생성 (테스트 2건) |
| 3 | LOOP_TodoItems | Split In Batches | 항목별 1건씩 반복 (typeVersion 3) |
| 4 | HTTP_GenerateTaskPlan | HTTP Request | Backend `POST /api/workflow/generate-task-plan` — **Task Plan만** 응답 |
| 5 | JS_PrepareTaskOutput | Code | task_plan, plan_md_path 등만 추출 (test_plan 미사용) |
| 6 | CMD_WriteTaskFiles | Execute Command | task-N-plan.md 파일만 쓰기 |
| 7 | DB_InsertWorkflowTask | Postgres | workflow_tasks INSERT (plan_doc 또는 plan_md_path, test_plan_doc 빈 값 또는 미저장) |
| 8 | DISCORD_SendTaskPlansComplete | Discord | (선택, 기본 비활성) 알림 |

**루프**: DB_InsertWorkflowTask → LOOP_TodoItems (다음 항목). LOOP_TodoItems 출력 1(done) → DISCORD.

**테스트 Task DB 등록**: `scripts/db/insert_test_tasks.sql` 또는 `python scripts/db/insert_test_tasks_to_db.py` 실행 후 `SELECT * FROM workflow_tasks`로 확인.

---

## 🔄 워크플로우 구조 (요약)

**Todo-List 기반 Task Plan만 생성:**

```
[Manual Trigger 또는 Phase 8-2-5 완료 트리거]
    ↓
[PostgreSQL] (승인된 Todo-List 조회)
    ↓
[Code] (Todo-List 파싱 - 배열로 변환)
    ↓
[Split In Batches] (Todo 항목별 반복, batchSize=1)
    ↓
[HTTP Request] Backend POST /api/workflow/generate-task-plan
    → 요청: task_num, task_title, phase_slug, context_hint
    → 응답: task_plan, analyzed_files (test_plan 없음)
    ↓
[Code] (task_plan → plan_md_path 등 산출물 정리)
    ↓
[Execute Command 또는 Write Binary File] (task-N-plan.md 만 저장)
    ↓
[PostgreSQL] (workflow_tasks INSERT — plan_doc / plan_md_path, test_plan_doc 미사용 또는 null)
    ↓
[Discord] (간단 알림, 승인 생략 가능)
```

---

## 📝 작업 목록

### 1. "Task Plan Generation" 워크플로우 (Task Plan만)

**워크플로우 이름**: "Task Plan Generation" (또는 "Todo-List 기반 Task Plan 생성")

### 2. Code 노드 (Todo-List 파싱)

**Todo-List를 배열로 변환:**

```javascript
// todo-list.md 내용을 파싱하여 배열로 변환
const todoList = $input.item.json.todo_content;
const items = todoList
  .split("\n")
  .filter((line) => line.trim().startsWith("- [ ]"))
  .map((line, index) => ({
    index: index + 1,
    content: line.replace("- [ ]", "").trim(),
  }));

return items;
```

### 3. Loop Over Items 노드

**Todo 항목별 반복:** 각 항목에 대해 Task Plan만 생성.

### 4. HTTP Request 노드 (Task Plan만 생성)

- **URL**: `{{ $env.BACKEND_URL }}/api/workflow/generate-task-plan`
- **Method**: POST
- **Body (JSON)**:
  ```json
  {
    "task_num": "8-2-N",
    "task_title": "Todo 항목 제목",
    "phase_slug": "phase-8-2",
    "context_hint": "선택"
  }
  ```
- **응답**: `success`, `task_plan`, `analyzed_files`, `error` (test_plan 필드 없음)

### 5. Write Files 노드

- **파일**: `docs/phases/phase-8-2/tasks/task-{{ $json.todo_index }}-plan.md`
- **내용**: `{{ $json.task_plan }}`
- **Test Plan 파일(task-*-test.md)**: 생성하지 않음.

### 6. PostgreSQL 노드 (workflow_tasks)

**저장 시**: plan_doc 또는 plan_md_path 만 사용. test_plan_doc 은 빈 문자열 또는 null.

```sql
INSERT INTO workflow_tasks (
    phase_id, task_name, status, plan_doc, plan_md_path, created_at
) VALUES (
    $1, $2, 'pending', $3, $4, NOW()
)
RETURNING id;
```

(테이블에 test_plan_doc 컬럼이 있으면 null 또는 '' 로 설정)

### 7. Discord 알림 (선택)

**메시지 포맷:**

```
📋 Task Plans 생성 완료 (Task Plan만)

생성된 Task:
- Task 1: [이름]
- Task 2: [이름]
...
```

---

## ✅ 완료 기준

- [ ] Todo 항목별 Task Plan만 생성 가능
- [ ] Backend API 응답에 test_plan 없음 (Task Plan만 반환)
- [ ] task-N-plan.md 파일만 자동 저장
- [ ] PostgreSQL workflow_tasks 저장 (plan_doc / plan_md_path)
- [ ] Discord 알림 전송 (선택)
- [ ] 테스트 완료

---

## ⚠️ 보류·제외 사항

- **Test Plan / Test Report**: 본 워크플로우에서 생성하지 않음. 추후 task-result-report 기반 test-report 생성 워크플로우에서 별도 구현.
- **Claude 사용 토큰 표기**: CLI 경로에서는 usage 미제공. 구현 불가 시 **보류**.

---

## 📝 다음 단계

**Phase 8-2-7: Task 실행 워크플로우 (Claude-Code 실행 자동화)**

- 의존성: Phase 8-2-6 완료
- 입력: workflow_tasks 테이블의 Task 목록, task-N-plan.md
- 출력: Task .md를 실제로 수행하는 자동화 (run_task_execution.py + n8n)
- 문서: `phase8-2-7-task-execution-workflow.md`

**Phase 8-2-8: Task 테스트 및 결과 저장**

- 의존성: Phase 8-2-7 완료
- 입력: 8-2-7 완료 Task, 개발 완료 후 task-result-report
- 출력: task-result-report 기반 test-report 생성 워크플로우 별도 추가 예정
- 문서: `phase8-2-8-task-test-and-store-workflow.md`

---

## 🔗 관련 문서

- `phase8-2-5-todo-list-generation.md` - Todo-List 생성 워크플로우
- `phase8-1-0-plan.md` - n8n 워크플로우 개발 계획
- `phase8-master-plan.md` - Phase 8 전체 계획 (docs/phases/phase8-master-plan.md)
- Backend API: `POST /api/workflow/generate-task-plan` — Task Plan만 생성

---

**문서 버전**: 2.0  
**최종 업데이트**: 2026-02-01 — todo-list 기반 Task Plan만, test-report 삭제, usage 보류 반영
