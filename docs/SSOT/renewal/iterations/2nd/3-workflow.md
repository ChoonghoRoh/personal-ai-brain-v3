# SSOT — 워크플로우 (요약 v2)

**버전**: 5.0-renewal-r2
**최종 수정**: 2026-02-17
**기반**: 3-workflow-ssot.md (v4.5, 1,059줄)

---

## 0. ENTRYPOINT 정의

Phase 실행의 **단일 진입점**은 `phase-X-Y-status.md` 파일이다.

### ENTRYPOINT 규칙

| 규칙 ID     | 규칙                     | 설명                                                                                  |
| ----------- | ------------------------ | ------------------------------------------------------------------------------------- |
| **ENTRY-1** | 단일 진입점              | 모든 Phase 작업은 `docs/phases/phase-X-Y/phase-X-Y-status.md`를 먼저 읽는 것으로 시작 |
| **ENTRY-2** | 상태 기반 분기           | `current_state` 값에 따라 다음 행동을 결정 ([§3.1](#31-상태별-action-table) 참조)     |
| **ENTRY-3** | SSOT 버전 확인           | 진입 시 `ssot_version` 필드와 현재 SSOT 버전의 일치 여부를 확인                       |
| **ENTRY-4** | Blocker 우선 확인        | `blockers` 배열이 비어있지 않으면 다른 작업보다 Blocker 해결을 우선                   |
| **ENTRY-5** | 진입점 외 직접 시작 금지 | status 파일을 읽지 않고 Task 구현을 바로 시작하는 것을 금지                           |

**ENTRYPOINT 플로우**:

```
세션 시작 / Phase 재개
  │
  ▼
[1] SSOT 로딩 (0→1→2→3) ← FRESH-1
  │
  ▼
[2] phase-X-Y-status.md 읽기 ← ENTRY-1
  │
  ▼
[3] ssot_version 확인 ← ENTRY-3
  │
  ├── 불일치 → SSOT 리로드 ← FRESH-3
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

➜ [상세 ENTRYPOINT 규칙](../claude/3-workflow-ssot.md#0-entrypoint-정의)

---

## 1. 워크플로우 상태 머신

### 1.1 상태 정의 (14개)

| 상태 코드       | 상태명           | 설명                                    | 진입 조건                 |
| --------------- | ---------------- | --------------------------------------- | ------------------------- |
| `IDLE`          | 대기             | Phase 미시작                            | 초기 상태                 |
| `TEAM_SETUP`    | 팀 구성          | TeamCreate + 팀원 스폰                  | Phase 시작 명령           |
| `PLANNING`      | 계획             | planner 팀원이 요구사항 분석, Task 분해 | 팀 구성 완료              |
| `PLAN_REVIEW`   | 계획 검토 (G1)   | Team Lead가 planner 결과 검증           | PLANNING 완료             |
| `TASK_SPEC`     | Task 내역서 작성 | Task별 실행 계획 문서 생성              | PLAN_REVIEW 통과          |
| `BUILDING`      | 구현             | backend-dev/frontend-dev가 코드 작성    | TASK_SPEC 완료            |
| `VERIFYING`     | 검증 (G2)        | verifier가 코드 리뷰 → Team Lead 보고   | BUILDING 완료 (Task 단위) |
| `TESTING`       | 테스트 (G3)      | tester가 테스트 실행 → Team Lead 보고   | VERIFYING 통과            |
| `INTEGRATION`   | 통합 테스트      | Phase 전체 통합 검증 (API↔UI 연동)      | 모든 Task TESTING 통과    |
| `E2E`           | E2E 테스트       | 사용자 시나리오 기반 전체 테스트        | INTEGRATION 통과          |
| `E2E_REPORT`    | E2E 리포트       | Verification Report + E2E 리포트 작성   | E2E 통과                  |
| `TEAM_SHUTDOWN` | 팀 해산          | 팀원 셧다운 + TeamDelete                | E2E_REPORT 완료           |
| `BLOCKED`       | 차단             | Blocker 이슈 발생                       | 어떤 상태에서든 진입 가능 |
| `REWINDING`     | 리와인드         | 이전 상태로 롤백 중                     | FAIL 판정 시              |
| `DONE`          | 완료             | Phase 종료                              | TEAM_SHUTDOWN 완료        |

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

## 2. 상태 파일 (Status File)

### 2.1 파일 경로

```
docs/phases/phase-X-Y/phase-X-Y-status.md
```

### 2.2 상태 파일 스키마 (핵심 필드)

```yaml
---
phase: "X-Y"
ssot_version: "5.0-renewal-r2" # 현재 참조 중인 SSOT 버전
ssot_loaded_at: "2026-02-17T10:00:00Z"
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
rewind_target: null # REWINDING 시 목표 상태
retry_count: 0 # 현재 상태 재시도 횟수 (최대 3)
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
error_log: [] # 누적 에러 기록
last_updated: "2026-02-17T10:30:00Z"
---
```

➜ [상세 스키마](../claude/3-workflow-ssot.md#22-상태-파일-스키마)

---

## 3. 워크플로우 실행

### 3.1 상태별 Action Table

| 현재 상태         | 다음 행동                                                              | 담당                 |
| ----------------- | ---------------------------------------------------------------------- | -------------------- |
| **IDLE**          | TeamCreate + 팀원 스폰                                                 | Team Lead            |
| **TEAM_SETUP**    | SendMessage → planner: "Phase X-Y 계획 분석 요청"                      | Team Lead            |
| **PLANNING**      | planner 결과 대기 → PLAN_REVIEW로 전이                                 | Team Lead            |
| **PLAN_REVIEW**   | planner 결과 검토 → PASS: TASK_SPEC, FAIL: REWINDING→PLANNING          | Team Lead            |
| **TASK_SPEC**     | Task 내역서 일괄 생성 (task-X-Y-N.md × N) + TaskCreate                 | Team Lead            |
| **BUILDING**      | SendMessage → 팀원: "Task 구현 시작" (backend-dev/frontend-dev)        | 팀원                 |
| **VERIFYING**     | SendMessage → verifier: "검증 요청" → PASS: TESTING, FAIL: REWINDING   | Team Lead + verifier |
| **TESTING**       | SendMessage → tester: "테스트 실행" → PASS: 다음 Task 또는 INTEGRATION | Team Lead + tester   |
| **INTEGRATION**   | tester가 통합 테스트 실행 → PASS: E2E, FAIL: REWINDING                 | tester               |
| **E2E**           | tester가 E2E 실행 → PASS: E2E_REPORT, FAIL: REWINDING                  | tester               |
| **E2E_REPORT**    | Verification Report + E2E 리포트 작성 → TEAM_SHUTDOWN                  | Team Lead            |
| **TEAM_SHUTDOWN** | SendMessage(shutdown_request) × N → TeamDelete → DONE                  | Team Lead            |
| **BLOCKED**       | Blocker 해결 → 이전 상태 복귀                                          | 해당 팀원            |
| **REWINDING**     | rewind_target 상태로 전이 → 재시도                                     | Team Lead            |
| **DONE**          | Phase 완료, 다음 Phase 준비                                            | Team Lead            |

### 3.2 상태별 상세 플로우

#### IDLE → TEAM_SETUP

```
1. Team Lead: SSOT 리로드 (0→1→2→3) ← FRESH-1
2. Team Lead: TeamCreate(team_name: "phase-X-Y")
3. Team Lead: Task tool로 팀원 스폰:
   - planner (Plan/opus)
   - backend-dev (general-purpose/sonnet)
   - frontend-dev (general-purpose/sonnet)
4. 상태 파일 생성 (phase-X-Y-status.md)
5. current_state = "TEAM_SETUP"
6. current_state = "PLANNING"
7. SendMessage → planner: "Phase X-Y 계획 분석 요청"
```

#### BUILDING → VERIFYING → TESTING

```
[BUILDING]
Team Lead → SendMessage → backend-dev: "Task X-Y-N [BE] 구현 시작"
backend-dev: 코드 작성 (backend/, tests/)
backend-dev → SendMessage → Team Lead: "구현 완료"
  │
  ▼
[VERIFYING]
Team Lead → SendMessage → verifier: "검증 요청"
verifier: 코드 리뷰 (Critical/High 체크)
verifier → SendMessage → Team Lead: "G2 결과: PASS/FAIL"
  │
  ├── FAIL → Team Lead → SendMessage → backend-dev: "수정 요청"
  │         → REWINDING → BUILDING
  │
  ▼ PASS
[TESTING]
Team Lead → SendMessage → tester: "테스트 실행"
tester: pytest 실행 + 커버리지 확인
tester → SendMessage → Team Lead: "G3 결과: PASS/FAIL"
  │
  ├── FAIL → REWINDING → BUILDING
  │
  ▼ PASS
다음 Task 또는 INTEGRATION
```

---

## 4. 품질 게이트 (Quality Gates)

### 4.1 게이트 구조

```
[G1: Plan Review]     planner 분석 → Team Lead 검토
        ↓
[G2: Code Review]     verifier가 BE+FE 코드 검증 → Team Lead 보고
        ↓
[G3: Test Gate]       tester가 테스트 실행 + 커버리지 확인
        ↓
[G4: Final Gate]      Team Lead가 G2+G3 종합 판정
```

### 4.2 게이트별 통과 기준

| 게이트 | 백엔드 기준                       | 프론트엔드 기준                  | 공통 기준                               |
| ------ | --------------------------------- | -------------------------------- | --------------------------------------- |
| **G1** | API Spec 확정, DB 스키마 정의     | 페이지 구조/동선 정의            | 완료 기준 명확, Task 3~7개, 리스크 식별 |
| **G2** | Critical 0건, ORM 사용, 타입 힌트 | CDN 미사용, ESM, innerHTML+esc() | 보안 취약점 없음                        |
| **G3** | pytest PASS, 커버리지 ≥80%        | 페이지 로드 OK, 콘솔 에러 0건    | 회귀 테스트 통과                        |
| **G4** | G2 PASS + G3 PASS                 | G2 PASS + G3 PASS                | Blocker 0건                             |

### 4.3 판정 기준

```
G4 Final Gate 판정 로직:

IF (G2_backend = PASS) AND (G2_frontend = PASS)
   AND (G3 = PASS) AND (Blockers = []):
    최종 판정 = "PASS"

ELSE IF (어디든 Critical 이슈):
    최종 판정 = "FAIL"
    → 해당 게이트로 리와인드

ELSE IF (High 이슈 있음):
    최종 판정 = "PARTIAL"
    → Tech Debt 등록 + 진행 가능 (사용자 판단)
```

---

## 5. 에러 처리

### 5.1 에러 등급

| 등급   | 명칭     | 설명                             | 처리                               |
| ------ | -------- | -------------------------------- | ---------------------------------- |
| **E0** | Critical | 시스템 장애, 데이터 손실 위험    | 즉시 중단, broadcast → 사용자 보고 |
| **E1** | Blocker  | 기능 차단, 다음 단계 진행 불가   | BLOCKED 전이, Fix Task 생성        |
| **E2** | High     | 기능 결함, 워크어라운드 존재     | REWINDING, 수정 요청               |
| **E3** | Medium   | 품질 이슈, 기능 동작에 지장 없음 | Technical Debt 등록                |
| **E4** | Low      | 코드 스타일, 개선 사항           | 기록만                             |

### 5.2 재시도 제한

```
IF retry_count >= 3 (동일 상태에서 3회 연속 실패):
  THEN:
    1. 현재 접근 방식 폐기
    2. 에러 로그 전체를 사용자에게 보고 (도메인별 분류)
    3. 대안 제시 (다른 구현 방식, 범위 축소 등)
    4. 사용자 판단 대기
```

---

## 6. 리와인드 (Rewind)

### 6.1 리와인드 매트릭스

| 실패 상태        | 리와인드 대상 | 담당 팀원                    |
| ---------------- | ------------- | ---------------------------- |
| PLAN_REVIEW 실패 | PLANNING      | `planner`                    |
| VERIFYING 실패   | BUILDING      | `backend-dev`/`frontend-dev` |
| TESTING 실패     | BUILDING      | `backend-dev`/`frontend-dev` |
| INTEGRATION 실패 | BUILDING      | 해당 개발자                  |
| E2E 실패         | BUILDING      | 해당 개발자                  |

### 6.2 리와인드 실행 절차

```
1. 실패 상태 기록 (error_log, gate_results)
2. rewind_target 결정
3. current_state = "REWINDING"
4. Team Lead → SendMessage → 해당 팀원: "수정 요청"
5. current_state = rewind_target
6. retry_count += 1
7. 재실행
```

---

## 7. 참조 문서

| 주제                      | 링크                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------- |
| **ENTRYPOINT 상세**       | [claude/3-workflow-ssot.md § 0](../claude/3-workflow-ssot.md#0-entrypoint-정의)       |
| **상태 전이 규칙 상세**   | [claude/3-workflow-ssot.md § 1.3](../claude/3-workflow-ssot.md#13-상태-전이-규칙)     |
| **상태 파일 스키마 상세** | [claude/3-workflow-ssot.md § 2](../claude/3-workflow-ssot.md#2-상태-파일-status-file) |
| **Phase 전체 흐름**       | [claude/3-workflow-ssot.md § 3](../claude/3-workflow-ssot.md#3-워크플로우-실행-순서)  |
| **에러 처리 상세**        | [claude/3-workflow-ssot.md § 4](../claude/3-workflow-ssot.md#4-에러-처리-체계)        |
| **리와인드 상세**         | [claude/3-workflow-ssot.md § 5](../claude/3-workflow-ssot.md#5-리와인드-rewind-체계)  |
| **작업 완료 판정**        | [claude/3-workflow-ssot.md § 6](../claude/3-workflow-ssot.md#6-작업-완료-판정)        |
| **다음 작업 결정 로직**   | [claude/3-workflow-ssot.md § 7](../claude/3-workflow-ssot.md#7-다음-작업-결정-로직)   |

---

**문서 관리**:

- 버전: 5.0-renewal-r2 (2nd iteration)
- 최종 수정: 2026-02-17
- 1차 대비 변경: 상태별 Action Table 추가 (§3.1), 줄 수 유지 (304줄 → 310줄)
- 기반: 3-workflow.md (1st iteration, 304줄)
