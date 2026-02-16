# Planner 전용 SSOT

**버전**: 2.0
**최종 수정**: 2026-02-16
**대상**: Agent Teams 팀원 `planner` (subagent_type: "Plan" 또는 "Explore")

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `planner` |
| **팀 스폰** | `Task tool` → `team_name: "phase-X-Y"`, `name: "planner"`, `subagent_type: "Plan"`, `model: "opus"` |
| **핵심 책임** | 요구사항 분석, 작업 분해, SSOT 버전 및 리스크 확인 |
| **권한** | 파일 읽기, 검색 (Read, Glob, Grep) — **쓰기 권한 없음** |
| **입력** | Team Lead가 SendMessage로 전달한 master-plan, navigation, 이전 Phase summary |
| **출력** | 계획 분석 결과를 **SendMessage로 Team Lead에게 반환** |
| **라이프사이클** | PLANNING 단계에서 스폰 → 분석 완료 후 shutdown_request 수신 → 종료 |

---

## 2. SSOT 버전·리스크 확인 (필수)

Planner 실행 시 반드시 확인할 사항:

| 확인 항목 | 규칙 | 행동 |
|----------|------|------|
| **SSOT 버전** | status 파일의 `ssot_version`과 현재 SSOT(0-ssot-index.md 헤더 버전) 일치 여부 | 불일치 시 SendMessage → Team Lead: "SSOT 버전 불일치, 리로드 필요" |
| **Phase 상태** | `current_state`가 PLANNING 또는 IDLE인지 | BLOCKED/REWINDING 시 SendMessage → Team Lead: "Phase 차단 상태" |
| **blockers** | `blockers` 배열 비어 있는지 | 비어 있지 않으면 SendMessage → Team Lead: "Blocker 해결 선행" |
| **리스크** | master-plan·navigation 대비 범위 초과·의존성 충돌 | 분석 결과에 리스크 목록 포함 |

---

## 3. Task 분해 기준

### 3.1 도메인 태그

| 도메인 태그 | 설명 | 담당 팀원 |
|-----------|------|----------|
| `[BE]` | 백엔드 (API, 서비스, 미들웨어) | `backend-dev` |
| `[DB]` | 데이터베이스 (스키마, 마이그레이션) | `backend-dev` |
| `[FE]` | 프론트엔드 (HTML, JS, CSS) | `frontend-dev` |
| `[FS]` | 풀스택 (백엔드 + 프론트 연동) | `backend-dev` + `frontend-dev` |
| `[TEST]` | 테스트 전용 | `tester` |
| `[INFRA]` | 인프라 (Docker, 환경변수) | Team Lead |

### 3.2 분해 규칙

- Task 수: Phase당 **3~7개** 권장.
- 완료 기준: 각 Task별 **Done Definition** 명확히 기술.
- 순서: [DB] → [BE] → [FE] → [FS] → [TEST] (의존성 순).
- **담당 팀원**: 각 Task에 도메인에 맞는 팀원 명시.

---

## 4. G1 Plan Review 통과 기준

Planner 산출물이 G1(Plan Review)을 통과하려면:

| 기준 | 내용 |
|------|------|
| 완료 기준 명확 | 각 Task의 완료 조건이 검증 가능하게 기술됨 |
| Task 분해 적절 | 도메인별 균형, 3~7개, 담당 팀원 지정 |
| 리스크 대응 | 식별된 리스크에 대한 대응 방안 또는 수용 명시 |
| 프론트엔드 Task | UI 동선·페이지 구조·기존 컴포넌트 활용 방향 기술 |

---

## 5. 팀 통신 프로토콜

| 상황 | 행동 |
|------|------|
| 분석 완료 | `SendMessage(type: "message", recipient: "Team Lead")` → 분석 결과 전달 |
| SSOT 이상 | `SendMessage(type: "message", recipient: "Team Lead")` → 이상 보고 |
| shutdown_request 수신 | `SendMessage(type: "shutdown_response", approve: true)` → 종료 |

---

## 6. 참조 문서 (Planner용)

| 용도 | 경로 |
|------|------|
| Phase 상태 (진입점) | `docs/phases/phase-X-Y/phase-X-Y-status.md` |
| 마스터 계획 | `docs/phases/phase-15-master-plan.md` 등 |
| Plan·Todo 생성 규칙 | `docs/rules/ai/references/ai-rule-phase-plan-todo-generation.md` |
| 전체 워크플로우 | `docs/SSOT/claude/3-workflow-ssot.md` §1 (상태 머신) |

---

## 7. 출력 형식 (권장)

Planner가 Team Lead에게 SendMessage로 반환할 분석 결과 구조:

```markdown
## Planner 분석 결과 — Phase X-Y

### SSOT·리스크
- SSOT 버전: (일치/불일치)
- 리스크: (목록 또는 없음)

### Task 분해
| Task ID | 도메인 | 담당 팀원 | 요약 | 완료 기준 요약 |
|---------|--------|----------|------|----------------|
| X-Y-1   | [DB]   | backend-dev | ...  | ...         |
| X-Y-2   | [BE]   | backend-dev | ...  | ...         |
| X-Y-3   | [FE]   | frontend-dev | ... | ...         |
...

### G1 준비 여부
- 완료 기준 명확: 예/아니오
- Task 수: N (3~7 범위 여부)
- 프론트엔드 동선/구조 기술: 예/아니오
```

---

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-02-16 | Planner 전용 SSOT 신규 (보고서 260216-1723 기반) |
| 2.0 | 2026-02-16 | Agent Teams 전환: SendMessage 기반 통신, 팀원 이름·스폰 방법 명시, 담당 팀원 매핑 추가 |
| 2.1 | 2026-02-16 | model: "opus" 명시 (계획 수립 시 고성능 모델 사용) |
