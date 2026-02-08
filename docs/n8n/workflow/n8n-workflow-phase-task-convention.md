# n8n 워크플로우 — Phase·Task 규정 준수

**참조 문서**: `docs/phase-document-taxonomy.md`, `docs/ai/ai-rule-decision.md`  
**목적**: n8n 워크플로우가 Phase 정의, Phase 폴더·파일 규정, todo-list·Task 규정과 일치하도록 경로·파일명·입출력 규칙을 정리한다.

---

## 1. 참조 규정 요약

### 1.1 Phase 정의 (taxonomy·ai-rule)

- **Phase**: 하나의 명확한 목표를 가진 개발 단위. 완료 여부를 판단할 수 있고 반드시 종료되는 작업 묶음.
- **Phase ID**: `Phase-X-Y-Z` (파일·폴더에서는 `phase-X-Y`, `phaseX-Y-Z` 형식 사용).

### 1.2 Phase 폴더 규정 (ai-rule-decision §2)

| 구분 | 경로 | 비고 |
|------|------|------|
| Phase 단위 | `docs/phases/phase-X-Y/` | 예: `docs/phases/phase-8-0/` |
| Task 문서 | `docs/phases/phase-X-Y/tasks/` | 해당 Phase의 todo-list에서 유도된 Task만 |

- Phase 루트에 전체 계획이 필요하면 `docs/phases/phaseX-master-plan.md` 등 사용 가능.

### 1.3 Phase 단위 파일 규정 (ai-rule-decision §2-1)

| 문서 종류 | 파일명 패턴 | 비고 |
|-----------|-------------|------|
| Phase 설계 | `phaseX-Y-Z-plan.md` | Z = 반복(0,1,2…), 생략 시 0 |
| Phase 할 일 | `phaseX-Y-Z-todo-list.md` | todo-list에서 Task 유도 |
| Phase 요약 | `phaseX-Y-Z-summary.md` | Phase 종료 시 |
| 테스트 증빙 | `phaseX-Y-Z-test-report.md` | |
| 변경 이력 | `phaseX-Y-Z-change-report.md` | |

### 1.4 Task 문서 규정 (ai-rule-decision §2-2, taxonomy §2.4)

| 문서 종류 | 파일명 패턴 (권장) | 파일명 패턴 (변형, phase-8-0 실적) |
|-----------|---------------------|-------------------------------------|
| Task 실행 계획 | `phaseX-Y-N-task.md` | (선택) |
| Task 테스트 결과 | `phaseX-Y-N-task-test-result.md` | `phaseX-Y-N-<topic>-test-report.md` |
| Task 변경 이력 | (통합 가능) | `phaseX-Y-N-<topic>-change-report.md` |

- **N**: todo-list 항목 순번 (0 또는 1부터, Phase별 일관).
- **topic**: kebab-case 작업 주제 (변형 사용 시).
- **생성**: Task는 todo-list에서 유도; 변경·테스트 문서는 Task 실행·테스트 후 생성.

### 1.5 todo-list 규정 (taxonomy §2.1)

- **저장 위치**: `docs/phases/phase-X-Y/phaseX-Y-Z-todo-list.md`
- **역할**: 작업 진행 상태 추적. AI는 항목을 생성·수정하지 않고, **판단 및 Task 제안의 입력값**으로만 사용.
- Task 문서는 **todo-list에서 유도된 항목에 대해서만** 생성·저장.

---

## 2. n8n 워크플로우별 적용 규칙

### 2.1 Phase Auto Checker v1

| 항목 | 규정 준수 내용 |
|------|----------------|
| **Phase 디렉터리** | `docs/phases/{phaseDirId}/` — `phaseDirId`는 `phase-X-Y` 형식 (예: `phase-8-0`) |
| **Phase 파일 패턴** | `{phaseFileBase}-plan.md`, `-todo-list.md`, `-summary.md`(또는 `-final-summary-report.md`), `-test-report.md`, `-change-report.md` |
| **phaseFileBase** | Phase 파일명 접두사. 예: `phase8-0-0` (phase-X-Y-Z에서 Z 포함) |
| **다음 Phase Plan 저장** | `docs/phases/{nextPhaseDirId}/{nextPhaseFileBase}-plan.md` |
| **Task 관련 패턴** | tasks/ 내 `phaseX-Y-N-*-change-report.md`, `phaseX-Y-N-*-test-report.md` 인식 시 phaseFileBase(-N)?-.*-(change-report\|test-report).md 규칙 유지 |

**권장**: `SET_PhaseId`에서 `phaseDirId` = `phase-X-Y`, `phaseFileBase` = `phaseX-Y-Z` (Z 생략 시 0) 로 통일.

---

### 2.2 Task Plan and Test Plan Generation v1 (test)

| 항목 | 기존 (비규정) | 규정 준수 (개선) |
|------|----------------|------------------|
| **Phase 폴더** | `docs/phases/tasks` (Phase 무관 단일 폴더) | `docs/phases/phase-X-Y/tasks/` (phase-X-Y 단위) |
| **Task 실행 계획 파일명** | `task-{N}-plan.md` | `phaseX-Y-N-task.md` (권장) |
| **Task 테스트 결과 파일명** | `task-{N}-test.md` | `phaseX-Y-N-task-test-result.md` (권장) 또는 `phaseX-Y-N-<topic>-test-report.md` (변형) |
| **입력** | `phase_id` (숫자), Todo index/content | `phase_dir_id`(예: `phase-8-0`), `phase_id`(DB용), Todo index/content. topic(변형용)은 content에서 kebab-case 추출 가능 |

**경로·파일명 계산 (워크플로우 내부)**:

- `phase_dir_id` = 입력값 (예: `phase-8-0`). 미입력 시 기본값 `phase-8-0` 사용 가능.
- `phase_slug` = `phase_dir_id.replace(/^phase-/, '')` → 예: `8-0`
- Task 실행 계획 경로: `docs/phases/{phase_dir_id}/tasks/phase{phase_slug}-{N}-task.md`
- Task 테스트 결과 경로: `docs/phases/{phase_dir_id}/tasks/phase{phase_slug}-{N}-task-test-result.md`
- Write Binary / Execute Command 작업 디렉터리: `/workspace/docs/phases/{phase_dir_id}/tasks/`

**DB 저장**: `workflow_tasks.plan_md_path` 에 위 규정 준수 경로 저장 (Backend 경로 기반 실행과 동일).

---

### 2.3 Task Execution v1

| 항목 | 규정 준수 내용 |
|------|----------------|
| **입력** | `workflow_tasks`에서 pending 1건 조회. `plan_md_path` 사용 |
| **경로** | Backend는 `plan_md_path`(예: `docs/phases/phase-8-0/tasks/phase8-0-1-task.md`)를 workspace 기준으로 해석. n8n은 경로 생성하지 않음 |
| **출력** | `workflow_tasks.status` 갱신. (8-2-8) Task 테스트 결과는 `phaseX-Y-N-task-test-result.md` 또는 `phaseX-Y-N-<topic>-test-report.md` 규정에 따라 별도 워크플로우에서 생성 |

---

## 3. 워크플로우 입력·출력 정리

### 3.1 Task Plan and Test Plan Generation — 권장 입력

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `phase_dir_id` | string | 권장 | Phase 폴더 ID. 예: `phase-8-0`. 미설정 시 `phase-8-0` 등 기본값 사용 |
| `phase_id` | number | 예 | DB `workflow_tasks.phase_id` 용 |
| Todo 항목 | array | 예 | `{ index, content }[]`. index = N (순번) |

### 3.2 Task Plan and Test Plan Generation — 출력 (규정 준수)

| 출력 | 규정 준수 값 |
|------|--------------|
| **파일 쓰기 경로** | `docs/phases/{phase_dir_id}/tasks/` |
| **실행 계획 파일명** | `phase{phase_slug}-{N}-task.md` |
| **테스트 결과 파일명** | `phase{phase_slug}-{N}-task-test-result.md` |
| **plan_md_path** | `docs/phases/{phase_dir_id}/tasks/phase{phase_slug}-{N}-task.md` |
| **test_plan_md_path** | `docs/phases/{phase_dir_id}/tasks/phase{phase_slug}-{N}-task-test-result.md` |

---

## 4. 적용 체크리스트

- [ ] **Phase Auto Checker**: `phaseDirId`/`phaseFileBase`가 `phase-X-Y`·`phaseX-Y-Z` 규정과 일치하는지 확인
- [ ] **Task Plan and Test Plan Generation**: `phase_dir_id` 입력 추가, 경로를 `docs/phases/phase-X-Y/tasks/`, 파일명을 `phaseX-Y-N-task.md`·`phaseX-Y-N-task-test-result.md` 로 변경
- [ ] **Task Execution**: `plan_md_path`가 규정 경로 형식이면 그대로 사용; Backend는 이미 경로 기반 실행 지원
- [ ] **8-2-8 Task 테스트 및 결과 저장**: 결과 파일 저장 시 `phaseX-Y-N-task-test-result.md` 또는 `phaseX-Y-N-<topic>-test-report.md` 규정 준수

---

## 5. 문서 위치

- 본 규정: `docs/n8n/workflow/n8n-workflow-phase-task-convention.md`
- 참조: `docs/phase-document-taxonomy.md`, `docs/ai/ai-rule-decision.md`, `docs/ai/ai-rule-phase-naming.md`
