# AI Team — Project SSOT

**버전**: 4.2
**최종 수정**: 2026-02-16

---

## 1. 프로젝트 정의

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Personal AI Brain v3 |
| **목적** | 로컬 설치형 개인 AI 브레인 — 문서 벡터화, 의미 검색, AI 응답, 지식 구조화, Reasoning |
| **배포 형태** | Docker Compose (On-Premise, 폐쇄망 동작 필수) |
| **현재 Phase** | Phase 14 완료, Phase 15 계획 수립 대기 |

---

## 2. 팀 구성

### 2.1 Agent Teams 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│               Team Lead + Orchestrator (메인 세션)                    │
│  Charter: LEADER.md                                                  │
│  역할: TeamCreate → 팀원 스폰 → SendMessage 조율 → 판정 → TeamDelete │
│  도구: Edit, Write, Read, Glob, Grep, Bash, Task, TeamCreate,       │
│        SendMessage, TaskCreate/Update/List, TeamDelete               │
└──┬──────────┬──────────────┬──────────────┬──────────────┬──────────┘
   │          │              │              │              │
┌──▼───┐ ┌───▼──────────┐ ┌─▼──────────┐ ┌▼──────────┐ ┌▼─────────┐
│plan- │ │backend-dev   │ │frontend-   │ │verifier   │ │tester    │
│ner   │ │              │ │dev         │ │           │ │          │
│      │ │subagent_type:│ │subagent_   │ │subagent_  │ │subagent_ │
│sub-  │ │"general-     │ │type:       │ │type:      │ │type:     │
│agent │ │ purpose"     │ │"general-   │ │"Explore"  │ │"Bash"    │
│_type:│ │              │ │ purpose"   │ │           │ │          │
│"Plan"│ │Charter:      │ │Charter:    │ │Charter:   │ │Charter:  │
│      │ │BACKEND.md    │ │FRONTEND.md │ │QA.md      │ │QA.md     │
│      │ │              │ │            │ │           │ │          │
│읽기  │ │**코드 편집** │ │**코드 편집**│ │읽기 전용  │ │Bash 전용 │
│전용  │ │**가능**      │ │**가능**    │ │           │ │          │
│opus  │ │sonnet        │ │sonnet      │ │sonnet     │ │sonnet    │
└──────┘ └──────────────┘ └────────────┘ └───────────┘ └──────────┘
           ↕ 모든 통신은 Team Lead 경유 (Hub-and-Spoke) ↕
```

### 2.2 역할-실행 매핑

| 역할 | Charter | 팀원 이름 | `subagent_type` | `model` | 코드 편집 |
|------|---------|----------|:---------------:|:-------:|:--------:|
| **Team Lead** | `LEADER.md` | — (메인 세션) | — | opus | **X** (코드 수정 안 함) |
| **Planner** | — (고유) | `planner` | `Plan` 또는 `Explore` | **opus** | X |
| **Backend Developer** | `BACKEND.md` | `backend-dev` | `general-purpose` | sonnet | **O** |
| **Frontend Developer** | `FRONTEND.md` | `frontend-dev` | `general-purpose` | sonnet | **O** |
| **Verifier** | `QA.md` | `verifier` | `Explore` | sonnet | X |
| **Tester** | `QA.md` | `tester` | `Bash` | sonnet | X |

**코드 편집 원칙 (v4.1)**:
- **Team Lead는 코드를 직접 수정하지 않는다.** 조율·판정·통신 허브 역할에 집중한다.
- `backend-dev`는 백엔드 코드(`backend/`, `tests/`, `scripts/`)를 편집한다.
- `frontend-dev`는 프론트엔드 코드(`web/`, `e2e/`)를 편집한다.
- `verifier`는 읽기 전용으로 코드 리뷰만 수행하고, 수정이 필요하면 **Team Lead에게 보고**한다.

### 2.3 역할별 상세

#### Team Lead + Orchestrator (메인 세션)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/LEADER.md` |
| **핵심 역할** | 팀 생성·해산, 워크플로우 지휘, 상태 관리, 최종 판정, **통신 허브** |
| **권한** | TeamCreate, TeamDelete, SendMessage, Task tool, 파일 읽기, Git, Bash |
| **책임** | Phase 상태 관리, 판정 결정(PASS/FAIL/PARTIAL), Task 할당(TaskCreate/TaskUpdate), 팀원 조율, 이슈 해결 |
| **금지** | **코드 직접 수정 금지** — 모든 코드 작성은 `backend-dev` 또는 `frontend-dev`에게 위임 |

#### Planner (팀원: `planner`)

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `planner` |
| **실행 방법** | `Task tool` → `team_name: "phase-X-Y"`, `name: "planner"`, `subagent_type: "Plan"`, `model: "opus"` |
| **핵심 역할** | 요구사항 분석, 영향 범위 탐색, 계획 수립 |
| **권한** | 파일 읽기, 검색 (Glob, Grep, Read) — 쓰기 권한 없음 |
| **입력** | master-plan, navigation, 이전 Phase summary |
| **출력** | 계획 분석 결과를 SendMessage로 Team Lead에게 전달 |

#### Backend Developer (팀원: `backend-dev`)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/BACKEND.md` |
| **팀원 이름** | `backend-dev` |
| **실행 방법** | `Task tool` → `team_name: "phase-X-Y"`, `name: "backend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **핵심 역할** | API, DB, 서비스 로직 구현 — **코드 편집 가능** |
| **권한** | 파일 읽기/쓰기/편집, Bash, Glob, Grep, Read |
| **담당 범위** | `backend/`, `tests/`, `scripts/` 디렉토리 |
| **통신** | TaskList로 할당된 작업 확인, 완료 시 TaskUpdate + SendMessage로 Team Lead에게 보고 |

**팀원 스폰 예시 (Backend Developer)**:
```
Task tool:
  team_name: "phase-15-1"
  name: "backend-dev"
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: "docs/SSOT/claude/role-backend-dev-ssot.md를 먼저 읽어라.
           docs/rules/role/BACKEND.md의 페르소나를 적용하라.
           팀 설정 파일: ~/.claude/teams/phase-15-1/config.json
           TaskList를 확인하여 너에게 할당된 작업을 수행하라.
           작업 완료 시 TaskUpdate(completed) 후 Team Lead에게 SendMessage로 보고하라."
```

#### Frontend Developer (팀원: `frontend-dev`)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/FRONTEND.md` |
| **팀원 이름** | `frontend-dev` |
| **실행 방법** | `Task tool` → `team_name: "phase-X-Y"`, `name: "frontend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **핵심 역할** | UI/UX 분석 + 구현 — **코드 편집 가능** |
| **권한** | 파일 읽기/쓰기/편집, Bash, Glob, Grep, Read |
| **담당 범위** | `web/`, `e2e/` 디렉토리 |
| **원칙** | On-Premise 최적화, CDN 금지, Vanilla JS ESM |

**팀원 스폰 예시 (Frontend Developer)**:
```
Task tool:
  team_name: "phase-15-1"
  name: "frontend-dev"
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: "docs/SSOT/claude/role-frontend-dev-ssot.md를 먼저 읽어라.
           docs/rules/role/FRONTEND.md의 페르소나를 적용하라.
           TaskList를 확인하여 너에게 할당된 [FE] 작업을 수행하라.
           On-Premise 원칙: 외부 CDN 절대 금지, Vanilla JS ESM.
           작업 완료 시 TaskUpdate(completed) 후 Team Lead에게 SendMessage로 보고하라."
```

#### Verifier (팀원: `verifier`)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/QA.md` |
| **팀원 이름** | `verifier` |
| **실행 방법** | `Task tool` → `team_name: "phase-X-Y"`, `name: "verifier"`, `subagent_type: "Explore"`, `model: "sonnet"` |
| **핵심 역할** | 코드 리뷰, 품질 게이트, 보안 점검 — **읽기 전용** |
| **권한** | 파일 읽기, 검색 — 쓰기 권한 없음 |
| **입력** | Team Lead가 SendMessage로 전달한 변경 파일 목록, 완료 기준 |
| **출력** | 검증 결과 (PASS/FAIL/PARTIAL + 이슈 목록)를 SendMessage로 반환 |
| **통신** | 검증 결과를 SendMessage로 **Team Lead에게만** 보고. Team Lead가 수정을 개발자에게 전달 |

#### Tester (팀원: `tester`)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/QA.md` |
| **팀원 이름** | `tester` |
| **실행 방법** | `Task tool` → `team_name: "phase-X-Y"`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **핵심 역할** | 테스트 실행, 커버리지 분석, 결함 문서화 |
| **권한** | Bash 명령 실행 (pytest, playwright 등) |
| **입력** | Team Lead가 SendMessage로 전달한 테스트 범위, 명령 |
| **출력** | 테스트 결과를 SendMessage로 Team Lead에게 반환 |

### 2.4 에이전트 팀 운용 원칙

| 원칙 | 설명 |
|------|------|
| **팀 생성** | Phase 시작 시 `TeamCreate(team_name: "phase-X-Y")`로 팀 생성 |
| **팀원 스폰** | `Task tool`에 `team_name`, `name`, `subagent_type` 지정하여 팀원 스폰 |
| **Charter 장착** | 팀원 스폰 시 해당 역할의 Charter 경로를 프롬프트에 포함 |
| **역할별 SSOT** | 각 팀원은 전용 `role-*-ssot.md` 1개만 로딩 (컨텍스트 최소화) |
| **작업 할당** | `TaskCreate` → `TaskUpdate(owner: "팀원이름")`으로 작업 할당 |
| **통신 모델** | Hub-and-Spoke: 모든 통신은 Team Lead 경유. 팀원끼리 직접 메시지 금지 |
| **작업 완료** | 팀원이 `TaskUpdate(status: "completed")` 후 Team Lead에게 SendMessage |
| **병렬 실행** | 독립적인 Task는 여러 팀원이 동시 수행 (BE + FE 병렬) |
| **팀 해산** | Phase 완료 후 `SendMessage(type: "shutdown_request")` → `TeamDelete` |
| **모델 선택** | planner: `opus` (계획 수립), 나머지 팀원: `sonnet` (구현/검증/테스트) |
| **지연 스폰** | verifier, tester는 VERIFYING/TESTING 단계 진입 시 스폰 (비용 절감) |

### 2.4.1 도메인별 편집 원칙

Agent Teams에서 파일 충돌을 방지하기 위한 편집 권한 규칙이다.

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **EDIT-1** | 도메인별 편집 범위 | `backend-dev`는 `backend/`, `tests/`, `scripts/`만, `frontend-dev`는 `web/`, `e2e/`만 편집 |
| **EDIT-2** | Team Lead 코드 수정 금지 | Team Lead(메인 세션)는 코드를 직접 수정하지 않고 팀원에게 위임 |
| **EDIT-3** | 상태·SSOT 쓰기 독점 | `phase-X-Y-status.md`와 SSOT 문서는 Team Lead만 수정 가능 |
| **EDIT-4** | 읽기 전용 팀원 | `verifier`(Explore)와 `planner`(Plan)는 파일 쓰기/편집 권한 없음 |
| **EDIT-5** | 동시 편집 금지 | 동일 파일을 두 팀원이 동시에 편집하지 않음. [FS] Task는 BE 파트 → FE 파트 순차 진행 |

### 2.5 병렬 실행 패턴

```
# 패턴 1: BE/FE 개발 병렬
Team Lead →
  TaskCreate("Task X-Y-1 [BE] API 구현", owner: "backend-dev")
  TaskCreate("Task X-Y-2 [FE] UI 구현", owner: "frontend-dev")
  → backend-dev와 frontend-dev가 동시 작업
  → 각자 완료 시 TaskUpdate(completed) + SendMessage 보고
  → Team Lead: 두 결과 확인 후 다음 단계

# 패턴 2: 검증 + 테스트 병렬
Team Lead →
  SendMessage → verifier: "Task X-Y-1 변경 파일 검증 요청"
  SendMessage → tester: "pytest tests/ -v 실행 요청"
  → verifier와 tester가 동시 작업
  → 각자 결과를 SendMessage로 보고
  → Team Lead: 두 결과 종합 판정

# 패턴 3: Verifier → Team Lead → Developer 수정 요청 패턴
verifier:
  코드 리뷰 중 이슈 발견
  → SendMessage → Team Lead: "line 45 타입 힌트 누락, FAIL"
Team Lead:
  → SendMessage → backend-dev: "line 45 타입 힌트 누락, 수정 요청"
  → backend-dev가 수정
  → backend-dev → SendMessage → Team Lead: "수정 완료"
  → Team Lead → SendMessage → verifier: "재검증 요청"
  → verifier: 재검증 → Team Lead 보고

# 패턴 4: 풀스택 Task 순차+병렬 혼합
Team Lead →
  [1단계] backend-dev: BE API 구현 (선행)
  [2단계] 완료 알림 수신 → frontend-dev: FE UI 구현 (API 의존)
  [3단계] 완료 알림 수신 → verifier + tester 병렬 검증
```

### 2.6 팀 라이프사이클 상세

#### Phase 시작 시 팀 생성

```python
# 1. 팀 생성
TeamCreate(team_name="phase-15-1", description="Phase 15-1 개발 팀")

# 2. Task 생성 (공유 TaskList)
TaskCreate(subject="[BE] Admin API CRUD", description="...", owner="backend-dev")
TaskCreate(subject="[FE] Admin UI 페이지", description="...", owner="frontend-dev")
TaskCreate(subject="[QC] 코드 리뷰", description="...", owner="verifier")
TaskCreate(subject="[TEST] pytest + E2E", description="...", owner="tester")

# 3. 팀원 스폰 (필요한 역할만 선택적으로)
Task tool(team_name="phase-15-1", name="planner", subagent_type="Plan", ...)
Task tool(team_name="phase-15-1", name="backend-dev", subagent_type="general-purpose", ...)
Task tool(team_name="phase-15-1", name="frontend-dev", subagent_type="general-purpose", ...)
# verifier, tester는 검증 단계에서 스폰 (지연 스폰)
```

#### Phase 완료 시 팀 해산

```python
# 1. 모든 Task 완료 확인
TaskList()  # 전체 completed 확인

# 2. 팀원 순차 셧다운
SendMessage(type="shutdown_request", recipient="tester")
SendMessage(type="shutdown_request", recipient="verifier")
SendMessage(type="shutdown_request", recipient="frontend-dev")
SendMessage(type="shutdown_request", recipient="backend-dev")

# 3. 모든 팀원 셧다운 확인 후
TeamDelete()
```

---

## 3. Task 도메인 분류

각 Task는 도메인을 명시하여 적절한 팀원이 구현/검증한다.

| 도메인 태그 | 설명 | 구현 팀원 | 검증 팀원 |
|-----------|------|:--------:|:-------:|
| `[BE]` | 백엔드 (API, 서비스, 미들웨어) | `backend-dev` | `verifier` + `tester` |
| `[DB]` | 데이터베이스 (스키마, 마이그레이션) | `backend-dev` | `verifier` + `tester` |
| `[FE]` | 프론트엔드 (HTML, JS, CSS) | `frontend-dev` | `verifier` + `tester` |
| `[FS]` | 풀스택 (백엔드 + 프론트 연동) | `backend-dev` + `frontend-dev` | `verifier` + `tester` |
| `[TEST]` | 테스트 전용 (테스트 코드 작성) | `tester` | `verifier` |
| `[INFRA]` | 인프라 (Docker, 환경변수, CI) | `backend-dev` | — |

**Todo-list 작성 예시**:
```markdown
- [ ] Task X-Y-1: [BE] Admin API CRUD 구현 (Owner: backend-dev)
- [ ] Task X-Y-2: [DB] Admin 테이블 마이그레이션 (Owner: backend-dev)
- [ ] Task X-Y-3: [FE] Admin 설정 UI 페이지 구현 (Owner: frontend-dev)
- [ ] Task X-Y-4: [FS] API-UI 연동 및 데이터 바인딩 (Owner: backend-dev + frontend-dev)
- [ ] Task X-Y-5: [TEST] 통합 테스트 시나리오 작성/실행 (Owner: tester)
```

---

## 4. 품질 게이트 정의

### 4.1 게이트 구조

```
[G1: Plan Review]     planner 분석 → Team Lead 검토
        ↓
[G2: Code Review]     verifier가 BE+FE 코드 검증 (결과를 Team Lead에게 보고)
        ↓
[G3: Test Gate]       tester가 테스트 실행 + 커버리지 확인
        ↓
[G4: Final Gate]      Team Lead가 G2+G3 종합 판정
```

### 4.2 게이트별 통과 기준

| 게이트 | 백엔드 기준 | 프론트엔드 기준 | 공통 기준 |
|--------|-----------|--------------|----------|
| **G1** | API Spec 확정, DB 스키마 정의 | 페이지 구조/동선 정의 | 완료 기준 명확, Task 3~7개, 리스크 식별 |
| **G2** | Critical 0건, ORM 사용, 타입 힌트, 에러 핸들링 | CDN 미사용, ESM 준수, innerHTML 미사용 또는 esc() 적용 | 보안 취약점 없음 |
| **G3** | pytest 전체 통과, 커버리지 >= 80% (변경 파일) | 페이지 로드 확인, 콘솔 에러 없음 | 회귀 테스트 통과 |
| **G4** | G2 PASS + G3 PASS | G2 PASS + G3 PASS | Blocker 0건 |

### 4.3 판정 기준

```
G4 Final Gate 판정 로직:

IF (G2_backend = PASS) AND (G2_frontend = PASS)
   AND (G3 = PASS) AND (Blockers = []):
    최종 판정 = "PASS"

ELSE IF (어디든 Critical 이슈):
    최종 판정 = "FAIL"
    → 해당 게이트로 리와인드

ELSE IF (High 이슈만 존재):
    최종 판정 = "PARTIAL"
    → Team Lead 판단:
      - 기능 차단 → FAIL
      - 개선 사항 → Technical Debt 등록 후 진행
```

### 4.4 팀 기반 품질 게이트 흐름

```
backend-dev / frontend-dev: 구현 완료
  │
  ▼ SendMessage → Team Lead: "Task X-Y-N 구현 완료"
  │
Team Lead:
  ▼ SendMessage → verifier: "변경 파일 목록 + 완료 기준" (G2 검증 요청)
  ▼ SendMessage → tester: "테스트 실행 요청" (G3 테스트 요청)
  │
  │ (verifier + tester 병렬 수행)
  │
  ▼ verifier → SendMessage → Team Lead: "G2 결과: PASS/FAIL + 이슈 목록"
  ▼ tester → SendMessage → Team Lead: "G3 결과: PASS/FAIL + 테스트 리포트"
  │
  ▼ (FAIL 시) Team Lead → SendMessage → backend-dev/frontend-dev: "수정 요청"
  │            → 개발자 수정 → Team Lead → verifier 재검증 요청
  │
Team Lead: G2 + G3 종합 → G4 판정
```

---

## 5. 테스트 전략 (강화)

### 5.1 테스트 레벨

| 레벨 | 대상 | 실행 팀원 | 도구 | 실행 시점 |
|------|------|----------|------|----------|
| **L1: 정적 분석** | BE+FE | `verifier` | mypy, ruff / ESLint (코드 리뷰) | 매 구현 완료 후 |
| **L2: 단위 테스트** | BE | `tester` | pytest | 매 구현 완료 후 |
| **L3: 통합 테스트** | BE | `tester` | pytest (integration markers) | Task 단위 완료 후 |
| **L4: API 테스트** | BE+FE | `tester` | pytest + httpx/TestClient | Phase 단위 완료 후 |
| **L5: UI 동작 테스트** | FE | `tester` | Playwright 또는 브라우저 확인 | Phase 단위 완료 후 |
| **L6: E2E 테스트** | FS | `tester` | Playwright (전체 시나리오) | Phase 최종 검증 시 |

### 5.2 테스트 필수 요건

| 요건 | 기준 | 비고 |
|------|------|------|
| **새 API 엔드포인트** | 반드시 테스트 파일 동반 | `tests/test_{module}.py` |
| **DB 스키마 변경** | 마이그레이션 + 롤백 테스트 | 순방향/역방향 모두 |
| **서비스 로직 변경** | 단위 테스트 추가/수정 | 핵심 분기 커버 |
| **새 UI 페이지** | 페이지 로드 + 기본 동작 확인 | E2E spec 또는 수동 확인 |
| **API-UI 연동** | API 호출 + 응답 렌더링 확인 | 통합 시나리오 포함 |
| **커버리지** | 변경 파일 기준 80% 이상 (백엔드) | `pytest-cov` 측정 |
| **회귀 테스트 (pytest)** | 기존 테스트 전체 통과 | `pytest tests/` |
| **회귀 테스트 (E2E)** | 기존 E2E spec 전체 통과 | `npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js` |
| **Dev API 회귀** | 기존 API 엔드포인트 HTTP 200 + 응답 구조 유지 | curl + JSON 파싱 |
| **메뉴 라우트 검사** | 전 메뉴 path HTTP 200 확인 (Phase 13-3 패턴) | curl 일괄 확인 |

### 5.3 테스트 실행 명령 표준

```bash
# L2+L3: 단위 + 통합 테스트
pytest tests/ -v --tb=short

# L2+L3 + 커버리지
pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=80

# L4: API 테스트 (특정 모듈)
pytest tests/test_admin_api.py -v

# L5: UI 동작 테스트 (특정 페이지)
npx playwright test e2e/smoke.spec.js

# L6: E2E 테스트 (Phase 전체)
npx playwright test e2e/phase-X-Y.spec.js

# L6: E2E 회귀 테스트 (기존 Phase spec 전체 실행)
npx playwright test e2e/smoke.spec.js e2e/phase-12-qc.spec.js \
  e2e/phase-13-menu-user.spec.js e2e/phase-13-menu-admin-knowledge.spec.js \
  e2e/phase-13-menu-cross.spec.js

# L6: webtest 스크립트 사용 (E2E spec 있는 Phase)
python3 scripts/webtest.py X-Y start

# Dev API 검사: 전 메뉴 path HTTP 200 일괄 확인
# 실제 등록 라우트는 backend/main.py _HTML_ROUTES 참조
for path in /dashboard /search /knowledge /reason /ask /logs \
  /admin/labels /admin/groups /admin/approval \
  /admin/chunk-labels /admin/chunk-create /admin/statistics \
  /admin/settings/presets /admin/settings/templates \
  /admin/settings/rag-profiles /admin/settings/policy-sets \
  /admin/settings/audit-logs \
  /knowledge-admin /knowledge-detail \
  /knowledge-label-matching /knowledge-relation-matching; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001${path}")
  echo "${path}: ${code}"
done

# Dev API 검사: 주요 API 엔드포인트 상태 확인
curl -s http://localhost:8001/health | python3 -c "import sys,json; print(json.load(sys.stdin))"
curl -s http://localhost:8001/api/labels | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'labels: {len(d)}개')" 2>/dev/null
```

### 5.4 테스트 리포트 형식

```
[TEST_REPORT]
Phase: X-Y
Domain: [BE | FE | FS]
Level: L2 (단위 테스트)
Total: 45
Passed: 43
Failed: 2
Skipped: 0
Coverage: 82% (backend only)
Frontend Check: 페이지 로드 OK, 콘솔 에러 0건
Failed Tests:
  - test_admin_api::test_create_template → AssertionError
  - test_reasoning_api::test_stream_cancel → TimeoutError
Verdict: FAIL (2 failures)
Reported by: tester (via SendMessage)
```

---

## 6. 프론트엔드 구현 원칙

### 6.1 기본 원칙 (FRONTEND.md Charter 기반)

| 원칙 | 설명 |
|------|------|
| **On-Premise** | 외부 CDN 절대 금지, 모든 라이브러리 로컬 배치 (`web/public/libs/`) |
| **Vanilla JS ESM** | 프레임워크 없음, ES Modules 기반 import/export |
| **결함 제로** | innerHTML 사용 시 반드시 `esc()` 이스케이프 적용 |
| **사용자 동선** | 관리자 업무 흐름에 최적화된 메뉴 단위 모듈화 |
| **시각적 일관성** | Bootstrap 기반 디자인 시스템 준수 |

### 6.2 프론트엔드 수정 시 체크리스트

`frontend-dev`가 코드 작성 시, `verifier`가 검증 시 확인할 항목:

- [ ] 외부 CDN 참조 없음 (cdn.jsdelivr.net 등)
- [ ] ESM import/export 패턴 사용 (`type="module"`)
- [ ] `window` 전역 객체에 함수 할당 금지 (기존 것 제외)
- [ ] `innerHTML` 사용 시 `esc()` 적용 또는 `textContent` 사용
- [ ] 기존 컴포넌트 재사용 (`layout-component.js`, `header-component.js`)
- [ ] API 호출 시 에러 핸들링 (try-catch + 사용자 메시지)
- [ ] 페이지 로드 시 콘솔 에러 없음

---

## 6.5 Task 문서 생성 표준

### 6.5.1 Task 문서 생성 절차 (TASK_SPEC)

워크플로우 Step 2.5(TASK_SPEC) 진입 시, todo-list 기반으로 Task별 실행 계획 문서를 일괄 생성한다.

| 항목 | 내용 |
|------|------|
| **트리거** | PLAN_REVIEW 통과 후 (또는 `[task-x-y:make]` 명령) |
| **입력** | `docs/phases/phase-X-Y/phase-X-Y-todo-list.md` |
| **출력** | `docs/phases/phase-X-Y/tasks/task-X-Y-N-{topic}.md` (todo-list Task 수만큼) |
| **참조 규칙** | `docs/rules/ai/references/ai-rule-task-creation.md` |

### 6.5.2 Task 문서 필수 구조

```
# Task X-Y-N: <Task 명>

**우선순위**: X-Y 내 N순위
**예상 작업량**: <todo-list에서 추출>
**의존성**: <todo-list에서 추출>
**담당 팀원**: <backend-dev | frontend-dev | tester>
**상태**: 대기

§1. 개요 (목표)
§2. 파일 변경 계획 (신규 생성 / 수정 대상 파일 목록)
§3. 작업 체크리스트 (완료 기준 = Done Definition)
§4. (선택) 참조·비고
```

### 6.5.3 Task 문서 파일명 규칙

| 패턴 | 예시 |
|------|------|
| `task-X-Y-N-{topic}.md` | `task-13-4-1-access-log.md` |
| topic = Task 명에서 유도한 kebab-case | "True Streaming" → `true-streaming` |

### 6.5.4 Task 문서 검증 기준

- [ ] todo-list Task 수 == tasks/ 디렉토리 문서 수
- [ ] Task ID·Task 명이 todo-list와 일치
- [ ] §3 작업 체크리스트가 todo-list 해당 블록과 대응
- [ ] 기반 문서 링크(plan, todo-list) 존재
- [ ] **담당 팀원**이 도메인에 맞게 지정됨

---

## 7. 산출물 저장 위치

| 산출물 | 경로 | 작성 주체 |
|--------|------|----------|
| Phase 상태 | `docs/phases/phase-X-Y/phase-X-Y-status.md` | Team Lead |
| Phase 계획 | `docs/phases/phase-X-Y/phase-X-Y-plan.md` | Team Lead (planner 결과 기반) |
| Phase Todo | `docs/phases/phase-X-Y/phase-X-Y-todo-list.md` | Team Lead (planner 결과 기반) |
| Task 문서 | `docs/phases/phase-X-Y/tasks/task-X-Y-N-{topic}.md` | Team Lead |
| 검증 리포트 | `docs/phases/phase-X-Y/phase-X-Y-verification-report.md` | Team Lead (verifier 결과 기반) |
| Backend 코드 | `backend/`, `tests/`, `scripts/` | `backend-dev` |
| Frontend 코드 | `web/`, `e2e/` | `frontend-dev` |
| Backend 테스트 | `tests/test_{module}.py` | `backend-dev` |
| E2E 스펙 | `e2e/phase-X-Y.spec.js` | `frontend-dev` |
| E2E 실행 리포트 | `docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md` | Team Lead |
| 회귀 시나리오 | `docs/devtest/scenarios/phase-X-Y-regression-scenarios.md` | Team Lead |
| 최종 요약 | `docs/phases/phase-X-Y/phase-X-Y-final-summary.md` | Team Lead |

---

## 8. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| Leader Charter | Team Lead 역할 | `docs/rules/role/LEADER.md` |
| Backend Charter | Backend Developer 역할 | `docs/rules/role/BACKEND.md` |
| Frontend Charter | Frontend Developer 역할 | `docs/rules/role/FRONTEND.md` |
| QA Charter | Verifier/Tester 역할 | `docs/rules/role/QA.md` |
| 에이전트 프롬프트 | Agent 상세 프롬프트 | `docs/rules/prompts/agent-system-prompts.md` |
| 검증 템플릿 | Verification report 형식 | `docs/rules/templates/verification-report-template.md` |
| 실행 워크플로우 | 전체 실행 순서 | `docs/rules/ai-execution-workflow.md` |
| 통합 테스트 가이드 | 테스트 작성법 | `docs/devtest/integration-test-guide.md` |
| Task 생성 규칙 | Task 문서 생성·명명·검증 | `docs/rules/ai/references/ai-rule-task-creation.md` |
| Task 검사 규칙 | Task 완료 검사·산출물 | `docs/rules/ai/references/ai-rule-task-inspection.md` |
| Plan·Todo 생성 규칙 | Phase plan/todo 생성 순서 | `docs/rules/ai/references/ai-rule-phase-plan-todo-generation.md` |

---

## 9. 버전 히스토리

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초안 작성 (백엔드 전용) | Claude Code (Backend & Logic Expert) |
| 2.0 | 2026-02-09 | 프론트엔드 구조 추가, 보안/검증 기준 분리, 공통 AI 팀 언어로 전환 | Claude Code (Backend & Logic Expert) |
| 3.0 | 2026-02-15 | Claude Code 내부 에이전트 팀 전환 | Claude Code (Backend & Logic Expert) |
| 3.1 | 2026-02-16 | E2E 회귀/Dev API 회귀/메뉴 라우트 검사 추가 | Claude Code (Backend & Logic Expert) |
| 3.2 | 2026-02-16 | §6.5 Task 문서 생성 표준 신규 추가 | Claude Code (Backend & Logic Expert) |
| 4.0 | 2026-02-16 | **Agent Teams 전환**: TeamCreate/SendMessage/TaskList 기반 팀 운영으로 전면 개편. Backend Developer·Frontend Developer를 general-purpose 에이전트로 승격 | Claude Code (Backend & Logic Expert) |
| 4.1 | 2026-02-16 | Hub-and-Spoke 통신 모델 (Peer DM 제거). Team Lead 코드 수정 금지. 모델 지정: planner=opus, 나머지=sonnet | Claude Code (Backend & Logic Expert) |
| 4.2 | 2026-02-16 | §2.4.1 도메인별 편집 원칙 신설 (EDIT-1~5). 지연 스폰 원칙 추가 | Claude Code (Backend & Logic Expert) |
