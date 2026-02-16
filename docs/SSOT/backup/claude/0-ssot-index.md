# AI Team SSOT Index

**버전**: 3.2
**작성일**: 2026-02-09
**최종 수정**: 2026-02-16
**관리 주체**: Orchestrator (메인 세션)
**실행 환경**: Claude Code (Task tool 기반 내부 에이전트 팀)

---

## SSOT 목적

이 SSOT는 **Claude Code 내부 에이전트 팀 운영**을 위한 단일 진실 공급원이다.
Claude Code 메인 세션이 Orchestrator로서 Task tool 서브에이전트를 생성·관리하며, 모든 역할을 내부적으로 운영한다.

역할 정의는 `docs/rules/role/`의 4개 Charter를 기반으로 하며, 각 역할은 Task tool의 `subagent_type` 파라미터를 통해 서브에이전트로 실행된다.

### 역할-에이전트 매핑

| 역할 (Charter) | 실행 방법 | Task tool `subagent_type` | 비고 |
|---------------|----------|:------------------------:|------|
| Orchestrator (`LEADER.md`) | 메인 세션 직접 실행 | — (메인 세션) | 워크플로우 지휘, 판정, 코드 편집 |
| Planner | 서브에이전트 | `Plan` 또는 `Explore` | 요구사항 분석, 계획 수립 |
| Backend Builder (`BACKEND.md`) | 메인 세션 직접 실행 | — (메인 세션) | API, DB, 서비스 로직 구현 |
| Frontend Analyzer (`FRONTEND.md`) | 서브에이전트 | `Explore` | UI/UX 분석, 기존 패턴 조사 |
| Verifier (`QA.md`) | 서브에이전트 | `Explore` | 코드 리뷰, 품질 게이트 |
| Tester (`QA.md`) | 서브에이전트 | `Bash` | 테스트 실행, 커버리지 분석 |

**핵심 원칙**: 코드 편집(`Edit`, `Write`)은 메인 세션만 수행한다. 서브에이전트는 분석/검증/테스트만 수행하고 결과를 반환한다.

### 적용 범위

- 백엔드 + 프론트엔드 풀스택 커버
- Phase 기반 개발 워크플로우 전체 관리
- 검증과 테스트 강화 (4단계 품질 게이트)

### 기존 SSOT와의 관계

| 문서 | 역할 |
|------|------|
| `docs/SSOT/` (루트) | 프로젝트 전체 SSOT (멀티 에이전트 협업 기준) |
| `docs/SSOT/claude/` (본 문서) | AI 팀 운영 SSOT (Claude Code 내부 에이전트 팀 구조) |

충돌 시 우선순위: **루트 SSOT > AI Team SSOT > Rules > Phase Docs > Task Docs**

---

## SSOT Lock Rules

Phase 실행 중 SSOT 문서의 무분별한 변경을 방지하기 위한 규칙이다.

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **LOCK-1** | Phase 실행 중 SSOT 변경 금지 | `current_state`가 `IDLE` 또는 `DONE`이 아닌 동안 SSOT 4개 파일 수정 불가 |
| **LOCK-2** | 변경 필요 시 Phase 일시정지 | SSOT 수정이 불가피하면 `current_state`를 `BLOCKED`로 전이 후 변경 |
| **LOCK-3** | 변경 후 리로드 필수 | SSOT 변경 후 반드시 모든 활성 세션에서 SSOT를 다시 로딩 |
| **LOCK-4** | 서브에이전트 SSOT 수정 금지 | 서브에이전트는 SSOT를 읽기 전용으로만 참조 |
| **LOCK-5** | 변경 이력 필수 기록 | SSOT 변경 시 해당 파일의 버전 히스토리에 반드시 기록 |

### SSOT Lock 상태 머신

```
Phase 실행 중 (PLANNING~E2E_REPORT)
  │
  ├── SSOT 변경 필요 발견
  │     → current_state = BLOCKED (사유: "SSOT 변경 필요")
  │     → 사용자 승인 요청
  │     → 승인 시: SSOT 수정 → 버전 갱신 → SSOT 리로드
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

---

## SSOT 문서 구성

| # | 파일명 | 내용 |
|---|--------|------|
| 0 | `0-ssot-index.md` | 인덱스, 역할 매핑, Lock/Freshness/Authority Chain (본 문서) |
| 1 | `1-project-ssot.md` | 팀 구성, 역할 정의, 품질 게이트, 테스트 전략 |
| 2 | `2-architecture-ssot.md` | 기술 스택, 백엔드/프론트엔드 코드 구조, 검증 기준 |
| 3 | `3-workflow-ssot.md` | 워크플로우 상태 머신, 에러 처리, 리와인드, 완료 판정 |

## 로딩 순서

AI 세션 시작 시 다음 순서로 로딩한다:

```
1. 0-ssot-index.md        ← 현재 문서 (역할 매핑, Lock/Freshness 규칙)
2. 1-project-ssot.md      ← 팀 구성, 서브에이전트 설정
3. 2-architecture-ssot.md ← 기술 기준 (백엔드+프론트엔드)
4. 3-workflow-ssot.md      ← 실행 순서, 상태 관리
```

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
- 서브에이전트는 SSOT를 **읽기 전용**으로 참조

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-02-09 | 초안 (Claude 단독 백엔드 전용) |
| 2.0 | 2026-02-09 | 프론트엔드 추가, 공통 AI 팀 구조로 전환, 역할 Charter 연동 |
| 3.0 | 2026-02-15 | Claude Code 내부 에이전트 팀 전환, SSOT Lock Rules/Document Authority Chain/SSOT Freshness Rules 추가 |
| 3.2 | 2026-02-16 | E2E_REPORT 상태 참조 반영 (LOCK 상태 머신), 버전 체계 통일 (전체 SSOT 버전 = 가장 높은 파일 버전) |
