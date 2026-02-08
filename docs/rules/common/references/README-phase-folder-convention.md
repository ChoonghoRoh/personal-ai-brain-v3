# phase-8-0 폴더·파일 규칙 (Option 1 정렬)

**기준 규칙**: `docs/ai/ai-rule-decision.md` §2, `docs/ai/ai-rule-phase-naming.md` §7

---

## 1. 이 폴더(phase-X-Y)에 두는 문서

| 문서 종류 | 파일명 패턴 (예시) | 비고 |
| --------- | ------------------- | ----- |
| Phase 설계 | `phase8-0-Z-plan.md` | Z=반복(0,1,…). 현행: phase8-0-0-plan.md |
| Phase 할 일 | `phase8-0-Z-todo-list.md` | 현행: phase8-0-0-todo-list.md |
| Phase 요약 | `phase8-0-Z-summary.md` | 현행: phase8-0-0-summary-report.md 등 |
| 테스트 증빙 | `phase8-0-Z-test-report.md` | 현행: phase8-0-0-N-*-test-report.md |
| 변경 이력 | `phase8-0-Z-change-report.md` | 현행: phase8-0-0-N-*-change-report.md |

---

## 2. tasks/ 하위에 두는 문서

| 문서 종류 | 파일명 패턴 (예시) | 비고 |
| --------- | ------------------- | ----- |
| Task 실행 계획 | `phase8-0-N-task.md` | N=todo 항목 순번(1,2,…). 신규 생성 시 사용 |
| Task 테스트 결과 | `phase8-0-N-task-test-result.md` | 동일 N |

---

## 3. 현행 파일과의 대응

- **기존 파일**: `phase8-0-0-*-change-report.md`, `phase8-0-0-*-test-report.md` 등은 **이 폴더(phase-8-0)에 그대로 유지**한다. 패턴 `phaseX-Y-Z-*` 또는 `phaseX-Y-Z-N-*`로 인식한다.
- **신규 Task 문서**: todo-list 기반으로 생성하는 Task는 **tasks/** 아래 `phase8-0-N-task.md`, `phase8-0-N-task-test-result.md` 형식으로 저장한다.
- **phase8-2-* 문서**: phase-8-2용 계획·가이드 문서(phase8-2-4, phase8-2-5 등)는 현재도 이 폴더(phase-8-0)에 혼재되어 있음. Y 변경 시 `docs/phases/phase-8-2/` 폴더를 새로 두는 것이 규칙에 부합하며, 마이그레이션 시 phase-8-2 전용 파일을 해당 폴더로 옮길 수 있다.
