# Phase 10 테스트 시나리오 가이드 (E2E + MCP 시나리오 Task당 10개)

**용도**: Phase 10-1·10-2 웹테스트를 **E2E 선행 실행** 후 **MCP 시나리오(Task당 10개) .md** 기준으로 수행하고, 결과를 기록하는 순차 절차입니다.

---

## 1. 순차 진행 흐름

| 순서  | 단계                                                   | 문서/명령                                                                                                                                                                    | 설명                                                 |
| ----- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **1** | 환경 구축                                              | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)                                                                                                            | 백엔드 기동, Base URL `http://localhost:8001`        |
| **2** | E2E 실행                                               | `python3 scripts/webtest.py 10-1 start` / `10-2 start`                                                                                                                       | Phase 10-1·10-2 E2E 스펙 실행 (Playwright)           |
| **3** | MCP 시나리오 .md 확인                                  | [frontend-webtest-phase-10-1-mcp-scenarios.md](frontend-webtest-phase-10-1-mcp-scenarios.md), [frontend-webtest-phase-10-2-mcp-scenarios.md](frontend-webtest-phase-10-2-mcp-scenarios.md) | Task당 10개 시나리오 정의 (조치·기대 결과·검증 방법) |
| **4** | MCP cursor 브라우저 또는 Playwright 시나리오 스펙 실행 | [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md) / `npx playwright test e2e/phase-10-1-mcp-scenarios.spec.js`                        | 시나리오 .md 대로 조치 수행 후 기대 결과 검증        |
| **5** | 결과 기록                                              | [frontend-webtest-phase-10-1-mcp-result.md](frontend-webtest-phase-10-1-mcp-result.md), [frontend-webtest-phase-10-2-mcp-result.md](frontend-webtest-phase-10-2-mcp-result.md) | 시나리오별 통과/실패 기록, E2E 결과 요약             |

---

## 2. Phase 10-1 (UX/UI 개선)

| 항목                          | 내용                                                                                                                                   |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **E2E 스펙**                  | `e2e/phase-10-1.spec.js` (6항목)                                                                                                       |
| **E2E 실행**                  | `python3 scripts/webtest.py 10-1 start`                                                                                                |
| **MCP 시나리오 .md**          | [frontend-webtest-phase-10-1-mcp-scenarios.md](frontend-webtest-phase-10-1-mcp-scenarios.md) — Task 10-1-1·10-1-2·10-1-3 각 10개, **총 30개** |
| **시나리오 스펙(Playwright)** | `e2e/phase-10-1-mcp-scenarios.spec.js` (30항목, 시나리오 .md와 동일)                                                                   |
| **시나리오 스펙 실행**        | `npx playwright test e2e/phase-10-1-mcp-scenarios.spec.js`                                                                             |
| **결과 문서**                 | [frontend-webtest-phase-10-1-mcp-result.md](frontend-webtest-phase-10-1-mcp-result.md)                                                   |

---

## 3. Phase 10-2 (모드별 분석 고도화)

| 항목                          | 내용                                                                                                                                          |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **E2E 스펙**                  | `e2e/phase-10-2.spec.js` (6항목)                                                                                                              |
| **E2E 실행**                  | `python3 scripts/webtest.py 10-2 start`                                                                                                       |
| **MCP 시나리오 .md**          | [frontend-webtest-phase-10-2-mcp-scenarios.md](frontend-webtest-phase-10-2-mcp-scenarios.md) — Task 10-2-1·10-2-2·10-2-3·10-2-4 각 10개, **총 40개** |
| **시나리오 스펙(Playwright)** | (선택) phase-10-2-mcp-scenarios.spec.js 생성 시 동일 40개 자동 실행 가능                                                                      |
| **결과 문서**                 | [frontend-webtest-phase-10-2-mcp-result.md](frontend-webtest-phase-10-2-mcp-result.md)                                                      |

---

## 4. MCP Cursor 브라우저로 수행 시

1. [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md)대로 브라우저 MCP 활성화.
2. Phase 10-1: `@docs/webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md` 첨부 후 "시나리오 1→…→10 (Task 10-1-1, 10-1-2, 10-1-3) 순서대로 가상 브라우저에서 수행해 줘" 지시.
3. Phase 10-2: `@docs/webtest/phase-10-2/phase-10-2-mcp-webtest-scenarios.md` 첨부 후 "시나리오 1→…→10 (Task 10-2-1~10-2-4) 순서대로 가상 브라우저에서 수행해 줘" 지시.
4. 결과는 각 phase의 **phase-X-Y-mcp-webtest-result.md** 시나리오별 결과 표에 기록.

---

## 5. 관련 문서

| 문서                                                           | 용도                                                 |
| -------------------------------------------------------------- | ---------------------------------------------------- |
| [frontend-webtest-readme.md](frontend-webtest-readme.md)                                         | webtest 문서 인덱스·순차 링크                        |
| [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md) | Phase 단위 유저 테스트 3가지 방안 (MCP·페르소나·E2E) |
| [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)                                | 환경 구축                                            |
| [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md)            | MCP Cursor 브라우저 활성화·수행 절차                 |
