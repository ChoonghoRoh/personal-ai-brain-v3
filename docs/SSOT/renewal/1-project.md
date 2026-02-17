# SSOT — 프로젝트 정의 (요약)

**버전**: 5.0-renewal
**최종 수정**: 2026-02-17
**기반**: 1-project-ssot.md (v4.2, 578줄)

---

## 1. 프로젝트 정의

| 항목           | 내용                                                                                 |
| -------------- | ------------------------------------------------------------------------------------ |
| **프로젝트명** | Personal AI Brain v3                                                                 |
| **목적**       | 로컬 설치형 개인 AI 브레인 — 문서 벡터화, 의미 검색, AI 응답, 지식 구조화, Reasoning |
| **배포 형태**  | Docker Compose (On-Premise, 폐쇄망 동작 필수)                                        |
| **현재 Phase** | Phase 14 완료, Phase 15 계획 수립 대기                                               |
| **실행 환경**  | Claude Code Agent Teams (TeamCreate / SendMessage / TaskList)                        |

---

## 2. 팀 구성

### 2.1 Agent Teams 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│               Team Lead + Orchestrator (메인 세션)                    │
│  Charter: LEADER.md                                                  │
│  역할: TeamCreate → 팀원 스폰 → SendMessage 조율 → 판정 → TeamDelete │
│  코드 편집: ❌ 금지 (조율·판정·통신 허브)                             │
└──┬──────────┬──────────────┬──────────────┬──────────────┬──────────┘
   │          │              │              │              │
┌──▼───┐ ┌───▼──────────┐ ┌─▼──────────┐ ┌▼──────────┐ ┌▼─────────┐
│plan- │ │backend-dev   │ │frontend-   │ │verifier   │ │tester    │
│ner   │ │              │ │dev         │ │           │ │          │
│      │ │Charter:      │ │Charter:    │ │Charter:   │ │Charter:  │
│opus  │ │BACKEND.md    │ │FRONTEND.md │ │QA.md      │ │QA.md     │
│      │ │              │ │            │ │           │ │          │
│읽기  │ │**코드 편집** │ │**코드 편집**│ │읽기 전용  │ │Bash 전용 │
│전용  │ │**가능**      │ │**가능**    │ │           │ │          │
│      │ │sonnet        │ │sonnet      │ │sonnet     │ │sonnet    │
└──────┘ └──────────────┘ └────────────┘ └───────────┘ └──────────┘
           ↕ 모든 통신은 Team Lead 경유 (Hub-and-Spoke) ↕
```

### 2.2 역할-실행 매핑

| 역할                   | Charter       | 팀원 이름      |    `subagent_type`    | `model` | 코드 편집 |       담당 도메인        |
| ---------------------- | ------------- | -------------- | :-------------------: | :-----: | :-------: | :----------------------: |
| **Team Lead**          | `LEADER.md`   | — (메인 세션)  |           —           |  opus   |    ❌     |      — (조율·판정)       |
| **Planner**            | — (고유)      | `planner`      | `Plan` 또는 `Explore` |  opus   |    ❌     |      — (계획 수립)       |
| **Backend Developer**  | `BACKEND.md`  | `backend-dev`  |   `general-purpose`   | sonnet  |    ✅     | `[BE]` `[DB]` `[FS]`(BE) |
| **Frontend Developer** | `FRONTEND.md` | `frontend-dev` |   `general-purpose`   | sonnet  |    ✅     |    `[FE]` `[FS]`(FE)     |
| **Verifier**           | `QA.md`       | `verifier`     |       `Explore`       | sonnet  |    ❌     |      — (코드 리뷰)       |
| **Tester**             | `QA.md`       | `tester`       |        `Bash`         | sonnet  |    ❌     |     — (테스트 실행)      |

**코드 편집 원칙**:

- Team Lead는 코드를 직접 수정하지 않는다 (조율·판정·통신 허브)
- `backend-dev`는 `backend/`, `tests/`, `scripts/` 편집
- `frontend-dev`는 `web/`, `e2e/` 편집
- `verifier`는 읽기 전용 (수정 필요 시 Team Lead에게 보고)

---

### 2.3 역할별 상세

#### Team Lead + Orchestrator (메인 세션)

| 항목          | 내용                                                                                  |
| ------------- | ------------------------------------------------------------------------------------- |
| **Charter**   | `docs/rules/role/LEADER.md`                                                           |
| **핵심 역할** | 팀 생성·해산, 워크플로우 지휘, 상태 관리, 최종 판정, 통신 허브                        |
| **권한**      | TeamCreate, TeamDelete, SendMessage, Task tool, 파일 읽기, Git, Bash                  |
| **책임**      | Phase 상태 관리, 판정 결정(PASS/FAIL/PARTIAL), Task 할당, 팀원 조율, 이슈 해결        |
| **금지**      | **코드 직접 수정 금지** — 모든 코드 작성은 `backend-dev` 또는 `frontend-dev`에게 위임 |

<details>
<summary>상세 가이드</summary>

- **SSOT 리로드 필수**: 세션 시작 시 FRESH-1 규칙 적용 (0→1→2→3 순서)
- **ENTRYPOINT 진입**: `phase-X-Y-status.md` 읽기 → `current_state` 확인 → 다음 행동 결정
- **상태 전이 책임**: IDLE → TEAM_SETUP → PLANNING → ... → DONE 전체 관장
- **판정 권한**: G1~G4 게이트 최종 판정 (PASS/FAIL/PARTIAL)
- **통신 허브**: 모든 팀원의 SendMessage를 받아 라우팅

➜ [상세 Team Lead 가이드](../claude/0-ssot-index.md)

</details>

---

#### Planner (팀원: `planner`)

| 항목          | 내용                                                                                   |
| ------------- | -------------------------------------------------------------------------------------- |
| **팀원 이름** | `planner`                                                                              |
| **실행 방법** | `Task tool` → `team_name`, `name: "planner"`, `subagent_type: "Plan"`, `model: "opus"` |
| **핵심 역할** | 요구사항 분석, 영향 범위 탐색, 계획 수립, Task 분해 (3~7개)                            |
| **권한**      | 파일 읽기, 검색 (Glob, Grep, Read) — 쓰기 권한 없음                                    |
| **입력**      | master-plan, navigation, 이전 Phase summary                                            |
| **출력**      | plan + todo-list (도메인 태그 포함)를 SendMessage로 Team Lead에게 전달                 |

<details>
<summary>상세 가이드</summary>

- **Task 분해 전략**: 3~7개로 분해 (너무 많지 않게)
- **도메인 태그 필수**: `[BE]` `[FE]` `[FS]` `[DB]` 명시
- **완료 기준**: Done Definition 구체적으로 작성
- **리스크 식별**: 기술적 난이도, 의존성 명시

➜ [상세 Plan 가이드](../claude/role-planner-ssot.md)

</details>

---

#### Backend Developer (팀원: `backend-dev`)

| 항목            | 내용                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------- |
| **Charter**     | `docs/rules/role/BACKEND.md`                                                                            |
| **팀원 이름**   | `backend-dev`                                                                                           |
| **실행 방법**   | `Task tool` → `team_name`, `name: "backend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **핵심 역할**   | API, DB, 서비스 로직 구현 — **코드 편집 가능**                                                          |
| **권한**        | 파일 읽기/쓰기/편집, Bash, Glob, Grep, Read                                                             |
| **담당 범위**   | `backend/`, `tests/`, `scripts/` 디렉토리                                                               |
| **담당 도메인** | `[BE]` `[DB]` `[FS]`(백엔드 파트)                                                                       |

<details>
<summary>필수 준수 사항</summary>

| 규칙                    | 설명                                            |
| ----------------------- | ----------------------------------------------- |
| **ORM 필수**            | raw SQL 절대 금지, SQLAlchemy ORM만 사용        |
| **Pydantic 검증**       | 모든 API 입력은 Pydantic 스키마로 검증          |
| **타입 힌트**           | 함수 파라미터 + 반환 타입 힌트 필수             |
| **에러 핸들링**         | try-except + HTTPException 패턴                 |
| **Team Lead 경유 통신** | 구현 완료 시 SendMessage로 Team Lead에게만 보고 |

➜ [상세 Backend 가이드](ROLES/backend-dev.md)

</details>

---

#### Frontend Developer (팀원: `frontend-dev`)

| 항목            | 내용                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| **Charter**     | `docs/rules/role/FRONTEND.md`                                                                            |
| **팀원 이름**   | `frontend-dev`                                                                                           |
| **실행 방법**   | `Task tool` → `team_name`, `name: "frontend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **핵심 역할**   | UI/UX 분석 + 구현 — **코드 편집 가능**                                                                   |
| **권한**        | 파일 읽기/쓰기/편집, Bash, Glob, Grep, Read                                                              |
| **담당 범위**   | `web/`, `e2e/` 디렉토리                                                                                  |
| **담당 도메인** | `[FE]` `[FS]`(프론트엔드 파트)                                                                           |

<details>
<summary>필수 준수 사항</summary>

| 규칙                    | 설명                                             |
| ----------------------- | ------------------------------------------------ |
| **ESM import/export**   | `type="module"` 필수                             |
| **innerHTML + esc()**   | XSS 방지 필수                                    |
| **외부 CDN 금지**       | 모든 리소스는 로컬에서 제공 (`web/public/libs/`) |
| **window 전역 금지**    | 기존 것 제외하고 새로 할당 금지                  |
| **Team Lead 경유 통신** | 구현 완료 시 SendMessage로 Team Lead에게만 보고  |

➜ [상세 Frontend 가이드](ROLES/frontend-dev.md)

</details>

---

#### Verifier (팀원: `verifier`)

| 항목          | 내용                                                                                         |
| ------------- | -------------------------------------------------------------------------------------------- |
| **Charter**   | `docs/rules/role/QA.md`                                                                      |
| **팀원 이름** | `verifier`                                                                                   |
| **실행 방법** | `Task tool` → `team_name`, `name: "verifier"`, `subagent_type: "Explore"`, `model: "sonnet"` |
| **핵심 역할** | 코드 리뷰, 품질 게이트(G2) 판정 — **읽기 전용**                                              |
| **권한**      | 파일 읽기, 검색 — 쓰기·편집 권한 없음                                                        |
| **입력**      | Team Lead가 SendMessage로 전달한 변경 파일 목록, 완료 기준                                   |
| **출력**      | 검증 결과 (PASS/FAIL/PARTIAL + 이슈 목록)를 SendMessage로 Team Lead에게만 반환               |

<details>
<summary>판정 기준</summary>

| 조건                    | 판정        |
| ----------------------- | ----------- |
| Critical 1건 이상       | **FAIL**    |
| Critical 0건, High 있음 | **PARTIAL** |
| Critical 0, High 0      | **PASS**    |

**Critical (필수 통과)**:

- 구문 오류 없음
- ORM 사용 (raw SQL 없음)
- Pydantic 검증 존재
- innerHTML 시 esc() 적용
- 외부 CDN 없음
- 기존 테스트 깨지지 않음

➜ [상세 Verifier 가이드](ROLES/verifier.md)

</details>

---

#### Tester (팀원: `tester`)

| 항목          | 내용                                                                                    |
| ------------- | --------------------------------------------------------------------------------------- |
| **Charter**   | `docs/rules/role/QA.md`                                                                 |
| **팀원 이름** | `tester`                                                                                |
| **실행 방법** | `Task tool` → `team_name`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **핵심 역할** | 테스트 실행, 커버리지 분석, 품질 게이트(G3) 판정                                        |
| **권한**      | Bash 명령 실행 (pytest, playwright 등)                                                  |
| **입력**      | Team Lead가 SendMessage로 전달한 테스트 범위, 명령                                      |
| **출력**      | 테스트 결과를 SendMessage로 Team Lead에게 반환                                          |

<details>
<summary>테스트 명령</summary>

```bash
# 단위 + 통합 테스트
pytest tests/ -v --tb=short

# 커버리지
pytest tests/ --cov=backend --cov-report=term-missing

# E2E 테스트
npx playwright test e2e/phase-X-Y.spec.js

# E2E 회귀 테스트
npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js
```

➜ [상세 Tester 가이드](ROLES/tester.md)

</details>

---

## 3. 팀 라이프사이클

```
Phase 시작
  │
  ▼
[1] TeamCreate(team_name: "phase-X-Y")  ← 팀 생성 (Team Lead)
  │
  ▼
[2] Task tool(team_name, name, subagent_type, model) × N  ← 팀원 스폰
  │   예: Task(team_name: "phase-15-1", name: "planner", subagent_type: "Plan", model: "opus")
  │       Task(team_name: "phase-15-1", name: "backend-dev", subagent_type: "general-purpose", model: "sonnet")
  │
  ▼
[3] TaskCreate → TaskUpdate(owner) → SendMessage  ← 작업 할당·조율
  │   Team Lead: TaskCreate로 작업 생성
  │   Team Lead: TaskUpdate(owner: "backend-dev")로 할당
  │   Team Lead: SendMessage로 작업 지시
  │
  ▼
[4] 팀원들이 TaskList로 작업 확인, 완료 시 TaskUpdate(completed) + SendMessage 보고
  │   backend-dev: 코드 작성 → SendMessage(Team Lead)
  │   verifier: 코드 리뷰 → SendMessage(Team Lead, 판정 결과)
  │   tester: 테스트 실행 → SendMessage(Team Lead, 테스트 결과)
  │
  ▼
[5] 모든 작업 완료 → SendMessage(type: "shutdown_request") × N
  │   Team Lead: 각 팀원에게 shutdown_request 전송
  │
  ▼
[6] TeamDelete  ← 팀 해산 (Team Lead)
  │
  ▼
Phase 완료 (current_state: DONE)
```

**지연 스폰 원칙**: verifier, tester는 VERIFYING/TESTING 단계 진입 시 스폰 (비용 절감)

➜ [상세 라이프사이클](../claude/1-project-ssot.md#26-팀-라이프사이클-상세)

---

## 4. Hub-and-Spoke 통신 모델

모든 팀원 간 통신은 **Team Lead를 경유**한다. 팀원끼리 직접 메시지를 주고받지 않는다.

```
       planner
          ↕
backend-dev ← → Team Lead ← → frontend-dev
          ↕                ↕
       verifier          tester
```

**통신 원칙**:

1. 팀원은 `SendMessage(team_name, recipient: "team-lead", ...)`로 Team Lead에게만 보고
2. Team Lead는 `SendMessage(team_name, recipient: "backend-dev", ...)`로 특정 팀원에게 전달
3. 팀원끼리 직접 통신 금지

**예시**:

1. backend-dev가 구현 완료 → SendMessage로 Team Lead에게 보고
2. Team Lead가 verifier에게 검증 지시 → SendMessage로 verifier에게 전달
3. verifier가 검증 결과 FAIL → SendMessage로 Team Lead에게 보고
4. Team Lead가 backend-dev에게 수정 요청 → SendMessage로 backend-dev에게 전달

➜ [상세 통신 프로토콜](../claude/1-project-ssot.md#35-hub-and-spoke-통신-모델)

---

## 5. Task 도메인 분류

각 Task는 도메인 태그를 명시하여 적절한 팀원이 구현/검증한다.

| 도메인 태그 | 설명                                |           구현 팀원            |       검증 팀원       |
| ----------- | ----------------------------------- | :----------------------------: | :-------------------: |
| `[BE]`      | 백엔드 (API, 서비스, 미들웨어)      |         `backend-dev`          | `verifier` + `tester` |
| `[DB]`      | 데이터베이스 (스키마, 마이그레이션) |         `backend-dev`          | `verifier` + `tester` |
| `[FE]`      | 프론트엔드 (HTML, JS, CSS)          |         `frontend-dev`         | `verifier` + `tester` |
| `[FS]`      | 풀스택 (백엔드 + 프론트 연동)       | `backend-dev` + `frontend-dev` | `verifier` + `tester` |
| `[TEST]`    | 테스트 전용 (테스트 코드 작성)      |            `tester`            |      `verifier`       |
| `[INFRA]`   | 인프라 (Docker, 환경변수, CI)       |         `backend-dev`          |           —           |

**Todo-list 작성 예시**:

```markdown
- [ ] Task X-Y-1: [BE] Admin API CRUD 구현 (Owner: backend-dev)
- [ ] Task X-Y-2: [DB] Admin 테이블 마이그레이션 (Owner: backend-dev)
- [ ] Task X-Y-3: [FE] Admin 설정 UI 페이지 구현 (Owner: frontend-dev)
- [ ] Task X-Y-4: [FS] API-UI 연동 및 데이터 바인딩 (Owner: backend-dev + frontend-dev)
- [ ] Task X-Y-5: [TEST] 통합 테스트 시나리오 작성/실행 (Owner: tester)
```

---

## 6. 품질 게이트 정의

### 6.1 게이트 구조

```
[G1: Plan Review]     planner 분석 → Team Lead 검토
        ↓
[G2: Code Review]     verifier가 BE+FE 코드 검증 (→ Team Lead 보고)
        ↓
[G3: Test Gate]       tester가 테스트 실행 + 커버리지 확인 (→ Team Lead 보고)
        ↓
[G4: Final Gate]      Team Lead가 G2+G3 종합 판정
```

### 6.2 게이트별 통과 기준

| 게이트 | 백엔드 기준                       | 프론트엔드 기준                  | 공통 기준                               |
| ------ | --------------------------------- | -------------------------------- | --------------------------------------- |
| **G1** | API Spec 확정, DB 스키마 정의     | 페이지 구조/동선 정의            | 완료 기준 명확, Task 3~7개, 리스크 식별 |
| **G2** | Critical 0건, ORM 사용, 타입 힌트 | CDN 미사용, ESM, innerHTML+esc() | 보안 취약점 없음                        |
| **G3** | pytest PASS, 커버리지 ≥80%        | 페이지 로드 OK, 콘솔 에러 0건    | 회귀 테스트 통과                        |
| **G4** | G2 PASS + G3 PASS                 | G2 PASS + G3 PASS                | Blocker 0건                             |

### 6.3 판정 기준

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

➜ [상세 게이트 규칙](../claude/1-project-ssot.md#4-품질-게이트-정의)

---

## 7. 에이전트 팀 운용 원칙

| 원칙             | 설명                                                                      |
| ---------------- | ------------------------------------------------------------------------- |
| **팀 생성**      | Phase 시작 시 `TeamCreate(team_name: "phase-X-Y")`로 팀 생성              |
| **팀원 스폰**    | `Task tool`에 `team_name`, `name`, `subagent_type`, `model` 지정하여 스폰 |
| **Charter 장착** | 팀원 스폰 시 해당 역할의 Charter 경로를 프롬프트에 포함                   |
| **역할별 SSOT**  | 각 팀원은 전용 `role-*-ssot.md` 1개만 로딩 (컨텍스트 최소화)              |
| **작업 할당**    | `TaskCreate` → `TaskUpdate(owner: "팀원이름")`으로 작업 할당              |
| **통신 모델**    | Hub-and-Spoke: 모든 통신은 Team Lead 경유. 팀원끼리 직접 메시지 금지      |
| **작업 완료**    | 팀원이 `TaskUpdate(status: "completed")` 후 Team Lead에게 SendMessage     |
| **병렬 실행**    | 독립적인 Task는 여러 팀원이 동시 수행 (BE + FE 병렬)                      |
| **팀 해산**      | Phase 완료 후 `SendMessage(type: "shutdown_request")` → `TeamDelete`      |
| **모델 선택**    | planner: `opus` (계획 수립), 나머지 팀원: `sonnet` (구현/검증/테스트)     |
| **지연 스폰**    | verifier, tester는 VERIFYING/TESTING 단계 진입 시 스폰 (비용 절감)        |

### 7.1 도메인별 편집 원칙

| 규칙 ID    | 규칙                     | 설명                                                                                       |
| ---------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| **EDIT-1** | 도메인별 편집 범위       | `backend-dev`는 `backend/`, `tests/`, `scripts/`만, `frontend-dev`는 `web/`, `e2e/`만 편집 |
| **EDIT-2** | Team Lead 코드 수정 금지 | Team Lead(메인 세션)는 코드를 직접 수정하지 않고 팀원에게 위임                             |
| **EDIT-3** | 상태·SSOT 쓰기 독점      | `phase-X-Y-status.md`와 SSOT 문서는 Team Lead만 수정 가능                                  |
| **EDIT-4** | 읽기 전용 팀원           | `verifier`(Explore)와 `planner`(Plan)는 파일 쓰기/편집 권한 없음                           |
| **EDIT-5** | 동시 편집 금지           | 동일 파일을 두 팀원이 동시에 편집하지 않음. [FS] Task는 BE 파트 → FE 파트 순차 진행        |

---

## 8. 참조 문서

| 문서                | 용도                      | 경로                                                             |
| ------------------- | ------------------------- | ---------------------------------------------------------------- |
| Leader Charter      | Team Lead 역할            | `docs/rules/role/LEADER.md`                                      |
| Backend Charter     | Backend Developer 역할    | `docs/rules/role/BACKEND.md`                                     |
| Frontend Charter    | Frontend Developer 역할   | `docs/rules/role/FRONTEND.md`                                    |
| QA Charter          | Verifier/Tester 역할      | `docs/rules/role/QA.md`                                          |
| 검증 템플릿         | Verification report 형식  | `docs/rules/templates/verification-report-template.md`           |
| 실행 워크플로우     | 전체 실행 순서            | `docs/rules/ai-execution-workflow.md`                            |
| Task 생성 규칙      | Task 문서 생성·명명·검증  | `docs/rules/ai/references/ai-rule-task-creation.md`              |
| Task 검사 규칙      | Task 완료 검사·산출물     | `docs/rules/ai/references/ai-rule-task-inspection.md`            |
| Plan·Todo 생성 규칙 | Phase plan/todo 생성 순서 | `docs/rules/ai/references/ai-rule-phase-plan-todo-generation.md` |

**상세 프로젝트 정의**: [1-project-ssot.md (v4.2, 578줄)](../claude/1-project-ssot.md)

---

**문서 관리**:

- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 기반: 1-project-ssot.md (v4.2, 578줄 → 400줄 요약)
