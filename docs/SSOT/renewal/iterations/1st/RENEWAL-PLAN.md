# SSOT 리뉴얼 상세 플랜

**작성일**: 2026-02-17 11:00  
**작성자**: QA & Security Analyst  
**목적**: SSOT 문서 단기(1주) 리뉴얼 상세 실행 계획  
**전략**: 방안 C (요약+상세 분리) 적용 → 500줄 이내 읽기 가능  

---

## 📋 리뉴얼 목표

| 구분 | 현재 | 목표 (1차 리뉴얼) |
|------|------|------------------|
| **총 줄 수** | 2,756줄 | 1,550줄 (43% 감소) |
| **첫 진입 읽기** | 300줄 (Index) | 500줄 (요약형 Index) |
| **Backend 개발자 읽기** | 2,756줄 (전체) | 550줄 (80% 감소) |
| **Verifier 읽기** | 2,756줄 (전체) | 800줄 (71% 감소) |
| **역할별 진입점** | 불명확 | 명확한 체크리스트 |
| **버전 관리** | 파일별 개별 | 통합 VERSION.md |

---

## 🏗️ 폴더 구조

```
docs/SSOT/
├── claude/              (기존 — 수정 금지, 읽기 전용)
│   ├── 0-ssot-index.md
│   ├── 1-project-ssot.md
│   ├── 2-architecture-ssot.md
│   ├── 3-workflow-ssot.md
│   └── role-*-ssot.md
│
└── renewal/             (리뉴얼 — 신규 작성)
    ├── RENEWAL-PLAN.md  (본 문서)
    ├── VERSION.md       (통합 버전 관리)
    ├── 0-entrypoint.md  (500줄 — 요약형 진입점)
    ├── 1-project.md     (400줄 — 팀/역할 요약)
    ├── 2-architecture.md (350줄 — 인프라/BE/FE 요약)
    ├── 3-workflow.md    (300줄 — 상태머신 요약)
    ├── ROLES/
    │   ├── backend-dev.md    (120줄)
    │   ├── frontend-dev.md   (120줄)
    │   ├── verifier.md       (100줄)
    │   └── tester.md         (80줄)
    └── VERIFICATION/
        ├── verification-1-report.md (1차 검증)
        ├── verification-2-report.md (2차 검증)
        └── verification-3-report.md (3차 검증)
```

---

## 📝 1차 리뉴얼 작업 목록

### Task 1: VERSION.md 생성 (10분)

**목적**: 전체 SSOT 버전 통합 관리

```yaml
ssot_release: "5.0-renewal"
ssot_released_at: "2026-02-17T11:00:00Z"
renewal_strategy: "방안 C — 요약+상세 분리"
target_read_time: "10-15분 (500줄)"

file_versions:
  - file: "0-entrypoint.md"
    lines: 500
    update: "신규 작성"
  - file: "1-project.md"
    lines: 400
    update: "기존 578줄 → 400줄 (요약)"
  - file: "2-architecture.md"
    lines: 350
    update: "기존 516줄 → 350줄 (요약)"
  - file: "3-workflow.md"
    lines: 300
    update: "기존 1,059줄 → 300줄 (요약)"

role_specific_guides:
  - role: "Backend Developer"
    files: ["0-entrypoint.md", "ROLES/backend-dev.md", "1-project.md § 팀/상태", "2-architecture.md § BE"]
    total_lines: 550
    read_time: "10-15분"
  - role: "Frontend Developer"
    files: ["0-entrypoint.md", "ROLES/frontend-dev.md", "1-project.md § 팀/상태", "2-architecture.md § FE"]
    total_lines: 550
    read_time: "10-15분"
  - role: "Verifier"
    files: ["0-entrypoint.md", "ROLES/verifier.md", "1-project.md", "2-architecture.md § BE+FE"]
    total_lines: 800
    read_time: "15-20분"

breaking_changes:
  - "v4.x → v5.0: 파일 구조 변경 (claude/ → renewal/)"
  - "진입점 변경: 0-ssot-index.md → 0-entrypoint.md"
  - "상세 내용은 기존 claude/ 참조 링크 제공"
```

### Task 2: 0-entrypoint.md 작성 (60분)

**목적**: 500줄 이내 전체 SSOT 요약 + 역할별 체크리스트

**구조**:
```markdown
# SSOT 진입점 (v5.0-renewal)

## 📌 빠른 시작 (50줄)
- SSOT 목적
- 역할 선택 (6가지)
- 읽기 경로 요약

## 🎯 역할별 필독 체크리스트 (150줄)
### Backend Developer (550줄, 10-15분)
- [ ] 0-entrypoint.md (50줄)
- [ ] ROLES/backend-dev.md (120줄)
- [ ] 1-project.md § 팀/상태 (100줄)
- [ ] 2-architecture.md § BE (200줄)

### Verifier (800줄, 15-20분)
...

## 🏛️ 코어 개념 요약 (200줄)
### 상태 머신 (50줄)
- 상태 정의 8가지 (IDLE → DONE)
- 전이 규칙 핵심
- ➜ [상세 전이 규칙](3-workflow.md)

### Hub-and-Spoke 통신 (50줄)
- Team Lead 중심
- SendMessage 프로토콜
- ➜ [통신 상세](1-project.md#communication)

### SSOT Lock (50줄)
- LOCK-1~5 규칙
- Phase 실행 중 수정 금지
- ➜ [Lock 상세](../claude/0-ssot-index.md#lock)

### ENTRYPOINT 규칙 (50줄)
- status.md 기반 분기
- 진입 플로우
- ➜ [워크플로우 상세](3-workflow.md)

## 🏗️ 아키텍처 요약 (100줄)
- 인프라 (Docker Compose)
- 백엔드 (FastAPI)
- 프론트엔드 (Vanilla JS)
- ➜ [아키텍처 상세](2-architecture.md)
```

**포함 내용**:
- 역할별 읽기 경로 명확화
- <details> 펼침형 활용
- 상세는 링크 제공 (기존 claude/ 또는 renewal/ 내 파일)

### Task 3: 1-project.md 작성 (40분)

**목적**: 프로젝트·팀 구성 요약 (578줄 → 400줄)

**구조**:
```markdown
# 프로젝트 SSOT (요약)

## 1. 프로젝트 정의 (50줄)
- Personal AI Brain v3
- 배포: Docker Compose
- 현재: Phase 14 완료, Phase 15 계획

## 2. 팀 구성 요약 (100줄)
- 역할 6가지 (Team Lead, Backend, Frontend, Verifier, Tester, Planner)
- 각 역할 핵심 책임 (표 형식)
- 코드 편집 권한 매핑
- ➜ [상세 역할 정의](../claude/1-project-ssot.md)

## 3. 팀 라이프사이클 (100줄)
- TeamCreate → 팀원 스폰 → Task 할당 → 완료 → TeamDelete
- 다이어그램 포함
- ➜ [상세 시나리오](../claude/1-project-ssot.md#lifecycle)

## 4. 역할별 상세 (선택, 150줄)
<details>
<summary>Backend Developer</summary>
- Charter: BACKEND.md
- 권한: 코드 편집 가능
- 담당: backend/, tests/
- ➜ [Backend 전용 가이드](ROLES/backend-dev.md)
</details>

<details>
<summary>Verifier</summary>
- Charter: QA.md
- 권한: 읽기 전용
- 담당: 코드 리뷰 (G2 게이트)
- ➜ [Verifier 전용 가이드](ROLES/verifier.md)
</details>
```

### Task 4: 2-architecture.md 작성 (40분)

**목적**: 아키텍처 요약 (516줄 → 350줄)

**구조**:
```markdown
# 아키텍처 SSOT (요약)

## 1. 인프라 구성 (100줄)
- Docker Compose 다이어그램
- 컨테이너 4개 (PostgreSQL, Qdrant, Redis, Backend)
- 포트 매핑 (ver3 전용: 5433, 6343, 8001)
- ➜ [상세 사양](../claude/2-architecture-ssot.md#infra)

## 2. 백엔드 구조 요약 (120줄)
- 디렉토리 맵 (간략)
- 기술 스택 (FastAPI, SQLAlchemy)
- 코드 규칙 핵심 (ORM 필수 등)
- ➜ [백엔드 상세](ROLES/backend-dev.md)

## 3. 프론트엔드 구조 요약 (120줄)
- 디렉토리 맵 (간략)
- 기술 스택 (Vanilla JS, Jinja2)
- 코드 규칙 핵심 (ESM, esc() 등)
- ➜ [프론트엔드 상세](ROLES/frontend-dev.md)

## 4. 데이터베이스 (10줄)
- PostgreSQL: 메타데이터
- Qdrant: 벡터 검색
- Redis: 캐싱
- ➜ [상세 스키마](../claude/2-architecture-ssot.md#db)
```

### Task 5: 3-workflow.md 작성 (40분)

**목적**: 워크플로우 요약 (1,059줄 → 300줄)

**구조**:
```markdown
# 워크플로우 SSOT (요약)

## 0. ENTRYPOINT 정의 (50줄)
- status.md 기반 진입
- 상태 확인 → 다음 행동 결정
- ➜ [ENTRYPOINT 상세](../claude/3-workflow-ssot.md#entrypoint)

## 1. 상태 머신 (100줄)
### 상태 정의 (50줄, 표 형식)
- IDLE, TEAM_SETUP, PLANNING, BUILDING, VERIFYING, TESTING, E2E, DONE

### 상태 전이 다이어그램 (50줄)
- 간략 다이어그램
- ➜ [상세 전이 규칙](../claude/3-workflow-ssot.md#state-transition)

## 2. 상태 파일 스키마 (50줄)
- phase-X-Y-status.md 구조
- 필수 필드 (current_state, team_members, gate_results 등)
- ➜ [전체 스키마](../claude/3-workflow-ssot.md#status-file)

## 3. 품질 게이트 (50줄)
- G1: Plan Review
- G2: Code Review (Backend/Frontend)
- G3: Test Gate
- G4: Final Gate
- ➜ [게이트 상세](../claude/3-workflow-ssot.md#quality-gates)

## 4. SSOT Lock (50줄)
- LOCK-1~5 규칙
- Lock 레벨 (STRICT, NORMAL, FLEXIBLE)
- ➜ [Lock 상세](../claude/0-ssot-index.md#lock)
```

### Task 6: ROLES/*.md 작성 (80분)

**목적**: 역할별 전용 가이드 (기존 role-*-ssot.md 개선)

#### ROLES/backend-dev.md (120줄)
```markdown
# Backend Developer 가이드 (v5.0)

## 1. 역할 정의 (30줄)
- 팀원: backend-dev
- Charter: BACKEND.md
- 권한: 코드 편집 가능
- 담당: backend/, tests/

## 2. 필독 체크리스트 (20줄)
- [ ] 0-entrypoint.md (50줄)
- [ ] 본 문서 (120줄)
- [ ] 1-project.md § 상태머신 (50줄)
- [ ] 2-architecture.md § 백엔드 (200줄)

## 3. 코드 규칙 (40줄)
- ORM 필수 (raw SQL 금지)
- Pydantic 검증
- 타입 힌트 필수
- ➜ [상세 규칙](../claude/role-backend-dev-ssot.md)

## 4. Task 실행 프로세스 (30줄)
- TaskList 확인
- TaskUpdate(in_progress)
- 구현 → SendMessage 보고
- ➜ [프로세스 상세](../claude/role-backend-dev-ssot.md#process)
```

#### ROLES/frontend-dev.md (120줄)
```markdown
# Frontend Developer 가이드 (v5.0)

## 1. 역할 정의 (30줄)
- 팀원: frontend-dev
- Charter: FRONTEND.md
- 권한: 코드 편집 가능
- 담당: web/

## 2. 필독 체크리스트 (20줄)
- [ ] 0-entrypoint.md (50줄)
- [ ] 본 문서 (120줄)
- [ ] 1-project.md § 상태머신 (50줄)
- [ ] 2-architecture.md § 프론트엔드 (200줄)

## 3. 코드 규칙 (40줄)
- ESM import/export
- innerHTML 시 esc() 필수
- 외부 CDN 금지
- ➜ [상세 규칙](../claude/role-frontend-dev-ssot.md)

## 4. Task 실행 프로세스 (30줄)
- (Backend와 동일)
```

#### ROLES/verifier.md (100줄)
```markdown
# Verifier 가이드 (v5.0)

## 1. 역할 정의 (30줄)
- 팀원: verifier
- Charter: QA.md
- 권한: 읽기 전용
- 담당: 코드 리뷰 (G2 게이트)

## 2. 필독 체크리스트 (20줄)
- [ ] 0-entrypoint.md (50줄)
- [ ] 본 문서 (100줄)
- [ ] 1-project.md (100줄)
- [ ] 2-architecture.md § BE+FE (300줄)

## 3. 검증 기준 (40줄)
### Backend Critical
- 구문 오류 없음
- ORM 사용
- FK 정합성

### Frontend Critical
- 콘솔 에러 없음
- innerHTML + esc()
- 기존 기능 유지

➜ [상세 기준](../claude/role-verifier-ssot.md)

## 4. 판정 규칙 (10줄)
- Critical 1건+ → FAIL
- Critical 0, High 있음 → PARTIAL
- Critical 0, High 0 → PASS
```

#### ROLES/tester.md (80줄)
```markdown
# Tester 가이드 (v5.0)

## 1. 역할 정의 (25줄)
- 팀원: tester
- Charter: QA.md
- 권한: Bash 전용
- 담당: 테스트 실행 (G3 게이트)

## 2. 필독 체크리스트 (15줄)
- [ ] 0-entrypoint.md (50줄)
- [ ] 본 문서 (80줄)
- [ ] 3-workflow.md § 게이트 (50줄)

## 3. 테스트 실행 (40줄)
- pytest 실행
- E2E 실행 (Playwright)
- 커버리지 분석
- ➜ [테스트 가이드](../claude/role-tester-ssot.md)
```

---

## 🔍 1차 검증 기준

### 검증 체크리스트

1. **줄 수 목표 달성**
   - [ ] 0-entrypoint.md ≤ 500줄
   - [ ] 1-project.md ≤ 400줄
   - [ ] 2-architecture.md ≤ 350줄
   - [ ] 3-workflow.md ≤ 300줄
   - [ ] ROLES/*.md 각 ≤ 120줄

2. **내용 완전성**
   - [ ] 모든 핵심 개념 포함 (상태머신, 팀구성, Lock 등)
   - [ ] 역할별 체크리스트 명확
   - [ ] 상세 링크 모두 유효

3. **가독성**
   - [ ] 마크다운 문법 정확
   - [ ] 다이어그램/표 적절히 사용
   - [ ] <details> 펼침형 적절히 배치

4. **일관성**
   - [ ] 용어 통일 (팀원 vs 에이전트)
   - [ ] 버전 표기 통일 (v5.0-renewal)
   - [ ] 파일 경로 일관성

5. **누락 확인**
   - [ ] 기존 claude/ 대비 누락 개념 없음
   - [ ] 역할별 필수 정보 모두 포함
   - [ ] 상세 참조 링크 모두 제공

---

## 📊 예상 결과

| 지표 | 현재 (claude/) | 1차 리뉴얼 (renewal/) | 개선율 |
|------|----------------|----------------------|--------|
| 총 줄 수 | 2,756줄 | 1,670줄 | 39% 감소 |
| 진입점 | 300줄 | 500줄 | 66% 확장 (요약형) |
| Backend 읽기 | 2,756줄 | 550줄 | 80% 감소 |
| Verifier 읽기 | 2,756줄 | 800줄 | 71% 감소 |
| 역할별 진입점 | 불명확 | 명확 (체크리스트) | — |
| 읽기 시간 | 60분+ | 10-20분 | 70% 단축 |

---

## ⏱️ 작업 일정

| Task | 예상 시간 | 담당 | 완료 기준 |
|------|----------|------|----------|
| VERSION.md | 10분 | QA | 버전 정보 완료 |
| 0-entrypoint.md | 60분 | QA | 500줄 이내, 체크리스트 완료 |
| 1-project.md | 40분 | QA | 400줄 이내, 요약 완료 |
| 2-architecture.md | 40분 | QA | 350줄 이내, 요약 완료 |
| 3-workflow.md | 40분 | QA | 300줄 이내, 요약 완료 |
| ROLES/*.md (4개) | 80분 | QA | 각 120줄 이내 |
| **합계** | **270분 (4.5시간)** | — | 모든 문서 완료 |

---

## 🔄 검증 단계 (3회 반복)

### 1차 검증 (작성 직후)
- 기존 claude/ 문서와 대조
- 누락 개념 확인
- 줄 수 목표 달성 확인
- **리포트**: verification-1-report.md

### 2차 검증 (1차 수정 후)
- 역할별 읽기 시뮬레이션
- 링크 유효성 검증
- 가독성 검토
- **리포트**: verification-2-report.md

### 3차 검증 (2차 수정 후)
- 최종 품질 확인
- 버전 일관성 검증
- 배포 준비 완료 확인
- **리포트**: verification-3-report.md

---

**문서 관리**:
- 버전: 1.0
- 최종 수정: 2026-02-17
- 다음 단계: 1차 리뉴얼 문서 작성 시작
