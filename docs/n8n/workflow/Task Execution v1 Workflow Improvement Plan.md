# Task Execution v1 워크플로우 개선안

**작성일**: 2026-01-28  
**기준 워크플로우**: Phase Auto Checker v1  
**적용 대상**: Phase 8-2-7 Task 실행 워크플로우 (task-N-plan.md → Claude 실행 → DB 갱신)

---

## 1. 개선 목적

Phase Auto Checker v1과 동일한 **문서 구조·실행 흐름·노드 명명 규칙**을 Task 실행 워크플로우에 적용한다.

- **참조 문서**
  - `docs/n8n/workflow/Phase Auto Checker v1 Workflow.md` — 전체 이름 형식, STEP 구성, 참조 파일 구조
  - `docs/n8n/rules/n8n node nameing Rules.md` — 노드 명명 규칙 (PREFIX_VerbObject)
- **결과**
  - 노드 이름만으로 역할 파악 가능
  - AI/사람이 구조적으로 이해·생성·수정 가능
  - Phase Auto Checker와 동일한 설계 철학으로 일관성 유지

---

## 2. 적용할 문서 구조 (Phase Auto Checker v1과 동일)

| 섹션 | 내용 |
|------|------|
| 1. Workflow 목적 | 한 문단으로 목적 정의 |
| 2. 참조 파일 구조 | 2.1 산출물/입력 디렉토리, 2.2 규칙·판단 문서, 2.3 시스템 컨텍스트, 2.4 Node Naming 규칙 참조 |
| 3. 전체 실행 흐름 | STEP 0~N, 각 STEP별 노드 이름(PREFIX_VerbObject) 명시 |
| 4. Workflow 성격 요약 | 철학·원칙 한 줄 요약 |
| 5. 향후 리팩토링 분리 기준 | 서브 워크플로우 분리 가이드 |

---

## 3. Task 실행 워크플로우에 적용할 노드 명명 (n8n 규칙)

형식: **PREFIX_VerbObject**

| STEP | 노드 이름 (예시) | 노드 유형 | 설명 |
|------|------------------|-----------|------|
| 0 | (Trigger) | Manual / Webhook | 수동 또는 8-2-6 완료 트리거 |
| 1 | DB_SelectPendingTask | PostgreSQL | status='pending' Task 1건 조회 |
| 2 | IF_HasPendingTask | If | 결과 있음 → 실행 분기 |
| 3 | JS_PrepareTaskPayload | Code | task_id, plan_doc, workspace 경로 등 정리 |
| 4 | CMD_RunTaskExecution | Execute Command | run_task_execution.py 호출 |
| 5 | DB_UpdateTaskStatus | PostgreSQL | status='in_progress' → 'completed' (또는 스크립트 내 갱신) |
| 6 | DISCORD_SendTaskComplete | Discord Webhook | (선택) Task-N 실행 완료 알림 |
| 7 | LOOP_NextTaskOrTrigger | Loop / 다음 워크플로우 | 남은 Task 반복 또는 8-2-8 트리거 |

- **실패 분기**: CMD 실패 시 DB_UpdateTaskStatus(status='failed'), DISCORD_SendTaskFailure(선택)

---

## 4. 참조 파일 구조 (Task 실행용)

### 2.1 Task 산출물 디렉토리

- **경로**: `docs/phases/tasks/`
- **검사/입력 대상 파일**
  - `task-{N}-plan.md` — 실행할 Task Plan
  - `task-{N}-test.md` — (8-2-8에서 사용) Test Plan
- **출력**: 스크립트가 코드 변경 수행; 필요 시 `task-{N}-result.md` (8-2-8에서 생성)

### 2.2 규칙 / 판단 문서

- `docs/n8n/rules/n8n node nameing Rules.md` — 노드 명명
- (선택) `docs/ai/` — Task Plan 형식, 완료 기준 등 AI 판단 규칙

### 2.3 시스템 컨텍스트

- `README.md` — 프로젝트 개요 (참고용)
- PostgreSQL `workflow_tasks` — Task 메타데이터, plan_doc, test_plan_doc, status

### 2.4 Workflow Node Naming 규칙

- `docs/n8n/rules/n8n node nameing Rules.md` — 워크플로우 생성 시 노드 이름 규칙

---

## 5. 전체 실행 흐름 (개선안 요약)

```
STEP 0. Manual Trigger (또는 Phase 8-2-6 완료 Webhook)
STEP 1. DB_SelectPendingTask — pending 1건 조회
STEP 2. IF_HasPendingTask — 있으면 실행 분기
STEP 3. JS_PrepareTaskPayload — 실행 인자 정리
STEP 4. CMD_RunTaskExecution — run_task_execution.py --task-id {{ id }}
STEP 5. DB_UpdateTaskStatus — completed / failed
STEP 6. DISCORD_SendTaskComplete — (선택) 알림
STEP 7. LOOP_NextTaskOrTrigger — 다음 Task 또는 8-2-8 트리거
```

---

## 6. 개발 준비 체크리스트

- [ ] `phase8-2-7-task-execution-workflow.md`를 위 구조·노드 명명에 맞게 업데이트
- [ ] n8n 워크플로우 생성 시 위 노드 이름(PREFIX_VerbObject) 적용
- [ ] `scripts/n8n/run_task_execution.py` 스펙 확정 (인자, 환경 변수, exit code)
- [ ] Phase Auto Checker v1과 동일하게 "문서 = 상태, 상태 = 다음 행동 트리거" 관점 유지

---

## 7. n8n Import용 JSON

**파일**: `docs/n8n/workflow/Task Execution v1.json`

- 위 STEP 0~7 및 노드 명명 규칙을 반영한 n8n 워크플로우 JSON.
- **Import 방법**: n8n UI → Workflows → Import from File → `Task Execution v1.json` 선택.
- **Import 후 설정**
  - **DB_SelectPendingTask**, **DB_UpdateTaskStatus**: PostgreSQL Credential 선택 (또는 `YOUR_POSTGRES_CREDENTIAL_ID` 교체).
  - **DISCORD_SendTaskComplete**: Discord Credential 및 Channel ID 설정 (필요 시 노드 활성화).
  - **CMD_RunTaskExecution**: 작업 디렉토리(프로젝트 루트) 및 `scripts/n8n/run_task_execution.py` 경로 확인.
- **추가 노드**: 0건 조회 시 흐름 정리용 `JS_NormalizePendingTaskResult`, exit code 기반 status 설정용 `JS_SetTaskStatusFromExitCode` 포함.

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-28
