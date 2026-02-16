# AI Team — Project SSOT

**버전**: 3.0
**최종 수정**: 2026-02-16

---

## 1. 프로젝트 정의

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Personal AI Brain v3 |
| **목적** | 로컬 설치형 개인 AI 브레인 — 문서 벡터화, 의미 검색, AI 응답, 지식 구조화, Reasoning |
| **배포 형태** | Docker Compose (On-Premise, 폐쇄망 동작 필수) |
| **현재 Phase** | Phase 13 완료, Phase 14 계획 수립 대기 |

---

## 2. 팀 구성

### 2.1 Claude Code 내부 에이전트 팀 구조

```
┌───────────────────────────────────────────────────────────────┐
│            Orchestrator + Backend Builder (메인 세션)           │
│  Charter: LEADER.md + BACKEND.md                              │
│  역할: 워크플로우 지휘, 상태 관리, 판정, 코드 편집 (BE+FE)    │
│  도구: Edit, Write, Read, Glob, Grep, Bash, Task tool         │
└──┬──────────┬──────────────┬──────────────┬───────────────────┘
   │          │              │              │
┌──▼───┐ ┌───▼──────────┐ ┌─▼──────────┐ ┌▼─────────────┐
│Plan- │ │Frontend      │ │Verifier    │ │Tester        │
│ner   │ │Analyzer      │ │            │ │              │
│      │ │              │ │            │ │              │
│sub-  │ │subagent_type:│ │subagent_   │ │subagent_     │
│agent │ │"Explore"     │ │type:       │ │type:         │
│_type:│ │              │ │"Explore"   │ │"Bash"        │
│"Plan"│ │Charter:      │ │            │ │              │
│또는  │ │FRONTEND.md   │ │Charter:    │ │Charter:      │
│"Exp- │ │              │ │QA.md       │ │QA.md         │
│lore" │ │              │ │            │ │              │
└──────┘ └──────────────┘ └────────────┘ └──────────────┘
```

### 2.2 역할-실행 매핑

| 역할 | Charter | Task tool `subagent_type` | 코드 편집 |
|------|---------|:------------------------:|:--------:|
| **Orchestrator** | `LEADER.md` | — (메인 세션 직접 실행) | O |
| **Backend Builder** | `BACKEND.md` | — (메인 세션 직접 실행) | O |
| **Planner** | — (고유) | `Plan` 또는 `Explore` | X |
| **Frontend Analyzer** | `FRONTEND.md` | `Explore` | X |
| **Verifier** | `QA.md` | `Explore` | X |
| **Tester** | `QA.md` | `Bash` | X |

**코드 편집 원칙**: `Edit`, `Write` 도구는 메인 세션에서만 사용 가능하다. 서브에이전트는 분석/검증/테스트만 수행하고 결과를 반환하며, 메인 세션이 결과를 바탕으로 코드를 작성한다.

### 2.3 역할별 상세

#### Orchestrator + Backend Builder (메인 세션)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/LEADER.md` + `docs/rules/role/BACKEND.md` |
| **핵심 역할** | 워크플로우 지휘 + 코드 구현 (Backend/Frontend 모두) |
| **권한** | 파일 읽기/쓰기/편집, Git, Bash, 서브에이전트 생성 |
| **책임** | Phase 상태 관리, 판정 결정(PASS/FAIL/PARTIAL), API/DB/서비스 로직 구현, 프론트엔드 구현, 이슈 해결 |

메인 세션이 Orchestrator와 Backend Builder를 겸임하는 이유: 서브에이전트는 코드 수정 불가하므로 모든 코드 구현(백엔드+프론트엔드)은 메인 세션이 담당한다. 다만 구현 전에 해당 도메인의 서브에이전트 분석 결과를 반드시 참조한다.

#### Planner Agent (서브에이전트)

| 항목 | 내용 |
|------|------|
| **실행 방법** | `Task tool` → `subagent_type: "Plan"` 또는 `"Explore"` |
| **핵심 역할** | 요구사항 분석, 영향 범위 탐색, 계획 수립 |
| **권한** | 파일 읽기, 검색 (Glob, Grep, Read) — 쓰기 권한 없음 |
| **입력** | master-plan, navigation, 이전 Phase summary |
| **출력** | 계획 분석 결과 (Task 분해, 완료 기준, 리스크) |

#### Frontend Analyzer (서브에이전트)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/FRONTEND.md` |
| **실행 방법** | `Task tool` → `subagent_type: "Explore"` |
| **핵심 역할** | UI/UX 분석, 기존 패턴 조사, 구현 방향 제시 |
| **권한** | 파일 읽기, 검색 — 쓰기 권한 없음 |
| **원칙** | On-Premise 최적화, CDN 금지, Vanilla JS ESM |

**서브에이전트 호출 예시 (Frontend 분석)**:
```
Task tool:
  subagent_type: "Explore"
  prompt: "docs/rules/role/FRONTEND.md의 페르소나를 적용하여 분석하라.
           대상: web/public/js/admin/settings/ 디렉토리
           확인 항목:
           1. ESM import/export 패턴 준수 여부
           2. window 전역 객체 의존 여부
           3. 외부 CDN 참조 유무
           4. 기존 컴포넌트 패턴 (layout-component, header-component)
           5. 새 페이지 추가 시 따라야 할 HTML/JS/CSS 구조
           코드를 수정하지 말고 분석 결과만 반환하라."
```

#### Verifier (서브에이전트)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/QA.md` |
| **실행 방법** | `Task tool` → `subagent_type: "Explore"` |
| **핵심 역할** | 코드 리뷰, 품질 게이트, 보안 점검 |
| **권한** | 파일 읽기, 검색 — 쓰기 권한 없음 |
| **입력** | 변경 파일 목록, 완료 기준 |
| **출력** | 검증 결과 (PASS/FAIL/PARTIAL + 이슈 목록) |

**서브에이전트 호출 예시 (풀스택 검증)**:
```
Task tool:
  subagent_type: "Explore"
  prompt: "docs/rules/role/QA.md의 페르소나를 적용하여 검증하라.
           변경 파일:
           [Backend]
           - backend/routers/admin/schema_crud.py
           - backend/models/admin_models.py
           [Frontend]
           - web/public/js/admin/settings/templates.js
           - web/src/pages/admin/settings/templates.html
           검증 항목:
           [Backend] 타입 힌트, 에러 핸들링, SQL Injection, API 호환성
           [Frontend] ESM 준수, innerHTML XSS, CDN 미사용, JSDoc 존재
           [공통] 완료 기준 충족 여부: [기준 목록]
           코드를 수정하지 말고 검증 결과만 반환하라."
```

#### Tester (서브에이전트)

| 항목 | 내용 |
|------|------|
| **Charter** | `docs/rules/role/QA.md` |
| **실행 방법** | `Task tool` → `subagent_type: "Bash"` |
| **핵심 역할** | 테스트 실행, 커버리지 분석, 결함 문서화 |
| **권한** | Bash 명령 실행 (pytest, playwright 등) |
| **입력** | 테스트 파일 경로, 테스트 명령, 기대 결과 |
| **출력** | 테스트 결과, 커버리지, 실패 목록 |

### 2.4 서브에이전트 운용 원칙

| 원칙 | 설명 |
|------|------|
| **Charter 장착** | 서브에이전트 호출 시 해당 역할의 Charter 경로를 프롬프트에 포함 |
| **독립 실행** | 의존성 없는 작업은 병렬 실행 (Verifier + Tester 동시 등) |
| **읽기 전용** | 서브에이전트는 코드 수정 불가, 분석/검증/테스트만 수행 |
| **결과 반환** | 서브에이전트는 메인 세션에 텍스트 결과만 반환 |
| **코드 변경** | 모든 코드 편집은 반드시 메인 세션(Orchestrator)이 수행 |
| **컨텍스트 격리** | 서브에이전트는 자체 컨텍스트 윈도우 사용 (메인 세션 소비 없음) |
| **모델 선택** | 빠른 탐색: `haiku`, 심층 분석: `sonnet`, 복잡한 판단: `opus` |

### 2.5 병렬 실행 패턴

```
# 패턴 1: 백엔드/프론트엔드 사전 분석 병렬
Main → [Backend Analyzer (API 영향 분석)]  병렬
     → [Frontend Analyzer (UI 영향 분석)]  병렬
     ← 합산 후 구현 순서 결정

# 패턴 2: 풀스택 검증 + 테스트 병렬
Main → [Verifier (백엔드+프론트 코드 리뷰)] 병렬
     → [Tester (pytest + Playwright)]       병렬
     ← 두 결과 수집 후 종합 판정

# 패턴 3: 구현 후 즉시 검증
Main → 코드 작성 완료 (백엔드 또는 프론트)
     → [Verifier (해당 도메인 검증)] 실행
     ← 결과에 따라 수정 또는 다음 단계
```

---

## 3. Task 도메인 분류

각 Task는 도메인을 명시하여 적절한 역할이 분석/구현/검증한다.

| 도메인 태그 | 설명 | 구현 주체 | 분석 서브에이전트 |
|-----------|------|:--------:|:---------------:|
| `[BE]` | 백엔드 (API, 서비스, 미들웨어) | 메인 세션 (BACKEND.md) | Backend Analyzer |
| `[DB]` | 데이터베이스 (스키마, 마이그레이션) | 메인 세션 (BACKEND.md) | Backend Analyzer |
| `[FE]` | 프론트엔드 (HTML, JS, CSS) | 메인 세션 (FRONTEND.md 참조) | Frontend Analyzer |
| `[FS]` | 풀스택 (백엔드 + 프론트 연동) | 메인 세션 (양쪽 참조) | 양쪽 병렬 분석 |
| `[TEST]` | 테스트 전용 (테스트 코드 작성) | 메인 세션 | Tester |
| `[INFRA]` | 인프라 (Docker, 환경변수, CI) | 메인 세션 | — |

**Todo-list 작성 예시**:
```markdown
- [ ] Task X-Y-1: [BE] Admin API CRUD 구현 (Owner: Backend Builder)
- [ ] Task X-Y-2: [DB] Admin 테이블 마이그레이션 (Owner: Backend Builder)
- [ ] Task X-Y-3: [FE] Admin 설정 UI 페이지 구현 (Owner: Frontend Analyzer → 메인 세션)
- [ ] Task X-Y-4: [FS] API-UI 연동 및 데이터 바인딩 (Owner: Backend+Frontend)
- [ ] Task X-Y-5: [TEST] 통합 테스트 시나리오 작성/실행 (Owner: Tester)
```

---

## 4. 품질 게이트 정의

### 4.1 게이트 구조

```
[G1: Plan Review]     Planner 분석 → Orchestrator 검토
        ↓
[G2: Code Review]     Verifier가 백엔드+프론트 코드 검증
        ↓
[G3: Test Gate]       Tester가 테스트 실행 + 커버리지 확인
        ↓
[G4: Final Gate]      Orchestrator가 G2+G3 종합 판정
```

### 4.2 게이트별 통과 기준

| 게이트 | 백엔드 기준 | 프론트엔드 기준 | 공통 기준 |
|--------|-----------|--------------|----------|
| **G1** | API Spec 확정, DB 스키마 정의 | 페이지 구조/동선 정의 | 완료 기준 명확, Task 3~7개, 리스크 식별 |
| **G2** | Critical 0건, ORM 사용, 타입 힌트, 에러 핸들링 | CDN 미사용, ESM 준수, innerHTML 미사용 또는 esc() 적용 | 보안 취약점 없음 |
| **G3** | pytest 전체 통과, 커버리지 ≥ 80% (변경 파일) | 페이지 로드 확인, 콘솔 에러 없음 | 회귀 테스트 통과 |
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
    → Orchestrator 판단:
      - 기능 차단 → FAIL
      - 개선 사항 → Technical Debt 등록 후 진행
```

---

## 5. 테스트 전략 (강화)

### 5.1 테스트 레벨

| 레벨 | 대상 | 실행 주체 | 도구 | 실행 시점 |
|------|------|----------|------|----------|
| **L1: 정적 분석** | BE+FE | Verifier | mypy, ruff / ESLint (코드 리뷰) | 매 구현 완료 후 |
| **L2: 단위 테스트** | BE | Tester | pytest | 매 구현 완료 후 |
| **L3: 통합 테스트** | BE | Tester | pytest (integration markers) | Task 단위 완료 후 |
| **L4: API 테스트** | BE+FE | Tester | pytest + httpx/TestClient | Phase 단위 완료 후 |
| **L5: UI 동작 테스트** | FE | Tester | Playwright 또는 브라우저 확인 | Phase 단위 완료 후 |
| **L6: E2E 테스트** | FS | Tester | Playwright (전체 시나리오) | Phase 최종 검증 시 |

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

프론트엔드 코드를 변경할 때 Verifier가 확인할 항목:

- [ ] 외부 CDN 참조 없음 (cdn.jsdelivr.net 등)
- [ ] ESM import/export 패턴 사용 (`type="module"`)
- [ ] `window` 전역 객체에 함수 할당 금지 (기존 것 제외)
- [ ] `innerHTML` 사용 시 `esc()` 적용 또는 `textContent` 사용
- [ ] 기존 컴포넌트 재사용 (`layout-component.js`, `header-component.js`)
- [ ] API 호출 시 에러 핸들링 (try-catch + 사용자 메시지)
- [ ] 페이지 로드 시 콘솔 에러 없음

---

## 7. 산출물 저장 위치

| 산출물 | 경로 | 작성 주체 |
|--------|------|----------|
| Phase 상태 | `docs/phases/phase-X-Y/phase-X-Y-status.md` | Orchestrator |
| Phase 계획 | `docs/phases/phase-X-Y/phase-X-Y-plan.md` | Orchestrator (Planner 결과 기반) |
| Phase Todo | `docs/phases/phase-X-Y/phase-X-Y-todo-list.md` | Orchestrator (Planner 결과 기반) |
| Task 문서 | `docs/phases/phase-X-Y/tasks/task-X-Y-N-{topic}.md` | Orchestrator |
| 검증 리포트 | `docs/phases/phase-X-Y/phase-X-Y-verification-report.md` | Orchestrator (Verifier 결과 기반) |
| Backend 테스트 | `tests/test_{module}.py` | Orchestrator |
| E2E 스펙 | `e2e/phase-X-Y.spec.js` | Orchestrator |
| E2E 실행 리포트 | `docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md` | Orchestrator |
| 회귀 시나리오 | `docs/devtest/scenarios/phase-X-Y-regression-scenarios.md` | Orchestrator |
| 최종 요약 | `docs/phases/phase-X-Y/phase-X-Y-final-summary.md` | Orchestrator |

---

## 8. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| Leader Charter | Orchestrator 역할 | `docs/rules/role/LEADER.md` |
| Backend Charter | 백엔드 역할 | `docs/rules/role/BACKEND.md` |
| Frontend Charter | 프론트엔드 역할 | `docs/rules/role/FRONTEND.md` |
| QA Charter | QA/테스트 역할 | `docs/rules/role/QA.md` |
| 에이전트 프롬프트 | Agent 상세 프롬프트 | `docs/rules/prompts/agent-system-prompts.md` |
| 검증 템플릿 | Verification report 형식 | `docs/rules/templates/verification-report-template.md` |
| 실행 워크플로우 | 전체 실행 순서 | `docs/rules/ai-execution-workflow.md` |
| 통합 테스트 가이드 | 테스트 작성법 | `docs/devtest/integration-test-guide.md` |

---

## 9. 버전 히스토리

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초안 작성 (백엔드 전용) | Claude Code (Backend & Logic Expert) |
| 2.0 | 2026-02-09 | 프론트엔드 구조 추가, 보안/검증 기준 분리, 공통 AI 팀 언어로 전환 | Claude Code (Backend & Logic Expert) |
| 3.0 | 2026-02-15 | Claude Code 내부 에이전트 팀 전환: 외부 AI 참조(Cursor/Gemini/Copilot) 제거, Task tool subagent_type 기반 구조로 재구성, Backend Builder를 Orchestrator에 통합, 섹션 6.3(전담 AI Gemini) 삭제 | Claude Code (Backend & Logic Expert) |
| 3.1 | 2026-02-16 | §5.2 테스트 필수 요건에 E2E 회귀/Dev API 회귀/메뉴 라우트 검사 추가, §5.3 테스트 실행 명령에 E2E 회귀·Dev API 검사 명령 추가, §7 산출물에 E2E 실행 리포트·회귀 시나리오 추가. Phase 13-3 E2E 패턴 반영 | Claude Code (Backend & Logic Expert) |
