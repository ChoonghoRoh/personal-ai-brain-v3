# MCP(Cursor) 웹 테스트 수행 가이드

**용도**: Cursor에서 **브라우저 MCP**를 사용해 phase 단위 웹 체크리스트를 수행할 수 있도록, **활성화 방법**과 **실행 절차·지시문**을 정리한 문서입니다.

---

## 1. Cursor에서 브라우저(MCP) 활성화

Cursor는 **별도 MCP 서버 설치 없이** 내장 브라우저 기능을 제공합니다. 아래 설정으로 사용 가능 여부를 확인·활성화합니다.

### 1.1 설정 경로

1. **Cursor Settings** 열기 (`Cmd + ,` 또는 `Ctrl + ,`)
2. **Tools & MCP** → **Browser Automation** 이동
3. **Browser context** 선택: **Chrome** 또는 **Browser Tab**
   - **Chrome**: 별도 Chrome 프로세스에서 전체 화면
   - **Browser Tab**: Cursor 창 내 인라인 탭
4. 변경 사항은 **새 브라우저 세션**부터 적용됩니다.

참고: [Cursor Docs – Browser](https://cursor.com/docs/agent/browser)

### 1.2 Enterprise / 팀 사용 시

- **Admin Dashboard** → **MCP Configuration** → **Browser features** (또는 **Enable Browser Automation Features**) 토글이 **켜져 있는지** 확인합니다.
- Origin 제한이 있으면 `http://localhost:8001`(또는 사용하는 Base URL)이 허용 목록에 있는지 확인합니다.

### 1.3 동작 확인

- Agent(Composer) 채팅에서 **@browser** 를 입력해 브라우저 컨텍스트가 제안되는지 확인합니다.
- 또는 _"http://localhost:8001/dashboard 로 이동해 줘"_ 라고 지시했을 때 브라우저가 열리고 페이지가 로드되면 정상입니다.

---

## 2. 테스트 전 준비

| 항목                  | 내용                                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **백엔드 기동**       | [web-user-test-setup-guide.md](web-user-test-setup-guide.md) 2절 — `docker-compose up -d` 또는 `uvicorn ... --port 8000` |
| **Base URL**          | `http://localhost:8001` (로컬에서 Cursor와 같은 PC면 접근 가능)                                                          |
| **체크리스트 위치**   | `docs/phases/phase-<X>-<Y>/phase-<X>-<Y>-web-user-checklist.md`                                                          |
| **테스트 계획(선택)** | `docs/webtest/phase-<X>-<Y>/phase-<X>-<Y>-user-test-plan.md`                                                             |

---

## 3. MCP Cursor 테스트 수행 절차

### 3.1 단계 요약

1. Cursor **Agent(Composer)** 를 연다.
2. **테스트할 phase**의 웹 체크리스트(및 필요 시 테스트 계획) 문서를 **@로 첨부**한다.
3. **지시문**을 입력해 체크리스트를 **가상 브라우저에서 순서대로 수행**하라고 요청한다.
4. (선택) 관점별 기록이 필요하면 [personas.md](personas.md)와 [prompts/](prompts/) 중 하나를 함께 붙이고 **기획자/개발자/UI·UX** 관점으로 기록하라고 지시한다.
5. 결과는 체크리스트의 **결과/비고**란 형식이나 [phase-x-y-web-user-test-report](phase-unit-user-test-guide.md#5-리포트-작성-프로세스-phase-x-y-web-user-test-report) 형식으로 정리하도록 요청한다.

### 3.2 지시문 예시 (방안 A — 기본)

아래를 복사해 phase 번호와 문서 경로만 바꿔 사용할 수 있습니다.

**Phase 9-1 예시:**

```
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md

이 문서의 "메뉴(라우터)별 시나리오 체크리스트"를 따라
가상 브라우저(MCP)에서 http://localhost:8001 기준으로 순서대로 수행해 줘.

- 각 시나리오(W1.1, W1.2, …)별로 접속·동작·결과를 확인하고
- 결과/비고란에 통과(OK)·실패·비고를 기록해 줘.
- 브라우저 스냅샷이나 콘솔/네트워크 확인이 필요하면 해당 내용도 요약해 줘.
```

**Phase 9-3 예시:**

```
@docs/phases/phase-9-3/phase-9-3-web-user-checklist.md

phase-9-3 웹 체크리스트를 가상 브라우저(MCP)에서
http://localhost:8001 기준으로 순서대로 수행해 줘.
결과는 체크리스트의 결과/비고 형식으로 기록해 줘.
```

### 3.3 지시문 예시 (방안 B — 페르소나 관점)

**기획자 관점:**

```
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md
@docs/webtest/personas.md
@docs/webtest/prompts/prompt-planner.md

위 문서를 참고해서 phase-9-1 웹 체크리스트를 가상 브라우저에서 순서대로 수행해 줘.
꼼꼼한 기획자 관점으로 발견 사항(요구사항·플로우·안내 문구)을 기록해 줘.
```

**개발자 관점:** `prompt-planner.md` 대신 `@docs/webtest/prompts/prompt-developer.md`  
**UI·UX 관점:** `@docs/webtest/prompts/prompt-uiux-designer.md`

---

## 4. Phase 10-1·10-2: E2E + MCP 시나리오(Task당 10개) .md

Phase 10-1·10-2는 **E2E 실행** 후 **Task당 10개** 시나리오가 정의된 .md 문서를 기준으로 MCP cursor 브라우저에서 수행합니다.

| Phase    | E2E 실행                                | MCP 시나리오 .md (Task당 10개)                                                               | 결과 문서                                                                       |
| -------- | --------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **10-1** | `python3 scripts/webtest.py 10-1 start` | [phase-10-1-mcp-webtest-scenarios.md](phase-10-1/phase-10-1-mcp-webtest-scenarios.md) (30개) | [phase-10-1-mcp-webtest-result.md](phase-10-1/phase-10-1-mcp-webtest-result.md) |
| **10-2** | `python3 scripts/webtest.py 10-2 start` | [phase-10-2-mcp-webtest-scenarios.md](phase-10-2/phase-10-2-mcp-webtest-scenarios.md) (40개) | [phase-10-2-mcp-webtest-result.md](phase-10-2/phase-10-2-mcp-webtest-result.md) |

- **순차 가이드**: [phase-10-test-scenario-guide.md](phase-10-test-scenario-guide.md).
- **지시문 예시 (10-1):** `@docs/webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md` 를 참고해서 phase-10-1 MCP 시나리오(Task당 10개)를 가상 브라우저에서 순서대로 수행해 줘. 결과는 phase-10-1-mcp-webtest-result.md 시나리오별 결과 표에 기록해 줘.
- **지시문 예시 (10-2):** `@docs/webtest/phase-10-2/phase-10-2-mcp-webtest-scenarios.md` 를 참고해서 phase-10-2 MCP 시나리오(Task당 10개)를 가상 브라우저에서 순서대로 수행해 줘. 결과는 phase-10-2-mcp-webtest-result.md에 기록해 줘.

---

## 5. 복사용 프롬프트 (한 줄 요청)

바로 붙여 넣기 편한 한 줄 요청문은 [prompts/prompt-mcp-webtest.md](prompts/prompt-mcp-webtest.md) 에 정리해 두었습니다. phase만 바꿔서 사용하면 됩니다.

---

## 6. 문제 해결

### 브라우저 도구가 보이지 않을 때

- **Cursor Settings** → **Tools & MCP** → **Browser Automation** 에서 Browser Tab 또는 Chrome이 선택되어 있는지 확인합니다.
- Cursor를 재시작한 뒤 Agent를 다시 열어 봅니다.
- Enterprise면 관리자에게 **Browser features** 활성화 여부를 확인합니다.

### "Tool not found" / MCP 호출 불가

- 해당 Cursor 세션에서 브라우저 MCP가 등록되지 않은 상태일 수 있습니다. (예: [phase-9-3-report-developer.md](phase-9-3/reports/phase-9-3-report-developer.md) 참고)
- **대안**: [방안 C: E2E](phase-unit-user-test-guide.md#방안-c-e2e-테스트-playwright) 로 `[webtest: X-Y start]` 명령을 실행해 Playwright E2E로 동일 체크리스트를 자동 실행할 수 있습니다.

### localhost 접근이 안 될 때

- 브라우저와 Cursor가 **같은 PC**에서 실행 중인지 확인합니다.
- 터널(ngrok 등)이나 배포 URL을 쓰는 경우, 해당 URL을 Base URL로 사용하고 Enterprise Origin 허용 목록에 추가합니다.

---

## 7. 관련 문서

| 문서                                                           | 용도                                                   |
| -------------------------------------------------------------- | ------------------------------------------------------ |
| [phase-unit-user-test-guide.md](phase-unit-user-test-guide.md) | 3가지 방안( MCP·페르소나·E2E ) 요약 및 리포트 프로세스 |
| [web-user-test-setup-guide.md](web-user-test-setup-guide.md)   | 백엔드 기동, Base URL, E2E/MCP 전제 조건               |
| [personas.md](personas.md)                                     | 페르소나·관점별 기록 가이드                            |
