# Phase 단위 유저 테스트 수행 가이드

**용도**: 특정 phase를 선택해 웹 사용자 테스트를 수행할 때 따를 절차입니다. Phase 단위 작업 완료 후 **web-user-checklist.md**를 생성하고, 본 가이드의 **3가지 테스트 방안** 중 하나(또는 조합)로 수행한 뒤 **phase-x-y-web-user-test-report** 리포트 작성 프로세스와 연결합니다.

---

## 흐름 요약

| 단계 | 내용                                                                                                                          |
| ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| 1    | Phase 작업 완료 → 해당 phase용 `phase-X-Y-web-user-checklist.md` 생성/확인                                                    |
| 2    | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)대로 환경 구축 (Base URL, 백엔드 기동)                       |
| 3    | 본 가이드 **테스트 수행 방안**(MCP·페르소나·E2E) 중 선택하여 체크리스트 수행                                                  |
| 4    | 결과를 **phase-x-y-web-user-test-report** 형식으로 정리 (`docs/webtest/phase-X-Y/reports/` 또는 `phase-X-Y-final-summary.md`) |

---

## 0. 테스트 실행 방법 요약 (3가지 방안)

| 방안                    | 실행 방법                                                                                                                                            | 비고                                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **방안 A: MCP(Cursor)** | Cursor 채팅에서 **테스트 계획 + 웹 체크리스트** 문서를 @로 붙이고, _"phase-X-Y 웹 체크리스트를 가상 브라우저(MCP)에서 순서대로 수행해 줘"_ 라고 지시 | CLI 명령 없음. [방안 A 상세](#방안-a-mcpcursor-테스트) 참고                                         |
| **방안 B: 페르소나**    | 위와 동일 + [frontend-webtest-personas.md](frontend-webtest-personas.md) + 관점별 prompt를 함께 전달해 **기획자/개발자/UI·UX** 관점으로 기록 지시  | 방안 A와 동일하게 Cursor에서 지시. [방안 B 상세](#방안-b-페르소나-기반-테스트-personasmd-참고) 참고 |
| **방안 C: E2E**         | **[webtest: X-Y start]** 명령으로 해당 phase E2E 자동 실행 (아래 명령 표 참고)                                                                       | E2E 스펙이 있는 phase만 가능. [방안 C 상세](#방안-c-e2e-테스트-playwright) 참고                     |

---

### [webtest: X-Y start] 명령 (방안 C — E2E 자동 실행)

**명령을 내리면** 해당 phase의 E2E 웹테스트를 자동 실행할 수 있습니다. (E2E 스펙이 있는 phase만 실행 가능)

| 명령                                   | 설명                                                      |
| -------------------------------------- | --------------------------------------------------------- |
| `python scripts/webtest.py 9-3 start`  | Phase 9-3 E2E 실행 (`e2e/phase-9-3.spec.js`)              |
| `python scripts/webtest.py 9-1 start`  | Phase 9-1 E2E 실행 (스펙 있으면 실행, 없으면 안내 메시지) |
| `python scripts/webtest.py 10-1 start` | Phase 10-1 E2E 실행 (`e2e/phase-10-1.spec.js`)            |
| `python scripts/webtest.py 10-2 start` | Phase 10-2 E2E 실행 (`e2e/phase-10-2.spec.js`)            |
| `npm run webtest:start -- 9-3`         | 위와 동일 (package.json 스크립트 경유)                    |

**사용 예:**

```bash
# 프로젝트 루트에서 (python3 또는 python)
python3 scripts/webtest.py 9-3 start
# 또는
npm run webtest:start -- 9-3
```

**동작 요약:**

- **E2E 스펙이 있는 phase** (예: `e2e/phase-9-3.spec.js`): `npx playwright test e2e/phase-X-Y.spec.js` 를 실행합니다.
- **E2E 스펙이 없는 phase**: 스크립트가 “E2E 스펙 없음” 안내를 출력하고, [방안 A(MCP)](#방안-a-mcpcursor-테스트) 또는 [방안 B(페르소나)](#방안-b-페르소나-기반-테스트-personasmd-참고)로 테스트하라고 안내합니다.

**전제:** [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)대로 백엔드(Base URL)가 기동 중이어야 E2E가 정상 동작합니다.

---

## 1. Phase 선택

테스트할 phase를 결정합니다. (예: Phase 9-1 보안 강화, Phase 9-3 AI 기능 고도화)

- Phase 목록·상태는 [common/common-phase-9-navigation.md](../../common/references/common-phase-9-navigation.md) 등을 참조할 수 있습니다.
- `frontend/` 아래 해당 phase용 문서가 있는지 확인합니다. (예: `frontend-webtest-phase-9-1-*`, `frontend-webtest-phase-9-3-*`)

---

## 2. 해당 Phase 폴더 및 문서 확인

- **테스트 계획 문서**: `frontend/frontend-webtest-phase-<X>-<Y>-user-test-plan.md`
  - 해당 phase의 테스트 목표, 범위, 참고 문서(웹 체크리스트·API 체크리스트) 링크가 있습니다.
- **웹 시나리오 체크리스트**: `frontend/frontend-phase-<X>-<Y>-web-user-checklist.md`
  - 예: Phase 9-1 → [frontend-phase-9-1-web-user-checklist.md](./frontend-phase-9-1-web-user-checklist.md)
  - 메뉴(라우터)별 시나리오와 결과/비고 칸이 있습니다.

---

## 3. 테스트 수행 방안 (3가지)

체크리스트를 수행하는 방법은 아래 **방안 A·B·C** 중 하나(또는 조합)를 선택합니다. 가이드에 맞춰 수행한 뒤, [5. 리포트 작성 프로세스](#5-리포트-작성-프로세스-phase-x-y-web-user-test-report)에 따라 리포트를 작성합니다.

---

### 방안 A: MCP(Cursor) 테스트

**AI 에이전트(Cursor)가 브라우저 MCP로** 페이지 이동·클릭·입력·스냅샷을 수행하며 체크리스트를 따라가는 방식입니다.

| 항목          | 내용                                                                                                                                                                                                                                           |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **전제**      | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) 3.3절 — 백엔드 Base URL 기동, Cursor와 브라우저 MCP가 같은 호스트에서 동작하면 `http://localhost:8001` 접근 가능                                                             |
| **수행 절차** | 1) 테스트 계획 + 웹 체크리스트 문서를 에이전트에게 전달<br>2) "phase-X-Y 웹 체크리스트를 가상 브라우저에서 순서대로 수행해 줘"처럼 지시<br>3) 필요 시 [frontend-webtest-personas.md](frontend-webtest-personas.md) + 관점별 prompt를 함께 전달해 **어떤 관점으로 기록할지** 지정 |
| **참고 문서** | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) — MCP 브라우저 사용 가능 여부·Base URL 조건<br>**[MCP Cursor 테스트 수행 가이드](frontend-webtest-mcp-cursor-test-guide.md)** — Cursor에서 브라우저 활성화·수행 절차·지시문·문제 해결 |

**지시문 예시 (방안 A):**

```
@docs/webtest/phase-9-1/phase-9-1-user-test-plan.md
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md
를 참고해서 phase-9-1 웹 체크리스트를 가상 브라우저(MCP)에서 순서대로 수행해 줘.
결과는 체크리스트의 결과/비고란 형식으로 기록해.
```

---

### 방안 B: 페르소나 기반 테스트 ([frontend-webtest-personas.md](frontend-webtest-personas.md) 참고)

**[frontend-webtest-personas.md](frontend-webtest-personas.md)**에 정의된 **일반 웹 사용자** 기준과 **관점(기획자/개발자/UI·UX 디자이너)**에 맞춰 체크리스트를 수행·기록하는 방식입니다. 수동 테스트 또는 방안 A(MCP)와 함께 사용합니다.

| 항목              | 내용                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **기준 페르소나** | [frontend-webtest-personas.md](frontend-webtest-personas.md) 1절 — **일반 웹 사용자**: 메뉴 진입 → 화면 동작 → 결과 확인이 자연스러운지 검증                                                                                                                                                                                                                                                                 |
| **관점 지정**     | [frontend-webtest-personas.md](frontend-webtest-personas.md) 2절 — **꼼꼼한 기획자** / **개발자** / **UI·UX 디자이너** 중 하나 선택 후, 해당 관점에서 발견 사항 기록                                                                                                                                                                                                                                         |
| **수행 절차**     | 1) 테스트 계획 + 웹 체크리스트 + **frontend-webtest-personas.md** + **관점별 prompt**([frontend-webtest-prompt-planner.md](frontend-webtest-prompt-planner.md), [frontend-webtest-prompt-developer.md](frontend-webtest-prompt-developer.md), [frontend-webtest-prompt-uiux-designer.md](frontend-webtest-prompt-uiux-designer.md)) 준비<br>2) 선택한 관점으로 체크리스트 시나리오 수행<br>3) 발견 사항을 해당 관점의 초점(요구사항·플로우 / 버그·API / 시인성·접근성)에 맞춰 기록 |
| **지시문 예시**   | [frontend-webtest-personas.md](frontend-webtest-personas.md) 3.2절 — 기획자/개발자/UIUX 관점별 지시문 예시 참조                                                                                                                                                                                                                                                                                             |

**지시문 예시 (방안 B, 기획자 관점 + MCP):**

```
@docs/webtest/phase-9-1/phase-9-1-user-test-plan.md
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md
@docs/webtest/personas.md
@docs/webtest/prompts/prompt-planner.md
를 참고해서 phase-9-1 웹 체크리스트를 가상 브라우저에서 순서대로 수행해 줘.
꼼꼼한 기획자 관점으로 발견 사항을 기록해.
```

---

### 방안 C: E2E 테스트 (Playwright)

**Playwright**로 체크리스트 시나리오를 스크립트화해 자동 실행하는 방식입니다.

| 항목          | 내용                                                                                                                                                                                                                                                                                                                                           |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **전제**      | [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) 3.2절 — `baseURL: 'http://localhost:8001'`, 필요 시 `webServer`로 테스트 전 백엔드 기동                                                                                                                                                                                  |
| **위치**      | 프로젝트 루트 또는 `e2e/` — 예: [e2e/phase-9-3.spec.js](../../../../e2e/phase-9-3.spec.js)                                                                                                                                                                                                                                                    |
| **수행 절차** | 1) 해당 phase의 **web-user-checklist.md** 시나리오를 E2E 스펙으로 변환(또는 기존 `e2e/phase-X-Y.spec.js` 활용)<br>2) **자동 실행**: 위 [webtest: X-Y start](#0-webtest-x-y-start-명령으로-웹테스트-자동-실행) 명령 사용 (`python scripts/webtest.py 9-3 start` 또는 `npm run webtest:start -- 9-3`)<br>3) 실행 결과(통과/실패)를 리포트에 반영 |
| **설치·설정** | `npm init -y` → `npm install -D @playwright/test` → `npx playwright install` / `playwright.config.js`에 baseURL 설정                                                                                                                                                                                                                           |

**E2E ↔ 체크리스트 매핑:** 체크리스트의 시나리오 번호(예: W1.1, W2.1)와 E2E 테스트 describe/test 이름을 대응시키면 리포트 작성 시 추적이 쉽습니다.

**Phase 10-1·10-2: E2E 후 MCP 시나리오(Task당 10개) .md 실행 및 결과 기록**

- Phase 10-1·10-2는 **E2E 실행** 후 **MCP 시나리오(Task당 10개) .md** 기준으로 MCP cursor 브라우저 또는 Playwright 시나리오 스펙을 실행하고, 결과를 phase-X-Y-mcp-webtest-result.md에 기록합니다.
- **순차 가이드**: [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md) — E2E → 시나리오 .md 확인 → 실행 → 결과 기록.
- **Phase 10-1 시나리오 .md**: [frontend-webtest-phase-10-1-mcp-scenarios.md](frontend-webtest-phase-10-1-mcp-scenarios.md) (Task 10-1-1·10-1-2·10-1-3 각 10개, 총 30개).
- **Phase 10-2 시나리오 .md**: [frontend-webtest-phase-10-2-mcp-scenarios.md](frontend-webtest-phase-10-2-mcp-scenarios.md) (Task 10-2-1~10-2-4 각 10개, 총 40개).

---

## 4. 수행 순서 (공통)

1. **테스트 계획 문서**에서 범위·목표·시나리오를 확인합니다.
2. **체크리스트(시나리오)**대로 선택한 방안(A/B/C)으로 실행합니다. (Base URL·환경은 [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) 참조)
3. **방안 B**를 사용할 때는 [frontend-webtest-personas.md](frontend-webtest-personas.md)에 맞춰 **일반 웹 사용자** 관점으로 동작을 검증하고, 관점별 프롬프트로 발견 사항을 기록합니다.
4. **결과**는 체크리스트의 "결과/비고"란 또는 해당 phase 테스트 계획 문서 하단 요약 표에 기록합니다.
5. **[5. 리포트 작성 프로세스](#5-리포트-작성-프로세스-phase-x-y-web-user-test-report)**에 따라 `phase-x-y-web-user-test-report` 형식으로 정리합니다.

---

## 5. 리포트 작성 프로세스 (phase-x-y-web-user-test-report)

테스트 수행 후 결과를 다음 형식으로 정리해 **phase 단위 웹 유저 테스트 리포트**를 완성합니다.

| 산출물            | 위치                                                              | 용도                                                     |
| ----------------- | ----------------------------------------------------------------- | -------------------------------------------------------- | --------- | -------------------------------------------------- |
| **관점별 리포트** | `docs/webtest/phase-<X>-<Y>/reports/phase-<X>-<Y>-report-{planner | developer                                                | uiux}.md` | 페르소나 관점(기획자/개발자/UIUX)별 발견 사항·결과 |
| **리포트 인덱스** | `docs/webtest/phase-<X>-<Y>/reports/README.md`                    | 관점별 문서 링크, 테스트 기준(체크리스트)·수행 방안 요약 |
| **최종 요약**     | `docs/webtest/phase-<X>-<Y>/phase-<X>-<Y>-final-summary.md`       | Phase 전체 테스트 결과 요약, 이슈·조치 요약              |

**연결 흐름:**
`phase-X-Y-web-user-checklist.md` (가이드에 맞춰 수행) → **방안 A/B/C** 실행 → 결과 기록 → **phase-x-y-web-user-test-report** (reports/ + final-summary) 작성

- 예: Phase 9-3 — [phase-9-3/reports/README.md](../../../webtest/phase-9-3/reports/README.md), [phase-9-3-final-summary.md](../../../webtest/phase-9-3/phase-9-3-final-summary.md) 참조

---

## 6. 다른 Phase 추가 시

새 phase(예: 9-1, 9-4)에 대해 유저 테스트를 수행하려면:

1. `docs/webtest/phase-<X>-<Y>/` 폴더를 생성합니다.
2. `phase-<X>-<Y>-user-test-plan.md` 테스트 계획 문서를 작성합니다. (목표, 범위, 참고 체크리스트 링크, 테스트 환경, 수행 절차 참조)
3. `docs/phases/phase-<X>-<Y>/phase-<X>-<Y>-web-user-checklist.md` 가 없으면 해당 phase 작업 완료 후 체크리스트를 생성합니다.
4. 위 1~5와 동일하게 **3가지 방안** 중 선택하여 체크리스트를 수행하고, **phase-x-y-web-user-test-report** 리포트를 작성합니다.

**템플릿**: [frontend-webtest-template-phase-x-y-user-test-plan.md](frontend-webtest-template-phase-x-y-user-test-plan.md)를 복사한 뒤 phase 번호와 이름을 치환해 사용할 수 있습니다.
