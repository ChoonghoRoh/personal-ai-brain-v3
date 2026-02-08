# Web 사용자 테스트 (webtest)

웹 사용자 테스트 환경, 절차, 페르소나, 관점별 프롬프트를 한곳에서 관리하는 문서 영역입니다.

---

## 테스트 시나리오 가이드 — 순차 진행 (Index)

테스트를 **순서대로** 진행할 때 아래 링크를 따라가면 됩니다.

| 순서  | 단계                          | 문서                                                                                                               | 설명                                                                     |
| ----- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| **1** | 환경 구축                     | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)                                                 | 백엔드 기동, Base URL, 브라우저·E2E·MCP 전제                             |
| **2** | Phase 단위 절차               | [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md)                   | 3가지 방안(MCP·페르소나·E2E), [webtest: X-Y start] 명령                  |
| **3** | E2E + MCP 시나리오 (Phase 10) | [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md)               | E2E 실행 → MCP 시나리오(Task당 10개) .md → 결과 기록                     |
| **4** | MCP Cursor 브라우저           | [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md)                             | Cursor에서 브라우저 MCP 활성화·수행 절차·지시문                          |
| **5** | Phase별 시나리오·결과         | [docs/webtest/phase-10-1/](../../../webtest/phase-10-1/), [docs/webtest/phase-10-2/](../../../webtest/phase-10-2/) | 시나리오 .md(Task당 10개), 결과 .md 링크는 아래 Phase별 테스트 계획 참고 |

---

## 문서 목록

| 문서                                                                                                 | 설명                                                        |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)                                   | 테스트 수행 전 환경 구축 (백엔드 기동, Base URL, 브라우저)  |
| [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md)     | Phase 단위로 유저 테스트를 수행하는 절차                    |
| [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md) | Phase 10-1·10-2 E2E + MCP 시나리오(Task당 10개) 순차 가이드 |
| [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md)               | MCP(Cursor) 웹 테스트 수행 가이드 (브라우저 활성화·지시문)  |
| [frontend-webtest-personas.md](frontend-webtest-personas.md)                                         | 페르소나 정의 (일반 웹 사용자 + 테스터 관점 3가지)          |
| [docs/webtest/prompts/](../../../webtest/prompts/)                                                   | 관점별 테스트 수행 가이드 및 프롬프트                       |

---

## 관점별 프롬프트 (prompts/)

| 파일                                                                                 | 관점                                   |
| ------------------------------------------------------------------------------------ | -------------------------------------- |
| [frontend-webtest-prompt-planner.md](frontend-webtest-prompt-planner.md)             | 꼼꼼한 기획자 (요구사항·플로우·정합성) |
| [frontend-webtest-prompt-developer.md](frontend-webtest-prompt-developer.md)         | 개발자 (버그·에러·API·성능)            |
| [frontend-webtest-prompt-uiux-designer.md](frontend-webtest-prompt-uiux-designer.md) | UI·UX 디자이너 (시인성·일관성·접근성)  |

---

## Phase별 테스트 계획

| Phase                         | 폴더                                                     | E2E 실행              | MCP 시나리오 .md (Task당 10개)                                                                                | 결과 문서                                                                                                                                              |
| ----------------------------- | -------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 9-1                           | [docs/webtest/phase-9-1/](../../../webtest/phase-9-1/)   | `webtest: 9-1 start`  | (체크리스트 기반)                                                                                             | [phase-9-1-test-result-summary.md](../../../webtest/phase-9-1/phase-9-1-test-result-summary.md)                                                        |
| 9-3 (AI 기능 고도화)          | [docs/webtest/phase-9-3/](../../../webtest/phase-9-3/)   | `webtest: 9-3 start`  | [phase-9-3-user-test-plan.md](../../../webtest/phase-9-3/phase-9-3-user-test-plan.md)                         | [phase-9-3-final-summary.md](../../../webtest/phase-9-3/phase-9-3-final-summary.md), [reports/README.md](../../../webtest/phase-9-3/reports/README.md) |
| **10-1 (UX/UI 개선)**         | [docs/webtest/phase-10-1/](../../../webtest/phase-10-1/) | `webtest: 10-1 start` | [phase-10-1-mcp-webtest-scenarios.md](../../../webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md) (30개) | [phase-10-1-mcp-webtest-result.md](../../../webtest/phase-10-1/phase-10-1-mcp-webtest-result.md)                                                       |
| **10-2 (모드별 분석 고도화)** | [docs/webtest/phase-10-2/](../../../webtest/phase-10-2/) | `webtest: 10-2 start` | [phase-10-2-mcp-webtest-scenarios.md](../../../webtest/phase-10-2/phase-10-2-mcp-webtest-scenarios.md) (40개) | [phase-10-2-mcp-webtest-result.md](../../../webtest/phase-10-2/phase-10-2-mcp-webtest-result.md)                                                       |

- **Phase 10-1·10-2**: E2E 완료 후 [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md)에 따라 MCP 시나리오(Task당 10개) .md 기준으로 MCP cursor 브라우저 또는 Playwright 시나리오 스펙 실행 → 결과 문서에 기록.
- 다른 phase 추가 시: [docs/webtest/\_template/phase-X-Y-user-test-plan.md](../../../webtest/_template/phase-X-Y-user-test-plan.md) 복사 후 `phase-<X>-<Y>/` 폴더·문서 치환.

---

## 관련 문서

- Phase별 기획·체크리스트: [docs/phases/](../../../phases/)
- Phase 9-3 웹 체크리스트: [docs/phases/phase-9-3/phase-9-3-web-user-checklist.md](../../../phases/phase-9-3/phase-9-3-web-user-checklist.md)
