# Task 검사 규정

**용도**: Task 완료 검사 시 확인할 항목·판단 기준·산출물 규정을 한곳에 정리한다.
**기준 문서**: [ai-rule-decision.md](ai-rule-decision.md), [common/common-phase-document-taxonomy.md](../../common/references/common-phase-document-taxonomy.md)
**버전**: 1.0
**작성일**: 2026-02-05

---

## 1. 검사 시 확인 항목 (체크리스트)

Task를 **검사(완료 여부 판단)** 할 때 아래 항목을 순서대로 확인한다.

| #   | 확인 항목                | 내용                                                                                                           | 참조                                    |
| --- | ------------------------ | -------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1   | **Task 실행 계획 문서**  | `phase-X-Y/tasks/task-X-Y-N-*.md` 또는 `phaseX-Y-N-task.md` 존재                                               | taxonomy §2.4, ai-rule-decision §2-2    |
| 2   | **Done Definition 충족** | 해당 Task 문서의 "완료 기준"·"Done 정의"·"작업 체크리스트" 항목이 모두 충족됨                                  | Task 문서 §완료 기준 / §작업 체크리스트 |
| 3   | **테스트·검증 증빙**     | Task 테스트 결과 또는 Phase 웹테스트/E2E 결과로 동작·품질 검증됨                                               | ai-rule-decision §6                     |
| 4   | **테스트 결과 문서**     | `phaseX-Y-N-task-test-result.md` 또는 `phaseX-Y-N-<topic>-test-report.md` 존재(해당 Task가 테스트 대상인 경우) | taxonomy §2.4                           |
| 5   | **Phase 완료 기준 연동** | Phase plan/todo-list의 "완료 기준"·"Validation/Exit Criteria"에 해당 Task가 반영되어 있으면 해당 항목 충족     | Phase plan §4                           |
| 6   | **회귀 유지**            | 선행 Phase·기존 기능 회귀 테스트 유지(해당 Phase에서 요구하는 경우)                                            | Phase todo-list·Master Plan             |

- **1~2**: Task 문서 존재 및 Done 정의 충족이 최소 조건이다.
- **3~4**: 테스트 대상 Task는 테스트 증빙 문서 또는 Phase 웹테스트/E2E 결과로 검증된 후 완료로 판단한다.
- **5~6**: Phase 단위 완료 기준·회귀 요구가 있으면 함께 확인한다.

---

## 2. Task 완료 판단 기준 (ai-rule-decision §6 요약)

| 조건                                                                        | 판정                             |
| --------------------------------------------------------------------------- | -------------------------------- |
| test-result/test-report에 **오류 없음** AND Task의 **Done Definition 충족** | ✅ **DONE (완료)**               |
| 기능 정상 BUT **성능 목표 미달**                                            | ⚠️ **NEEDS IMPROVE (보완 필요)** |
| 테스트 실패·Done 미충족                                                     | 🔁 **REVISE (재작업 필요)**      |
| test-result/test-report 없음 AND 해당 Task가 테스트 대상                    | ⏸ **WAITING (테스트 대기)**      |

- 상세: [ai-rule-decision.md](ai-rule-decision.md) §5 Task 실행 상태 판단, §6 Task 완료 판단.

---

## 3. 산출물·문서 규정 (파일명 저장 규칙 포함)

### 3.1 파일명 저장 규칙

- **문자**: 영소문자·숫자·하이픈(`-`)만 사용. 공백·밑줄 사용 금지.
- **구성자**: Phase ID `X-Y`, Task 번호 `N`(1부터), 주제/토픽은 짧은 영문(`<주제>`, `<topic>`).
- **확장자**: 마크다운 문서는 반드시 `.md`.
- **위치**: Phase 문서는 `docs/phases/phase-X-Y/`, Task 단위 문서는 `docs/phases/phase-X-Y/tasks/`에 저장.
- **일관성**: 한 Phase·Task 내에서는 권장 패턴을 우선 사용하고, 변형 패턴을 쓸 경우 동일 Phase에서 혼용하지 않도록 한다.

| 구분                        | 파일명 패턴 (권장)               | 파일명 패턴 (변형)                  | 저장 위치                      |
| --------------------------- | -------------------------------- | ----------------------------------- | ------------------------------ |
| Task 실행 계획              | `task-X-Y-N-<주제>.md`           | `phaseX-Y-N-task.md`                | `docs/phases/phase-X-Y/tasks/` |
| Task 테스트 결과            | `phaseX-Y-N-task-test-result.md` | `phaseX-Y-N-<topic>-test-report.md` | `docs/phases/phase-X-Y/`       |
| Phase 단위 Task 수행 리포트 | `phase-X-Y-task-report.md`       | (Phase별 통합 리포트)               | `docs/phases/phase-X-Y/`       |

- **Task 당 report 작성**: 각 Task 완료 시 해당 Task에 대한 수행·검증 결과를 문서로 남긴다. 테스트 대상 Task는 `phaseX-Y-N-task-test-result.md` 또는 `phaseX-Y-N-<topic>-test-report.md`를 작성하고, 그 외 Task는 수행 내역·완료 기준 충족을 요약한 Task 단위 리포트를 같은 규칙으로 둘 수 있다.
- **task-test-report 저장 위치**: Task 테스트 결과·test-report 문서는 **phase-X-Y**(`docs/phases/phase-X-Y/`)에 둔다. `tasks/` 하위가 아니다.
- **Phase 단위 Task 수행 리포트**: Phase 내 여러 Task를 한 문서에서 정리할 때 `phase-X-Y-task-report.md` 사용 (예: [common/common-phase-10-1-0-plan.md](../../common/references/common-phase-10-1-0-plan.md)).
- Task 단위 상세 증빙은 `phaseX-Y-N-<topic>-test-report.md` 또는 E2E/webtest 결과 문서로 남긴다.

---

## 4. 검사 절차 (권장 순서)

1. **Phase todo-list** 확인 → 해당 Task ID·완료 기준 파악.
2. **Task 문서** (`phase-X-Y/tasks/`) 확인 → Done Definition·작업 체크리스트 파악.
3. **테스트·검증** 확인 → E2E/webtest 결과, `*-test-result.md` / `*-test-report.md` 또는 Phase 웹테스트 결과 문서.
4. **완료 판정** → §2 기준으로 DONE / NEEDS IMPROVE / REVISE / WAITING 출력.
5. **(선택) Task 수행 리포트** 작성 → Phase 단위로 `phase-X-Y-task-report.md`에 Task별 수행 내역·검증 결과·완료 기준 충족 여부 정리.
6. **Task 검사 완료 후 webtest 규정 연결** → §6에 따라 해당 Phase의 웹테스트(E2E·MCP 시나리오) 수행 및 결과 기록.

---

## 5. 참조 문서

| 문서                                                                                                                       | 용도                                                        |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| [ai-rule-decision.md](ai-rule-decision.md)                                                                                 | Task 실행 상태·완료 판단 규칙 (§5, §6)                      |
| [common/common-phase-document-taxonomy.md](../../common/references/common-phase-document-taxonomy.md)                      | Phase·Task 문서 종류·파일명·저장 위치                       |
| [ai-rule-phase-naming.md](ai-rule-phase-naming.md)                                                                         | Phase ID·Task ID 명명 규칙                                  |
| Phase plan/todo-list                                                                                                       | 해당 Phase 완료 기준·Validation/Exit Criteria               |
| [docs/webtest/README.md](../../frontend/references/frontend-webtest-readme.md)                                             | webtest 인덱스·순차 진행 (Task 검사 완료 후 §6 연결)        |
| [docs/webtest/phase-unit-user-test-guide.md](../../frontend/references/frontend-rule-phase-unit-user-test-guide.md)        | Phase 단위 유저 테스트 3가지 방안·webtest: X-Y start        |
| [docs/webtest/phase-10-test-scenario-guide.md](../../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md) | Phase 10-1·10-2 E2E + MCP 시나리오(Task당 10개) 순차 가이드 |

---

## 6. Task 검사 완료 후 webtest 규정 연결

Task 검사가 **완료(DONE)** 로 판정된 Phase에 대해서는, **webtest 규정**에 따라 웹 사용자 테스트를 수행하고 결과를 기록한 뒤 다음 Phase로 진행한다.

### 6.1 적용 조건

| 조건     | 내용                                                              |
| -------- | ----------------------------------------------------------------- |
| **대상** | Task 검사 완료(DONE)가 나온 Phase 중, 웹 UI·API가 변경된 Phase    |
| **시점** | Phase 내 모든 Task 검사 완료 후, Phase 종료(summary) 전 또는 직후 |

### 6.2 진행 순서 (webtest 규정)

| 순서 | 단계                       | 문서/명령                                                                                                                  | 설명                                                                                             |
| ---- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 1    | **환경 구축**              | [docs/webtest/web-user-test-setup-guide.md](../../frontend/references/frontend-webtest-setup-guide.md)                     | 백엔드 기동, Base URL `http://localhost:8001`                                                    |
| 2    | **Phase 단위 절차**        | [docs/webtest/phase-unit-user-test-guide.md](../../frontend/references/frontend-rule-phase-unit-user-test-guide.md)        | 3가지 방안(MCP·페르소나·E2E) 선택, [webtest: X-Y start] 명령                                     |
| 3    | **E2E 실행**               | `python3 scripts/webtest.py X-Y start`                                                                                     | 해당 Phase E2E 스펙 실행 (스펙이 있는 Phase만)                                                   |
| 4    | **MCP 시나리오(Phase 10)** | [docs/webtest/phase-10-test-scenario-guide.md](../../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md) | Phase 10-1·10-2: E2E 후 MCP 시나리오(Task당 10개) .md 실행 → 결과 기록                           |
| 5    | **결과 기록**              | `docs/webtest/phase-X-Y/` 내 결과 문서                                                                                     | phase-X-Y-mcp-webtest-result.md, phase-X-Y-test-result-summary.md 등에 시나리오별 통과/실패 기록 |

- **webtest 인덱스**: [docs/webtest/README.md](../../frontend/references/frontend-webtest-readme.md) — 테스트 시나리오 가이드 순차 진행(Index) 참고.
- **Phase 10-1·10-2**: E2E 실행 후 [phase-10-test-scenario-guide.md](../../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md)에 따라 MCP 시나리오 .md(Task당 10개) 기준으로 실행하고, [phase-10-1-mcp-webtest-result.md](../../frontend/references/frontend-webtest-phase-10-1-mcp-result.md) 등에 결과 기록.

### 6.3 산출물

| 구분                  | 내용                                                                               |
| --------------------- | ---------------------------------------------------------------------------------- |
| **E2E 결과**          | `npx playwright test e2e/phase-X-Y.spec.js` 통과 여부                              |
| **MCP 시나리오 결과** | Phase 10 등: Task당 10개 시나리오 통과/실패 기록 (phase-X-Y-mcp-webtest-result.md) |
| **회귀 유지**         | 선행 Phase·기존 E2E/webtest 유지 여부 확인                                         |

- Task 검사 완료 후 **webtest 규정 연결**까지 수행한 Phase만, Phase 종료(summary) 시 "웹테스트·회귀 검증 완료"로 기록한다.
