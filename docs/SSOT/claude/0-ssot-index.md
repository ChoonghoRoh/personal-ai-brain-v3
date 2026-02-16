# AI Team SSOT Index

**버전**: 4.2
**작성일**: 2026-02-09
**최종 수정**: 2026-02-16
**관리 주체**: Team Lead (메인 세션)
**실행 환경**: Claude Code Agent Teams (TeamCreate / SendMessage / TaskList 기반)

---

## SSOT 목적

이 SSOT는 **Claude Code Agent Teams 운영**을 위한 단일 진실 공급원이다.
메인 세션이 Team Lead로서 `TeamCreate`로 팀을 생성하고, `Task tool`(team_name 파라미터)으로 팀원을 스폰하며, `SendMessage`로 팀원 간 실시간 통신을 조율한다.

역할 정의는 `docs/rules/role/`의 4개 Charter를 기반으로 하며, 각 역할은 **팀원 에이전트**로서 팀 내에서 병렬·협업 수행한다.

### 역할-에이전트 매핑

| 역할 (Charter) | 팀원 이름 | `subagent_type` | `model` | 코드 편집 | 비고 |
|---------------|----------|:---------------:|:-------:|:--------:|------|
| Team Lead + Orchestrator (`LEADER.md`) | — (메인 세션) | — | opus | **X** | 팀 생성·해산, 워크플로우 지휘, 판정, 통신 허브 (**코드 수정 안 함**) |
| Planner | `planner` | `Plan` 또는 `Explore` | **opus** | X | 요구사항 분석, 계획 수립 (읽기 전용, 고성능 모델) |
| Backend Developer (`BACKEND.md`) | `backend-dev` | `general-purpose` | sonnet | **O** | API, DB, 서비스 로직 구현 (코드 편집 가능) |
| Frontend Developer (`FRONTEND.md`) | `frontend-dev` | `general-purpose` | sonnet | **O** | UI/UX 분석 + 구현 (코드 편집 가능) |
| Verifier (`QA.md`) | `verifier` | `Explore` | sonnet | X | 코드 리뷰, 품질 게이트 (읽기 전용) |
| Tester (`QA.md`) | `tester` | `Bash` | sonnet | X | 테스트 실행, 커버리지 분석 |

**핵심 원칙 (v4.1)**:
- **Team Lead는 코드를 직접 수정하지 않는다.** 모든 코드 작성은 `backend-dev`와 `frontend-dev`에게 위임한다.
- **모든 팀원 간 통신은 Team Lead를 경유한다.** 팀원끼리 직접 메시지를 주고받지 않는다 (Hub-and-Spoke 모델).
- **계획 수립(planner)은 opus 모델**, 나머지 팀원은 **sonnet 모델**을 사용한다.

### 팀 라이프사이클

```
Phase 시작
  │
  ▼
[1] TeamCreate(team_name: "phase-X-Y")  ← 팀 생성
  │
  ▼
[2] Task tool(team_name, name, subagent_type) × N  ← 팀원 스폰
  │
  ▼
[3] TaskCreate → TaskUpdate(owner) → SendMessage  ← 작업 할당·조율
  │
  ▼
[4] 팀원들이 TaskList로 작업 확인, 완료 시 TaskUpdate(completed)
  │
  ▼
[5] 모든 작업 완료 → SendMessage(type: "shutdown_request") × N
  │
  ▼
[6] TeamDelete  ← 팀 해산
```

### 적용 범위

- 백엔드 + 프론트엔드 풀스택 커버
- Phase 기반 개발 워크플로우 전체 관리
- 검증과 테스트 강화 (4단계 품질 게이트)
- 팀원 간 실시간 통신을 통한 병렬 협업

### 기존 SSOT와의 관계

| 문서 | 역할 |
|------|------|
| `docs/SSOT/` (루트) | 프로젝트 전체 SSOT (멀티 에이전트 협업 기준) |
| `docs/SSOT/claude/` (본 문서) | AI 팀 운영 SSOT (Claude Code Agent Teams 구조) |

충돌 시 우선순위: **루트 SSOT > AI Team SSOT > Rules > Phase Docs > Task Docs**

---

## SSOT Lock Rules

Phase 실행 중 SSOT 문서의 무분별한 변경을 방지하기 위한 규칙이다.

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **LOCK-1** | Phase 실행 중 SSOT 변경 금지 | `current_state`가 `IDLE` 또는 `DONE`이 아닌 동안 SSOT 4개 파일 수정 불가 |
| **LOCK-2** | 변경 필요 시 Phase 일시정지 | SSOT 수정이 불가피하면 `current_state`를 `BLOCKED`로 전이 후 변경 |
| **LOCK-3** | 변경 후 리로드 필수 | SSOT 변경 후 반드시 모든 팀원에게 SendMessage로 리로드 지시 |
| **LOCK-4** | 팀원 SSOT 수정 금지 | 팀원 에이전트는 SSOT를 읽기 전용으로만 참조 (backend-dev, frontend-dev 포함) |
| **LOCK-5** | 변경 이력 필수 기록 | SSOT 변경 시 해당 파일의 버전 히스토리에 반드시 기록 |

### SSOT Lock 상태 머신

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
        → SSOT 자유 수정 가능
        → 변경 시 버전 히스토리 기록
```

---

## Document Authority Chain

SSOT 문서와 Phase 문서 간의 권위 체계를 정의한다.

```
[Level 1] SSOT 문서 (docs/SSOT/claude/)
    │      ← 최고 권위, 시스템 수준 규칙 정의
    │
    ▼
[Level 2] Phase Template (docs/rules/templates/)
    │      ← SSOT 규칙을 Phase에 적용하는 템플릿
    │
    ▼
[Level 3] Phase Docs (docs/phases/phase-X-Y/)
    │      ← 특정 Phase의 실행 문서 (plan, todo-list, status)
    │
    ▼
[Level 4] Task Docs (docs/phases/phase-X-Y/tasks/)
           ← 개별 Task 실행 문서
```

### 권위 체인 규칙

| 규칙 | 설명 |
|------|------|
| **하위 문서는 상위 문서를 오버라이드할 수 없다** | Phase Docs가 SSOT의 품질 게이트 기준을 완화할 수 없음 |
| **충돌 시 상위 문서 우선** | Task Docs의 내용이 SSOT와 충돌하면 SSOT 기준 적용 |
| **상위 문서 참조 필수** | Phase Template 작성 시 SSOT 섹션 번호를 명시적으로 참조 |
| **하위 문서에서 확장 가능** | SSOT에 없는 Phase-specific 규칙은 Phase Docs에서 추가 가능 |

---

## SSOT Freshness Rules

새 Phase 시작 또는 세션 재개 시 SSOT가 최신 상태인지 확인하는 규칙이다.

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **FRESH-1** | 세션 시작 시 SSOT 리로드 | 새 AI 세션 시작 시 반드시 SSOT 4개 파일을 순서대로 로딩 |
| **FRESH-2** | 새 Phase 시작 시 버전 확인 | Phase 시작 전 SSOT 버전이 상태 파일의 `ssot_version`과 일치하는지 확인 |
| **FRESH-3** | 버전 불일치 시 갱신 우선 | SSOT 버전이 변경되었으면 Phase 진행 전 SSOT를 먼저 리로드 |
| **FRESH-4** | 리로드 시각 기록 | SSOT 로딩 완료 시 상태 파일의 `ssot_loaded_at`에 타임스탬프 기록 |
| **FRESH-5** | 장기 세션 중 주기적 확인 | Phase가 3개 이상의 Task를 처리한 경우 SSOT 버전 재확인 권장 |
| **FRESH-6** | 팀원 역할별 로딩 | 각 팀원은 스폰 시 해당 `role-*-ssot.md` 1개만 로딩 (컨텍스트 최소화) |

---

## SSOT 문서 구성

### 공통 SSOT (Team Lead)

| # | 파일명 | 내용 |
|---|--------|------|
| 0 | `0-ssot-index.md` | 인덱스, 역할 매핑, 팀 라이프사이클, Lock/Freshness/Authority Chain (본 문서) |
| 1 | `1-project-ssot.md` | 팀 구성, 역할 정의, 품질 게이트, 테스트 전략 |
| 2 | `2-architecture-ssot.md` | 기술 스택, 백엔드/프론트엔드 코드 구조, 검증 기준 |
| 3 | `3-workflow-ssot.md` | 워크플로우 상태 머신, 에러 처리, 리와인드, 완료 판정 |

### 역할별 SSOT (팀원용)

각 팀원은 **해당 역할 전용 SSOT 1개**만 로딩하여 컨텍스트를 최소화한다.

| 역할 | 팀원 이름 | `subagent_type` | 전용 SSOT 파일 | 핵심 책임 |
|------|----------|:---------------:|----------------|----------|
| **Planner** | `planner` | Plan / Explore | `role-planner-ssot.md` | 요구사항 분석, 작업 분해, SSOT 버전·리스크 확인 |
| **Backend Developer** | `backend-dev` | general-purpose | `role-backend-dev-ssot.md` | API/DB/서비스 구현, 백엔드 코드 편집 |
| **Frontend Developer** | `frontend-dev` | general-purpose | `role-frontend-dev-ssot.md` | UI/UX 분석 + 구현, 프론트엔드 코드 편집 |
| **Verifier** | `verifier` | Explore | `role-verifier-ssot.md` | 코드 리뷰, 품질 게이트 통과 여부 판정 (읽기 전용) |
| **Tester** | `tester` | Bash | `role-tester-ssot.md` | 테스트 실행(pytest, playwright 등), 커버리지 분석 |

## 로딩 순서

### Team Lead (메인 세션)

AI 세션 시작 시 다음 순서로 로딩한다 (FRESH-1):

```
1. 0-ssot-index.md        ← 현재 문서 (역할 매핑, 팀 라이프사이클, Lock/Freshness 규칙)
2. 1-project-ssot.md      ← 팀 구성, 팀원 설정
3. 2-architecture-ssot.md ← 기술 기준 (백엔드+프론트엔드)
4. 3-workflow-ssot.md     ← 실행 순서, 상태 관리
```

### 팀원 에이전트

팀원 스폰 시 **해당 역할 전용 SSOT 1개**만 로딩한다.

| 팀원 | 로딩 파일 |
|------|----------|
| `planner` | `role-planner-ssot.md` |
| `backend-dev` | `role-backend-dev-ssot.md` |
| `frontend-dev` | `role-frontend-dev-ssot.md` |
| `verifier` | `role-verifier-ssot.md` |
| `tester` | `role-tester-ssot.md` |

(선택) 역할 매핑만 필요할 때는 `0-ssot-index.md`만 로딩해도 된다.

## 팀 통신 프로토콜

### SendMessage 유형별 용도

| 유형 | 용도 | 사용 예시 |
|------|------|----------|
| `message` | Team Lead ↔ 팀원 간 DM | Team Lead → `backend-dev`: "Task 15-1 API 구현 시작" |
| `broadcast` | 전 팀원에게 일괄 전달 | "SSOT 리로드 필요" / "Phase 긴급 중단" |
| `shutdown_request` | 팀원 종료 요청 | Phase 완료 후 순차 셧다운 |
| `shutdown_response` | 종료 승인/거부 | 팀원이 작업 중이면 거부 가능 |

### Hub-and-Spoke 통신 모델

모든 팀원 간 통신은 **Team Lead를 경유**한다. 팀원끼리 직접 메시지를 주고받지 않는다.

```
          backend-dev
              ↕
frontend-dev ↔ Team Lead ↔ verifier
              ↕
            tester
```

- verifier가 이슈 발견 → Team Lead에게 보고 → Team Lead가 해당 개발자에게 수정 요청
- backend-dev가 API 변경 → Team Lead에게 보고 → Team Lead가 frontend-dev에게 전달

## 자원 및 비용 관리

Agent Teams 운영 시 팀원 에이전트가 각각 독립 컨텍스트 윈도우를 사용하므로 토큰 비용이 증가한다. 이를 관리하기 위한 운영 지침이다.

### 모델 혼합 운영

| 역할 | 모델 | 사유 |
|------|------|------|
| Team Lead (메인 세션) | opus | 복잡한 조율·판정·전체 상황 인식 필요 |
| planner | opus | 고품질 설계·분석 (컨텍스트 소모 큼, 단기 사용) |
| backend-dev, frontend-dev | sonnet | 구현 작업은 범위가 좁고 반복적 — 비용 효율 우선 |
| verifier, tester | sonnet | 검증·테스트는 정형화된 기준 적용 — 비용 효율 우선 |

### 컨텍스트 최적화

| 전략 | 설명 |
|------|------|
| **역할별 SSOT 분리** | 팀원은 전용 `role-*-ssot.md` 1개만 로딩 (FRESH-6). 공통 SSOT 4개 전체 로딩은 Team Lead만 수행 |
| **지연 스폰** | verifier, tester는 해당 단계 진입 시 스폰하여 불필요한 대기 비용 제거 |
| **planner 조기 셧다운** | PLAN_REVIEW 통과 후 즉시 shutdown — 구현 단계에서 불필요한 컨텍스트 유지 방지 |
| **Skills 분리** | 반복 사용되는 검증·테스트 지식은 `.claude/skills/`로 외부화하여 필요 시만 로드 |

## 컨텍스트 우선순위

```
루트 SSOT > AI Team SSOT > Rules > Phase Docs > Task Docs > Legacy Docs
```

## 역할 Charter 참조 경로

| Charter | 경로 |
|---------|------|
| LEADER | `docs/rules/role/LEADER.md` |
| BACKEND | `docs/rules/role/BACKEND.md` |
| FRONTEND | `docs/rules/role/FRONTEND.md` |
| QA | `docs/rules/role/QA.md` |

## 버전 체계

SSOT는 4개 파일로 구성되며, 각 파일은 개별 버전 히스토리를 관리한다.

| 항목 | 규칙 |
|------|------|
| **전체 SSOT 버전** | 4개 파일 중 가장 높은 버전 = 전체 SSOT 버전 |
| **`ssot_version` (status 파일)** | 전체 SSOT 버전을 기록 |
| **파일별 버전** | 해당 파일 변경 시에만 해당 파일의 버전을 전체 SSOT 버전으로 올림 |
| **동기화 시점** | 어느 파일이든 수정 시, 해당 파일의 헤더 버전 = 전체 SSOT 버전 (최고값) |

## 변경 관리

- SSOT 문서는 **시스템 수준의 결정**이 있을 때만 변경
- Phase 실행 중에는 SSOT Lock Rules에 따라 변경 금지
- 변경 시 버전 번호 갱신 및 변경 이력 기록
- 팀원 에이전트는 SSOT를 **읽기 전용**으로 참조

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-02-09 | 초안 (Claude 단독 백엔드 전용) |
| 2.0 | 2026-02-09 | 프론트엔드 추가, 공통 AI 팀 구조로 전환, 역할 Charter 연동 |
| 3.0 | 2026-02-15 | Claude Code 내부 에이전트 팀 전환, SSOT Lock Rules/Document Authority Chain/SSOT Freshness Rules 추가 |
| 3.2 | 2026-02-16 | E2E_REPORT 상태 참조 반영, 버전 체계 통일 |
| 3.3 | 2026-02-16 | 역할별 SSOT 도입 (role-planner/frontend-analyzer/verifier/tester) |
| 3.4 | 2026-02-16 | 용어 통일: "서브에이전트" → "에이전트 팀원" |
| 4.0 | 2026-02-16 | **Agent Teams 전환**: TeamCreate/SendMessage/TaskList 기반 팀 운영 체계로 전면 개편. Backend Developer·Frontend Developer를 general-purpose 에이전트로 승격 (코드 편집 가능). 팀 라이프사이클·통신 프로토콜 추가. role-backend-dev-ssot·role-frontend-dev-ssot 신규 |
| 4.1 | 2026-02-16 | Hub-and-Spoke 통신 모델 (Peer DM 제거, 모든 통신 Team Lead 경유). Team Lead 코드 수정 금지 명시. 모델 지정: planner=opus, 나머지=sonnet. 불필요 섹션 정리 |
| 4.2 | 2026-02-16 | 자원 및 비용 관리 섹션 신설 (모델 혼합 운영 근거, 컨텍스트 최적화 전략) |
