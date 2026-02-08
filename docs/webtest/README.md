# Web 사용자 테스트 (webtest)

웹 사용자 테스트 환경, 절차, 페르소나, 관점별 프롬프트를 한곳에서 관리하는 문서 영역입니다.

---

## 테스트 시나리오 가이드 — 순차 진행 (Index)

테스트를 **순서대로** 진행할 때 아래 링크를 따라가면 됩니다.

| 순서  | 단계                          | 문서                                                               | 설명                                                                     |
| ----- | ----------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| **1** | 환경 구축                     | [web-user-test-setup-guide.md](web-user-test-setup-guide.md)       | 백엔드 기동, Base URL, 브라우저·E2E·MCP 전제                             |
| **2** | Phase 단위 절차               | [phase-unit-user-test-guide.md](phase-unit-user-test-guide.md)     | 3가지 방안(MCP·페르소나·E2E), [webtest: X-Y start] 명령                  |
| **3** | E2E + MCP 시나리오 (Phase 10) | [phase-10-test-scenario-guide.md](phase-10-test-scenario-guide.md) | E2E 실행 → MCP 시나리오(Task당 10개) .md → 결과 기록                     |
| **4** | MCP Cursor 브라우저           | [mcp-cursor-test-guide.md](mcp-cursor-test-guide.md)               | Cursor에서 브라우저 MCP 활성화·수행 절차·지시문                          |
| **5** | Phase별 시나리오·결과         | [phase-10-1/](phase-10-1/), [phase-10-2/](phase-10-2/)             | 시나리오 .md(Task당 10개), 결과 .md 링크는 아래 Phase별 테스트 계획 참고 |

---

## 문서 목록

| 문서                                                               | 설명                                                        |
| ------------------------------------------------------------------ | ----------------------------------------------------------- |
| [web-user-test-setup-guide.md](web-user-test-setup-guide.md)       | 테스트 수행 전 환경 구축 (백엔드 기동, Base URL, 브라우저)  |
| [phase-unit-user-test-guide.md](phase-unit-user-test-guide.md)     | Phase 단위로 유저 테스트를 수행하는 절차                    |
| [phase-10-test-scenario-guide.md](phase-10-test-scenario-guide.md) | Phase 10-1·10-2 E2E + MCP 시나리오(Task당 10개) 순차 가이드 |
| [mcp-cursor-test-guide.md](mcp-cursor-test-guide.md)               | MCP(Cursor) 웹 테스트 수행 가이드 (브라우저 활성화·지시문)  |
| [personas.md](personas.md)                                         | 페르소나 정의 (일반 웹 사용자 + 테스터 관점 3가지)          |
| [prompts/](prompts/)                                               | 관점별 테스트 수행 가이드 및 프롬프트                       |

---

## 관점별 프롬프트 (prompts/)

| 파일                                                       | 관점                                   |
| ---------------------------------------------------------- | -------------------------------------- |
| [prompt-planner.md](prompts/prompt-planner.md)             | 꼼꼼한 기획자 (요구사항·플로우·정합성) |
| [prompt-developer.md](prompts/prompt-developer.md)         | 개발자 (버그·에러·API·성능)            |
| [prompt-uiux-designer.md](prompts/prompt-uiux-designer.md) | UI·UX 디자이너 (시인성·일관성·접근성)  |

---

## Phase별 테스트 계획

| Phase                         | 폴더                       | E2E 실행              | MCP 시나리오 .md (Task당 10개)                                                               | 결과 문서                                                                                                            |
| ----------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 9-1                           | [phase-9-1/](phase-9-1/)   | `webtest: 9-1 start`  | (체크리스트 기반)                                                                            | [phase-9-1-test-result-summary.md](phase-9-1/phase-9-1-test-result-summary.md)                                       |
| 9-3 (AI 기능 고도화)          | [phase-9-3/](phase-9-3/)   | `webtest: 9-3 start`  | [phase-9-3-user-test-plan.md](phase-9-3/phase-9-3-user-test-plan.md)                         | [phase-9-3-final-summary.md](phase-9-3/phase-9-3-final-summary.md), [reports/README.md](phase-9-3/reports/README.md) |
| **10-1 (UX/UI 개선)**         | [phase-10-1/](phase-10-1/) | `webtest: 10-1 start` | [phase-10-1-mcp-webtest-scenarios.md](phase-10-1/phase-10-1-mcp-webtest-scenarios.md) (30개) | [phase-10-1-mcp-webtest-result.md](phase-10-1/phase-10-1-mcp-webtest-result.md)                                      |
| **10-2 (모드별 분석 고도화)** | [phase-10-2/](phase-10-2/) | `webtest: 10-2 start` | [phase-10-2-mcp-webtest-scenarios.md](phase-10-2/phase-10-2-mcp-webtest-scenarios.md) (40개) | [phase-10-2-mcp-webtest-result.md](phase-10-2/phase-10-2-mcp-webtest-result.md)                                      |
| **11-1 (DB 스키마·마이그레이션)** | [phase-11-1/](phase-11-1/) | (E2E 스펙 없음) | [phase-11-1-mcp-webtest-scenarios.md](phase-11-1/phase-11-1-mcp-webtest-scenarios.md) (30개, DB/API 검증) | [phase-11-1-mcp-webtest-result.md](phase-11-1/phase-11-1-mcp-webtest-result.md)                                      |
| **11-2 (Admin CRUD API)**         | [phase-11-2/](phase-11-2/) | (E2E 스펙 없음) | curl·API 검증                                                                                             | [phase-11-2-webtest-execution-report.md](phase-11-2/phase-11-2-webtest-execution-report.md)                           |
| **11-3 (Admin UI)**               | [phase-11-3/](phase-11-3/) | (E2E 스펙 없음) | HTTP 상태·UI 라우팅 검증                                                                                 | [phase-11-3-webtest-execution-report.md](phase-11-3/phase-11-3-webtest-execution-report.md)                           |
| **11-4 (통합 테스트·운영 준비)**  | [phase-11-4/](phase-11-4/) | `webtest: 11-4 start` | [phase-11-4-user-test-plan.md](phase-11-4/phase-11-4-user-test-plan.md) (통합·Draft→Publish→Rollback) | [phase-11-4-webtest-execution-report.md](phase-11-4/phase-11-4-webtest-execution-report.md)                             |
| **11-5 (Phase 10 고도화)**        | [phase-11-5/](phase-11-5/) | `webtest: 11-5 start` | [phase-11-5-user-test-plan.md](phase-11-5/phase-11-5-user-test-plan.md) (Phase 10 회귀·Phase 11 연동) | [phase-11-5-webtest-execution-report.md](phase-11-5/phase-11-5-webtest-execution-report.md)                           |

- **Phase 10-1·10-2**: E2E 완료 후 [phase-10-test-scenario-guide.md](phase-10-test-scenario-guide.md)에 따라 MCP 시나리오(Task당 10개) .md 기준으로 MCP cursor 브라우저 또는 Playwright 시나리오 스펙 실행 → 결과 문서에 기록.
- **Phase 11-1**: 웹 UI 없음. [phase-11-1-mcp-webtest-scenarios.md](phase-11-1/phase-11-1-mcp-webtest-scenarios.md) 기준으로 마이그레이션·시딩·테이블 확인·Admin API(11-2) 검증 수행 → [phase-11-1-mcp-webtest-result.md](phase-11-1/phase-11-1-mcp-webtest-result.md)에 기록. `webtest: 11-1 start` 시 E2E 스펙 없음 안내.
- **Phase 11-2·11-3**: E2E 스펙 없음. curl·HTTP 상태 확인 등 대체 테스트 → 각 phase 폴더의 webtest-execution-report에 기록.
- **Phase 11-4**: 통합 테스트. [phase-11-4-user-test-plan.md](phase-11-4/phase-11-4-user-test-plan.md) 기준으로 11-1~11-3 통합·Draft→Publish→Rollback 시나리오 수행 → [phase-11-4-webtest-execution-report.md](phase-11-4/phase-11-4-webtest-execution-report.md)에 기록. `webtest: 11-4 start` 시 E2E 스펙 없으면 대체 테스트(curl·MCP) 수행.
- **Phase 11-5**: Phase 10 고도화·회귀. [phase-11-5-user-test-plan.md](phase-11-5/phase-11-5-user-test-plan.md) 기준으로 Phase 10 E2E 회귀·Phase 11 연동 검증 수행 → [phase-11-5-webtest-execution-report.md](phase-11-5/phase-11-5-webtest-execution-report.md)에 기록. `webtest: 11-5 start` 시 Phase 10 E2E 실행 후 Phase 11 연동 시나리오 기록.
- 다른 phase 추가 시: [\_template/phase-X-Y-user-test-plan.md](_template/phase-X-Y-user-test-plan.md) 복사 후 `phase-<X>-<Y>/` 폴더·문서 치환.

---

## 관련 문서

- Phase별 기획·체크리스트: [docs/phases/](../phases/)
- Phase 9-3 웹 체크리스트: [docs/phases/phase-9-3/phase-9-3-web-user-checklist.md](../phases/phase-9-3/phase-9-3-web-user-checklist.md)
