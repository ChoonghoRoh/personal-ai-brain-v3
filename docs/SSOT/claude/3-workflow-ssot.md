# AI Team — Workflow SSOT

**버전**: 3.2
**최종 수정**: 2026-02-16

---

## 0. ENTRYPOINT 정의

Phase 실행의 **단일 진입점**은 `phase-X-Y-status.md` 파일이다.

### ENTRYPOINT 규칙

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **ENTRY-1** | 단일 진입점 | 모든 Phase 작업은 `docs/phases/phase-X-Y/phase-X-Y-status.md`를 먼저 읽는 것으로 시작 |
| **ENTRY-2** | 상태 기반 분기 | `current_state` 값에 따라 다음 행동을 결정 (섹션 7.1 참조) |
| **ENTRY-3** | SSOT 버전 확인 | 진입 시 `ssot_version` 필드와 현재 SSOT 버전의 일치 여부를 확인 |
| **ENTRY-4** | Blocker 우선 확인 | `blockers` 배열이 비어있지 않으면 다른 작업보다 Blocker 해결을 우선 |
| **ENTRY-5** | 진입점 외 직접 시작 금지 | status 파일을 읽지 않고 Task 구현을 바로 시작하는 것을 금지 |

### ENTRYPOINT 플로우

```
세션 시작 / Phase 재개
  │
  ▼
[1] SSOT 로딩 (0→1→2→3) ← FRESH-1 규칙
  │
  ▼
[2] phase-X-Y-status.md 읽기 ← ENTRY-1 (단일 진입점)
  │
  ▼
[3] ssot_version 확인 ← ENTRY-3
  │
  ├── 불일치 → SSOT 리로드 후 재진입
  │
  ▼
[4] blockers 확인 ← ENTRY-4
  │
  ├── 비어있지 않음 → Blocker 해결 우선
  │
  ▼
[5] current_state 기반 다음 행동 결정 ← ENTRY-2
  │
  ▼
[6] 워크플로우 실행
```

---

## 1. 워크플로우 상태 머신

### 1.1 상태 정의

| 상태 코드 | 상태명 | 설명 | 진입 조건 |
|----------|--------|------|----------|
| `IDLE` | 대기 | Phase 미시작 | 초기 상태 |
| `PLANNING` | 계획 | 요구사항 분석, Task 분해 (BE+FE 도메인 구분) | Phase 시작 명령 |
| `PLAN_REVIEW` | 계획 검토 | Planner 결과 검증 | PLANNING 완료 |
| `TASK_SPEC` | Task 내역서 작성 | Task별 실행 계획 문서(task-X-Y-N.md) 생성 | PLAN_REVIEW 통과 |
| `BUILDING` | 구현 | 코드 작성 (백엔드/프론트엔드/풀스택) | TASK_SPEC 완료 |
| `VERIFYING` | 검증 | 코드 리뷰 (도메인별 기준 적용) | BUILDING 완료 (Task 단위) |
| `TESTING` | 테스트 | 테스트 실행 (도메인별 레벨 적용) | VERIFYING 통과 |
| `INTEGRATION` | 통합 테스트 | Phase 전체 통합 검증 (API↔UI 연동 포함) | 모든 Task TESTING 통과 |
| `E2E` | E2E 테스트 | 사용자 시나리오 기반 전체 테스트 | INTEGRATION 통과 |
| `BLOCKED` | 차단 | Blocker 이슈 발생 | 어떤 상태에서든 진입 가능 |
| `REWINDING` | 리와인드 | 이전 상태로 롤백 중 | FAIL 판정 시 |
| `DONE` | 완료 | Phase 종료 | E2E 통과 + Final Gate PASS |

### 1.2 상태 전이 다이어그램

```
IDLE
  │
  ▼
PLANNING ──────────────────────────────────────┐
  │                                            │
  ▼                                            │
PLAN_REVIEW ─── FAIL ──► REWINDING ──► PLANNING│
  │                                            │
  │ PASS                                       │
  ▼                                            │
TASK_SPEC (Task 내역서 일괄 생성)              │
  │  task-X-Y-N-<topic>.md × N건              │
  ▼                                            │
BUILDING (Task N) [BE/FE/FS]                   │
  │                                            │
  ▼                                            │
VERIFYING ───── FAIL ──► REWINDING ──► BUILDING│
  │                                            │
  │ PASS                                       │
  ▼                                            │
TESTING ─────── FAIL ──► REWINDING ──► BUILDING│
  │                                            │
  │ PASS                                       │
  ▼                                            │
  ├── 다음 Task 있음? ──► BUILDING (Task N+1)  │
  │                                            │
  │ 모든 Task 완료                              │
  ▼                                            │
INTEGRATION ─── FAIL ──► REWINDING ──► BUILDING│
  │                                            │
  │ PASS                                       │
  ▼                                            │
E2E ──────────── FAIL ──► REWINDING ──► BUILDING
  │
  │ PASS → E2E 리포트 + Verification Report 작성
  ▼
DONE (G4 Final Gate)

※ 어떤 상태에서든 BLOCKED로 전이 가능
  BLOCKED → 이슈 해결 → 이전 상태로 복귀
  BLOCKED (사유: "SSOT 변경 필요") → SSOT Lock 프로세스 → 복귀
```

### 1.3 상태 전이 규칙

| 현재 상태 | 이벤트 | 다음 상태 | 조건 |
|----------|--------|----------|------|
| IDLE | Phase 시작 | PLANNING | SSOT 리로드 완료 (FRESH-1) |
| PLANNING | Planner 완료 | PLAN_REVIEW | plan + todo-list 생성됨 (도메인 태그 포함) |
| PLAN_REVIEW | 검토 통과 | TASK_SPEC | 완료 기준 명확, Task 3~7개, 도메인 분류 완료 |
| TASK_SPEC | 내역서 생성 완료 | BUILDING | 모든 Task에 task-X-Y-N.md 생성됨 |
| PLAN_REVIEW | 검토 실패 | REWINDING→PLANNING | 완료 기준 불명확 또는 범위 초과 |
| BUILDING | 구현 완료 | VERIFYING | Task 단위 코드 작성 완료 |
| VERIFYING | PASS | TESTING | 도메인별 Critical 0건 |
| VERIFYING | FAIL | REWINDING→BUILDING | Critical 또는 High 존재 |
| TESTING | PASS | BUILDING (다음 Task) 또는 INTEGRATION | 테스트 전체 통과 |
| TESTING | FAIL | REWINDING→BUILDING | 테스트 실패 |
| INTEGRATION | PASS (회귀+신규+연동) | E2E | Dev API 회귀 PASS + 현재 API PASS + 통합 연동 PASS |
| INTEGRATION | FAIL (회귀) | REWINDING→BUILDING | 기존 API 회귀 실패 — 변경사항에 의한 기존 기능 깨짐 |
| INTEGRATION | FAIL (신규) | REWINDING→BUILDING | 새/변경 API 실패 — 구현 결함 |
| INTEGRATION | FAIL (연동) | REWINDING→BUILDING | API↔UI 연동 실패 — 도메인 간 불일치 |
| E2E | PASS (회귀+신규) | DONE | 기존 E2E 회귀 PASS + 현재 E2E PASS + 리포트 작성 완료 |
| E2E | FAIL (회귀) | REWINDING→BUILDING | 기존 E2E 깨짐 — 변경사항에 의한 회귀 |
| E2E | FAIL (신규) | REWINDING→BUILDING | 현재 Phase E2E 실패 — 구현/셀렉터 결함 |
| BLOCKED | 이슈 해결 | (이전 상태) | Blocker 제거 |
| BLOCKED | SSOT 변경 완료 | (이전 상태) | SSOT 리로드 완료 (LOCK-3) |
| REWINDING | 롤백 완료 | (대상 상태) | — |

---

## 2. 상태 파일 (Status File)

### 2.1 파일 경로

```
docs/phases/phase-X-Y/phase-X-Y-status.md
```

### 2.2 상태 파일 스키마

```yaml
---
phase: "X-Y"
ssot_version: "3.0"                # 현재 참조 중인 SSOT 버전
ssot_loaded_at: "2026-02-15T10:00:00Z"  # SSOT 마지막 로딩 시각
current_state: "BUILDING"          # 상태 머신의 현재 상태
current_task: "X-Y-2"              # 현재 작업 중인 Task ID
current_task_domain: "[FE]"        # 현재 Task 도메인 태그
last_action: "Task X-Y-1 [BE] API 구현 완료"
last_action_result: "PASS"         # PASS | FAIL | PARTIAL | N/A
next_action: "Task X-Y-2 [FE] UI 페이지 구현 시작"
blockers: []                       # 차단 이슈 목록
rewind_target: null                # REWINDING 시 목표 상태
retry_count: 0                     # 현재 상태 재시도 횟수 (최대 3)
gate_results:                      # 품질 게이트 통과 기록
  G1_plan_review: null             # PASS | FAIL | null
  G2_code_review_be: null          # 백엔드 코드 리뷰
  G2_code_review_fe: null          # 프론트엔드 코드 리뷰
  G3_test_gate: null
  G4_final_gate: null
task_progress:                     # Task별 진행 현황
  X-Y-1: { status: "DONE", domain: "[BE]" }
  X-Y-2: { status: "IN_PROGRESS", domain: "[FE]" }
  X-Y-3: { status: "PENDING", domain: "[FS]" }
error_log: []                      # 누적 에러 기록
last_updated: "2026-02-15T10:30:00Z"
---
```

### 2.3 상태 파일 관리 규칙

| 규칙 | 설명 |
|------|------|
| **쓰기 권한** | Orchestrator(메인 세션)만 상태 파일 수정 가능 |
| **읽기 권한** | 모든 서브에이전트가 읽기 가능 |
| **업데이트 시점** | 상태 전이 시 즉시 업데이트 |
| **게이트 기록** | 각 게이트 통과 시 결과 기록 (백엔드/프론트 분리) |
| **에러 누적** | 에러 발생 시 `error_log`에 추가 (삭제 금지) |
| **도메인 태그** | 모든 Task에 도메인 태그 필수 ([BE], [FE], [FS], [DB], [TEST], [INFRA]) |
| **SSOT 버전 동기화** | SSOT 리로드 시 `ssot_version`과 `ssot_loaded_at` 갱신 |

---

## 3. 워크플로우 실행 순서

### 3.1 Phase 전체 흐름

```
Step 1: PLANNING
  ├── Planner 서브에이전트 실행 (Task tool → subagent_type: "Plan")
  ├── master-plan, navigation 분석
  ├── 백엔드/프론트엔드 영향 범위 식별
  ├── 결과: Task 분해 (도메인 태그 포함), 완료 기준, 리스크
  └── 산출물: plan 분석 결과 (메인 세션에 반환)

Step 2: PLAN_REVIEW (G1)
  ├── Orchestrator가 Planner 결과 검토
  ├── 확인:
  │   - 완료 기준 명확성
  │   - Task 분해 적절성 (도메인별 균형)
  │   - 리스크 대응
  │   - 프론트엔드 Task에 UI 동선/구조 기술 여부
  ├── PASS → plan.md + todo-list.md 작성 (도메인 태그 포함), TASK_SPEC으로 전이
  └── FAIL → REWINDING→PLANNING

Step 2.5: TASK_SPEC (Task 내역서 일괄 생성)
  ├── todo-list 기반으로 Task별 실행 계획 문서 생성
  │   참조: docs/rules/ai/references/ai-rule-task-creation.md
  ├── 각 Task에 대해 task-X-Y-N-<topic>.md 생성:
  │   - §1 개요 (목표)
  │   - §2 파일 변경 계획 (신규 생성 / 수정 대상 파일 목록)
  │   - §3 작업 체크리스트 (완료 기준 = Done Definition)
  │   - §4 참조·비고 (선택)
  ├── 저장 위치: docs/phases/phase-X-Y/tasks/
  ├── 누락 검사: todo-list Task 수 == task 문서 수
  └── 완료 → BUILDING으로 전이

Step 3: BUILDING (Task 단위 반복)
  ├── task-X-Y-N.md (내역서)를 읽고 해당 Task의 구현 범위·체크리스트 확인
  ├── Task 도메인에 따른 구현:
  │   [BE/DB] → BACKEND.md 기준으로 구현
  │   [FE]    → FRONTEND.md 기준으로 구현 (필요 시 Frontend Analyzer 선행)
  │   [FS]    → 백엔드 먼저, 프론트 후속 (또는 병렬 분석)
  ├── Task 완료 후 → task-X-Y-N.md 체크리스트 갱신 → VERIFYING으로 전이
  └── 산출물: 코드 변경, task-X-Y-N.md 체크리스트 완료

Step 4: VERIFYING (G2 - Task 단위)
  ├── Verifier 서브에이전트 실행 (Task tool → subagent_type: "Explore")
  ├── 도메인별 검증 기준 적용:
  │   [BE] → 타입 힌트, 에러 핸들링, ORM, 보안
  │   [FE] → CDN 미사용, ESM, innerHTML XSS, 컴포넌트 재사용
  │   [FS] → 백엔드 + 프론트엔드 기준 모두 적용
  ├── PASS → TESTING으로 전이
  └── FAIL → REWINDING→BUILDING (수정 후 재검증)

Step 5: TESTING (G3 - Task 단위)
  ├── Tester 서브에이전트 실행 (Task tool → subagent_type: "Bash")
  ├── 도메인별 테스트:
  │   [BE] → pytest (L2 단위, L3 통합)
  │   [FE] → 페이지 로드 확인, 콘솔 에러 확인 (L5)
  │   [FS] → pytest + API↔UI 연동 확인 (L4)
  ├── PASS → 다음 Task(BUILDING) 또는 INTEGRATION
  └── FAIL → REWINDING→BUILDING (수정 후 재테스트)

  ※ Step 4 + Step 5 병렬 실행 가능:
    Verifier와 Tester를 동시에 실행하여 시간 단축

Step 6: INTEGRATION (Dev API 검사 + 통합 테스트)
  ├── 6-A. Dev API 회귀 검사 — 기존 Phase 엔드포인트 정상 동작 확인
  │   ├── 대상: 이전 Phase에서 구현한 API 엔드포인트 전체
  │   ├── 방법: curl + HTTP 상태 코드 + JSON 응답 구조 검증
  │   │   ```bash
  │   │   # 예: 전체 API 헬스체크
  │   │   curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health
  │   │   # 예: API 응답 구조 검증
  │   │   curl -s http://localhost:8001/api/labels | python3 -c \
  │   │     "import sys,json; d=json.load(sys.stdin); assert isinstance(d,list)"
  │   │   ```
  │   ├── PASS → 6-B로 진행
  │   └── FAIL → REWINDING→BUILDING (회귀 결함 — 기존 기능 깨짐)
  │
  ├── 6-B. 현재 Phase API 검사 — 새/변경 엔드포인트 동작 확인
  │   ├── 대상: 현재 Phase에서 추가·수정한 엔드포인트
  │   ├── 방법: curl 호출 + 기대 응답 비교 (상태코드, 필드 존재, 값 범위)
  │   ├── PASS → 6-C로 진행
  │   └── FAIL → REWINDING→BUILDING (구현 결함 수정)
  │
  ├── 6-C. 통합 연동 검사
  │   ├── [BE] → API 연동, DB 정합성, 서비스 간 연계
  │   ├── [FE] → 페이지 간 네비게이션, 공유 컴포넌트 동작
  │   ├── [FS] → API 호출 → 응답 렌더링 → 사용자 인터랙션 전체 흐름
  │   ├── 페이지 로드 검사: 모든 HTML 라우트 HTTP 200 확인
  │   │   ```bash
  │   │   # Phase 13-3 패턴: 전 메뉴 path 일괄 확인
  │   │   for path in /dashboard /search /knowledge /reason /ask /logs \
  │   │     /admin/knowledge/chunks /admin/knowledge/labels ...; do
  │   │     code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001${path}")
  │   │     echo "${path}: ${code}"
  │   │   done
  │   │   ```
  │   ├── PASS → E2E로 전이
  │   └── FAIL → REWINDING→BUILDING (연동 결함 수정)
  │
  └── 회귀 분기 판정 기준:
      ├── 기존 API 응답 구조 변경 → E2 (High), REWINDING 필수
      ├── 기존 페이지 HTTP 404/500 → E1 (Blocker), BLOCKED 전이
      ├── 새 API만 실패 → E2 (High), 해당 Task로 REWINDING
      └── 연동 불일치 (API 응답 ↔ UI 기대값) → E2, REWINDING→BUILDING

Step 7: E2E (Playwright E2E 검사)
  ├── 7-A. 기존 E2E 회귀 실행 — 이전 Phase spec 파일 전체 실행
  │   ├── 대상: e2e/ 디렉토리의 기존 spec 파일들
  │   ├── 실행:
  │   │   ```bash
  │   │   # 기존 E2E 전체 회귀 (smoke + 이전 Phase)
  │   │   npx playwright test e2e/smoke.spec.js
  │   │   npx playwright test e2e/phase-12-qc.spec.js
  │   │   npx playwright test e2e/phase-13-menu-user.spec.js \
  │   │     e2e/phase-13-menu-admin-knowledge.spec.js \
  │   │     e2e/phase-13-menu-cross.spec.js
  │   │   ```
  │   ├── PASS → 7-B로 진행
  │   └── FAIL → REWINDING→BUILDING (회귀 결함 — 기존 E2E 깨짐)
  │       ├── 실패 spec 파일·테스트명 기록 (error_log)
  │       └── 원인 분석: 셀렉터 변경? DOM 구조 변경? API 응답 변경?
  │
  ├── 7-B. 현재 Phase E2E 실행 — 새 spec 파일 또는 대체 테스트
  │   ├── E2E spec 파일 확인: e2e/phase-X-Y.spec.js 존재 여부
  │   │   ├── 존재 → Playwright 실행
  │   │   │   ```bash
  │   │   │   npx playwright test e2e/phase-X-Y.spec.js
  │   │   │   # 또는 webtest 스크립트 사용
  │   │   │   python3 scripts/webtest.py X-Y start
  │   │   │   ```
  │   │   └── 미존재 → E2E spec 생성 또는 대체 테스트
  │   │       ├── 방법 1: E2E spec 생성 (기존 spec 참조)
  │   │       │   참조: docs/devtest/integration-test-guide.md §4
  │   │       ├── 방법 2: 대체 테스트 (curl API + HTTP 상태)
  │   │       │   참조: docs/webtest/phase-unit-user-test-guide.md §0
  │   │       └── 대체 테스트 사용 시 E2E 리포트에 반드시 기재
  │   ├── Phase 13-3 검증 패턴 (메뉴·헤더 관련 Phase 적용):
  │   │   ├── 1단계: 페이지 로드 (HTTP 200 + 콘텐츠 확인)
  │   │   ├── 2단계: 헤더 렌더링 (.container > header 가시성)
  │   │   └── 3단계: 활성 메뉴 하이라이트 (nav a.active 텍스트 일치)
  │   ├── PASS → E2E 리포트 작성 (Step 7.5)
  │   └── FAIL → REWINDING→BUILDING (E2E 결함 수정)
  │       ├── 실패 테스트 식별 → 관련 Task 역추적
  │       └── 셀렉터 오류 vs 기능 결함 구분
  │
  └── 회귀 분기 판정 기준:
      ├── 기존 E2E 실패 → E1 (Blocker), 신규 코드에 의한 회귀
      │   → 현재 Phase 변경사항 중 기존 기능에 영향을 준 부분 식별·수정
      ├── 새 E2E만 실패 → E2 (High), 해당 Task로 REWINDING
      ├── 셀렉터 불일치 → DOM 구조 변경 반영 (spec 수정, E3 수준)
      └── 전체 E2E 통과 + 시나리오 커버리지 100% → PASS

Step 7.5: E2E 리포트 작성
  ├── 7.5-A. Verification Report 작성
  │   ├── 참조 템플릿: docs/rules/templates/verification-report-template.md
  │   ├── 저장: docs/phases/phase-X-Y/phase-X-Y-verification-report.md
  │   └── 포함 내용:
  │       - §2 Syntax Check (BE/FE/DB)
  │       - §3 Logic Check (Task 완료 기준, API, UI, DB 정합성)
  │       - §4 Edge Case Check
  │       - §5 코드 오류 (Critical/High/Low)
  │       - §8.1 Integration Test 결과 (Dev API 검사 결과 포함)
  │       - §8.2 E2E Test 결과 (회귀 + 신규 E2E 결과 분리 기재)
  │       - §10 최종 판정 (PASS/FAIL/PARTIAL)
  │
  ├── 7.5-B. E2E 실행 결과 리포트 작성
  │   ├── 참조: docs/devtest/integration-test-guide.md §5 (리포트 규정)
  │   ├── 참조: docs/webtest/phase-unit-user-test-guide.md §0 (방안 A/B/C)
  │   ├── 저장: docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md
  │   └── 포함 내용:
  │       - E2E Spec 상태 (존재/부재, 대체 방법 사용 여부)
  │       - 회귀 E2E 결과 (기존 spec 실행 결과)
  │       - 신규 E2E 결과 (현재 Phase spec 실행 결과)
  │       - 시나리오 ↔ E2E 테스트 매핑 표 (Phase 13-3 패턴)
  │       - 실패 테스트 상세 (재현 조건, 원인 분석)
  │       - 해결된 이슈 / 미해결 이슈
  │
  ├── 7.5-C. Web User Test Report 작성 (해당 시)
  │   ├── 참조: docs/webtest/phase-unit-user-test-guide.md §5
  │   └── 저장: docs/webtest/phase-X-Y/reports/
  │
  └── 리포트 완료 → G4 Final Gate (Step 8)

Step 8: DONE (G4)
  ├── Orchestrator가 전체 결과 종합
  │   - G2_be + G2_fe 모두 PASS 확인
  │   - G3 PASS 확인
  │   - Verification Report 최종 판정 확인
  ├── 최종 판정: PASS → phase-X-Y-final-summary.md 작성
  └── 상태 파일: current_state = "DONE"
```

### 3.2 Task 단위 내부 루프

하나의 Task 처리 흐름:

```
[task-X-Y-N.md 읽기] → BUILDING → VERIFYING → TESTING → (다음 Task 또는 INTEGRATION)
                          ▲          │           │
                          │      FAIL│       FAIL│
                          └──────────┴───────────┘
                               REWINDING
```

**BUILDING 진입 전 필수**: 해당 Task의 내역서(task-X-Y-N.md)를 읽고 구현 범위·완료 기준을 확인한 후 코드 작성에 착수한다. 내역서가 없으면 TASK_SPEC 단계에서 생성 누락이므로 보완 후 진행한다.

### 3.3 도메인별 BUILDING 패턴

```
[BE] Task:
  Main Session → BACKEND.md 기준 구현 → 코드 작성

[FE] Task:
  [Frontend Analyzer] → Task tool (subagent_type: "Explore")
    → FRONTEND.md 기반 기존 패턴 분석 → 분석 결과 반환
    → Main Session → 코드 작성

[FS] Task:
  Main Session →
    [Backend Analyzer] → BE 영향 분석 (병렬, Task tool Explore)
    [Frontend Analyzer] → FE 영향 분석 (병렬, Task tool Explore)
    ← 합산 → 백엔드 구현 → 프론트엔드 구현

[DB] Task:
  Main Session → SQL 마이그레이션 작성 → ORM 동기화 → 롤백 SQL 작성
```

### 3.4 병렬 실행 최적화

```
# Task 구현 완료 후 (풀스택 예시)
Main Session: Task X-Y-N [FS] 구현 완료

# Verifier + Tester 동시 실행
Task tool (병렬):
  [Verifier] → subagent_type: "Explore" → 백엔드+프론트엔드 코드 리뷰 결과 반환
  [Tester]   → subagent_type: "Bash" → pytest + 페이지 로드 테스트 결과 반환

# 결과 수집
Main Session:
  IF Verifier=PASS AND Tester=PASS:
    → 다음 Task
  ELSE:
    → 도메인별 실패 항목 수정 후 재실행
```

### 3.5 Phase Template SSOT Connection

Phase Template 작성 시 SSOT 문서의 어떤 섹션을 참조해야 하는지 매핑한다.

| Template 항목 | 참조 SSOT | 참조 섹션 |
|--------------|----------|----------|
| Task 도메인 분류 | `1-project-ssot.md` | Section 3 (Task 도메인 분류) |
| 품질 게이트 기준 | `1-project-ssot.md` | Section 4 (품질 게이트 정의) |
| 테스트 레벨/명령 | `1-project-ssot.md` | Section 5 (테스트 전략) |
| 프론트엔드 체크리스트 | `1-project-ssot.md` | Section 6 (프론트엔드 구현 원칙) |
| 상태 파일 스키마 | `3-workflow-ssot.md` | Section 2 (상태 파일) |
| 상태 전이 규칙 | `3-workflow-ssot.md` | Section 1.3 (상태 전이 규칙) |
| 에러 등급/처리 | `3-workflow-ssot.md` | Section 4 (에러 처리 체계) |
| 백엔드 코드 규칙 | `2-architecture-ssot.md` | Section 2.2 (백엔드 코드 작성 규칙) |
| 프론트엔드 코드 규칙 | `2-architecture-ssot.md` | Section 3.2 (프론트엔드 코드 작성 규칙) |
| 검증 기준 체크리스트 | `2-architecture-ssot.md` | Section 8 (검증 기준 요약) |
| Task 내역서 생성 규칙 | `3-workflow-ssot.md` | Section 3.1 Step 2.5 (TASK_SPEC) |
| Task 문서 구조/명명 | `ai-rule-task-creation.md` | §3 Task 문서 공통 규약 |
| E2E 리포트/Verification Report | `3-workflow-ssot.md` | Section 3.1 Step 7.5 (E2E 리포트) |
| Verification Report 템플릿 | `verification-report-template.md` | 전체 (§1~§11) |
| SSOT Lock 규칙 | `0-ssot-index.md` | SSOT Lock Rules |
| Document Authority | `0-ssot-index.md` | Document Authority Chain |

---

## 4. 에러 처리 체계

### 4.1 에러 분류

| 등급 | 명칭 | 설명 | 처리 |
|------|------|------|------|
| **E0** | Critical | 시스템 장애, 데이터 손실 위험 | 즉시 중단, 사용자 개입 요청 |
| **E1** | Blocker | 기능 차단, 다음 단계 진행 불가 | BLOCKED 전이, Fix Task 생성 |
| **E2** | High | 기능 결함, 워크어라운드 존재 | REWINDING, 수정 후 재검증 |
| **E3** | Medium | 품질 이슈, 기능 동작에 지장 없음 | Technical Debt 등록, 진행 가능 |
| **E4** | Low | 코드 스타일, 개선 사항 | 기록만, 현재 Phase에서 수정 불필요 |

### 4.2 에러 기록 형식

상태 파일의 `error_log`에 다음 형식으로 기록:

```yaml
error_log:
  - id: "ERR-001"
    grade: "E2"
    domain: "[BE]"
    state: "VERIFYING"
    task: "X-Y-2"
    description: "backend/routers/admin/template_crud.py:45 — 타입 힌트 누락"
    detected_by: "Verifier"
    resolved: false
    resolution: null
    timestamp: "2026-02-09T10:30:00Z"
  - id: "ERR-002"
    grade: "E2"
    domain: "[FE]"
    state: "VERIFYING"
    task: "X-Y-3"
    description: "web/public/js/admin/settings/templates.js:120 — innerHTML XSS 위험"
    detected_by: "Verifier"
    resolved: true
    resolution: "esc() 함수 적용"
    timestamp: "2026-02-09T11:00:00Z"
  - id: "ERR-003"
    grade: "E1"
    domain: "[FS]"
    state: "TESTING"
    task: "X-Y-4"
    description: "API 응답 형식 불일치 — 프론트에서 items 배열 기대하나 백엔드에서 list 반환"
    detected_by: "Tester"
    resolved: true
    resolution: "API 응답을 표준 형식(items/total/limit/offset)으로 통일"
    timestamp: "2026-02-09T11:30:00Z"
```

### 4.3 에러 대응 플로우

```
에러 발생
  │
  ▼
에러 등급 판정 (E0~E4) + 도메인 식별 ([BE]/[FE]/[FS])
  │
  ├── E0 (Critical)
  │     → 즉시 중단
  │     → 사용자에게 상황 보고
  │     → 수동 개입 대기
  │
  ├── E1 (Blocker)
  │     → current_state = "BLOCKED"
  │     → blockers 배열에 추가 (도메인 태그 포함)
  │     → Fix Task 생성 (task-X-Y-N-fix.md, 도메인 태그 포함)
  │     → 수정 완료 후 blockers에서 제거
  │     → 이전 상태로 복귀
  │
  ├── E2 (High)
  │     → current_state = "REWINDING"
  │     → 해당 상태로 롤백 (BUILDING)
  │     → 도메인에 맞는 기준으로 수정 후 재검증
  │     → retry_count 증가
  │
  ├── E3 (Medium)
  │     → error_log에 기록
  │     → Technical Debt로 등록
  │     → 현재 워크플로우 계속 진행
  │
  └── E4 (Low)
        → error_log에 기록만
        → 현재 워크플로우 계속 진행
```

### 4.4 재시도 제한

```
IF retry_count >= 3 (동일 상태에서 3회 연속 실패):
  THEN:
    1. 현재 접근 방식 폐기
    2. 에러 로그 전체를 사용자에게 보고 (도메인별 분류)
    3. 대안 제시 (다른 구현 방식, 범위 축소 등)
    4. 사용자 판단 대기
  NEVER:
    - 4번째 동일 시도
    - 에러 무시하고 진행
    - 자의적 범위 변경
```

---

## 5. 리와인드 (Rewind) 체계

### 5.1 리와인드 정의

**리와인드**란 현재 상태에서 이전 상태로 롤백하여 문제를 수정하고 재진행하는 메커니즘이다.

### 5.2 리와인드 매트릭스

| 실패 상태 | 리와인드 대상 | 수행 작업 | 도메인 고려 |
|----------|-------------|----------|-----------|
| PLAN_REVIEW 실패 | PLANNING | Planner 재실행 (다른 프롬프트/관점) | 도메인 분류 재검토 |
| VERIFYING 실패 | BUILDING | 지적 사항 수정 | 도메인별 기준 적용 |
| TESTING 실패 | BUILDING | 테스트 실패 원인 수정 | [BE] pytest / [FE] 콘솔 에러 / [FS] 연동 |
| INTEGRATION 실패 (회귀) | BUILDING | 기존 API 깨뜨린 변경사항 식별·수정 | 이전 Phase API 응답 구조 보존 확인 |
| INTEGRATION 실패 (신규) | BUILDING | 새 API 구현 결함 수정 | 현재 Phase Task 기준 |
| INTEGRATION 실패 (연동) | BUILDING | API↔UI 연동 이슈 수정 (관련 Task 식별) | 도메인 간 인터페이스 일치 확인 |
| E2E 실패 (회귀) | BUILDING | 기존 E2E 깨뜨린 변경사항 식별·수정 | 셀렉터 변경 vs 기능 결함 구분 |
| E2E 실패 (신규) | BUILDING | E2E 시나리오 기준 수정 | 사용자 동선 기준 |

### 5.3 리와인드 실행 절차

```
1. 실패 상태 기록
   - error_log에 실패 내용 추가 (도메인 태그 포함)
   - gate_results에 FAIL 기록 (G2_be/G2_fe 분리)

2. 리와인드 대상 결정
   - rewind_target = 리와인드 매트릭스 참조
   - current_state = "REWINDING"

3. Fix Task 생성 (필요 시)
   - task-X-Y-N-fix.md 생성
   - 도메인 태그, 수정 대상 파일, 수정 내용, 재검증 방법 명시

4. 상태 전이
   - current_state = rewind_target
   - retry_count += 1
   - rewind_target = null

5. 재실행
   - 리와인드 대상 상태부터 워크플로우 재개
   - 수정 사항에 대해서만 재검증 (전체 재검증 아님)
   - 도메인별 검증 기준 재적용
```

### 5.4 리와인드 시점 판단 기준

| 판단 기준 | 리와인드 실행 | 리와인드 미실행 |
|----------|:----------:|:------------:|
| Critical 에러 발견 | O | — |
| 테스트 실패 (pytest) | O | — |
| 페이지 로드 실패 / 콘솔 에러 | O | — |
| High 에러 (기능 차단) | O | — |
| High 에러 (개선 사항) | — | O (Tech Debt) |
| Medium 에러 | — | O (기록만) |
| Low 에러 | — | O (기록만) |
| 기존 테스트 깨짐 | O | — |
| 새 테스트만 실패 | O | — |
| 커버리지 미달 (< 80%, 백엔드) | O | — |
| CDN 참조 발견 (프론트) | O | — |
| innerHTML XSS 위험 (프론트) | O | — |

---

## 6. 작업 완료 판정

### 6.1 Task 완료 기준

하나의 Task가 DONE으로 판정되려면:

```
Task DONE 조건 ([BE] Task):
  AND(
    코드 구현 완료,
    Verifier PASS — G2_be (백엔드 기준),
    Tester PASS — G3 (pytest 통과),
    task-X-Y-N.md 작성 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )

Task DONE 조건 ([FE] Task):
  AND(
    코드 구현 완료,
    Verifier PASS — G2_fe (프론트 기준: CDN, ESM, XSS),
    페이지 로드 확인 + 콘솔 에러 0건,
    task-X-Y-N.md 작성 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )

Task DONE 조건 ([FS] Task):
  AND(
    백엔드 + 프론트엔드 코드 구현 완료,
    Verifier PASS — G2_be + G2_fe,
    Tester PASS — G3 (pytest + UI 확인),
    API↔UI 연동 동작 확인,
    task-X-Y-N.md 작성 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )
```

### 6.2 Phase 완료 기준

Phase가 DONE으로 판정되려면:

```
Phase DONE 조건:
  AND(
    모든 Task = DONE,
    G1 (Plan Review) = PASS,
    G2_be (백엔드 Code Review) = PASS (해당 Task 있을 때),
    G2_fe (프론트 Code Review) = PASS (해당 Task 있을 때),
    G4 (Final Gate) = PASS,
    INTEGRATION 테스트 PASS,
    E2E 테스트 PASS (또는 대체 테스트 PASS),
    phase-X-Y-verification-report.md 작성 완료,
    blockers = [],
    phase-X-Y-final-summary.md 작성 완료
  )
```

### 6.3 완료 판정 플로우

```
Orchestrator:
  1. task_progress 전체 확인 → 모든 Task "DONE"?
     NO → 남은 Task 처리 계속
     YES ↓

  2. gate_results 확인 → G1, G2_be, G2_fe, G3 모두 PASS?
     NO → 실패한 게이트로 리와인드
     YES ↓

  3. INTEGRATION 실행 (Dev API 검사 + 통합 연동)
     3-a. Dev API 회귀 검사 → 기존 API 엔드포인트 정상?
       NO → REWINDING→BUILDING (회귀 결함 — 기존 기능 깨짐)
       YES ↓
     3-b. 현재 Phase API 검사 → 새/변경 엔드포인트 정상?
       NO → REWINDING→BUILDING (구현 결함)
       YES ↓
     3-c. 통합 연동 검사
       [BE] API 연동, DB 정합성
       [FE] 페이지 간 네비게이션, 전 메뉴 HTTP 200 확인
       [FS] API↔UI 데이터 흐름 확인
       NO → REWINDING→BUILDING (실패 도메인 식별)
       YES ↓

  4. E2E 실행 (Playwright 회귀 + 신규)
     4-a. 기존 E2E 회귀 → 이전 Phase spec 파일 전체 실행
       NO → REWINDING→BUILDING (회귀 결함 — 기존 E2E 깨짐)
       YES ↓
     4-b. 현재 Phase E2E → 새 spec 파일 실행 (또는 대체 테스트)
       NO → REWINDING→BUILDING (E2E 결함)
       YES ↓

  4.5. E2E 리포트 작성
     → phase-X-Y-verification-report.md 작성 (템플릿 기반)
     → phase-X-Y-webtest-execution-report.md 작성
       (회귀 E2E 결과, 신규 E2E 결과, 시나리오↔E2E 매핑 표)
     → E2E 결과, Integration 결과, 코드 오류 종합 기록
     → Web User Test Report 작성 (해당 시)
     → 리포트 최종 판정: PASS/FAIL/PARTIAL
     FAIL → 원인 분석 후 리와인드
     PASS ↓

  5. G4 Final Gate 판정
     → blockers = [] 확인
     → error_log에 미해결 E0/E1 없음 확인
     → Verification Report 최종 판정 = PASS 확인
     → PASS → DONE
     → FAIL → 원인 분석 후 리와인드
```

---

## 7. 다음 작업 결정 로직

### 7.1 자동 결정 규칙

```python
def decide_next_action(status):
    """상태 파일 기반으로 다음 작업을 자동 결정"""

    # SSOT Freshness Check (FRESH-2, FRESH-3)
    if status.ssot_version != current_ssot_version():
        return "SSOT_RELOAD: SSOT 버전 불일치, 리로드 필요"

    # SSOT Lock Check (LOCK-1)
    if ssot_modified_during_phase(status):
        return "BLOCKED: SSOT 변경 감지, Lock 프로세스 필요"

    if status.blockers:
        return "BLOCKED: 차단 이슈 먼저 해결"

    if status.current_state == "IDLE":
        return "PLANNING: Planner 서브에이전트 실행 (Task tool → Plan)"

    if status.current_state == "PLANNING":
        return "PLAN_REVIEW: Planner 결과 검토 (도메인 분류 포함)"

    if status.current_state == "PLAN_REVIEW":
        if status.last_action_result == "PASS":
            return "TASK_SPEC: Task 내역서 일괄 생성 (ai-rule-task-creation.md)"
        return "REWINDING→PLANNING"

    if status.current_state == "TASK_SPEC":
        first_task = find_first_pending_task(status.task_progress)
        domain = first_task.domain
        return f"BUILDING: {first_task.id} {domain} 구현 시작 (task-X-Y-N.md 참조)"

    if status.current_state == "BUILDING":
        domain = status.current_task_domain
        return f"VERIFYING: Verifier 실행 (Task tool → Explore, {domain} 기준 적용)"

    if status.current_state == "VERIFYING":
        if status.last_action_result == "PASS":
            domain = status.current_task_domain
            return f"TESTING: Tester 실행 (Task tool → Bash, {domain} 테스트)"
        return "REWINDING→BUILDING: 지적사항 수정"

    if status.current_state == "TESTING":
        if status.last_action_result == "PASS":
            next_task = find_next_pending_task(status.task_progress)
            if next_task:
                return f"BUILDING: {next_task.id} {next_task.domain} 구현 시작"
            return "INTEGRATION: 통합 테스트 실행 (BE+FE 연동)"
        return "REWINDING→BUILDING: 테스트 실패 수정"

    if status.current_state == "INTEGRATION":
        if status.last_action_result == "PASS":
            return "E2E: E2E 테스트 실행 (회귀 E2E → 신규 E2E 순서)"
        if "회귀" in (status.last_action or ""):
            return "REWINDING→BUILDING: 기존 API 회귀 결함 수정 (변경사항 역추적)"
        return "REWINDING→BUILDING: 통합 이슈 수정 (도메인 식별 필요)"

    if status.current_state == "E2E":
        if status.last_action_result == "PASS":
            return "E2E_REPORT: Verification Report + E2E 리포트 작성 (회귀+신규 결과 분리 기재)"
        if "회귀" in (status.last_action or ""):
            return "REWINDING→BUILDING: 기존 E2E 회귀 결함 수정 (기존 기능 깨짐)"
        return "REWINDING→BUILDING: E2E 실패 수정 (현재 Phase 결함)"

    if status.current_state == "E2E_REPORT":
        return "DONE: G4 Final Gate + Final Summary 작성"

    if status.current_state == "DONE":
        return "완료: 다음 Phase 준비"
```

### 7.2 Task 실행 순서 권장 패턴

풀스택 Phase에서 Task 실행 순서:

```
권장 순서:
  1. [DB] 스키마/마이그레이션 (기반 작업)
  2. [BE] API/서비스 (데이터 계층)
  3. [FE] UI 페이지 (표현 계층)
  4. [FS] API↔UI 연동 (통합)
  5. [TEST] 통합/E2E 테스트 (검증)

이유:
  - DB → BE → FE 순서로 의존성이 흐른다
  - API가 먼저 완성되어야 프론트에서 데이터 바인딩 가능
  - 연동 Task는 양쪽 완성 후 수행
```

### 7.3 사용자 개입 필요 시점

| 시점 | 이유 | Orchestrator 행동 |
|------|------|------------------|
| retry_count >= 3 | 동일 문제 반복 | 대안 제시 후 사용자 판단 요청 |
| E0 (Critical) 발생 | 시스템 장애 | 즉시 중단, 상황 보고 |
| Phase 범위 변경 필요 | 구현 중 요구사항 변경 발견 | 범위 조정 안 제시 후 승인 요청 |
| 기술적 결정 필요 | 두 가지 이상의 접근법 | 선택지와 트레이드오프 제시 |
| 도메인 간 충돌 | BE-FE 인터페이스 불일치 | API Spec 조정안 제시 |
| CDN 로컬 전환 필요 | 새 외부 라이브러리 필요 | 라이브러리 선택 + 로컬 배치 방안 제시 |
| SSOT 변경 필요 | Phase 중 SSOT 규칙 수정 필요 | LOCK-2 절차에 따라 일시정지 후 승인 요청 |

---

## 8. 부트로더 시퀀스

### 8.1 Cold Start (새 Phase 시작)

```
1. 사용자: "Phase X-Y 시작"

2. Orchestrator:
   a. SSOT 리로드 (0→1→2→3) ← FRESH-1
   b. SSOT 버전 확인 ← FRESH-2
   c. 상태 파일 생성 (phase-X-Y-status.md)
      - ssot_version: "3.0"
      - ssot_loaded_at: (현재 시각)
      - current_state: "IDLE"
      - task_progress: {}
      - gate_results: 모두 null (G2_be, G2_fe 분리)
   d. 상태 → PLANNING
   e. Planner 서브에이전트 실행 (Task tool → subagent_type: "Plan")

3. Planner (서브에이전트):
   a. master-plan, navigation 분석
   b. 백엔드/프론트엔드 영향 범위 식별
   c. Task 분해 (도메인 태그 포함), 완료 기준, 리스크 반환

4. Orchestrator:
   a. PLAN_REVIEW (G1)
      - 도메인 분류 적절성 확인
      - 프론트엔드 Task에 UI 구조/동선 기술 여부 확인
   b. PASS → plan.md, todo-list.md 작성 (도메인 태그 포함)
   c. 상태 → TASK_SPEC
   d. Task 내역서 일괄 생성 (ai-rule-task-creation.md 기준)
      - todo-list의 각 Task에 대해 task-X-Y-N-<topic>.md 생성
      - 저장: docs/phases/phase-X-Y/tasks/
      - 누락 검사: todo-list Task 수 == task 문서 수
   e. 상태 → BUILDING
   f. 첫 번째 Task 구현 시작 (권장: [DB] → [BE] → [FE] → [FS])
```

### 8.2 Warm Start (중단 재개)

```
1. Orchestrator:
   a. SSOT 리로드 (0→1→2→3) ← FRESH-1
   b. SSOT 버전 확인 ← FRESH-2
   c. phase-X-Y-status.md 읽기 ← ENTRY-1 (ENTRYPOINT)
   d. ssot_version 확인 ← ENTRY-3
      - 불일치 시: ssot_version 갱신, ssot_loaded_at 갱신
   e. current_state 확인
   f. current_task_domain 확인 (도메인별 컨텍스트 전환)
   g. blockers 확인 (비어있지 않으면 이슈 해결 우선) ← ENTRY-4
   h. task_progress 확인 (다음 PENDING Task 식별, 도메인 확인)
   i. next_action에 명시된 작업 재개
```

### 8.3 세션 전환 시 컨텍스트 유지

AI 세션이 끊기고 새 세션에서 재개할 때:

```
1. SSOT 로딩 (0→1→2→3) ← FRESH-1
2. phase-X-Y-status.md 읽기 ← ENTRY-1
3. ssot_version 확인 ← FRESH-2, ENTRY-3
   - 불일치 시: SSOT 리로드 후 ssot_version/ssot_loaded_at 갱신
4. current_state와 current_task 기반으로 재개 지점 판단
5. current_task_domain 확인하여 해당 Charter 참조
6. error_log 확인하여 이전 실패 내역 파악 (도메인별)
7. gate_results 확인하여 통과한 게이트 재실행 방지
   - G2_be, G2_fe 개별 확인
```

---

## 9. 참조 문서 매핑

| 워크플로우 단계 | 참조 규칙 문서 | 참조 Charter |
|---------------|--------------|-------------|
| PLANNING | `docs/rules/ai/references/ai-rule-phase-plan-todo-generation.md` | — |
| TASK_SPEC | `docs/rules/ai/references/ai-rule-task-creation.md` | — |
| BUILDING [BE/DB] | `docs/rules/ai/references/ai-rule-task-creation.md` | `BACKEND.md` |
| BUILDING [FE] | `docs/rules/ai/references/ai-rule-task-creation.md` | `FRONTEND.md` |
| BUILDING [FS] | `docs/rules/ai/references/ai-rule-task-creation.md` | `BACKEND.md` + `FRONTEND.md` |
| VERIFYING | `docs/rules/ai/references/ai-rule-task-inspection.md` | `QA.md` |
| TESTING [BE] | `docs/rules/testing/integration-test-guide.md` | `QA.md` |
| TESTING [FE] | `docs/rules/testing/phase-unit-user-test-guide.md` | `QA.md` |
| INTEGRATION (Dev API) | `docs/devtest/integration-test-guide.md` §4-§5 | `QA.md` |
| INTEGRATION (회귀 분기) | `docs/devtest/scenarios/phase-10-regression-scenarios.md` | `QA.md` |
| E2E (실행) | `docs/webtest/phase-unit-user-test-guide.md` §0 (방안 A/B/C) | `QA.md` |
| E2E (회귀) | `e2e/smoke.spec.js` + 기존 Phase spec 파일들 | `QA.md` |
| E2E (Phase 13-3 패턴) | `e2e/phase-13-menu-*.spec.js` (메뉴·헤더·활성 3단계) | `QA.md` |
| E2E_REPORT | `docs/rules/templates/verification-report-template.md` | `QA.md` |
| E2E_REPORT (실행 결과) | `docs/devtest/integration-test-guide.md` §5 (리포트 규정) | `QA.md` |

**Charter 파일 경로**:

| Charter | 경로 |
|---------|------|
| LEADER | `docs/rules/role/LEADER.md` |
| BACKEND | `docs/rules/role/BACKEND.md` |
| FRONTEND | `docs/rules/role/FRONTEND.md` |
| QA | `docs/rules/role/QA.md` |

---

## 10. 버전 히스토리

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초안 작성 (백엔드 전용) | Claude Code (Backend & Logic Expert) |
| 2.0 | 2026-02-09 | 프론트엔드 워크플로우 추가, 도메인 태그 시스템, G2 분리(be/fe), 공통 AI 팀 언어로 전환 | Claude Code (Backend & Logic Expert) |
| 3.0 | 2026-02-15 | ENTRYPOINT 정의 추가, Phase Template SSOT Connection 추가, 상태 파일에 ssot_version/ssot_loaded_at 필드 추가, SSOT Lock/Freshness enforcement 통합, 부트로더 시퀀스에 SSOT 리로드 명시, 외부 AI 참조 제거 | Claude Code (Backend & Logic Expert) |
| 3.1 | 2026-02-16 | TASK_SPEC 상태 추가 (PLAN_REVIEW→BUILDING 사이 Task 내역서 생성 단계), E2E_REPORT 단계 추가 (E2E→DONE 사이 Verification Report + E2E 리포트 작성), 참조 문서 매핑에 TASK_SPEC/E2E_REPORT 행 추가 | Claude Code (Backend & Logic Expert) |
| 3.2 | 2026-02-16 | INTEGRATION/E2E 절차 상세화: (1) Dev API 회귀+신규+연동 3단계 검사, (2) E2E 회귀+신규 2단계 실행, (3) 각 절차별 회귀 분기(REWINDING) 판정 기준 삽입, (4) 리포트에 회귀/신규 결과 분리 기재, (5) Phase 13-3 E2E 패턴(메뉴·헤더·활성 3단계) 적용, (6) 리와인드 매트릭스 회귀/신규/연동 분리, (7) 참조 문서 매핑 확대 | Claude Code (Backend & Logic Expert) |
