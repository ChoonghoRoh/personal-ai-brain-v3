# SSOT — 워크플로우 (요약)

**버전**: 5.0-renewal
**최종 수정**: 2026-02-17
**기반**: 3-workflow-ssot.md (v4.5, 1,059줄)

---

## 0. ENTRYPOINT 정의

Phase 실행의 **단일 진입점**은 `phase-X-Y-status.md` 파일이다.

### ENTRYPOINT 규칙

| 규칙 ID     | 규칙                     | 설명                                                                                  |
| ----------- | ------------------------ | ------------------------------------------------------------------------------------- |
| **ENTRY-1** | 단일 진입점              | 모든 Phase 작업은 `docs/phases/phase-X-Y/phase-X-Y-status.md`를 먼저 읽는 것으로 시작 |
| **ENTRY-2** | 상태 기반 분기           | `current_state` 값에 따라 다음 행동을 결정                                            |
| **ENTRY-3** | SSOT 버전 확인           | 진입 시 `ssot_version` 필드와 현재 SSOT 버전의 일치 여부를 확인                       |
| **ENTRY-4** | Blocker 우선 확인        | `blockers` 배열이 비어있지 않으면 다른 작업보다 Blocker 해결을 우선                   |
| **ENTRY-5** | 진입점 외 직접 시작 금지 | status 파일을 읽지 않고 Task 구현을 바로 시작하는 것을 금지                           |

**ENTRYPOINT 플로우**:

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

➜ [상세 ENTRYPOINT 규칙](../claude/3-workflow-ssot.md#0-entrypoint-정의)

---

## 1. 워크플로우 상태 머신

### 1.1 상태 정의 (8단계)

| 상태 코드     | 상태명           | 설명                                    | 진입 조건                 |
| ------------- | ---------------- | --------------------------------------- | ------------------------- |
| `IDLE`        | 대기             | Phase 미시작                            | 초기 상태                 |
| `TEAM_SETUP`  | 팀 구성          | TeamCreate + 팀원 스폰                  | Phase 시작 명령           |
| `PLANNING`    | 계획             | planner 팀원이 요구사항 분석, Task 분해 | 팀 구성 완료              |
| `PLAN_REVIEW` | 계획 검토 (G1)   | Team Lead가 planner 결과 검증           | PLANNING 완료             |
| `TASK_SPEC`   | Task 내역서 작성 | Task별 실행 계획 문서 생성              | PLAN_REVIEW 통과          |
| `BUILDING`    | 구현             | backend-dev/frontend-dev가 코드 작성    | TASK_SPEC 완료            |
| `VERIFYING`   | 검증 (G2)        | verifier가 코드 리뷰 → Team Lead 보고   | BUILDING 완료 (Task 단위) |
| `TESTING`     | 테스트 (G3)      | tester가 테스트 실행 → Team Lead 보고   | VERIFYING 통과            |

**추가 상태**: INTEGRATION, E2E, E2E_REPORT, TEAM_SHUTDOWN, BLOCKED, REWINDING, DONE

---

### 1.2 상태 전이 다이어그램

```
IDLE → TEAM_SETUP → PLANNING → PLAN_REVIEW → TASK_SPEC
                         ↑          │ FAIL
                         └──────────┘ REWINDING

TASK_SPEC → BUILDING → VERIFYING → TESTING → (다음 Task 또는 INTEGRATION)
                ↑          │ FAIL      │ FAIL
                └──────────┴───────────┘ REWINDING

모든 Task 완료 → INTEGRATION → E2E → E2E_REPORT → TEAM_SHUTDOWN → DONE
                      │ FAIL     │ FAIL
                      └──────────┘ REWINDING → BUILDING

※ 어떤 상태에서든 BLOCKED로 전이 가능 (Blocker 이슈 발생 시)
```

---

### 1.3 상태 전이 규칙

| 현재 상태     | 이벤트           | 다음 상태                             | 조건                                               |
| ------------- | ---------------- | ------------------------------------- | -------------------------------------------------- |
| IDLE          | Phase 시작       | TEAM_SETUP                            | SSOT 리로드 완료 (FRESH-1)                         |
| TEAM_SETUP    | 팀 구성 완료     | PLANNING                              | TeamCreate + 필요 팀원 스폰 완료                   |
| PLANNING      | planner 완료     | PLAN_REVIEW                           | plan + todo-list 생성됨 (도메인 태그 포함)         |
| PLAN_REVIEW   | 검토 통과        | TASK_SPEC                             | 완료 기준 명확, Task 3~7개, 도메인 분류 완료       |
| TASK_SPEC     | 내역서 생성 완료 | BUILDING                              | 모든 Task에 task-X-Y-N.md 생성됨                   |
| PLAN_REVIEW   | 검토 실패        | REWINDING→PLANNING                    | 완료 기준 불명확 또는 범위 초과                    |
| BUILDING      | 구현 완료        | VERIFYING                             | Task 단위 코드 작성 완료 (개발자 SendMessage 보고) |
| VERIFYING     | PASS             | TESTING                               | 도메인별 Critical 0건 (verifier SendMessage 보고)  |
| VERIFYING     | FAIL             | REWINDING→BUILDING                    | verifier → Team Lead → 개발자 수정 요청            |
| TESTING       | PASS             | BUILDING (다음 Task) 또는 INTEGRATION | tester SendMessage 보고                            |
| TESTING       | FAIL             | REWINDING→BUILDING                    | 테스트 실패                                        |
| INTEGRATION   | PASS             | E2E                                   | Dev API 회귀 PASS + 현재 API PASS + 통합 연동 PASS |
| INTEGRATION   | FAIL             | REWINDING→BUILDING                    | 실패 도메인 식별 후 해당 개발자에게 수정 요청      |
| E2E           | PASS             | E2E_REPORT                            | 기존 E2E 회귀 PASS + 현재 E2E PASS                 |
| E2E           | FAIL             | REWINDING→BUILDING                    | E2E 결함 수정                                      |
| E2E_REPORT    | 리포트 작성 완료 | TEAM_SHUTDOWN                         | Verification Report + E2E 리포트 작성 완료         |
| TEAM_SHUTDOWN | 팀 해산 완료     | DONE                                  | 모든 팀원 shutdown + TeamDelete                    |

➜ [상세 전이 규칙](../claude/3-workflow-ssot.md#13-상태-전이-규칙)

---

## 2. 상태 파일 (Status File)

### 2.1 파일 경로

```
docs/phases/phase-X-Y/phase-X-Y-status.md
```

### 2.2 상태 파일 스키마 (핵심 필드)

```yaml
---
phase: "X-Y"
ssot_version: "5.0-renewal" # 현재 참조 중인 SSOT 버전
current_state: "BUILDING" # 상태 머신의 현재 상태
current_task: "X-Y-2" # 현재 작업 중인 Task ID
current_task_domain: "[FE]" # 현재 Task 도메인 태그
team_name: "phase-X-Y" # Agent Teams 팀 이름
team_members: # 현재 활성 팀원 목록
  - { name: "backend-dev", status: "idle" }
  - { name: "frontend-dev", status: "working" }
last_action: "Task X-Y-1 [BE] API 구현 완료 (backend-dev)"
last_action_result: "PASS" # PASS | FAIL | PARTIAL | N/A
next_action: "Task X-Y-2 [FE] UI 페이지 구현 시작 (frontend-dev)"
blockers: [] # 차단 이슈 목록
gate_results: # 품질 게이트 통과 기록
  G1_plan_review: null # PASS | FAIL | null
  G2_code_review_be: null # 백엔드 코드 리뷰 (verifier)
  G2_code_review_fe: null # 프론트엔드 코드 리뷰 (verifier)
  G3_test_gate: null # tester 테스트 결과
  G4_final_gate: null
task_progress: # Task별 진행 현황
  X-Y-1: { status: "DONE", domain: "[BE]", owner: "backend-dev" }
  X-Y-2: { status: "IN_PROGRESS", domain: "[FE]", owner: "frontend-dev" }
  X-Y-3: { status: "PENDING", domain: "[FS]", owner: "backend-dev+frontend-dev" }
last_updated: "2026-02-17T10:30:00Z"
---
```

➜ [상세 스키마](../claude/3-workflow-ssot.md#22-상태-파일-스키마)

---

## 3. 품질 게이트 (Quality Gates)

### 3.1 게이트 구조

```
[G1: Plan Review]     planner 분석 → Team Lead 검토
        ↓
[G2: Code Review]     verifier가 BE+FE 코드 검증 → Team Lead 보고
        ↓
[G3: Test Gate]       tester가 테스트 실행 + 커버리지 확인 → Team Lead 보고
        ↓
[G4: Final Gate]      Team Lead가 G2+G3 종합 판정
```

### 3.2 게이트별 통과 기준

| 게이트 | 백엔드 기준                       | 프론트엔드 기준                  | 공통 기준                               |
| ------ | --------------------------------- | -------------------------------- | --------------------------------------- |
| **G1** | API Spec 확정, DB 스키마 정의     | 페이지 구조/동선 정의            | 완료 기준 명확, Task 3~7개, 리스크 식별 |
| **G2** | Critical 0건, ORM 사용, 타입 힌트 | CDN 미사용, ESM, innerHTML+esc() | 보안 취약점 없음                        |
| **G3** | pytest PASS, 커버리지 ≥80%        | 페이지 로드 OK, 콘솔 에러 0건    | 회귀 테스트 통과                        |
| **G4** | G2 PASS + G3 PASS                 | G2 PASS + G3 PASS                | Blocker 0건                             |

### 3.3 판정 기준

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

➜ [상세 게이트 규칙](../claude/3-workflow-ssot.md#4-품질-게이트-quality-gates)

---

## 4. SSOT Lock Rules

Phase 실행 중 SSOT 문서의 무분별한 변경을 방지하기 위한 규칙이다.

| 규칙 ID    | 규칙                         | 설명                                                                         |
| ---------- | ---------------------------- | ---------------------------------------------------------------------------- |
| **LOCK-1** | Phase 실행 중 SSOT 변경 금지 | `current_state`가 `IDLE` 또는 `DONE`이 아닌 동안 SSOT 4개 파일 수정 불가     |
| **LOCK-2** | 변경 필요 시 Phase 일시정지  | SSOT 수정이 불가피하면 `current_state`를 `BLOCKED`로 전이 후 변경            |
| **LOCK-3** | 변경 후 리로드 필수          | SSOT 변경 후 반드시 모든 팀원에게 SendMessage로 리로드 지시                  |
| **LOCK-4** | 팀원 SSOT 수정 금지          | 팀원 에이전트는 SSOT를 읽기 전용으로만 참조 (backend-dev, frontend-dev 포함) |
| **LOCK-5** | 변경 이력 필수 기록          | SSOT 변경 시 해당 파일의 버전 히스토리에 반드시 기록                         |

**Lock 상태 머신**:

```
Phase 실행 중 (PLANNING~E2E_REPORT)
  │
  ├── SSOT 변경 필요 발견
  │     → current_state = BLOCKED (사유: "SSOT 변경 필요")
  │     → 사용자 승인 요청
  │     → 승인 시: SSOT 수정 → 버전 갱신
  │     → SendMessage(type: "broadcast") — "SSOT 리로드 필요" 전파
  │     → 리로드 완료 후: 이전 상태로 복귀
  │
  └── Phase 미실행 (IDLE / DONE)
        → SSOT 수정 가능 (버전 갱신 필수)
```

➜ [상세 Lock 규칙](../claude/0-ssot-index.md#ssot-lock-rules)

---

## 5. Task 실행 프로세스

### 5.1 Task 단위 실행 흐름

```
[1] Team Lead: phase-X-Y-status.md 읽기 → current_task 확인
  │
  ▼
[2] Team Lead: TaskList 조회 → 해당 Task 확인
  │
  ▼
[3] Team Lead: SendMessage → 해당 팀원(backend-dev 또는 frontend-dev)에게 Task 지시
  │   내용: "Task X-Y-N 구현 요청, 완료 기준 확인, 구현 후 SendMessage 보고"
  │
  ▼
[4] 팀원: TaskList로 할당된 작업 확인 → 구현 시작
  │
  ▼
[5] 팀원: 구현 완료 → TaskUpdate(status: "completed")
  │
  ▼
[6] 팀원: SendMessage → Team Lead에게 완료 보고
  │   내용: "Task X-Y-N 구현 완료, 변경 파일 목록, 확인 요청"
  │
  ▼
[7] Team Lead: verifier 스폰 (지연 스폰) → SendMessage(검증 요청)
  │
  ▼
[8] verifier: 코드 리뷰 → SendMessage → Team Lead에게 판정 보고
  │   PASS → [9]
  │   FAIL → Team Lead → SendMessage(수정 요청) → 팀원 → [4]로 돌아가기
  │
  ▼
[9] Team Lead: tester 스폰 (지연 스폰) → SendMessage(테스트 요청)
  │
  ▼
[10] tester: 테스트 실행 → SendMessage → Team Lead에게 결과 보고
  │   PASS → [11]
  │   FAIL → Team Lead → SendMessage(수정 요청) → 팀원 → [4]로 돌아가기
  │
  ▼
[11] Team Lead: G4 종합 판정 (PASS) → current_task 업데이트 (다음 Task로)
```

---

## 6. 참조 문서

| 문서            | 용도                     | 경로                                                  |
| --------------- | ------------------------ | ----------------------------------------------------- |
| 상세 워크플로우 | 전체 워크플로우 상세     | [3-workflow-ssot.md](../claude/3-workflow-ssot.md)    |
| Leader Charter  | Team Lead 역할           | `docs/rules/role/LEADER.md`                           |
| 실행 워크플로우 | 전체 실행 순서           | `docs/rules/ai-execution-workflow.md`                 |
| Task 생성 규칙  | Task 문서 생성·명명·검증 | `docs/rules/ai/references/ai-rule-task-creation.md`   |
| Task 검사 규칙  | Task 완료 검사·산출물    | `docs/rules/ai/references/ai-rule-task-inspection.md` |

---

**문서 관리**:

- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 기반: 3-workflow-ssot.md (v4.5, 1,059줄 → 300줄 요약)
