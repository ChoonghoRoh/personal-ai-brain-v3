# Phase 8-2-4 ~ 8-2-6 개발 진행사항 체크

**기준일**: 2026-01-28  
**대상**: Phase 8-2-4 (Discord 승인 루프), 8-2-5 (Todo-List 생성), 8-2-6 (Task Plan & Test Plan 생성)

---

## 요약

| Phase | 항목 | 상태 | 비고 |
|-------|------|------|------|
| **8-2-4** | Discord 승인 루프 구축 | ⏳ 미진행 | 계획·검토 문서만 있음, n8n 워크플로우 미구현 |
| **8-2-5** | Todo-List 생성 | ⏳ 미진행 | 8-2-4 의존, 워크플로우·GPT 연동 없음 |
| **8-2-6** | Task Plan & Test Plan 생성 | 🔄 부분 완료 | 테스트용 n8n 워크플로우만 구현, Todo-List 연동·GPT 버전 미구현 |

---

## Phase 8-2-4: Discord 승인 루프 구축

### 계획 요약

- Plan 문서를 Discord로 전송 → 사용자 승인/거절/수정 반응 → `workflow_approvals` 저장 → 다음 단계 분기
- 노드: PostgreSQL(Plan 조회) → Discord Webhook(Plan 전송) → Wait(Webhook) → Discord Trigger(Reaction) → IF → PostgreSQL(approvals)

### 체크리스트

| # | 작업 | 상태 | 비고 |
|---|------|------|------|
| 1 | 승인 요청 메시지 형식 정의 | ✅ 문서화됨 | phase8-2-4-discord-approval-loop.md, phase8-2-4-discord-approval-review.md |
| 2 | Discord Webhook 노드 설정 | ⏳ 미구현 | n8n에 "Plan 승인 요청" 워크플로우 없음 |
| 3 | Wait 노드 (Webhook Path: discord-approval) | ⏳ 미구현 | |
| 4 | Discord Trigger (Message Reaction 감지) | ⏳ 미구현 | 별도 워크플로우 "Discord Approval Trigger" 계획만 있음 |
| 5 | IF 분기 (승인/수정/거절) → PostgreSQL | ⏳ 미구현 | |
| 6 | workflow_approvals 테이블 활용 | ✅ 스키마 존재 | current-state-260128.md 기준 생성 완료, 사용 워크플로우 없음 |
| 7 | Discord 봇·Webhook URL·n8n Credential | ✅ 완료 | phase8-2-4-discord-approval-review.md 기준 |

### 결론

- **준비**: Discord 봇, PostgreSQL `workflow_approvals` 스키마, 계획·검토 문서 완료.
- **미완**: n8n 워크플로우(Plan 전송 → Wait → Reaction 감지 → DB 저장) 미구현. **다음 단계: 8-2-4 n8n 워크플로우 구축.**

---

## Phase 8-2-5: Todo-List 생성

### 계획 요약

- 승인된 Plan 조회 → GPT API로 Todo-List 생성 → todo-list.md 저장 → Discord 승인 루프(8-2-4 재사용) → 승인 시 PostgreSQL 저장

### 체크리스트

| # | 작업 | 상태 | 비고 |
|---|------|------|------|
| 1 | "Todo-List Generation" 워크플로우 생성 | ⏳ 미구현 | n8n에 해당 워크플로우 JSON 없음 |
| 2 | PostgreSQL 승인된 Plan 조회 | ⏳ 미구현 | |
| 3 | HTTP Request (GPT API) Todo-List 생성 | ⏳ 미구현 | |
| 4 | Write Binary File (todo-list.md) | ⏳ 미구현 | |
| 5 | Discord 전송 (8-2-4 승인 루프 재사용) | ⏳ 미구현 | 8-2-4 선행 필요 |
| 6 | 승인 후 todo-list 저장 (PostgreSQL 등) | ⏳ 미구현 | |

### 결론

- **의존성**: Phase 8-2-4 완료 후 진행.
- **현재**: 워크플로우·GPT 연동·파일 생성 모두 미구현. **8-2-4 완료 후 8-2-5 워크플로우 설계·구현 필요.**

---

## Phase 8-2-6: Task Plan & Test Plan 생성

### 계획 요약

- **테스트용**: 고정 Todo 항목 → Code(Task/Test Plan 텍스트) → Execute Command(파일 쓰기) → workflow_tasks INSERT → Discord 알림
- **전체용**: 승인된 Todo-List 조회 → Loop → GPT(Task Plan / Test Plan) → 파일 쓰기 → workflow_tasks INSERT

### 체크리스트

| # | 작업 | 상태 | 비고 |
|---|------|------|------|
| 1 | "Task Plan & Test Plan Generation" 워크플로우 | ✅ 테스트용 있음 | `Task Plan and Test Plan Generation v1 (test).json` |
| 2 | Trigger_Manual → SET_TestTodoList → JS_ExpandTodoItems | ✅ 구현됨 | 테스트용 고정 2건 |
| 3 | LOOP_TodoItems (Split In Batches) | ✅ 구현됨 | |
| 4 | JS_CreateTaskPlanAndTestPlan (Plan/Test 텍스트 + base64) | ✅ 구현됨 | |
| 5 | CMD_WriteTaskFiles (task-N-plan.md, task-N-test.md) | ✅ 구현됨 | /workspace/docs/phases/tasks/ |
| 6 | DB_InsertWorkflowTask (workflow_tasks INSERT) | ✅ 구현됨 | |
| 7 | DISCORD_SendTaskPlansComplete | ✅ 구현됨 | (기본 비활성 가능) |
| 8 | docs/phases/tasks/ 디렉터리 | ✅ 존재 | .gitkeep 포함 |
| 9 | PostgreSQL workflow_tasks 연동 | ✅ 사용 중 | Task Execution v1에서 pending 조회·실행·status 갱신 |
| 10 | 승인된 Todo-List 조회 → GPT API 연동 (전체 버전) | ⏳ 미구현 | 8-2-5 완료 후, Todo 기반 루프·GPT 호출 필요 |

### 결론

- **테스트용**: 수동 트리거 → 고정 Todo 2건 → Task/Test Plan 생성 → 파일 쓰기 → workflow_tasks INSERT → Discord 알림까지 **구현 완료**. 실행 검증 가능.
- **전체 버전**: Todo-List 연동·GPT API 호출은 미구현. **8-2-5 완료 후 Todo 기반 루프·GPT 노드 추가 필요.**

---

## 다음 액션 우선순위

1. **Phase 8-2-4**: n8n에서 "Discord Plan 승인 루프" 워크플로우 구축 (Discord Webhook → Wait → Reaction 감지 → workflow_approvals 저장).
2. **Phase 8-2-5**: 8-2-4 완료 후 "Todo-List Generation" 워크플로우 구축 (Plan 조회 → GPT → todo-list.md → Discord 승인 → 저장).
3. **Phase 8-2-6**: (선택) 승인된 Todo-List 연동 및 GPT 기반 Task/Test Plan 생성으로 "전체 버전" 확장.

---

## 참조 문서

- `phase8-2-4-discord-approval-loop.md` — 8-2-4 워크플로우 계획
- `phase8-2-4-discord-approval-review.md` — 8-2-4 검토·준비 상태
- `phase8-2-5-todo-list-generation.md` — 8-2-5 워크플로우 계획
- `phase8-2-6-task-test-plan-generation.md` — 8-2-6 워크플로우 계획·테스트 버전 설명
- `docs/n8n/workflow/Task Plan and Test Plan Generation v1 (test).json` — 8-2-6 테스트용 워크플로우
- `docs/n8n/workflow/Task Execution v1.json` — 8-2-7 Task 실행 (workflow_tasks 사용)
