# Web 사용자 테스트 환경 구축 가이드

**용도**: 웹 사용자 테스트를 수행하기 전에 필요한 환경(백엔드 기동, Base URL, 브라우저)을 준비합니다. **사람이 직접** 브라우저에서 수행하는 경우와 **가상 웹 브라우저에서 AI·자동화가 직접 실행**하는 경우 모두를 위한 전제 조건과 실행 방법을 다룹니다. 환경 구축을 마친 뒤, phase 단위로 `docs/webtest/phase-X-Y/` 폴더를 만들고 해당 phase용 테스트 계획 문서를 작성합니다. 상세 절차는 [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md)를 참조하세요.

---

## 1. 전제 조건

### 1.1 백엔드 및 Base URL

- **Base URL**: `http://localhost:8001` (기본값)
- 백엔드가 이 주소에서 응답해야 브라우저로 웹 화면(대시보드, 검색, Ask, Reasoning Lab, 지식 관리 등)에 접근할 수 있습니다.

### 1.2 브라우저

- **권장**: Chrome, Edge 등 최신 데스크톱 브라우저
- **선택**: 테스트 시 화면 해상도를 통일하려면 1920×1080 또는 1280×720 등 고정 후 수행

---

## 2. 테스트용 앱 기동

### 2.1 Docker Compose로 기동 (권장)

프로젝트 루트에서 다음을 실행합니다.

```bash
docker-compose up -d
```

- PostgreSQL, Qdrant, Backend 서비스가 기동됩니다.
- Backend: http://localhost:8001 (대시보드: `/dashboard`, API 문서: `/docs`)
- Ollama(로컬 LLM)는 호스트에서 별도 실행하는 구성을 권장합니다. AI 질의·Reasoning·키워드 추천 등을 테스트할 경우 Ollama가 동작 중이어야 합니다.

### 2.2 로컬에서 Backend만 기동

DB·Qdrant는 Docker로 띄운 뒤, Backend만 로컬에서 실행할 수도 있습니다.

```bash
# 가상환경 활성화 후
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

- 브라우저에서 http://localhost:8001/dashboard 로 접속해 화면이 뜨는지 확인합니다.

---

## 3. 가상 웹 브라우저에서 AI·자동화로 실행할 때

체크리스트를 **사람이 직접** 브라우저에서 수행하는 대신, **가상 웹 브라우저에서 AI 또는 자동화 스크립트가 직접 실행**하려면 아래를 준비합니다.

### 3.1 공통 전제

- **백엔드가 Base URL에서 기동 중**이어야 합니다. (위 2절대로 `docker-compose up -d` 또는 uvicorn)
- **Base URL**: `http://localhost:8001` (자동화/에이전트가 같은 호스트에서 실행할 때). 원격 에이전트가 접속할 경우에는 터널(예: ngrok) 또는 배포 URL이 필요할 수 있습니다.

### 3.2 Playwright E2E로 자동 실행

스크립트(또는 AI가 생성한 테스트 코드)가 브라우저를 제어해 체크리스트 시나리오를 자동 실행하는 방식입니다.

- **설치** (프로젝트 루트 또는 `e2e/` 등):
  ```bash
  npm init -y
  npm install -D @playwright/test
  npx playwright install
  ```
- **설정**: `playwright.config.js`에서 `baseURL: 'http://localhost:8001'` 지정. 필요 시 `webServer`로 테스트 전에 백엔드를 기동하도록 설정.
- **실행**: `npx playwright test` 로 체크리스트를 반영한 E2E 스펙을 실행. (체크리스트 → E2E 변환 가이드는 [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md) 또는 프로젝트 E2E 문서 참조)

### 3.3 에이전트(AI)·MCP 브라우저로 직접 실행

AI 에이전트(Cursor 등)가 **브라우저 MCP**로 페이지 이동·클릭·입력·스냅샷을 수행하며 체크리스트를 따라가는 방식입니다.

- **필요 조건**: 에이전트가 사용하는 브라우저 MCP 서버가 **테스트 대상 앱에 접근 가능한 URL**을 사용할 수 있어야 합니다. (일부 MCP는 격리된 서버에서 동작해 `localhost`·사설 IP에 접근하지 못할 수 있음.)
- **로컬 에이전트**: 에이전트와 브라우저가 같은 PC에서 동작하면 `http://localhost:8001` 으로 접속 가능. 백엔드만 위 2절대로 기동하면 됩니다.
- **Cursor에서 브라우저 활성화·지시문**: [frontend-webtest-mcp-cursor-test-guide.md](frontend-webtest-mcp-cursor-test-guide.md) 참고.
- **실행 방법**: 에이전트에게 “해당 phase 웹 체크리스트(예: phase-9-1)를 가상 브라우저에서 순서대로 수행해 줘”처럼 지시하고, 해당 phase 체크리스트 문서(예: [phase-9-1-web-user-checklist.md](../../../phases/phase-9-1/phase-9-1-web-user-checklist.md), [phase-9-3-web-user-checklist.md](../../../phases/phase-9-3/phase-9-3-web-user-checklist.md))를 참조하게 하면 됩니다. 관점별 프롬프트는 [docs/webtest/prompts/](../../../webtest/prompts/) 를 함께 주면 기획자/개발자/UIUX 관점으로 기록하도록 유도할 수 있습니다.

---

## 4. 체크리스트 및 테스트 계획 위치

- **Phase별 웹 체크리스트**: `docs/phases/phase-X-Y/` 아래에 있는 웹 사용자 체크리스트(예: `phase-9-1-web-user-checklist.md`, `phase-9-3-web-user-checklist.md`)를 참조합니다.
- **Phase별 테스트 계획**: `docs/webtest/phase-X-Y/phase-X-Y-user-test-plan.md` 에서 해당 phase의 테스트 목표, 범위, 참고 문서를 확인합니다.
- **Phase 10-1·10-2**: E2E 실행 후 **MCP 시나리오(Task당 10개) .md** 기준으로 수행 — [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md), [frontend-webtest-phase-10-1-mcp-scenarios.md](frontend-webtest-phase-10-1-mcp-scenarios.md), [frontend-webtest-phase-10-2-mcp-scenarios.md](frontend-webtest-phase-10-2-mcp-scenarios.md) 참조.

환경 구축을 마친 뒤에는 [frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md)에 따라 phase를 선택하고, **3가지 테스트 방안**(MCP·페르소나·E2E) 중 하나로 체크리스트를 수행한 뒤, phase-x-y-web-user-test-report 리포트 작성 프로세스와 연결하면 됩니다. Phase 10-1·10-2는 [frontend-webtest-phase-10-test-scenario-guide.md](frontend-webtest-phase-10-test-scenario-guide.md) 순차 진행을 따릅니다.
