---
doc_type: ai-rule
rule_domain: phase
rule_role: decision
version: 1.0
status: active
owner: ai
last_updated: 2026-01-28
---

# AI Decision Rules (if–then)

> 이 문서는 **AI 에이전트가 md 파일을 읽고 상태를 판단하기 위한 기준 규칙서**이다.
> AI는 이 규칙에 따라 *완료 / 보류 / 다음 단계*를 판단한다.

---

## 1. 문서 타입 인식 규칙

AI는 **파일명 규칙과 meta block을 함께 사용하여**
문서의 역할을 인식한다.

| 파일명 패턴                    | 인식 유형                  | 저장 위치 (Option 1)                   |
| ------------------------------ | -------------------------- | -------------------------------------- |
| `*-plan.md`                    | Phase 설계 문서            | `docs/phases/phase-X-Y/`               |
| `*-todo-list.md`               | Phase 할 일 목록           | `docs/phases/phase-X-Y/`               |
| `*-summary.md`                 | Phase 결과 요약            | `docs/phases/phase-X-Y/`               |
| `*-test-report.md`             | Phase·테스트 결과 증빙     | `docs/phases/phase-X-Y/`               |
| `*-change-report.md`           | 변경 이력 보고서           | `docs/phases/phase-X-Y/` 또는 `tasks/` |
| `*-task.md`                    | Task 실행 계획(지시서)     | `docs/phases/phase-X-Y/tasks/`         |
| `*-task-test-result.md`        | Task 실행 테스트 결과 증빙 | `docs/phases/phase-X-Y/tasks/`         |
| `*-*-change-report.md` (tasks) | Task 변경 이력             | `docs/phases/phase-X-Y/tasks/`         |
| `*-*-test-report.md` (tasks)   | Task 테스트 증빙           | `docs/phases/phase-X-Y/tasks/`         |

- **phase-X-Y 폴더**: Phase 단위 문서 (plan, todo-list, summary, test-report, change-report). 반복 Z가 있으면 파일명에 포함 예: `phase8-0-plan.md`.
- **phase-X-Y/tasks/ 폴더**: 해당 Phase의 todo-list에서 유도된 Task 문서만 저장.
  - **권장**: `phaseX-Y-N-task.md`, `phaseX-Y-N-task-test-result.md` (N = todo 항목 순번).
  - **변형(phase-8-0 실적)**: `phaseX-Y-N-<topic>-change-report.md` (Task 변경 이력), `phaseX-Y-N-<topic>-test-report.md` (Task 테스트 결과). topic = kebab-case 작업 주제.

---

## 2. 문서 저장 위치 (Phase 폴더·파일 규칙)

### 2-1. phase-X-Y 폴더 (Phase 단위 문서)

| 문서 종류   | 파일명 패턴 (예시)            | 비고                        |
| ----------- | ----------------------------- | --------------------------- |
| Phase 설계  | `phaseX-Y-Z-plan.md`          | Z = 반복(0,1,2…), 생략 시 0 |
| Phase 할 일 | `phaseX-Y-Z-todo-list.md`     | todo-list에서 Task 유도     |
| Phase 요약  | `phaseX-Y-Z-summary.md`       | Phase 종료 시               |
| 테스트 증빙 | `phaseX-Y-Z-test-report.md`   | 복수 시 Z 또는 접미사       |
| 변경 이력   | `phaseX-Y-Z-change-report.md` | 복수 시 Z 또는 접미사       |

**경로**: `docs/phases/phase-X-Y/` (예: `docs/phases/phase-8-0/`)

### 2-2. phase-X-Y/tasks/ 폴더 (Task 문서)

| 문서 종류        | 파일명 패턴 (예시)                    | 비고                           |
| ---------------- | ------------------------------------- | ------------------------------ |
| Task 실행 계획   | `phaseX-Y-N-task.md`                  | N = todo-list 항목 순번 (권장) |
| Task 테스트 결과 | `phaseX-Y-N-task-test-result.md`      | 동일 N (권장)                  |
| Task 변경 이력   | `phaseX-Y-N-<topic>-change-report.md` | phase-8-0 실적 변형            |
| Task 테스트 증빙 | `phaseX-Y-N-<topic>-test-report.md`   | phase-8-0 실적 변형            |

**경로**: `docs/phases/phase-X-Y/tasks/` (예: `docs/phases/phase-8-0/tasks/`)

- Task 문서는 **phaseX-Y-Z-todo-list**에 의해 생성·연결된다.
- Task ID 개념은 `task-X-Y-N` 유지. 구분: change-report = 변경 이력, test-report = 테스트 결과.
- Phase 루트에 Phase 전체 계획이 필요하면 `docs/phases/phaseX-master-plan.md` 등 사용 가능 (예: phase8-master-plan.md).

---

## 3. Phase 시작 판단 규칙

```
IF
- phase-X-Y-Z-plan.md 존재 (Z=0 등)
AND
- phase-X-Y-Z-todo-list.md 존재
THEN
- Phase 시작 상태로 판단
```

---

## 4. Todo → Task 판단 규칙

```
IF
- todo 항목 상태 = 미착수
AND
- 선행 조건 없음
THEN
- phaseX-Y-N-task.md 생성 제안 (저장: phase-X-Y/tasks/)
```

```
IF
- todo 항목이 너무 큼 (다중 영역, 장기 작업)
THEN
- task 분할 제안
```

---

## 5. Task 실행 상태 판단 규칙

```
IF
- phaseX-Y-N-task.md 존재 (phase-X-Y/tasks/)
AND
- phaseX-Y-N-task-test-result.md 없음
THEN
- 실행 대기 상태 (Waiting)
```

```
IF
- phaseX-Y-N-task-test-result.md 또는 phaseX-Y-N-<topic>-test-report.md 존재
AND
- 해당 Task가 테스트 대상임
THEN
- 테스트 필요 상태 (또는 완료 판단)
```

---

## 6. Task 완료 판단 규칙

```
IF
- phaseX-Y-N-task-test-result.md 또는 phaseX-Y-N-<topic>-test-report.md 에 오류 없음
AND
- phaseX-Y-N-task.md (또는 해당 Task의 Done Definition) 충족
THEN
- Task 완료 (DONE)
```

```
IF
- 기능 정상
BUT
- 성능 목표 미달
THEN
- 조건부 완료 (Needs Improve)
```

---

## 7. Phase 진행률 판단 규칙

```
Phase 진행률 = (완료 Task 수 / 전체 Task 수) * 100
```

```
IF
- Phase 진행률 ≥ 90%
AND
- High Priority Task 100% 완료
THEN
- Phase 종료 가능 상태
```

---

## 8. Phase 종료 판단 규칙

```
IF
- phase-X-Y-Z-summary.md 존재
AND
- 종료 조건 충족
THEN
- Phase 종료 판정
```

---

## 9. 다음 Phase 판단 규칙

```
IF
- Phase 종료 판정
AND
- 다음 Phase plan 없음
THEN
- 다음 Phase 생성 제안
```

---

## 10. 판단 결과 출력 규칙

AI는 항상 **아래 상태 중 하나로 판단 결과를 출력**한다.

- ✅ DONE (완료)
- ⚠️ NEEDS IMPROVE (보완 필요)
- 🔁 REVISE (재작업 필요)
- ⏸ WAITING (대기)
- ➕ NEW TASK SUGGESTED (신규 작업 제안)

---

## 11. AI 행동 원칙

- AI는 **판단만 수행**한다.
- 코드 수정, 파일 생성은 직접 수행하지 않는다.
- 규칙 변경은 하지 않는다.
- 판단 근거를 반드시 명시한다.

---

## 12. 문서 위치 (고정)

```
/docs/ai/ai-rule-decision.md
```

---

## 한 줄 요약

> **이 문서는 AI가 ‘지금 무엇을 해야 하는지’를 판단하는 사고 기준표이다.**
