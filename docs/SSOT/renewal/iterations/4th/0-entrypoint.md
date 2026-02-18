# SSOT 진입점 (v6.0-renewal-4th) — 단독 사용

**버전**: 6.0-renewal-4th  
**릴리스**: 2026-02-17  
**전략**: 요약+상세 분리 + **claude/ 의존성 제거** (본 세트만으로 SSOT 완결)  
**목표 읽기 시간**: 10~15분 (500줄)

---

## 📌 빠른 시작

### SSOT 목적

이 SSOT(Single Source of Truth)는 **Claude Code Agent Teams 운영**을 위한 단일 진실 공급원이다.

- 메인 세션이 **Team Lead**로서 팀을 생성·조율·판정·해산한다.
- 팀원은 역할별 Charter(본 4th [PERSONA/](PERSONA/) 내 페르소나 문서)를 기반으로 **병렬·협업** 작업을 수행한다.
- 모든 Phase 작업은 **상태 기반 워크플로우**로 진행된다.
- **본 iterations/4th 세트만으로 단독 사용 가능** (다른 SSOT 폴더 참조 불필요).

### 실행 환경

| 항목 | 내용 |
|------|------|
| **도구** | Claude Code Agent Teams (TeamCreate / SendMessage / TaskList) |
| **프로젝트** | Personal AI Brain v3 (Docker Compose 기반) |
| **현재 Phase** | Phase 16 완료 (Chain 16-1~16-7), Phase 17 계획 수립 대기 |

### 당신의 역할은?

| 역할 | 읽기 분량 | 읽기 시간 | 체크리스트로 이동 |
|------|----------|----------|------------------|
| **Planner** | 450줄 | 9분 | [§2.0](#20-planner) |
| **Backend Developer** | 500줄 | 10분 | [§2.1](#21-backend-developer) |
| **Frontend Developer** | 500줄 | 10분 | [§2.2](#22-frontend-developer) |
| **Verifier** | 700줄 | 15분 | [§2.3](#23-verifier) |
| **Tester** | 400줄 | 8분 | [§2.4](#24-tester) |
| **Team Lead** | 전체 | 25분 | [§2.5](#25-team-lead) |

---

## 🎯 역할별 필독 체크리스트

### 2.0 Planner

**팀원 이름**: `planner` | **Charter**: [PLANNER.md](PERSONA/PLANNER.md) | **코드 편집**: ❌

- [ ] 본 문서 § 코어 개념 ([§3](#3-코어-개념-요약))
- [ ] [ROLES/planner.md](ROLES/planner.md)
- [ ] [1-project.md](1-project.md) § 팀 구성·라이프사이클
- [ ] [3-workflow.md](3-workflow.md) § 상태머신

**핵심 원칙**: SSOT 버전·리스크 확인, Task 3~7개 분해, 도메인 태그·담당 팀원 명시, Team Lead 경유 통신

**계획 시작 시**: [GUIDES/planner-work-guide.md](GUIDES/planner-work-guide.md) 참조

---

### 2.1 Backend Developer

**팀원 이름**: `backend-dev` | **Charter**: [BACKEND.md](PERSONA/BACKEND.md) | **코드 편집**: ✅

- [ ] 본 문서 § 코어 개념 ([§3](#3-코어-개념-요약))
- [ ] [ROLES/backend-dev.md](ROLES/backend-dev.md)
- [ ] [1-project.md](1-project.md) § 팀 구성
- [ ] [2-architecture.md](2-architecture.md) § 백엔드
- [ ] [3-workflow.md](3-workflow.md) § 상태머신

**핵심 원칙**: ORM 필수, Pydantic 검증, 타입 힌트, Team Lead 경유 통신

**Task 시작 시**: [GUIDES/backend-work-guide.md](GUIDES/backend-work-guide.md) 참조

---

### 2.2 Frontend Developer

**팀원 이름**: `frontend-dev` | **Charter**: [FRONTEND.md](PERSONA/FRONTEND.md) | **코드 편집**: ✅

- [ ] 본 문서 § 코어 개념 ([§3](#3-코어-개념-요약))
- [ ] [ROLES/frontend-dev.md](ROLES/frontend-dev.md)
- [ ] [1-project.md](1-project.md) § 팀 구성
- [ ] [2-architecture.md](2-architecture.md) § 프론트엔드
- [ ] [3-workflow.md](3-workflow.md) § 상태머신

**핵심 원칙**: ESM import/export, innerHTML+esc(), CDN 금지, Team Lead 경유 통신

**Task 시작 시**: [GUIDES/frontend-work-guide.md](GUIDES/frontend-work-guide.md) 참조

---

### 2.3 Verifier

**팀원 이름**: `verifier` | **Charter**: [QA.md](PERSONA/QA.md) | **코드 편집**: ❌

- [ ] 본 문서 § 코어 개념 ([§3](#3-코어-개념-요약))
- [ ] [ROLES/verifier.md](ROLES/verifier.md)
- [ ] [1-project.md](1-project.md)
- [ ] [2-architecture.md](2-architecture.md) § BE+FE
- [ ] [3-workflow.md](3-workflow.md) § 품질 게이트

**검증 시작 시**: [GUIDES/verifier-work-guide.md](GUIDES/verifier-work-guide.md) 참조

**핵심 원칙**: Critical 1건+ → FAIL, Critical 0/High 있음 → PARTIAL, Critical 0/High 0 → PASS

---

### 2.4 Tester

**팀원 이름**: `tester` | **Charter**: [QA.md](PERSONA/QA.md) | **코드 편집**: ❌

- [ ] 본 문서 § 코어 개념 ([§3](#3-코어-개념-요약))
- [ ] [ROLES/tester.md](ROLES/tester.md)
- [ ] [3-workflow.md](3-workflow.md) § 품질 게이트

**테스트 시작 시**: [GUIDES/tester-work-guide.md](GUIDES/tester-work-guide.md) 참조

**핵심 원칙**: pytest 실행, E2E 실행, 커버리지 80%, Team Lead 경유 보고

---

### 2.5 Team Lead

**실행**: 메인 세션 | **Charter**: [LEADER.md](PERSONA/LEADER.md) | **코드 편집**: ❌

- [ ] 본 문서 전체
- [ ] [1-project.md](1-project.md)
- [ ] [2-architecture.md](2-architecture.md)
- [ ] [3-workflow.md](3-workflow.md)
- [ ] [ROLES/*.md](ROLES/)

**핵심 원칙**: 코드 직접 수정 금지, Hub-and-Spoke 통신, 상태 기반 판정, SSOT 리로드 필수

---

## 3. 코어 개념 요약

### 3.1 팀 구조

```
Team Lead (메인 세션)
  ├── planner (Plan/opus) — 계획 수립
  ├── backend-dev (general-purpose/sonnet) — 백엔드 구현
  ├── frontend-dev (general-purpose/sonnet) — 프론트엔드 구현
  ├── verifier (Explore/sonnet) — 코드 리뷰
  └── tester (Bash/sonnet) — 테스트 실행
```

**코드 편집 원칙**:
- Team Lead: ❌ 코드 수정 금지 (조율·판정만)
- backend-dev: ✅ `backend/`, `tests/`, `scripts/` 편집
- frontend-dev: ✅ `web/`, `e2e/` 편집
- verifier: ❌ 읽기 전용 (수정 필요 시 Team Lead에게 보고)

---

### 3.2 상태 머신 (14개 상태)

```
IDLE → TEAM_SETUP → PLANNING → PLAN_REVIEW → TASK_SPEC
  → BUILDING → VERIFYING → TESTING → (다음 Task 또는 INTEGRATION)
  → INTEGRATION → E2E → E2E_REPORT → TEAM_SHUTDOWN → DONE
```

**실패 시**: REWINDING → 이전 상태로 복귀  
**차단 시**: BLOCKED → 이슈 해결 후 복귀

---

### 3.3 Hub-and-Spoke 통신 모델

**모든 팀원 통신은 Team Lead 경유**:
- 팀원 → SendMessage → Team Lead
- Team Lead → SendMessage → 특정 팀원
- 팀원끼리 직접 메시지 금지

**예시**:
1. backend-dev가 구현 완료 → SendMessage → Team Lead
2. Team Lead → SendMessage → verifier (검증 지시)
3. verifier → SendMessage → Team Lead (판정 보고)
4. Team Lead → SendMessage → backend-dev (수정 요청)

---

### 3.4 SSOT Lock Rules

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **LOCK-1** | Phase 실행 중 SSOT 변경 금지 | `current_state`가 `IDLE` 또는 `DONE`이 아닌 동안 SSOT 수정 불가 |
| **LOCK-2** | 변경 필요 시 Phase 일시정지 | SSOT 수정 불가피하면 `current_state`를 `BLOCKED`로 전이 후 변경 |
| **LOCK-3** | 변경 후 리로드 필수 | SSOT 변경 후 모든 팀원에게 SendMessage로 리로드 지시 |
| **LOCK-4** | 팀원 SSOT 수정 금지 | 팀원은 SSOT를 읽기 전용으로만 참조 |
| **LOCK-5** | 변경 이력 필수 기록 | SSOT 변경 시 버전 히스토리에 반드시 기록 |

**Lock 상태 머신**:
```
Phase 실행 중 (PLANNING~E2E_REPORT)
  │
  ├── SSOT 변경 필요 발견
  │     → current_state = BLOCKED (사유: "SSOT 변경 필요")
  │     → 사용자 승인 → SSOT 수정 → 버전 갱신
  │     → SendMessage(broadcast) — "SSOT 리로드 필요"
  │     → 리로드 완료 → 이전 상태 복귀
  │
  └── Phase 미실행 (IDLE / DONE)
        → SSOT 수정 가능 (버전 갱신 필수)
```

---

### 3.5 SSOT Freshness Rules

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **FRESH-1** | 세션 시작 시 SSOT 리로드 | 새 AI 세션 시작 시 SSOT 4개 파일을 순서대로 로딩 (0→1→2→3) |
| **FRESH-2** | 새 Phase 시작 시 버전 확인 | Phase 시작 전 SSOT 버전이 `ssot_version`과 일치하는지 확인 |
| **FRESH-3** | 버전 불일치 시 갱신 우선 | SSOT 버전이 변경되었으면 Phase 진행 전 SSOT를 먼저 리로드 |
| **FRESH-4** | 리로드 시각 기록 | SSOT 로딩 완료 시 `ssot_loaded_at`에 타임스탬프 기록 |
| **FRESH-5** | 장기 세션 중 주기적 확인 | Phase가 3개 이상의 Task를 처리한 경우 SSOT 버전 재확인 권장 |
| **FRESH-6** | 팀원 역할별 로딩 | 각 팀원은 스폰 시 해당 **ROLES/*.md** 1개만 로딩 (본 4th 세트 내) |

**로딩 순서 (Team Lead)**:
```
[0] 0-entrypoint.md (진입점, 역할별 체크리스트)
  ↓
[1] 1-project.md (팀 구성, 역할 정의)
  ↓
[2] 2-architecture.md (인프라, BE, FE 구조)
  ↓
[3] 3-workflow.md (상태 머신, 워크플로우, Phase Chain)
```

---

### 3.6 ENTRYPOINT 규칙

Phase 실행의 **단일 진입점**은 `phase-X-Y-status.md` 파일이다.

| 규칙 ID | 규칙 | 설명 |
|---------|------|------|
| **ENTRY-1** | 단일 진입점 | 모든 Phase 작업은 `docs/phases/phase-X-Y/phase-X-Y-status.md`를 먼저 읽는 것으로 시작 |
| **ENTRY-2** | 상태 기반 분기 | `current_state` 값에 따라 다음 행동을 결정 |
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
[6] 팀 상태 확인 (TeamCreate 필요 여부, 팀원 idle 상태)
  │
  ▼
[7] 워크플로우 실행
```

---

### 3.7 품질 게이트 (G1~G4)

```
[G1: Plan Review]     planner 분석 → Team Lead 검토
  ↓
[G2: Code Review]     verifier가 BE+FE 코드 검증 → Team Lead 보고
  ↓
[G3: Test Gate]       tester가 테스트 실행 + 커버리지 확인
  ↓
[G4: Final Gate]      Team Lead가 G2+G3 종합 판정
```

**판정 기준**:
- **G1 PASS**: 완료 기준 명확, Task 3~7개, 도메인 분류 완료
- **G2 PASS**: Critical 0건 (ORM 사용, Pydantic 검증, CDN 미사용, XSS 방지)
- **G3 PASS**: pytest PASS, 커버리지 ≥80%, E2E PASS, 회귀 테스트 통과
- **G4 PASS**: G2 PASS + G3 PASS + Blocker 0건

---

### 3.8 도메인 태그

모든 Task는 도메인 태그 필수:
- `[BE]`: 백엔드 (API, 서비스 로직)
- `[FE]`: 프론트엔드 (UI, 페이지)
- `[FS]`: 풀스택 (BE → FE 순서 또는 병렬)
- `[DB]`: 데이터베이스 (스키마, 마이그레이션)
- `[TEST]`: 테스트 (pytest, E2E)
- `[INFRA]`: 인프라 (Docker, 설정)

---

### 3.9 팀 라이프사이클 (루프 가능)

**한 Phase 내 라이프사이클**:

```
Phase 시작
  │
  ▼
[1] TeamCreate(team_name: "phase-X-Y")  ← 팀 생성 (Team Lead)
  │
  ▼
[2] Task tool(team_name, name, subagent_type, model) × N  ← 팀원 스폰
  │   예: planner (Plan/opus), backend-dev, frontend-dev (general-purpose/sonnet),
  │       verifier (Explore/sonnet), tester (Bash/sonnet)
  │
  ▼
[3] TaskCreate → TaskUpdate(owner) → SendMessage  ← 작업 할당·조율
  │
  ▼
[4] 팀원들이 TaskList로 작업 확인, 완료 시 TaskUpdate(completed) + SendMessage 보고
  │
  ▼
[5] 모든 작업 완료 → SendMessage(type: "shutdown_request") × N
  │
  ▼
[6] TeamDelete  ← 팀 해산 (Team Lead)
  │
  ▼
Phase 완료 (current_state: DONE)
```

**루프(다음 Phase)**:
- **단일 Phase만 실행**: DONE 도달 후 Phase 종료. 필요 시 새 Phase 시작 시 위 [1]부터 다시 진행 (새 팀 생성).
- **Phase Chain 사용**: `docs/phases/phase-chain-{name}.md`에 phases 배열을 정의하고, DONE 후 `/clear` → 다음 Phase의 status.md 읽기 → [1] TeamCreate(team_name: "phase-X-Y")부터 반복. 자세한 프로토콜은 [3-workflow.md § Phase Chain](3-workflow.md#phase-chain-자동-순차-실행) 참조.

**지연 스폰**: verifier, tester는 VERIFYING/TESTING 단계 진입 시 스폰 가능 (비용 절감).

---

## 4. 백엔드 핵심 규칙

| 규칙 | 설명 |
|------|------|
| **ORM 필수** | raw SQL 절대 금지, SQLAlchemy ORM만 사용 |
| **Pydantic 검증** | 모든 API 입력은 Pydantic 스키마로 검증 |
| **타입 힌트** | 함수 파라미터 + 반환 타입 힌트 필수 |
| **에러 핸들링** | try-except + HTTPException 패턴 |
| **비동기** | async/await 활용 |
| **네이밍** | snake_case |

**금지**: raw SQL, 타입 힌트 생략, 입력 검증 생략, 에러 처리 생략

➜ [상세: ROLES/backend-dev.md](ROLES/backend-dev.md)

---

## 5. 프론트엔드 핵심 규칙

| 규칙 | 설명 |
|------|------|
| **ESM import/export** | `type="module"` 필수 |
| **innerHTML + esc()** | XSS 방지 필수 |
| **외부 CDN 금지** | 모든 리소스는 로컬에서 제공 (`web/public/libs/`) |
| **window 전역 금지** | 기존 것 제외하고 새로 할당 금지 |
| **컴포넌트 재사용** | `layout-component.js`, `header-component.js` 활용 |

**금지**: CDN 참조, innerHTML without esc(), 새 window 전역 변수

➜ [상세: ROLES/frontend-dev.md](ROLES/frontend-dev.md)

---

## 6. Verifier 판정 기준

### 6.1 백엔드 (G2_be)

**Critical (필수)**:
- [ ] ORM 사용 (raw SQL 없음)
- [ ] Pydantic 검증 존재
- [ ] 타입 힌트 완전
- [ ] 기존 테스트 깨지지 않음

**High (권장)**:
- [ ] 에러 핸들링 존재
- [ ] 새 기능 테스트 파일 존재

### 6.2 프론트엔드 (G2_fe)

**Critical (필수)**:
- [ ] CDN 참조 없음
- [ ] innerHTML 시 esc() 사용
- [ ] ESM import/export 패턴
- [ ] 페이지 로드 시 콘솔 에러 없음

**High (권장)**:
- [ ] window 전역 변수 할당 없음
- [ ] 기존 컴포넌트 재사용
- [ ] API 에러 핸들링

➜ [상세: ROLES/verifier.md](ROLES/verifier.md)

---

## 7. 상세 가이드 링크 (본 4th 세트 내)

| 주제 | 링크 |
|------|------|
| **팀 구성·역할 상세** | [1-project.md](1-project.md) |
| **아키텍처 (인프라·BE·FE)** | [2-architecture.md](2-architecture.md) |
| **워크플로우·상태머신·Phase Chain** | [3-workflow.md](3-workflow.md) |
| **Planner** | [ROLES/planner.md](ROLES/planner.md) |
| **Backend 개발 가이드** | [ROLES/backend-dev.md](ROLES/backend-dev.md) |
| **Frontend 개발 가이드** | [ROLES/frontend-dev.md](ROLES/frontend-dev.md) |
| **Verifier 검증 가이드** | [ROLES/verifier.md](ROLES/verifier.md) |
| **Tester 테스트 가이드** | [ROLES/tester.md](ROLES/tester.md) |

---

## 8. 버전 관리

**현재 버전**: 6.0-renewal-4th  
**릴리스 날짜**: 2026-02-17  
**특징**: **claude/ 의존성 제거** — 본 iterations/4th 만으로 SSOT 단독 사용 가능. 팀 라이프사이클 루프·Phase Chain 보완.

➜ [상세 버전 정보: VERSION.md](VERSION.md)

---

**문서 관리**:
- 버전: 6.0-renewal-4th (4th iteration)
- 최종 수정: 2026-02-17
- 3차 대비: claude/ 참조 제거, 팀 라이프사이클 §3.9 추가, Planner 체크리스트 §2.0 추가, FRESH-6 로딩 대상 ROLES/*.md 명시
