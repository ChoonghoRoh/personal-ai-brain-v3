# Task 생성 규칙

**용도**: Phase의 todo-list에서 **Task 문서**를 생성·갱신하기 위한 규칙과 **[task-x-y:make]** 명령을 정의한다.  
**기준 문서**: [phase-document-taxonomy.md](../phase-document-taxonomy.md) §2.4, [ai-rule-decision.md](ai-rule-decision.md) §2·§4, [ai-rule-phase-naming.md](ai-rule-phase-naming.md) §7, [ai-rule-task-inspection.md](ai-rule-task-inspection.md) §3  
**참고 결과물**: [phase-10-1/tasks/](../phases/phase-10-1/tasks/), [phase-10-2/tasks/](../phases/phase-10-2/tasks/)  
**버전**: 1.0  
**작성일**: 2026-02-04

---

## 1. 명령 등록

### 1.1 [task-x-y:make] 명령

| 항목 | 내용 |
|------|------|
| **명령** | `[task-x-y:make]` (X-Y = Phase ID, 예: 10-1, 11-2) |
| **트리거** | 사용자가 해당 명령을 요청하거나, phase-X-Y의 todo-list는 있으나 tasks/ 내 Task 문서가 없거나 보완이 필요할 때 |
| **필수 입력** | `docs/phases/phase-X-Y/phase-X-Y-0-todo-list.md` (또는 해당 Phase의 todo-list 파일). 없으면 "todo-list 없음" 안내 후 중단. |
| **선택 입력** | `docs/phases/phase-X-master-plan.md`, `docs/phases/phase-X-navigation.md` — Task 명·의존성·예상 참고용. |
| **출력** | `docs/phases/phase-X-Y/tasks/` 하위에 todo 항목별 **Task 실행 계획 문서** 1건씩 생성 또는 갱신. |

### 1.2 실행 절차

1. **phase-X-Y 확인**: `docs/phases/phase-X-Y/` 존재 여부 확인. 없으면 "phase-X-Y 폴더 없음" 안내 후 중단.
2. **todo-list 확인**: `phase-X-Y-0-todo-list.md`(또는 해당 Phase의 todo-list 파일명) 존재·읽기. "Task 목록" 또는 "Task 목록 (세부 단계 포함)" 섹션에서 **Task ID(X-Y-N)** 및 **Task 명** 추출.
3. **tasks/ 폴더 확보**: `docs/phases/phase-X-Y/tasks/` 없으면 생성.
4. **Task별 문서 생성**:
   - 각 Task ID(예: 10-1-1, 10-1-2)에 대해:
     - **파일명**: `task-X-Y-N-<topic>.md` (topic = 해당 Task 명에서 유도한 kebab-case, 예: progress-status, cancel, eta). Task 명이 긴 경우 핵심 키워드만 사용.
     - **저장 위치**: `docs/phases/phase-X-Y/tasks/`.
     - **내용**: §3 Task 문서 공통 규약에 따라 작성. todo-list의 해당 Task 블록(우선순위, 예상 작업량, 의존성, 체크리스트)을 반영.
5. **상호 참조**: 각 Task 문서에 기준 문서 링크(phase-X-Y-0-plan.md, phase-X-Y-0-todo-list.md, phase-X-navigation.md) 반영.
6. **누락 검사**: todo-list의 Task 개수와 생성된 task 문서 개수 일치 여부 확인.

---

## 2. Task 생성 규칙 (종합)

### 2.1 생성 조건

| 조건 | 내용 |
|------|------|
| **유도 원천** | Task 문서는 **todo-list에서 유도된 항목**에 대해서만 생성. [phase-document-taxonomy.md](../phase-document-taxonomy.md) §2.4, [ai-rule-decision.md](ai-rule-decision.md) §4. |
| **저장 위치** | `docs/phases/phase-X-Y/tasks/`. Phase 루트가 아님. |
| **N (순번)** | todo-list의 Task 순서와 동일. N = 1, 2, 3, … (todo 항목 순번). |
| **Phase 없이 생성 금지** | phase-X-Y 폴더·plan·todo-list 없이 Task만 생성하지 않음. [ai-rule-phase-naming.md](ai-rule-phase-naming.md) §8. |

### 2.2 파일명 규칙

| 구분 | 파일명 패턴 (권장) | 파일명 패턴 (변형) | 참고 결과물 |
|------|---------------------|---------------------|-------------|
| **Task 실행 계획** | `task-X-Y-N-<topic>.md` | `phaseX-Y-N-task.md` | phase-10-1: task-10-1-1-progress-status.md, task-10-1-2-cancel.md, task-10-1-3-eta.md. phase-10-2: task-10-2-1-design-explain-viz.md, task-10-2-2-risk-review-matrix.md 등. |
| **Task 테스트 결과** | `phaseX-Y-N-task-test-result.md` | `phaseX-Y-N-<topic>-test-report.md` | phase-X-Y/ 루트에 저장. [ai-rule-task-inspection.md](ai-rule-task-inspection.md) §3.1. |

- **topic**: 해당 Task 명에서 유도한 **kebab-case** 짧은 식별자. 예: "진행 상태 실시간 표시" → progress-status, "취소 기능" → cancel, "설계 설명 시각화" → design-explain-viz.
- **일관성**: 한 Phase 내에서는 권장 패턴을 우선 사용. phase-10-1, phase-10-2는 `task-X-Y-N-<topic>.md` 사용.

### 2.3 Task 문서당 1:1

- todo-list의 **하나의 Task 블록**(예: 10-1-1: 진행 상태 실시간 표시)당 **Task 실행 계획 문서 1건** 생성.
- 세부 단계(11-3-1a, 11-3-1b 등)가 있는 경우, Phase별 규약에 따라 하나의 Task 문서에 하위 단계를 섹션으로 넣거나, Phase에서 별도 Task ID를 부여한 경우에만 별도 파일 생성.

---

## 3. Task 문서 공통 규약 (task-X-Y-N-<topic>.md)

AI가 동일한 구조로 Task 문서를 생성·검증할 수 있도록 **필수 섹션과 순서**를 정한다.

### 3.1 문서 상단 (메타)

```markdown
# Task X-Y-N: <Task 명>

**우선순위**: X-Y 내 N순위
**예상 작업량**: <todo-list에서 추출>
**의존성**: <todo-list에서 추출>
**상태**: ⏳ 대기

**기반 문서**: [phase-X-Y-0-todo-list.md](../phase-X-Y-0-todo-list.md)
**Plan**: [phase-X-Y-0-plan.md](../phase-X-Y-0-plan.md)
**작업 순서**: [phase-X-navigation.md](../../phase-X-navigation.md) (있을 경우)
```

- **Task 명**: todo-list의 해당 Task 블록 제목과 **동일**하게 기재.

### 3.2 §1. 개요 (목표)

- **1.1 목표**: 해당 Task의 목표를 1~2문장으로 기술. todo-list·plan의 해당 Task 설명 반영.
- **1.2 (선택) 세부 목표·정의**: 표·리스트로 정의가 필요한 경우만 포함.

### 3.3 §2. 파일 변경 계획 (또는 작업 범위)

- **2.1 신규 생성**: 생성할 파일·경로·용도 표로 정리.
- **2.2 수정**: 수정할 파일·경로·용도 표로 정리.
- 코드를 건드리지 않는 Task(문서화, 검토 등)는 "작업 범위"로 대체 가능.

### 3.4 §3. 작업 체크리스트 (또는 완료 기준)

- todo-list의 해당 Task 체크리스트 항목을 **그대로 또는 세분화**하여 나열.
- 완료 시 [x], 미완료 시 [ ] 유지.
- **Done Definition**: 이 섹션을 모두 충족하면 Task 완료로 판단. [ai-rule-task-inspection.md](ai-rule-task-inspection.md) §1·§2 참고.

### 3.5 §4. (선택) 참조·비고

- 관련 이슈, 선행 Task, 테스트 방법 등.

### 3.6 Task 문서 누락 방지 체크리스트 (AI 검증용)

- [ ] Task ID·Task 명이 todo-list·plan과 일치하는가?
- [ ] 우선순위·예상 작업량·의존성이 todo-list에서 추출한 값과 동일한가?
- [ ] 작업 체크리스트(완료 기준)가 todo-list 해당 블록과 대응하는가?
- [ ] 기반 문서 링크(plan, todo-list, navigation)가 올바른가?

---

## 4. 참고 결과물 폴더

| Phase | 경로 | Task 문서 예시 |
|-------|------|----------------|
| **10-1** | [docs/phases/phase-10-1/tasks/](../phases/phase-10-1/tasks/) | task-10-1-1-progress-status.md, task-10-1-2-cancel.md, task-10-1-3-eta.md |
| **10-2** | [docs/phases/phase-10-2/tasks/](../phases/phase-10-2/tasks/) | task-10-2-1-design-explain-viz.md, task-10-2-2-risk-review-matrix.md, task-10-2-3-next-steps-roadmap.md, task-10-2-4-history-trace-timeline.md |

- 위와 동일한 **파일명 패턴**(task-X-Y-N-<topic>.md)과 **문서 구조**(개요, 파일 변경 계획, 작업 체크리스트)를 따르면 된다.
- Task 테스트 결과는 phase-X-Y **루트**에 `phaseX-Y-N-task-test-result.md` 형태로 둔다(phase-10-1, phase-10-2 참고).

---

## 5. 관련 룰·규약

| 문서 | 용도 |
|------|------|
| [ai-rule-decision.md](ai-rule-decision.md) §2·§4 | 문서 저장 위치, Todo → Task 판단 규칙 |
| [phase-document-taxonomy.md](../phase-document-taxonomy.md) §2.4 | Task 문서 종류·파일명·생성 주체 |
| [ai-rule-phase-naming.md](ai-rule-phase-naming.md) §7·§8 | phase-X-Y/tasks/ 구조, Phase 없이 Task 생성 금지 |
| [ai-rule-task-inspection.md](ai-rule-task-inspection.md) §1·§3 | Task 완료 검사·산출물·파일명 저장 규칙 |
| [ai-rule-phase-plan-todo-generation.md](ai-rule-phase-plan-todo-generation.md) | plan·todo-list 생성 후 Task 생성 순서 권장 |

---

## 6. 실행 순서 권장

1. **phase-X-master-plan** 작성  
2. **[phase-x-navi:make]** → phase-X-navigation.md 생성  
3. **[phase-x-plan-todo:make]** → 각 phase-X-Y에 plan·todo-list 생성  
4. **[task-x-y:make]** → 특정 phase-X-Y에 대해 todo-list 기반 Task 문서 생성  

- 특정 Phase(예: 11-1)만 Task 문서가 필요할 때는 `[task-11-1:make]`만 실행하면 된다.
