# docs/ai/ 인덱스 — 요약·명령어·참조

**용도**: `docs/ai/`에 등록된 문서의 요약, **명령어 정리**, 사람이 읽기 쉬운 인덱스.
**참조**: [n8n-rules-index.md](../n8n/n8n-rules-index.md) — n8n 노드 명명 규칙·Prefix·동사·대상.
**최종 수정**: 2026-02-04

---

## 1. 등록 문서 목록 (docs/ai/)

### 1.1 AI 룰 (Phase·Task 판단·생성)

| 문서                                                                                        | 한 줄 요약                                                                                                                         |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| [ai-rule-decision.md](references/ai-rule-decision.md)                                       | **AI 판단 규칙** — 문서 타입 인식, Phase/Task 시작·완료·보류 판단 (if–then)                                                        |
| [ai-rule-phase-naming.md](references/ai-rule-phase-naming.md)                               | **Phase 명명 규칙** — Phase ID(X-Y-Z), Phase Name, 폴더·파일명 패턴                                                                |
| [ai-rule-phase-auto-generation.md](references/ai-rule-phase-auto-generation.md)             | **Phase 자동 생성 규칙** — Phase/Task 생성 조건, ID 증가 규칙, 기본 파일 세트                                                      |
| [ai-rule-task-inspection.md](references/ai-rule-task-inspection.md)                         | **Task 검사 규정** — Task 완료 체크리스트, 완료 판정(DONE/REVISE/WAITING), 산출물·webtest 연결                                     |
| [ai-rule-phase-navigation-generation.md](references/ai-rule-phase-navigation-generation.md) | **phase-X-navigation 생성** — [phase-x-navi:make] 명령, 문서 구조·작성 규약                                                        |
| [ai-rule-phase-plan-todo-generation.md](references/ai-rule-phase-plan-todo-generation.md)   | **phase-X-Y plan·todo-list 생성** — [phase-x-plan-todo:make] 명령, Plan/Todo 공통 규약·누락 방지                                   |
| [ai-rule-task-creation.md](references/ai-rule-task-creation.md)                             | **Task 생성 규칙** — todo-list → tasks/ Task 문서 생성, [task-x-y:make] 명령, 파일명·공통 규약·참고 결과물(phase-10-1, phase-10-2) |

### 1.2 참고 문서 (LLM·추론·설계)

| 문서                                                                                                                      | 한 줄 요약                                                               |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [ai-ref-8gb-inference-and-keyword-alternatives.md](../common/references/ai-ref-8gb-inference-and-keyword-alternatives.md) | 8GB 환경 추론·키워드용 Ollama 모델 및 대안 (Qwen2.5 3B 등)               |
| [ai-ref-korean-local-llm-recommendation.md](../common/references/ai-ref-korean-local-llm-recommendation.md)               | 한국어 로컬 LLM 추천 (Bllossom 3B, Qwen2.5 7B, Docker·Backend 공유 환경) |
| [ai-ref-llm-dedicated-server-design.md](../common/references/ai-ref-llm-dedicated-server-design.md)                       | LLM 전용 서버 설계·구성 참고                                             |
| [ai-ref-ollama-llm-run.md](../common/references/ai-ref-ollama-llm-run.md)                                                 | Ollama 설치·실행·모델 로드 가이드                                        |

---

## 2. 명령어 정리

아래 명령은 **사람이 요청**하거나 **AI가 규칙에 따라 실행 제안**할 때 사용한다.

### 2.1 Phase·문서 생성 명령

| 명령                         | 입력                                                             | 출력                                                                  | 규칙 문서                                                                                   |
| ---------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **[phase-x-navi:make]**      | `phase-X-master-plan.md` (필수)                                  | `phase-X-navigation.md`                                               | [ai-rule-phase-navigation-generation.md](references/ai-rule-phase-navigation-generation.md) |
| **[phase-x-plan-todo:make]** | `phase-X-master-plan.md`, `phase-X-navigation.md` (둘 다 필수)   | 각 phase-X-Y에 `phase-X-Y-0-plan.md`, `phase-X-Y-0-todo-list.md`      | [ai-rule-phase-plan-todo-generation.md](references/ai-rule-phase-plan-todo-generation.md)   |
| **[task-x-y:make]**          | `phase-X-Y-0-todo-list.md` (필수), Phase ID X-Y (예: 10-1, 11-2) | `phase-X-Y/tasks/` 하위 todo 항목별 `task-X-Y-N-<topic>.md` 생성·갱신 | [ai-rule-task-creation.md](references/ai-rule-task-creation.md)                             |

- **실행 순서 권장**: phase-X-master-plan 작성 → [phase-x-navi:make] → [phase-x-plan-todo:make] → [task-x-y:make] (필요한 phase-X-Y만)
- **n8n 연동 시**: 워크플로우 노드 이름은 [n8n rules-index](../n8n/n8n-rules-index.md)의 Prefix·동사·대상 규칙 준수.

### 2.2 webtest · E2E 명령

| 명령/실행                                                  | 설명                                                 | 참조 문서                                                                                                                                                              |
| ---------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[webtest: X-Y start]**                                   | 해당 Phase의 E2E 웹테스트 실행 (스펙이 있는 Phase만) | [phase-unit-user-test-guide.md](../frontend/references/frontend-rule-phase-unit-user-test-guide.md)                                                                    |
| `python3 scripts/webtest.py X-Y start`                     | Phase X-Y E2E 스펙 실행 (예: 9-3, 10-1, 10-2)        | [frontend README](../frontend/references/frontend-webtest-readme.md), [phase-unit-user-test-guide](../frontend/references/frontend-rule-phase-unit-user-test-guide.md) |
| `npm run webtest:start -- X-Y`                             | 위와 동일 (package.json 스크립트 경유)               | 동일                                                                                                                                                                   |
| `npx playwright test e2e/phase-X-Y.spec.js`                | Phase X-Y E2E 스펙 직접 실행                         | [phase-10-test-scenario-guide](../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md)                                                                |
| `npx playwright test e2e/phase-10-1-mcp-scenarios.spec.js` | Phase 10-1 MCP 시나리오 30개 실행                    | [phase-10-test-scenario-guide](../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md)                                                                |

- **전제**: [web-user-test-setup-guide.md](../frontend/references/frontend-webtest-setup-guide.md)대로 백엔드(Base URL `http://localhost:8000`) 기동 후 실행.

---

## 3. webtest · E2E 요약 (빠지지 않게 반영)

Task 검사 완료 후 **webtest 규정 연결**은 [ai-rule-task-inspection.md](references/ai-rule-task-inspection.md) §6에 정의되어 있다. 아래 순서로 진행하면 된다.

### 3.1 webtest 순차 진행 (Index)

| 순서  | 단계                          | 문서                                                                                                       | 설명                                                        |
| ----- | ----------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **1** | 환경 구축                     | [web-user-test-setup-guide.md](../frontend/references/frontend-webtest-setup-guide.md)                     | 백엔드 기동, Base URL, 브라우저·E2E·MCP 전제                |
| **2** | Phase 단위 절차               | [phase-unit-user-test-guide.md](../frontend/references/frontend-rule-phase-unit-user-test-guide.md)        | 3가지 방안(MCP·페르소나·E2E), **[webtest: X-Y start]** 명령 |
| **3** | E2E + MCP 시나리오 (Phase 10) | [phase-10-test-scenario-guide.md](../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md) | E2E 실행 → MCP 시나리오(Task당 10개) .md → 결과 기록        |
| **4** | MCP Cursor 브라우저           | [mcp-cursor-test-guide.md](../frontend/references/frontend-webtest-mcp-cursor-test-guide.md)               | Cursor에서 브라우저 MCP 활성화·수행 절차·지시문             |
| **5** | Phase별 시나리오·결과         | (frontend/, 복사본 참조)                                                                                   | 시나리오 .md(Task당 10개), 결과 .md                         |

### 3.2 테스트 수행 3가지 방안

| 방안               | 실행 방법                                                                                                              | 비고                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- | --------------------- |
| **A: MCP(Cursor)** | Cursor에서 테스트 계획+체크리스트 @ 붙이고 "가상 브라우저(MCP)에서 순서대로 수행해 줘" 지시                            | CLI 명령 없음         |
| **B: 페르소나**    | A + [personas.md](../frontend/references/frontend-webtest-personas.md) + 관점별 prompt로 기획자/개발자/UI·UX 관점 기록 | Cursor에서 지시       |
| **C: E2E**         | **[webtest: X-Y start]** → `python3 scripts/webtest.py X-Y start`                                                      | E2E 스펙 있는 Phase만 |

### 3.3 Phase별 E2E·MCP 시나리오 (요약)

| Phase    | E2E 실행              | MCP 시나리오 .md                                                                                                  | 결과 문서                                                                                                    |
| -------- | --------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 9-1      | `webtest: 9-1 start`  | 체크리스트 기반                                                                                                   | [phase-9-1-test-result-summary.md](../frontend/references/frontend-webtest-phase-9-1-test-result-summary.md) |
| 9-3      | `webtest: 9-3 start`  | [phase-9-3-user-test-plan.md](../frontend/references/frontend-webtest-phase-9-3-user-test-plan.md)                | [phase-9-3-final-summary.md](../frontend/references/frontend-webtest-phase-9-3-final-summary.md)             |
| **10-1** | `webtest: 10-1 start` | [phase-10-1-mcp-webtest-scenarios.md](../frontend/references/frontend-webtest-phase-10-1-mcp-scenarios.md) (30개) | [phase-10-1-mcp-webtest-result.md](../frontend/references/frontend-webtest-phase-10-1-mcp-result.md)         |
| **10-2** | `webtest: 10-2 start` | [phase-10-2-mcp-webtest-scenarios.md](../frontend/references/frontend-webtest-phase-10-2-mcp-scenarios.md) (40개) | [phase-10-2-mcp-webtest-result.md](../frontend/references/frontend-webtest-phase-10-2-mcp-result.md)         |

### 3.4 Task 검사 완료 후 webtest 연결 (ai-rule-task-inspection §6)

- **대상**: Task 검사 완료(DONE)가 나온 Phase 중, 웹 UI·API가 변경된 Phase.
- **시점**: Phase 내 모든 Task 검사 완료 후, Phase 종료(summary) 전 또는 직후.
- **진행 순서**: (1) 환경 구축 (2) Phase 단위 절차([webtest: X-Y start]) (3) E2E 실행 (4) MCP 시나리오(Phase 10) (5) 결과 기록(`docs/webtest/phase-X-Y/`).
- **산출물**: E2E 결과(`npx playwright test e2e/phase-X-Y.spec.js`), MCP 시나리오 결과(phase-X-Y-mcp-webtest-result.md), 회귀 유지 확인.

---

## 4. 규칙 요약 (사람이 읽기 쉽게)

### 4.1 Phase·Task 판단 흐름

1. **문서 타입 인식** (ai-rule-decision): 파일명 패턴으로 plan / todo-list / task / summary / test-report 구분.
2. **Phase 시작**: plan + todo-list 존재 → Phase 시작 상태.
3. **Task 생성**: todo-list 항목 → `phase-X-Y/tasks/` 에 task 문서 생성. **[task-x-y:make]** 명령으로 phase-X-Y의 todo-list 기반 Task 문서 일괄 생성. 규칙: [ai-rule-task-creation.md](references/ai-rule-task-creation.md).
4. **Task 완료**: Task 검사 규정(ai-rule-task-inspection) 체크리스트·완료 판정(DONE/REVISE/WAITING) → 필요 시 webtest §6 연결.

### 4.2 Phase 명명 (ai-rule-phase-naming)

- **Phase ID**: `Phase-X-Y-Z` (X=Major, Y=목표 단위, Z=반복).
- **폴더**: X 또는 Y가 바뀌면 새 폴더 `phase-X-Y/`. Z만 바뀌면 폴더 생성 안 함.
- **파일명**: `phaseX-Y-Z-plan.md`, `phaseX-Y-Z-todo-list.md`, `phaseX-Y-N-task.md` 등.

### 4.3 산출물·저장 위치 (ai-rule-task-inspection §3)

- **Task 실행 계획**: `docs/phases/phase-X-Y/tasks/task-X-Y-N-<주제>.md` (또는 `phaseX-Y-N-task.md`).
- **Task 테스트 결과·report**: `docs/phases/phase-X-Y/` (tasks/ 하위 아님).
- **Phase 단위 Task 수행 리포트**: `phase-X-Y-task-report.md`.
- **Task 당 report**: 각 Task 완료 시 수행·검증 결과 문서화.

### 4.4 n8n 규칙 참조

- **노드 명명**: [n8n/n8n-rules-index.md](../n8n/n8n-rules-index.md) — `<PREFIX>_<Verb><Object>`, Phase/Step/순서 번호 노드 이름에 포함 금지.
- Phase·Task 관련 워크플로우와 연동 시 위 규칙 준수.

---

## 5. 관련 문서 (한눈에)

| 영역                                | 문서                                                                                                                                 | 용도                                                             |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| **룰·규약 인덱스**                  | [rules-index.md](../rules-index.md)                                                                                                  | 통합 Rules 인덱스 (문서 분류, n8n, AI 룰, Phase 폴더, 명령 링크) |
| ~~common-rules-and-conventions.md~~ | ⚠️ DEPRECATED                                                                                                                        | -                                                                |
| **n8n 규칙**                        | [n8n/n8n-rules-index.md](../n8n/n8n-rules-index.md)                                                                                  | 노드 명명 규칙·Prefix·동사·대상·금지 규칙                        |
| **Phase 문서 분류**                 | [common/common-phase-document-taxonomy.md](../common/references/common-phase-document-taxonomy.md)                                   | plan/todo-list/task/summary 역할·저장 위치                       |
| **webtest 인덱스**                  | [frontend/frontend-webtest-readme.md](../frontend/references/frontend-webtest-readme.md)                                             | webtest 순차 진행·Phase별 테스트 계획                            |
| **Phase 단위 테스트**               | [frontend/frontend-rule-phase-unit-user-test-guide.md](../frontend/references/frontend-rule-phase-unit-user-test-guide.md)           | 3가지 방안, [webtest: X-Y start] 명령                            |
| **Phase 10 E2E+MCP**                | [frontend/frontend-webtest-phase-10-test-scenario-guide.md](../frontend/references/frontend-webtest-phase-10-test-scenario-guide.md) | E2E 실행 → MCP 시나리오(Task당 10개) → 결과 기록                 |
