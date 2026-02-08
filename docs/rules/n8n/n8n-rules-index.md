# n8n Rules 인덱스

**용도**: `docs/n8n/rules/`에 등록된 규칙 문서의 요약·명령(패턴)·주석 정리.
**최종 수정**: 2026-02-04

---

## 1. 등록 문서 목록

| 파일                                                          | 설명                                                            |
| ------------------------------------------------------------- | --------------------------------------------------------------- |
| [n8n-rule-node-naming.md](references/n8n-rule-node-naming.md) | n8n 워크플로우 **노드 명명 규칙** (Prefix·동사·대상, 금지 규칙) |

※ Phase·Task 문서 생성 명령([phase-x-navi:make], [phase-x-plan-todo:make])은 `docs/ai/` 룰에 등록되어 있으며, n8n 워크플로우와 연동 시 본 노드 명명 규칙을 따른다.

---

## 2. 규칙 요약

### 2.1 노드 명명 규칙 (Node Naming Rules) 요약

- **목적**: 노드 이름만으로 역할 파악, AI의 구조적 이해·생성·수정, Phase/자동화/로그 시 일관된 기준 제공.
- **기본 원칙**:
  1. 노드는 **기능 단위**만 표현. Phase/Step/순서 번호는 노드 이름에 넣지 않음.
  2. **Prefix**로 노드 타입을 구분 (JS*, GPT*, CMD*, DB* 등).
  3. **동사 + 대상(Object)** 구조로, 한 문장으로 해석 가능하게 작성.

---

## 3. 명령(패턴) 정리 — 노드 이름 형식

### 3.1 기본 형식

```
<PREFIX>_<Verb><Object>
```

- **PREFIX**: 노드 유형 (대문자·밑줄 뒤 동사)
- **Verb**: 동사 (Create, Set, Write 등)
- **Object**: 대상 (단수형, 워크플로우 전반 동일 개념은 동일 명칭)

### 3.2 Prefix 별 용도 (명령·역할)

| Prefix        | 노드 유형         | 역할                       | 예시                                           |
| ------------- | ----------------- | -------------------------- | ---------------------------------------------- |
| **JS\_**      | Code (JavaScript) | 데이터 가공, 계산, 파싱    | JS_SetNextPhaseId, JS_ParseTodoItems           |
| **GPT\_**     | LLM 호출          | AI 응답 생성               | GPT_CreatePlan, GPT_CreateTodoList             |
| **CMD\_**     | Execute Command   | 쉘·CLI·스크립트 실행       | CMD_WritePlanFile, CMD_WriteTodoFile           |
| **DB\_**      | Database          | PostgreSQL 등 DB 읽기/쓰기 | DB_InsertWorkflowPlan, DB_UpdateApprovalStatus |
| **IF\_**      | If                | 조건 분기                  | IF_CheckApproval                               |
| **LOOP\_**    | Loop / Split      | 반복 처리                  | LOOP_TodoItems                                 |
| **FILE\_**    | Binary File       | 파일 읽기/쓰기             | FILE_ReadPlanFile                              |
| **DISCORD\_** | Discord           | 메시지·승인·알림           | DISCORD_SendApprovalRequest                    |
| **SET\_**     | Set               | 변수 설정                  | SET_PhaseId                                    |
| **HTTP\_**    | HTTP Request      | 외부 API 호출              | HTTP_GenerateTaskPlan                          |
| **TEST\_**    | 테스트용          | 테스트·실험 (제거 대상)    | TEST_DiscordWebhook                            |
| **TEMP\_**    | 임시용            | 임시 처리 (제거 대상)      | TEMP_ParsePlanResult                           |

### 3.3 동사(Verb) 권장 목록

| 동사     | 의미           |
| -------- | -------------- |
| Create   | 생성           |
| Set      | 값 설정        |
| Parse    | 파싱           |
| Check    | 조건 확인      |
| Validate | 검증           |
| Generate | 생성 (AI 결과) |
| Insert   | DB 삽입        |
| Update   | DB 갱신        |
| Read     | 읽기           |
| Write    | 쓰기           |
| Send     | 전송           |
| Receive  | 수신           |

### 3.4 Object(대상) 예시

- PhaseId, Plan, TodoList, TaskPlan, TestPlan, ApprovalResult, WorkflowPlan, PlanMdPath 등.
- 동일 개념은 워크플로우 전반에서 **동일 Object 명칭** 사용.

---

## 4. 금지 규칙 (주석)

- **Phase/Step/순서 번호 포함 금지**
  예: `Phase8_CreatePlan_JS`, `Step3_WriteFile` ❌

- **추상적·의미 없는 이름 금지**
  예: `ProcessData`, `HandleThis` ❌

- **한 노드에 여러 책임 금지**
  예: `JS_ParseAndSaveAndNotify` ❌

- **테스트/임시 노드**: Prefix **TEST\_**·**TEMP\_** 로 구분하고, 최종 워크플로우에서는 제거 또는 교체 대상으로 둠.

---

## 5. 적용 범위·변경 관리 (원문 주석)

- **적용 범위**: 모든 n8n 워크플로우, Phase 자동화·승인 루프·테스트 자동화·리포트 생성, 향후 AI 기반 워크플로우 자동 생성.
- **변경 관리**: 규칙 변경 시 버전 관리 문서에 기록. Prefix 추가 시 전체 워크플로우 영향 검토 필수.
- **문서 상태**: Active Rule. 권장 적용 시작 Phase: Phase 8 이후 전체.

---

## 6. 관련 문서 (n8n 외)

| 문서                                                                                                               | 용도                                                     |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| [../rules-index.md](../rules-index.md)                                                                             | 통합 Rules 인덱스 (문서 분류, n8n, AI 룰, Phase 폴더)    |
| ~~[../common/references/common-rules-and-conventions.md](../common/references/common-rules-and-conventions.md)~~   | ⚠️ DEPRECATED                                            |
| [../ai/references/ai-rule-phase-navigation-generation.md](../ai/references/ai-rule-phase-navigation-generation.md) | [phase-x-navi:make] — phase-X-navigation 생성            |
| [../ai/references/ai-rule-phase-plan-todo-generation.md](../ai/references/ai-rule-phase-plan-todo-generation.md)   | [phase-x-plan-todo:make] — phase-X-Y plan·todo-list 생성 |
| (n8n 워크플로우 JSON은 원본 docs/n8n/workflow/ 참고)                                                               | n8n 워크플로우 JSON·Workflow.md                          |
