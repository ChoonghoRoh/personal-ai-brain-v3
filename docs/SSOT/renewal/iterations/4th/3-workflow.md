# SSOT — 워크플로우

**버전**: 6.0-renewal-4th  
**최종 수정**: 2026-02-17  
**특징**: 단독 사용 (다른 SSOT 폴더 참조 불필요)

---

## 0. ENTRYPOINT 정의

Phase 실행의 **단일 진입점**은 `phase-X-Y-status.md` 파일이다.

### ENTRYPOINT 규칙

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **ENTRY-1** | 단일 진입점 | 모든 Phase 작업은 `docs/phases/phase-X-Y/phase-X-Y-status.md`를 먼저 읽는 것으로 시작 |
| **ENTRY-2** | 상태 기반 분기 | `current_state` 값에 따라 다음 행동을 결정 ([§3.1](#31-상태별-action-table) 참조) |
| **ENTRY-3** | SSOT 버전 확인 | 진입 시 `ssot_version` 필드와 현재 SSOT 버전의 일치 여부를 확인 |
| **ENTRY-4** | Blocker 우선 확인 | `blockers` 배열이 비어있지 않으면 다른 작업보다 Blocker 해결을 우선 |
| **ENTRY-5** | 진입점 외 직접 시작 금지 | status 파일을 읽지 않고 Task 구현을 바로 시작하는 것을 금지 |

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
[6] 팀 상태 확인 (TeamCreate 필요 여부, 팀원 idle 상태) ← [0-entrypoint §3.9](0-entrypoint.md#39-팀-라이프사이클)
  │
  ▼
[7] 워크플로우 실행
```

---

## 1. 워크플로우 상태 머신

### 1.1 상태 정의 (14개)

| 상태 코드 | 상태명 | 설명 | 진입 조건 |
|----------|--------|------|----------|
| `IDLE` | 대기 | Phase 미시작 | 초기 상태 |
| `TEAM_SETUP` | 팀 구성 | TeamCreate + 팀원 스폰 | Phase 시작 명령 |
| `PLANNING` | 계획 | planner 팀원이 요구사항 분석, Task 분해 | 팀 구성 완료 |
| `PLAN_REVIEW` | 계획 검토 (G1) | Team Lead가 planner 결과 검증 | PLANNING 완료 |
| `TASK_SPEC` | Task 내역서 작성 | Task별 실행 계획 문서 생성 | PLAN_REVIEW 통과 |
| `BUILDING` | 구현 | backend-dev/frontend-dev가 코드 작성 | TASK_SPEC 완료 |
| `VERIFYING` | 검증 (G2) | verifier가 코드 리뷰 → Team Lead 보고 | BUILDING 완료 (Task 단위) |
| `TESTING` | 테스트 (G3) | tester가 테스트 실행 → Team Lead 보고 | VERIFYING 통과 |
| `INTEGRATION` | 통합 테스트 | Phase 전체 통합 검증 (API↔UI 연동) | 모든 Task TESTING 통과 |
| `E2E` | E2E 테스트 | 사용자 시나리오 기반 전체 테스트 | INTEGRATION 통과 |
| `E2E_REPORT` | E2E 리포트 | Verification Report + E2E 리포트 작성 | E2E 통과 |
| `TEAM_SHUTDOWN` | 팀 해산 | 팀원 셧다운 + TeamDelete | E2E_REPORT 완료 |
| `BLOCKED` | 차단 | Blocker 이슈 발생 | 어떤 상태에서든 진입 가능 |
| `REWINDING` | 리와인드 | 이전 상태로 롤백 중 | FAIL 판정 시 |
| `DONE` | 완료 | Phase 종료 | TEAM_SHUTDOWN 완료 |

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
ssot_version: "6.0-renewal-4th"
ssot_loaded_at: "2026-02-17T10:00:00Z"
current_state: "BUILDING"
current_task: "X-Y-2"
current_task_domain: "[FE]"
team_name: "phase-X-Y"
team_members: []
last_action: "..."
last_action_result: "PASS"   # PASS | FAIL | PARTIAL | N/A
next_action: "..."
blockers: []
rewind_target: null
retry_count: 0
gate_results: { G1_plan_review: null, G2_code_review_be: null, ... }
task_progress: {}
error_log: []
last_updated: "2026-02-17T10:30:00Z"
---
```

---

## 3. 워크플로우 실행

### 3.1 상태별 Action Table

| 현재 상태 | 다음 행동 | 담당 |
|----------|----------|------|
| **IDLE** | TeamCreate + 팀원 스폰 | Team Lead |
| **TEAM_SETUP** | SendMessage → planner: "Phase X-Y 계획 분석 요청" | Team Lead |
| **PLANNING** | planner 결과 대기 → PLAN_REVIEW로 전이 | Team Lead |
| **PLAN_REVIEW** | planner 결과 검토 → PASS: TASK_SPEC, FAIL: REWINDING→PLANNING | Team Lead |
| **TASK_SPEC** | Task 내역서 일괄 생성 (task-X-Y-N.md × N) + TaskCreate | Team Lead |
| **BUILDING** | SendMessage → 팀원: "Task 구현 시작" (backend-dev/frontend-dev) | 팀원 |
| **VERIFYING** | SendMessage → verifier: "검증 요청" → PASS: TESTING, FAIL: REWINDING | Team Lead + verifier |
| **TESTING** | SendMessage → tester: "테스트 실행" → PASS: 다음 Task 또는 INTEGRATION | Team Lead + tester |
| **INTEGRATION** | tester가 통합 테스트 실행 → PASS: E2E, FAIL: REWINDING | tester |
| **E2E** | tester가 E2E 실행 → PASS: E2E_REPORT, FAIL: REWINDING | tester |
| **E2E_REPORT** | Verification Report + E2E 리포트 작성 → TEAM_SHUTDOWN | Team Lead |
| **TEAM_SHUTDOWN** | SendMessage(shutdown_request) × N → TeamDelete → DONE | Team Lead |
| **BLOCKED** | Blocker 해결 → 이전 상태 복귀 | 해당 팀원 |
| **REWINDING** | rewind_target 상태로 전이 → 재시도 | Team Lead |
| **DONE** | Phase 완료, 다음 Phase 준비 또는 [§8 Phase Chain](#8-phase-chain-자동-순차-실행) 진행 | Team Lead |

### 3.2 상태별 상세 플로우

#### IDLE → TEAM_SETUP
```
1. Team Lead: SSOT 리로드 (0→1→2→3) ← FRESH-1
2. Team Lead: TeamCreate(team_name: "phase-X-Y")
3. Task tool로 팀원 스폰: planner, backend-dev, frontend-dev (ROLES/*.md 로딩 ← FRESH-6)
4. 상태 파일 생성 (phase-X-Y-status.md)
5. current_state = "TEAM_SETUP" → "PLANNING"
6. SendMessage → planner: "Phase X-Y 계획 분석 요청"
```

#### BUILDING → VERIFYING → TESTING
```
[BUILDING] SendMessage → backend-dev/frontend-dev: Task 구현 → 완료 보고
[VERIFYING] SendMessage → verifier: 검증 요청 → G2 결과 PASS/FAIL
[TESTING]  SendMessage → tester: 테스트 실행 → G3 결과 PASS/FAIL
FAIL 시 REWINDING → BUILDING, PASS 시 다음 Task 또는 INTEGRATION
```

---

## 4. 품질 게이트 (Quality Gates)

- **G1 Plan Review**: planner 분석 → Team Lead 검토
- **G2 Code Review**: verifier가 BE+FE 검증 → Team Lead 보고
- **G3 Test Gate**: tester 테스트 + 커버리지
- **G4 Final Gate**: G2+G3 종합 판정. Critical 0건, Blocker 0건 시 PASS.

---

## 5. 에러 처리

| 등급 | 명칭 | 처리 |
|------|------|------|
| **E0** Critical | 즉시 중단, 사용자 보고 |
| **E1** Blocker | BLOCKED 전이, Fix Task 생성 |
| **E2** High | REWINDING, 수정 요청 |
| **E3** Medium | Technical Debt 등록 |
| **E4** Low | 기록만 |

**재시도**: 동일 상태에서 retry_count ≥ 3이면 접근 방식 폐기, 에러 로그 보고, 사용자 판단 대기.

---

## 6. 리와인드 (Rewind)

실패 시 rewind_target 결정 → current_state = "REWINDING" → 해당 팀원에게 수정 요청 → rewind_target으로 전이 → retry_count += 1.  
(PLAN_REVIEW 실패 → PLANNING, VERIFYING/TESTING/INTEGRATION/E2E 실패 → BUILDING)

---

## 7. 참조 문서 (4th 내부)

| 주제 | 링크 |
|------|------|
| **진입점·팀 라이프사이클** | [0-entrypoint.md](0-entrypoint.md) §3.9 |
| **프로젝트·역할** | [1-project.md](1-project.md), [ROLES/](ROLES/) |
| **아키텍처** | [2-architecture.md](2-architecture.md) |
| **역할별 가이드** | [GUIDES/](GUIDES/) |

---

## 8. Phase Chain (자동 순차 실행)

### 8.1 개요

Phase Chain은 복수의 Phase를 사전 정의된 순서로 자동 순차 실행하는 프로토콜이다.  
각 Phase DONE 후 `/clear`로 컨텍스트를 초기화하고, 다음 Phase를 자동 시작한다.

### 8.2 Phase Chain 정의 파일

```yaml
# docs/phases/phase-chain-{name}.md
---
chain_name: "phase-15-fullstack"
phases: ["15-4", "15-5", "15-6", "15-7", "15-8"]
current_index: 0          # 현재 실행 중인 Phase 인덱스
status: "running"         # pending | running | completed | aborted
ssot_version: "6.0-renewal-4th"
created_at: "2026-02-16T..."
---
```

### 8.3 Phase Chain 실행 프로토콜

```
[1] Chain 파일 생성 (phase-chain-{name}.md)
[2] Phase[current_index] Cold Start: SSOT 리로드 → TeamCreate + 팀원 스폰 → PLANNING → … → DONE
[3] Phase DONE → TEAM_SHUTDOWN + TeamDelete → Chain 파일 current_index += 1 → 완료 리포트 출력
[4] /clear 실행 (토큰 최적화, Chain 파일은 디스크에 유지)
[5] current_index < len(phases)? → 다음 Phase Cold Start(Step 2), else Chain 완료
```

### 8.4 `/clear` 후 컨텍스트 복구

1. Chain 파일 읽기  
2. current_index 확인  
3. current_index < len(phases)? → 해당 Phase의 status.md 확인 → DONE 아니면 Warm Start, DONE이면 current_index += 1 후 다음 Phase  
4. SSOT 리로드(FRESH-1) 후 Phase Cold Start

### 8.5 Chain 중단·재개

| 상황 | 처리 |
|------|------|
| Phase 실패 (retry ≥ 3) | Chain 일시정지, 사용자 판단 대기 |
| 사용자 중단 요청 | chain status = "aborted", TEAM_SHUTDOWN |
| 세션 끊김 | Chain 파일로 재개 (8.4 절차) |

### 8.6 Phase Chain 규칙

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **CHAIN-1** | Phase 독립성 | 각 Phase는 Chain 없이도 단독 실행 가능해야 함 |
| **CHAIN-2** | `/clear` 필수 | Phase 간 전환 시 `/clear`로 토큰 초기화 |
| **CHAIN-3** | Chain 파일 유지 | `/clear` 후에도 Chain 파일은 디스크에 영속 |
| **CHAIN-4** | 순차 보장 | phases 배열 순서대로만 실행 (건너뛰기 금지) |
| **CHAIN-5** | 완료 리포트 | 각 Phase DONE 시 1줄 요약을 Chain 파일에 기록 |
| **CHAIN-6** | 산출물 의무 | plan.md, todo-list.md, tasks/task-X-Y-N.md, status.md(YAML) 최소 필수 |
| **CHAIN-7** | Gate 의무 | G1~G4 생략 불가 (단독 실행 시 G2·G3는 자체 검증으로 대체 가능, status에 기록) |
| **CHAIN-8** | Status 형식 | status.md는 YAML frontmatter 형식(§2.2 스키마) 준수 |
| **CHAIN-9** | Task 문서 형식 | task-X-Y-N.md: 메타 필드 4종(우선순위/의존성/담당 팀원/상태) + §1~§4 섹션 번호 |
| **CHAIN-10** | 파일 경로 규칙 | 아래 §8.7 디렉토리 구조 준수 필수. 기존 파일 패턴을 반드시 확인 후 생성 |

### 8.7 Phase 문서 디렉토리 구조

```
docs/phases/
├── phase-chain-{name}.md           ← Chain 정의 (phases 루트)
├── phase-{N}-master-plan.md        ← 마스터 플랜 (phases 루트, 하위 폴더 아님)
├── phase-{N}-{M}/                  ← 개별 Phase 산출물 폴더
│    ├── phase-{N}-{M}-status.md    ← YAML 상태 파일 (ENTRY-1 진입점)
│    ├── phase-{N}-{M}-plan.md      ← Phase 계획서
│    ├── phase-{N}-{M}-todo-list.md ← Todo 체크리스트
│    └── tasks/                     ← Task 명세 폴더
│         └── task-{N}-{M}-{T}.md   ← 개별 Task 명세
```

**핵심 규칙**:
- `master-plan.md`와 `phase-chain-*.md`는 **`docs/phases/` 루트**에 위치 (하위 폴더 생성 금지)
- `status.md`, `plan.md`, `todo-list.md`, `tasks/`는 **`phase-{N}-{M}/` 폴더** 안에 위치
- 새 파일 생성 전 **기존 파일 패턴을 `Glob`으로 확인** 후 동일 경로 레벨에 생성

---

## 9. 컨텍스트 복구 프로토콜

### 9.1 개요

컨텍스트 압축, 세션 중단, 토큰 초과 등으로 작업이 중단된 후 복구하는 경우의 **필수 절차**를 정의한다.
이 프로토콜을 건너뛰고 "이전 요약을 바탕으로 바로 작업 재개"하는 것은 **금지**한다.

### 9.2 복구 절차

```
컨텍스트 복구 시점 (압축 발생 / 세션 재개 / /clear 후)
  │
  ▼
[1] SSOT 리로드 ← FRESH-1 (0-entrypoint.md 읽기)
  │
  ▼
[2] Phase Chain 파일 확인 (phase-chain-{name}.md)
  │   → current_index, status 확인
  │
  ▼
[3] 현재 Phase status.md 읽기 ← ENTRY-1
  │   → current_state, task_progress, team_name 확인
  │
  ▼
[4] 팀 상태 확인
  │   ├── team_name 존재 → 팀 config 읽기, idle 팀원 확인
  │   └── team_name null → 새 팀 생성 필수 (HR-1: 팀 없이 코드 수정 금지)
  │
  ▼
[5] 미완료 Task 식별
  │   → task_progress에서 status != "DONE" 항목 확인
  │   → 해당 Task의 task-X-Y-N.md 읽기
  │
  ▼
[6] 업무 재분배
  │   ├── 기존 팀원 idle 상태 → SendMessage로 작업 재개 지시
  │   ├── 기존 팀원 없음 → 새 팀원 스폰 + Task 할당
  │   └── Task 미할당 → TaskUpdate(owner) 설정
  │
  ▼
[7] 작업 재개 (BUILDING 상태부터)
```

### 9.3 복구 시 금지 사항

| 금지 항목 | 이유 |
|----------|------|
| SSOT 리로드 없이 작업 재개 | 규칙 변경·버전 불일치 감지 불가 |
| 팀 없이 Team Lead가 직접 코드 수정 | HR-1 위반. "빠르게 마무리"는 정당한 사유가 아님 |
| 산출물(tasks/, todo-list) 생략 | HR-2 위반. 중단 복구 시에도 산출물 의무 동일 |
| 이전 세션 요약만 보고 상태 추정 | status.md가 단일 진입점 (ENTRY-1). 요약은 참고일 뿐 |

### 9.4 복구 판정 기준

| 상황 | 처리 |
|------|------|
| current_state = DONE | 다음 Phase 진행 (Chain이면 current_index 확인) |
| current_state = BUILDING, task 일부 DONE | 미완료 Task만 재할당 |
| current_state = PLANNING/PLAN_REVIEW | planner 재스폰 후 계획 재수립 |
| team_name 존재하나 팀원 응답 없음 | TeamDelete → 새 팀 생성 |
| tasks/ 문서 미생성 상태 | 산출물 먼저 생성 후 BUILDING 진입 |

---

**문서 관리**:
- 버전: 6.0-renewal-4th (4th iteration)
- 최종 수정: 2026-02-21
- 단독 사용: 본 iterations/4th 세트만으로 SSOT 완결 (Phase Chain 포함)
