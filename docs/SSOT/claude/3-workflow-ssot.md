# AI Team — Workflow SSOT

**버전**: 4.3
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
[6] 팀 상태 확인 (TeamCreate 필요 여부, 팀원 idle 상태)
  │
  ▼
[7] 워크플로우 실행
```

---

## 1. 워크플로우 상태 머신

### 1.1 상태 정의

| 상태 코드 | 상태명 | 설명 | 진입 조건 |
|----------|--------|------|----------|
| `IDLE` | 대기 | Phase 미시작 | 초기 상태 |
| `TEAM_SETUP` | 팀 구성 | TeamCreate + 팀원 스폰 | Phase 시작 명령 |
| `PLANNING` | 계획 | planner 팀원이 요구사항 분석, Task 분해 | 팀 구성 완료 |
| `PLAN_REVIEW` | 계획 검토 | Team Lead가 planner 결과 검증 | PLANNING 완료 |
| `TASK_SPEC` | Task 내역서 작성 | Task별 실행 계획 문서 생성 | PLAN_REVIEW 통과 |
| `BUILDING` | 구현 | backend-dev/frontend-dev가 코드 작성 | TASK_SPEC 완료 |
| `VERIFYING` | 검증 | verifier가 코드 리뷰 (결과를 Team Lead에게 보고) | BUILDING 완료 (Task 단위) |
| `TESTING` | 테스트 | tester가 테스트 실행 | VERIFYING 통과 |
| `INTEGRATION` | 통합 테스트 | Phase 전체 통합 검증 (API↔UI 연동 포함) | 모든 Task TESTING 통과 |
| `E2E` | E2E 테스트 | 사용자 시나리오 기반 전체 테스트 | INTEGRATION 통과 |
| `E2E_REPORT` | E2E 리포트 | Verification Report + E2E 실행 리포트 작성 | E2E 통과 |
| `TEAM_SHUTDOWN` | 팀 해산 | 팀원 셧다운 + TeamDelete | E2E_REPORT 완료 |
| `BLOCKED` | 차단 | Blocker 이슈 발생 | 어떤 상태에서든 진입 가능 |
| `REWINDING` | 리와인드 | 이전 상태로 롤백 중 | FAIL 판정 시 |
| `DONE` | 완료 | Phase 종료 | TEAM_SHUTDOWN 완료 |

### 1.2 상태 전이 다이어그램

```
IDLE
  │
  ▼
TEAM_SETUP (TeamCreate + 팀원 스폰)
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
  │  backend-dev / frontend-dev 병렬 가능      │
  ▼                                            │
VERIFYING ───── FAIL ──► REWINDING ──► BUILDING│
  │  verifier → Team Lead → developer (수정)   │
  │ PASS                                       │
  ▼                                            │
TESTING ─────── FAIL ──► REWINDING ──► BUILDING│
  │  tester 실행                               │
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
  │ PASS
  ▼
E2E_REPORT (Verification Report + E2E 리포트 작성)
  │
  ▼
TEAM_SHUTDOWN (shutdown_request × N → TeamDelete)
  │
  ▼
DONE (G4 Final Gate)

※ 어떤 상태에서든 BLOCKED로 전이 가능
  BLOCKED → 이슈 해결 → 이전 상태로 복귀
  BLOCKED (사유: "SSOT 변경 필요") → SSOT Lock 프로세스 → 복귀
```

### 1.3 상태 전이 규칙

| 현재 상태 | 이벤트 | 다음 상태 | 조건 |
|----------|--------|----------|------|
| IDLE | Phase 시작 | TEAM_SETUP | SSOT 리로드 완료 (FRESH-1) |
| TEAM_SETUP | 팀 구성 완료 | PLANNING | TeamCreate + 필요 팀원 스폰 완료 |
| PLANNING | planner 완료 | PLAN_REVIEW | plan + todo-list 생성됨 (도메인 태그 포함) |
| PLAN_REVIEW | 검토 통과 | TASK_SPEC | 완료 기준 명확, Task 3~7개, 도메인 분류 완료 |
| TASK_SPEC | 내역서 생성 완료 | BUILDING | 모든 Task에 task-X-Y-N.md 생성됨 |
| PLAN_REVIEW | 검토 실패 | REWINDING→PLANNING | 완료 기준 불명확 또는 범위 초과 |
| BUILDING | 구현 완료 | VERIFYING | Task 단위 코드 작성 완료 (개발자 SendMessage 보고) |
| VERIFYING | PASS | TESTING | 도메인별 Critical 0건 (verifier SendMessage 보고) |
| VERIFYING | FAIL | REWINDING→BUILDING | verifier → Team Lead → 개발자 수정 요청 |
| TESTING | PASS | BUILDING (다음 Task) 또는 INTEGRATION | tester SendMessage 보고 |
| TESTING | FAIL | REWINDING→BUILDING | 테스트 실패 |
| INTEGRATION | PASS (회귀+신규+연동) | E2E | Dev API 회귀 PASS + 현재 API PASS + 통합 연동 PASS |
| INTEGRATION | FAIL | REWINDING→BUILDING | 실패 도메인 식별 후 해당 개발자에게 수정 요청 |
| E2E | PASS (회귀+신규) | E2E_REPORT | 기존 E2E 회귀 PASS + 현재 E2E PASS |
| E2E | FAIL | REWINDING→BUILDING | E2E 결함 수정 |
| E2E_REPORT | 리포트 작성 완료 | TEAM_SHUTDOWN | Verification Report + E2E 리포트 작성 완료 |
| TEAM_SHUTDOWN | 팀 해산 완료 | DONE | 모든 팀원 shutdown + TeamDelete |
| BLOCKED | 이슈 해결 | (이전 상태) | Blocker 제거 |
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
ssot_version: "4.0"                # 현재 참조 중인 SSOT 버전
ssot_loaded_at: "2026-02-16T10:00:00Z"  # SSOT 마지막 로딩 시각
current_state: "BUILDING"          # 상태 머신의 현재 상태
current_task: "X-Y-2"              # 현재 작업 중인 Task ID
current_task_domain: "[FE]"        # 현재 Task 도메인 태그
team_name: "phase-X-Y"            # Agent Teams 팀 이름
team_members:                      # 현재 활성 팀원 목록
  - { name: "backend-dev", status: "idle" }
  - { name: "frontend-dev", status: "working" }
  - { name: "verifier", status: "idle" }
  - { name: "tester", status: "idle" }
last_action: "Task X-Y-1 [BE] API 구현 완료 (backend-dev)"
last_action_result: "PASS"         # PASS | FAIL | PARTIAL | N/A
next_action: "Task X-Y-2 [FE] UI 페이지 구현 시작 (frontend-dev)"
blockers: []                       # 차단 이슈 목록
rewind_target: null                # REWINDING 시 목표 상태
retry_count: 0                     # 현재 상태 재시도 횟수 (최대 3)
gate_results:                      # 품질 게이트 통과 기록
  G1_plan_review: null             # PASS | FAIL | null
  G2_code_review_be: null          # 백엔드 코드 리뷰 (verifier)
  G2_code_review_fe: null          # 프론트엔드 코드 리뷰 (verifier)
  G3_test_gate: null               # tester 테스트 결과
  G4_final_gate: null
task_progress:                     # Task별 진행 현황
  X-Y-1: { status: "DONE", domain: "[BE]", owner: "backend-dev" }
  X-Y-2: { status: "IN_PROGRESS", domain: "[FE]", owner: "frontend-dev" }
  X-Y-3: { status: "PENDING", domain: "[FS]", owner: "backend-dev+frontend-dev" }
error_log: []                      # 누적 에러 기록
last_updated: "2026-02-16T10:30:00Z"
---
```

### 2.3 상태 파일 관리 규칙

| 규칙 | 설명 |
|------|------|
| **쓰기 권한** | Team Lead(메인 세션)만 상태 파일 수정 가능 |
| **읽기 권한** | 모든 팀원이 읽기 가능 |
| **업데이트 시점** | 상태 전이 시 즉시 업데이트 |
| **팀 정보 기록** | `team_name`, `team_members` 필드로 팀 상태 추적 |
| **게이트 기록** | 각 게이트 통과 시 결과 기록 (백엔드/프론트 분리) |
| **에러 누적** | 에러 발생 시 `error_log`에 추가 (삭제 금지) |
| **도메인 태그** | 모든 Task에 도메인 태그 필수 ([BE], [FE], [FS], [DB], [TEST], [INFRA]) |
| **SSOT 버전 동기화** | SSOT 리로드 시 `ssot_version`과 `ssot_loaded_at` 갱신 |

---

## 3. 워크플로우 실행 순서

### 3.1 Phase 전체 흐름

```
Step 0: TEAM_SETUP (팀 구성)
  ├── TeamCreate(team_name: "phase-X-Y")
  ├── 필요 팀원 스폰:
  │   ├── planner (subagent_type: "Plan", model: "opus") — 계획 단계용
  │   ├── backend-dev (subagent_type: "general-purpose", model: "sonnet") — BE 구현용
  │   ├── frontend-dev (subagent_type: "general-purpose", model: "sonnet") — FE 구현용
  │   └── (verifier, tester는 검증 단계에서 지연 스폰)
  └── 팀 구성 완료 → PLANNING으로 전이

Step 1: PLANNING
  ├── Team Lead → SendMessage → planner: "Phase X-Y 계획 분석 요청"
  │   (master-plan, navigation, 이전 Phase summary 참조 지시)
  ├── planner: 백엔드/프론트엔드 영향 범위 식별
  ├── planner → SendMessage → Team Lead: "분석 결과 반환"
  │   (Task 분해, 도메인 태그, 완료 기준, 리스크)
  └── 산출물: plan 분석 결과 (SendMessage로 수신)

Step 2: PLAN_REVIEW (G1)
  ├── Team Lead가 planner 결과 검토
  ├── 확인:
  │   - 완료 기준 명확성
  │   - Task 분해 적절성 (도메인별 균형)
  │   - 리스크 대응
  │   - 프론트엔드 Task에 UI 동선/구조 기술 여부
  ├── PASS → plan.md + todo-list.md 작성 (도메인 태그 + 담당 팀원 포함)
  │   → planner shutdown_request (계획 단계 종료)
  │   → TASK_SPEC으로 전이
  └── FAIL → REWINDING→PLANNING

Step 2.5: TASK_SPEC (Task 내역서 일괄 생성)
  ├── todo-list 기반으로 Task별 실행 계획 문서 생성
  │   참조: docs/rules/ai/references/ai-rule-task-creation.md
  ├── 각 Task에 대해 task-X-Y-N-<topic>.md 생성:
  │   - §1 개요 (목표)
  │   - §2 파일 변경 계획
  │   - §3 작업 체크리스트 (완료 기준 = Done Definition)
  │   - §4 참조·비고 (선택)
  │   - **담당 팀원** 명시
  ├── 저장 위치: docs/phases/phase-X-Y/tasks/
  ├── 누락 검사: todo-list Task 수 == task 문서 수
  ├── TaskCreate로 공유 TaskList에 등록 + TaskUpdate(owner)로 팀원 할당
  └── 완료 → BUILDING으로 전이

Step 3: BUILDING (Task 단위 반복 — 팀원 병렬 가능)
  ├── Team Lead:
  │   ├── TaskUpdate(owner: "backend-dev") — [BE/DB] Task 할당
  │   ├── TaskUpdate(owner: "frontend-dev") — [FE] Task 할당
  │   └── SendMessage → 각 팀원: "Task X-Y-N 구현 시작"
  ├── 팀원 구현 패턴:
  │   [BE/DB] → backend-dev가 BACKEND.md 기준으로 코드 작성
  │   [FE]    → frontend-dev가 FRONTEND.md 기준으로 코드 작성
  │   [FS]    → backend-dev(BE 먼저) → frontend-dev(FE 후속) 또는 병렬
  ├── 구현 완료 → 팀원이 TaskUpdate(completed) + SendMessage → Team Lead
  ├── [FS] Task: backend-dev → SendMessage → Team Lead → frontend-dev: "API 완료, 연동 가능"
  └── Team Lead: VERIFYING으로 전이

Step 4: VERIFYING (G2 - Task 단위)
  ├── [자동] TaskCompleted Hook: 기본 품질 검사 자동 실행
  │   └── syntax, CDN, ESM 검사 → 실패 시 완료 차단 (exit 2)
  ├── Team Lead:
  │   ├── `/verify-implementation` 스킬로 심층 코드 리뷰 실행 (원커맨드)
  │   └── 또는 verifier 스폰 (미스폰 시) / SendMessage → verifier: "검증 요청"
  │       (변경 파일 목록 + 도메인별 검증 기준 + 완료 기준)
  ├── verifier: 도메인별 검증 기준 적용
  │   [BE] → 타입 힌트, 에러 핸들링, ORM, 보안
  │   [FE] → CDN 미사용, ESM, innerHTML XSS, 컴포넌트 재사용
  │   [FS] → 백엔드 + 프론트엔드 기준 모두 적용
  ├── verifier → SendMessage → Team Lead: "G2 결과: PASS/FAIL + 이슈 목록"
  ├── (FAIL 시) Team Lead → SendMessage → 개발자: "수정 요청 + 상세"
  │   → 개발자 수정 → SendMessage → Team Lead: "수정 완료"
  │   → Team Lead → SendMessage → verifier: "재검증 요청"
  ├── PASS → TESTING으로 전이
  └── FAIL (재검증 후에도) → REWINDING→BUILDING

### 자동화 트리거 (Hooks + Skills)

| 트리거 | 이벤트 | 동작 |
|--------|--------|------|
| Task 완료 자동 검사 | `TaskCompleted` hook | 기본 품질 검사 (syntax, CDN, ESM). 실패 시 완료 차단 |
| 심층 코드 리뷰 | `/verify-implementation` skill | Team Lead가 호출. G2 게이트 판정 |

참조: `.claude/settings.json`, `.claude/skills/verify-*/SKILL.md`

Step 5: TESTING (G3 - Task 단위)
  ├── Team Lead:
  │   └── tester 스폰 (미스폰 시) 또는 SendMessage → tester: "테스트 실행 요청"
  │       (테스트 파일 경로, 명령, 기대 결과)
  ├── tester: 도메인별 테스트
  │   [BE] → pytest (L2 단위, L3 통합)
  │   [FE] → 페이지 로드 확인, 콘솔 에러 확인 (L5)
  │   [FS] → pytest + API↔UI 연동 확인 (L4)
  ├── tester → SendMessage → Team Lead: "G3 결과 + TEST_REPORT"
  ├── PASS → 다음 Task(BUILDING) 또는 INTEGRATION
  └── FAIL → REWINDING→BUILDING

  ※ Step 4 + Step 5 병렬 실행 가능:
    Team Lead → SendMessage → verifier + tester 동시 요청

Step 6: INTEGRATION (Dev API 검사 + 통합 테스트)
  ├── 6-A. Dev API 회귀 검사 — 기존 Phase 엔드포인트 정상 동작 확인
  │   ├── Team Lead → SendMessage → tester: "Dev API 회귀 검사 실행"
  │   ├── tester: curl + HTTP 상태 코드 + JSON 응답 구조 검증
  │   ├── PASS → 6-B로 진행
  │   └── FAIL → REWINDING→BUILDING (회귀 결함)
  │
  ├── 6-B. 현재 Phase API 검사
  │   ├── tester: 현재 Phase 추가·수정 엔드포인트 동작 확인
  │   ├── PASS → 6-C로 진행
  │   └── FAIL → REWINDING→BUILDING (구현 결함)
  │
  ├── 6-C. 통합 연동 검사
  │   ├── [BE] → API 연동, DB 정합성, 서비스 간 연계
  │   ├── [FE] → 페이지 간 네비게이션, 공유 컴포넌트 동작
  │   ├── [FS] → API 호출 → 응답 렌더링 → 사용자 인터랙션 전체 흐름
  │   ├── 페이지 로드 검사: 모든 HTML 라우트 HTTP 200 확인
  │   ├── tester → SendMessage → Team Lead: "INTEGRATION 결과"
  │   ├── PASS → E2E로 전이
  │   └── FAIL → REWINDING→BUILDING (연동 결함)
  │
  └── 회귀 분기 판정 기준:
      ├── 기존 API 응답 구조 변경 → E2 (High), REWINDING 필수
      ├── 기존 페이지 HTTP 404/500 → E1 (Blocker), BLOCKED 전이
      ├── 새 API만 실패 → E2 (High), 해당 Task로 REWINDING
      └── 연동 불일치 → E2, REWINDING→BUILDING

Step 7: E2E (Playwright E2E 검사)
  ├── 7-A. 기존 E2E 회귀 실행
  │   ├── Team Lead → SendMessage → tester: "기존 E2E 회귀 실행"
  │   ├── tester: 기존 spec 파일 전체 실행
  │   ├── PASS → 7-B로 진행
  │   └── FAIL → REWINDING→BUILDING (회귀 결함)
  │
  ├── 7-B. 현재 Phase E2E 실행
  │   ├── E2E spec 파일 확인: e2e/phase-X-Y.spec.js 존재 여부
  │   │   ├── 존재 → tester: Playwright 실행
  │   │   └── 미존재 → frontend-dev가 E2E spec 생성 또는 대체 테스트
  │   ├── tester → SendMessage → Team Lead: "E2E 결과"
  │   ├── PASS → E2E 리포트 작성 (Step 7.5)
  │   └── FAIL → REWINDING→BUILDING
  │
  └── 회귀 분기 판정 기준:
      ├── 기존 E2E 실패 → E1 (Blocker), 변경사항에 의한 회귀
      ├── 새 E2E만 실패 → E2 (High), 해당 Task로 REWINDING
      └── 셀렉터 불일치 → DOM 구조 변경 반영

Step 7.5: E2E 리포트 작성
  ├── 7.5-A. Verification Report 작성
  │   ├── Team Lead: verifier/tester 결과 종합
  │   ├── 참조 템플릿: docs/rules/templates/verification-report-template.md
  │   ├── 저장: docs/phases/phase-X-Y/phase-X-Y-verification-report.md
  │   └── 포함: §2 Syntax, §3 Logic, §4 Edge Case, §5 코드 오류, §8 테스트, §10 판정
  │
  ├── 7.5-B. E2E 실행 결과 리포트 작성
  │   ├── 저장: docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md
  │   └── 포함: E2E Spec 상태, 회귀/신규 결과, 시나리오↔E2E 매핑 표
  │
  └── 리포트 완료 → TEAM_SHUTDOWN (Step 8)

Step 8: TEAM_SHUTDOWN + DONE (G4)
  ├── Team Lead:
  │   ├── 전체 결과 종합 (G2_be + G2_fe + G3 모두 PASS 확인)
  │   ├── 최종 판정: PASS → phase-X-Y-final-summary.md 작성
  │   ├── 팀원 순차 셧다운:
  │   │   SendMessage(type: "shutdown_request") → tester
  │   │   SendMessage(type: "shutdown_request") → verifier
  │   │   SendMessage(type: "shutdown_request") → frontend-dev
  │   │   SendMessage(type: "shutdown_request") → backend-dev
  │   ├── 모든 팀원 shutdown_response(approve: true) 수신
  │   ├── TeamDelete()
  │   └── 상태 파일: current_state = "DONE"
  └── Phase 완료
```

### 3.2 Task 단위 내부 루프

하나의 Task 처리 흐름:

```
[task-X-Y-N.md 읽기]
       │
       ▼
Team Lead → SendMessage → 담당 팀원: "Task 구현 시작"
       │
       ▼
BUILDING (backend-dev 또는 frontend-dev가 코드 작성)
       │
       ▼ 팀원 → SendMessage → Team Lead: "구현 완료"
       │
       ▼
VERIFYING (verifier가 코드 리뷰)
       │
       ├── FAIL → verifier → Team Lead → 개발자: "수정 요청"
       │          → 개발자 수정 → Team Lead → verifier 재검증
       │
       ▼ PASS
TESTING (tester가 테스트 실행)
       │
       ├── FAIL → Team Lead → SendMessage → 개발자: "테스트 실패 수정"
       │          → REWINDING→BUILDING
       │
       ▼ PASS
다음 Task 또는 INTEGRATION
```

**BUILDING 진입 전 필수**: 해당 Task의 내역서(task-X-Y-N.md)를 읽고 구현 범위·완료 기준을 확인한 후 코드 작성에 착수한다.

### 3.3 도메인별 BUILDING 패턴

```
[BE] Task:
  Team Lead → SendMessage → backend-dev: "Task X-Y-N [BE] 구현 요청"
  backend-dev: BACKEND.md 기준 구현 → 코드 작성
  backend-dev → SendMessage → Team Lead: "구현 완료"

[FE] Task:
  Team Lead → SendMessage → frontend-dev: "Task X-Y-N [FE] 구현 요청"
  frontend-dev: FRONTEND.md 기준 구현 → 코드 작성
  frontend-dev → SendMessage → Team Lead: "구현 완료"

[FS] Task:
  Team Lead →
    SendMessage → backend-dev: "[FS] BE 파트 구현" (선행)
    ← backend-dev 완료 알림
    SendMessage → frontend-dev: "[FS] FE 파트 구현" (API 연동)
    ← frontend-dev 완료 알림
    또는: backend-dev + frontend-dev 동시 작업 (독립적인 부분)

[DB] Task:
  Team Lead → SendMessage → backend-dev: "SQL 마이그레이션 + ORM 동기화 + 롤백 SQL"
  backend-dev: 작업 수행 → 완료 보고
```

### 3.4 병렬 실행 최적화

```
# Task 구현 완료 후 (풀스택 예시)
backend-dev + frontend-dev: Task X-Y-N [FS] 구현 완료
  → 각자 SendMessage → Team Lead: "구현 완료"

# Team Lead: Verifier + Tester 동시 요청
Team Lead →
  SendMessage → verifier: "백엔드+프론트엔드 코드 리뷰 요청"
  SendMessage → tester: "pytest + 페이지 로드 테스트 요청"

# 결과 수집 (자동 배달)
verifier → SendMessage → Team Lead: "G2 결과"
tester → SendMessage → Team Lead: "G3 결과"

# Team Lead 종합 판정
IF verifier=PASS AND tester=PASS:
  → 다음 Task
ELSE:
  → 실패 팀원 식별 → SendMessage → 해당 개발자: "수정 요청"
```

### 3.5 Phase Template SSOT Connection

| Template 항목 | 참조 SSOT | 참조 섹션 |
|--------------|----------|----------|
| Task 도메인 분류 | `1-project-ssot.md` | Section 3 |
| 품질 게이트 기준 | `1-project-ssot.md` | Section 4 |
| 테스트 레벨/명령 | `1-project-ssot.md` | Section 5 |
| 프론트엔드 체크리스트 | `1-project-ssot.md` | Section 6 |
| 상태 파일 스키마 | `3-workflow-ssot.md` | Section 2 |
| 상태 전이 규칙 | `3-workflow-ssot.md` | Section 1.3 |
| 에러 등급/처리 | `3-workflow-ssot.md` | Section 4 |
| 백엔드 코드 규칙 | `2-architecture-ssot.md` | Section 2.2 |
| 프론트엔드 코드 규칙 | `2-architecture-ssot.md` | Section 3.2 |
| 검증 기준 체크리스트 | `2-architecture-ssot.md` | Section 8 |
| Task 내역서 생성 규칙 | `3-workflow-ssot.md` | Section 3.1 Step 2.5 |
| Task 문서 구조/명명 | `ai-rule-task-creation.md` | §3 |
| E2E 리포트 | `3-workflow-ssot.md` | Section 3.1 Step 7.5 |
| Verification Report 템플릿 | `verification-report-template.md` | 전체 |
| SSOT Lock 규칙 | `0-ssot-index.md` | SSOT Lock Rules |
| Document Authority | `0-ssot-index.md` | Document Authority Chain |
| 팀 통신 프로토콜 | `0-ssot-index.md` | 팀 통신 프로토콜 |

---

## 4. 에러 처리 체계

### 4.1 에러 분류

| 등급 | 명칭 | 설명 | 처리 |
|------|------|------|------|
| **E0** | Critical | 시스템 장애, 데이터 손실 위험 | 즉시 중단, broadcast → 전 팀원 작업 중단 |
| **E1** | Blocker | 기능 차단, 다음 단계 진행 불가 | BLOCKED 전이, Fix Task 생성 → 해당 개발자 할당 |
| **E2** | High | 기능 결함, 워크어라운드 존재 | REWINDING, 해당 개발자에게 SendMessage로 수정 요청 |
| **E3** | Medium | 품질 이슈, 기능 동작에 지장 없음 | Technical Debt 등록, 진행 가능 |
| **E4** | Low | 코드 스타일, 개선 사항 | 기록만, 현재 Phase에서 수정 불필요 |

### 4.2 에러 기록 형식

```yaml
error_log:
  - id: "ERR-001"
    grade: "E2"
    domain: "[BE]"
    state: "VERIFYING"
    task: "X-Y-2"
    description: "backend/routers/admin/template_crud.py:45 — 타입 힌트 누락"
    detected_by: "verifier"
    assigned_to: "backend-dev"
    resolved: false
    resolution: null
    timestamp: "2026-02-16T10:30:00Z"
```

### 4.3 에러 대응 플로우

```
에러 발생
  │
  ▼
에러 등급 판정 (E0~E4) + 도메인 식별 ([BE]/[FE]/[FS])
  │
  ├── E0 (Critical)
  │     → Team Lead: SendMessage(type: "broadcast"): "긴급 중단"
  │     → 사용자에게 상황 보고
  │     → 수동 개입 대기
  │
  ├── E1 (Blocker)
  │     → current_state = "BLOCKED"
  │     → Fix Task 생성 (TaskCreate + owner 할당)
  │     → Team Lead → SendMessage → 해당 팀원: "Blocker 수정 요청"
  │     → 수정 완료 후 이전 상태로 복귀
  │
  ├── E2 (High)
  │     → current_state = "REWINDING"
  │     → Team Lead → SendMessage → 해당 개발자: "수정 요청 + 상세 내역"
  │     → verifier → Team Lead → 개발자: "수정 요청"
  │     → retry_count 증가
  │
  ├── E3 (Medium)
  │     → error_log에 기록
  │     → Technical Debt로 등록
  │     → 워크플로우 계속 진행
  │
  └── E4 (Low)
        → error_log에 기록만
        → 워크플로우 계속 진행
```

### 4.4 재시도 제한

```
IF retry_count >= 3 (동일 상태에서 3회 연속 실패):
  THEN:
    1. 현재 접근 방식 폐기
    2. 에러 로그 전체를 사용자에게 보고 (도메인별 분류)
    3. 대안 제시 (다른 구현 방식, 범위 축소 등)
    4. 사용자 판단 대기
    5. (선택) 해당 팀원 shutdown → 다른 전략으로 재스폰
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

| 실패 상태 | 리와인드 대상 | 수행 작업 | 담당 팀원 |
|----------|-------------|----------|----------|
| PLAN_REVIEW 실패 | PLANNING | planner 재실행 (SendMessage) | `planner` |
| VERIFYING 실패 | BUILDING | verifier → Team Lead → 개발자 수정 | `backend-dev`/`frontend-dev` |
| TESTING 실패 | BUILDING | tester 결과 기반 → 개발자 수정 | `backend-dev`/`frontend-dev` |
| INTEGRATION 실패 (회귀) | BUILDING | 기존 API 깨뜨린 변경사항 식별·수정 | `backend-dev` |
| INTEGRATION 실패 (신규) | BUILDING | 새 API 구현 결함 수정 | `backend-dev`/`frontend-dev` |
| INTEGRATION 실패 (연동) | BUILDING | API↔UI 연동 이슈 수정 | `backend-dev` + `frontend-dev` |
| E2E 실패 (회귀) | BUILDING | 기존 E2E 깨뜨린 변경사항 식별·수정 | 해당 개발자 |
| E2E 실패 (신규) | BUILDING | E2E 시나리오 기준 수정 | 해당 개발자 |

### 5.3 리와인드 실행 절차

```
1. 실패 상태 기록
   - error_log에 실패 내용 추가 (도메인 태그 포함)
   - gate_results에 FAIL 기록 (G2_be/G2_fe 분리)

2. 리와인드 대상 결정
   - rewind_target = 리와인드 매트릭스 참조
   - current_state = "REWINDING"

3. 담당 팀원에게 수정 요청
   - Team Lead → SendMessage → 해당 팀원: "수정 요청 + 에러 상세"
   - verifier → Team Lead → 개발자: "수정 요청"

4. 상태 전이
   - current_state = rewind_target
   - retry_count += 1
   - rewind_target = null

5. 재실행
   - 팀원이 수정 → SendMessage → Team Lead: "수정 완료"
   - 수정 사항에 대해서만 재검증 (전체 재검증 아님)
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
    backend-dev가 코드 구현 완료 (SendMessage 보고),
    verifier PASS — G2_be (SendMessage 보고),
    tester PASS — G3 (SendMessage 보고),
    task-X-Y-N.md 체크리스트 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )

Task DONE 조건 ([FE] Task):
  AND(
    frontend-dev가 코드 구현 완료 (SendMessage 보고),
    verifier PASS — G2_fe (SendMessage 보고),
    페이지 로드 확인 + 콘솔 에러 0건 (tester 보고),
    task-X-Y-N.md 체크리스트 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )

Task DONE 조건 ([FS] Task):
  AND(
    backend-dev + frontend-dev 모두 구현 완료,
    verifier PASS — G2_be + G2_fe (SendMessage 보고),
    tester PASS — G3 (SendMessage 보고),
    API↔UI 연동 동작 확인,
    task-X-Y-N.md 체크리스트 완료,
    error_log에 E0/E1/E2 미해결 건 없음
  )
```

### 6.2 Phase 완료 기준

```
Phase DONE 조건:
  AND(
    모든 Task = DONE (TaskList 전체 completed),
    G1 (Plan Review) = PASS,
    G2_be (백엔드 Code Review) = PASS (해당 Task 있을 때),
    G2_fe (프론트 Code Review) = PASS (해당 Task 있을 때),
    G4 (Final Gate) = PASS,
    INTEGRATION 테스트 PASS,
    E2E 테스트 PASS (또는 대체 테스트 PASS),
    phase-X-Y-verification-report.md 작성 완료,
    blockers = [],
    phase-X-Y-final-summary.md 작성 완료,
    TEAM_SHUTDOWN 완료 (모든 팀원 shutdown + TeamDelete)
  )
```

### 6.3 완료 판정 플로우

```
Team Lead:
  1. TaskList 확인 → 모든 Task "completed"?
     NO → 남은 Task 처리 계속
     YES ↓

  2. gate_results 확인 → G1, G2_be, G2_fe, G3 모두 PASS?
     NO → 실패한 게이트로 리와인드
     YES ↓

  3. INTEGRATION 실행
     Team Lead → SendMessage → tester: "INTEGRATION 검사 실행"
     tester → SendMessage → Team Lead: "결과"
     FAIL → 해당 개발자에게 SendMessage로 수정 요청
     PASS ↓

  4. E2E 실행
     Team Lead → SendMessage → tester: "E2E 실행"
     tester → SendMessage → Team Lead: "결과"
     FAIL → 해당 개발자에게 SendMessage로 수정 요청
     PASS ↓

  4.5. E2E 리포트 작성
     → Team Lead: verifier/tester 결과 종합하여 리포트 작성
     → PASS ↓

  5. G4 Final Gate 판정
     → blockers = [] 확인
     → PASS → TEAM_SHUTDOWN

  6. TEAM_SHUTDOWN
     → SendMessage(type: "shutdown_request") × 각 팀원
     → 모든 shutdown_response(approve: true) 수신
     → TeamDelete()
     → current_state = "DONE"
```

---

## 7. 다음 작업 결정 로직

### 7.1 자동 결정 규칙

```python
def decide_next_action(status):
    """상태 파일 기반으로 다음 작업을 자동 결정"""

    # SSOT Freshness Check
    if status.ssot_version != current_ssot_version():
        return "SSOT_RELOAD: SSOT 버전 불일치, 리로드 필요"

    if ssot_modified_during_phase(status):
        return "BLOCKED: SSOT 변경 감지, Lock 프로세스 필요"

    if status.blockers:
        return "BLOCKED: 차단 이슈 먼저 해결"

    if status.current_state == "IDLE":
        return "TEAM_SETUP: TeamCreate + 팀원 스폰"

    if status.current_state == "TEAM_SETUP":
        return "PLANNING: planner에게 SendMessage로 분석 요청"

    if status.current_state == "PLANNING":
        return "PLAN_REVIEW: planner 결과 검토"

    if status.current_state == "PLAN_REVIEW":
        if status.last_action_result == "PASS":
            return "TASK_SPEC: Task 내역서 일괄 생성 + TaskCreate로 공유 TaskList 등록"
        return "REWINDING→PLANNING"

    if status.current_state == "TASK_SPEC":
        first_task = find_first_pending_task(status.task_progress)
        domain = first_task.domain
        owner = first_task.owner
        return f"BUILDING: SendMessage → {owner}: '{first_task.id} {domain} 구현 시작'"

    if status.current_state == "BUILDING":
        return "VERIFYING: SendMessage → verifier: '검증 요청'"

    if status.current_state == "VERIFYING":
        if status.last_action_result == "PASS":
            return "TESTING: SendMessage → tester: '테스트 실행 요청'"
        return "REWINDING→BUILDING: verifier→Team Lead→개발자 수정 요청"

    if status.current_state == "TESTING":
        if status.last_action_result == "PASS":
            next_task = find_next_pending_task(status.task_progress)
            if next_task:
                return f"BUILDING: SendMessage → {next_task.owner}: '{next_task.id} 구현'"
            return "INTEGRATION: SendMessage → tester: '통합 테스트 실행'"
        return "REWINDING→BUILDING: 테스트 실패 수정"

    if status.current_state == "INTEGRATION":
        if status.last_action_result == "PASS":
            return "E2E: SendMessage → tester: 'E2E 실행'"
        return "REWINDING→BUILDING: 통합 이슈 수정"

    if status.current_state == "E2E":
        if status.last_action_result == "PASS":
            return "E2E_REPORT: 리포트 작성"
        return "REWINDING→BUILDING: E2E 실패 수정"

    if status.current_state == "E2E_REPORT":
        return "TEAM_SHUTDOWN: 팀원 셧다운 + TeamDelete"

    if status.current_state == "TEAM_SHUTDOWN":
        return "DONE: Phase 완료"

    if status.current_state == "DONE":
        return "완료: 다음 Phase 준비"
```

### 7.2 Task 실행 순서 권장 패턴

```
권장 순서:
  1. [DB] 스키마/마이그레이션 (기반 작업) → backend-dev
  2. [BE] API/서비스 (데이터 계층) → backend-dev
  3. [FE] UI 페이지 (표현 계층) → frontend-dev (2와 병렬 가능)
  4. [FS] API↔UI 연동 (통합) → backend-dev + frontend-dev
  5. [TEST] 통합/E2E 테스트 (검증) → tester

병렬 가능:
  - [BE] + [FE]: 독립적이면 동시 수행 (backend-dev + frontend-dev)
  - [FS] 내부: BE 파트 → FE 파트 순차 (API 의존)
```

### 7.3 사용자 개입 필요 시점

| 시점 | 이유 | Team Lead 행동 |
|------|------|---------------|
| retry_count >= 3 | 동일 문제 반복 | 대안 제시 후 사용자 판단 요청 |
| E0 (Critical) 발생 | 시스템 장애 | broadcast → 전 팀원 중단, 사용자 보고 |
| Phase 범위 변경 필요 | 구현 중 요구사항 변경 발견 | 범위 조정 안 제시 후 승인 요청 |
| 기술적 결정 필요 | 두 가지 이상의 접근법 | 선택지와 트레이드오프 제시 |
| 도메인 간 충돌 | BE-FE 인터페이스 불일치 | Team Lead가 backend-dev + frontend-dev 간 조율 |
| SSOT 변경 필요 | Phase 중 SSOT 규칙 수정 필요 | LOCK-2 절차에 따라 일시정지 후 승인 요청 |

---

## 8. 부트로더 시퀀스

### 8.1 Cold Start (새 Phase 시작)

```
1. 사용자: "Phase X-Y 시작"

2. Team Lead:
   a. SSOT 리로드 (0→1→2→3) ← FRESH-1
   b. SSOT 버전 확인 ← FRESH-2
   c. TeamCreate(team_name: "phase-X-Y") ← 팀 생성
   d. 상태 파일 생성 (phase-X-Y-status.md)
      - ssot_version: "4.0"
      - ssot_loaded_at: (현재 시각)
      - current_state: "TEAM_SETUP"
      - team_name: "phase-X-Y"
      - team_members: []
   e. 팀원 스폰:
      - Task tool(team_name, name: "planner", subagent_type: "Plan", model: "opus")
      - Task tool(team_name, name: "backend-dev", subagent_type: "general-purpose", model: "sonnet")
      - Task tool(team_name, name: "frontend-dev", subagent_type: "general-purpose", model: "sonnet")
   f. 상태 → PLANNING
   g. SendMessage → planner: "Phase X-Y 계획 분석 요청"

3. planner (팀원):
   a. role-planner-ssot.md 로딩
   b. master-plan, navigation 분석
   c. 백엔드/프론트엔드 영향 범위 식별
   d. SendMessage → Team Lead: "분석 결과 (Task 분해, 도메인 태그, 완료 기준, 리스크)"

4. Team Lead:
   a. PLAN_REVIEW (G1) — planner 결과 검토
   b. PASS → plan.md, todo-list.md 작성
   c. SendMessage(type: "shutdown_request") → planner (계획 단계 종료)
   d. 상태 → TASK_SPEC
   e. Task 내역서 일괄 생성
   f. TaskCreate × N → TaskUpdate(owner) × N (공유 TaskList에 등록)
   g. 상태 → BUILDING
   h. SendMessage → backend-dev: "Task X-Y-1 [DB] 구현 시작"
   i. SendMessage → frontend-dev: "Task X-Y-3 [FE] 구현 시작" (병렬 가능)
```

### 8.2 Warm Start (중단 재개)

```
1. Team Lead:
   a. SSOT 리로드 (0→1→2→3) ← FRESH-1
   b. phase-X-Y-status.md 읽기 ← ENTRY-1
   c. ssot_version 확인 ← ENTRY-3
   d. team_name 확인 → 팀 상태 확인
      - 팀이 존재하면: 팀원 idle 상태 확인, 필요 시 SendMessage로 재개
      - 팀이 없으면: TeamCreate + 팀원 재스폰
   e. team_members 상태 확인 (idle/working)
   f. current_state 기반 다음 행동 결정
   g. blockers 확인 ← ENTRY-4
   h. task_progress 확인 (TaskList로 공유 상태 확인)
   i. 해당 팀원에게 SendMessage로 작업 재개 지시
```

### 8.3 세션 전환 시 컨텍스트 유지

AI 세션이 끊기고 새 세션에서 재개할 때:

```
1. SSOT 로딩 (0→1→2→3) ← FRESH-1
2. phase-X-Y-status.md 읽기 ← ENTRY-1
3. ssot_version 확인 ← FRESH-2, ENTRY-3
4. team_name 확인 → TeamCreate (팀 재생성, 이전 팀은 소멸)
5. 필요 팀원 재스폰 (현재 상태에 맞는 팀원만)
   - BUILDING 중: backend-dev / frontend-dev
   - VERIFYING 중: verifier + 해당 개발자
   - TESTING 중: tester
6. current_state와 current_task 기반으로 재개 지점 판단
7. error_log 확인하여 이전 실패 내역 파악
8. gate_results 확인하여 통과한 게이트 재실행 방지
9. SendMessage → 팀원: "재개 지점부터 작업 시작"
```

---

## 9. Phase Chain (자동 순차 실행)

### 9.1 개요

Phase Chain은 복수의 Phase를 사전 정의된 순서로 자동 순차 실행하는 프로토콜이다.
각 Phase 완료(DONE) 후 `/clear`로 컨텍스트를 초기화하고, 다음 Phase를 자동 시작한다.

### 9.2 Phase Chain 정의 파일

```yaml
# docs/phases/phase-chain-{name}.md
---
chain_name: "phase-15-fullstack"
phases: ["15-4", "15-5", "15-6", "15-7", "15-8"]
current_index: 0          # 현재 실행 중인 Phase 인덱스
status: "running"          # pending | running | completed | aborted
ssot_version: "4.3"
created_at: "2026-02-16T..."
---
```

### 9.3 Phase Chain 실행 프로토콜

```
[1] Chain 파일 생성 (phase-chain-{name}.md)
     │
     ▼
[2] Phase[current_index] Cold Start (Section 8.1)
     │  ├── SSOT 리로드 (FRESH-1)
     │  ├── TeamCreate + 팀원 스폰
     │  └── 워크플로우 실행 (PLANNING → ... → DONE)
     │
     ▼
[3] Phase DONE 도달
     │  ├── TEAM_SHUTDOWN + TeamDelete
     │  ├── Chain 파일 업데이트: current_index += 1
     │  └── 사용자에게 Phase 완료 리포트 출력
     │
     ▼
[4] 토큰 최적화: `/clear` 실행
     │  ├── 컨텍스트 윈도우 초기화
     │  └── Chain 파일은 디스크에 유지 (컨텍스트 독립)
     │
     ▼
[5] 다음 Phase 자동 시작
     │  ├── Chain 파일 읽기 → phases[current_index]
     │  ├── current_index >= len(phases)? → Chain 완료
     │  └── Phase Cold Start (Step 2로 복귀)
```

### 9.4 `/clear` 후 컨텍스트 복구

`/clear` 이후 새 세션에서 Chain을 이어가는 부트로더:

```
1. Chain 파일 읽기 (phase-chain-{name}.md)
2. current_index 확인
3. current_index < len(phases)?
   YES → phases[current_index]의 status.md 확인
         ├── DONE이 아님 → Warm Start (Section 8.2)
         └── DONE → current_index += 1, 다음 Phase
   NO  → Chain 완료
4. SSOT 리로드 (FRESH-1)
5. Phase Cold Start 실행
```

### 9.5 Chain 중단·재개

| 상황 | 처리 |
|------|------|
| Phase 실패 (retry >= 3) | Chain 일시정지, 사용자 판단 대기 |
| 사용자 중단 요청 | chain status = "aborted", 현재 Phase TEAM_SHUTDOWN |
| 세션 끊김 | Chain 파일로 재개 가능 (Section 9.4) |
| SSOT 변경 필요 | LOCK-2 절차 후 Chain 재개 |

### 9.6 Phase Chain 규칙

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **CHAIN-1** | Phase 독립성 | 각 Phase는 독립 실행 가능해야 함 (Chain 없이도 동작) |
| **CHAIN-2** | `/clear` 필수 | Phase 간 전환 시 `/clear`로 토큰 초기화 |
| **CHAIN-3** | Chain 파일 유지 | `/clear` 후에도 Chain 파일은 디스크에 영속 |
| **CHAIN-4** | 순차 보장 | phases 배열 순서대로만 실행 (건너뛰기 금지) |
| **CHAIN-5** | 완료 리포트 | 각 Phase DONE 시 1줄 요약을 Chain 파일에 기록 |

---

## 10. 참조 문서 매핑

| 워크플로우 단계 | 참조 규칙 문서 | 참조 Charter | 담당 팀원 |
|---------------|--------------|-------------|----------|
| TEAM_SETUP | `0-ssot-index.md` (팀 라이프사이클) | `LEADER.md` | Team Lead |
| PLANNING | `ai-rule-phase-plan-todo-generation.md` | — | `planner` |
| TASK_SPEC | `ai-rule-task-creation.md` | — | Team Lead |
| BUILDING [BE/DB] | `ai-rule-task-creation.md` | `BACKEND.md` | `backend-dev` |
| BUILDING [FE] | `ai-rule-task-creation.md` | `FRONTEND.md` | `frontend-dev` |
| BUILDING [FS] | `ai-rule-task-creation.md` | `BACKEND.md` + `FRONTEND.md` | `backend-dev` + `frontend-dev` |
| VERIFYING | `ai-rule-task-inspection.md` | `QA.md` | `verifier` |
| TESTING [BE] | `integration-test-guide.md` | `QA.md` | `tester` |
| TESTING [FE] | `phase-unit-user-test-guide.md` | `QA.md` | `tester` |
| INTEGRATION | `integration-test-guide.md` §4-§5 | `QA.md` | `tester` |
| E2E | `phase-unit-user-test-guide.md` §0 | `QA.md` | `tester` |
| E2E_REPORT | `verification-report-template.md` | `QA.md` | Team Lead |
| TEAM_SHUTDOWN | `0-ssot-index.md` (팀 라이프사이클) | `LEADER.md` | Team Lead |

**Charter 파일 경로**:

| Charter | 경로 |
|---------|------|
| LEADER | `docs/rules/role/LEADER.md` |
| BACKEND | `docs/rules/role/BACKEND.md` |
| FRONTEND | `docs/rules/role/FRONTEND.md` |
| QA | `docs/rules/role/QA.md` |

---

## 11. 버전 히스토리

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초안 작성 (백엔드 전용) | Claude Code (Backend & Logic Expert) |
| 2.0 | 2026-02-09 | 프론트엔드 워크플로우 추가, 도메인 태그, G2 분리 | Claude Code (Backend & Logic Expert) |
| 3.0 | 2026-02-15 | ENTRYPOINT 정의, SSOT Lock/Freshness enforcement, 부트로더 시퀀스 | Claude Code (Backend & Logic Expert) |
| 3.1 | 2026-02-16 | TASK_SPEC/E2E_REPORT 상태 추가 | Claude Code (Backend & Logic Expert) |
| 3.2 | 2026-02-16 | INTEGRATION/E2E 절차 상세화 (3단계 검사, 회귀 분기) | Claude Code (Backend & Logic Expert) |
| 4.0 | 2026-02-16 | **Agent Teams 전환**: TEAM_SETUP/TEAM_SHUTDOWN 상태 추가, 모든 워크플로우를 SendMessage 기반 팀 통신으로 전환, 부트로더에 TeamCreate/팀원 스폰 추가 | Claude Code (Backend & Logic Expert) |
| 4.1 | 2026-02-16 | Hub-and-Spoke 통신 모델 (Peer DM 제거). 모델 지정: planner=opus, 나머지=sonnet. 자동화 주기 점검 | Claude Code (Backend & Logic Expert) |
| 4.2 | 2026-02-16 | 자동화 트리거 추가: TaskCompleted hook (품질 자동 검사) + `/verify-implementation` skill (G2 심층 리뷰) | Claude Code (Backend & Logic Expert) |
| 4.3 | 2026-02-16 | Phase Chain (자동 순차 실행) 프로토콜 추가: Section 9 신설. `/clear` 기반 토큰 최적화, Chain 파일 정의, 중단·재개 규칙 | Claude Code (Backend & Logic Expert) |
