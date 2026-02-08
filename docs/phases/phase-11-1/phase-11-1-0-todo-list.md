# Phase 11-1: DB 스키마·마이그레이션 — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 11 내 1순위
**예상 작업량**: 2.5~3일
**시작일**: 2026-02-06
**완료일**: 2026-02-06

**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)
**Plan**: [phase-11-1-0-plan.md](phase-11-1-0-plan.md)

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 11-1
- **Phase 명**: DB 스키마·마이그레이션
- **핵심 목표**: 7종 테이블 마이그레이션·시딩, 관계 검증, 데이터 무손실·단계별 검증 후 진행

### 이전 Phase

- **Prev Phase ID**: 10-4 (또는 Phase 10 전체)
- **Prev Phase 명**: 고급 기능 / Phase 10
- **전환 조건**: Phase 10 완료

### 다음 Phase

- **Next Phase ID**: 11-2
- **Next Phase 명**: Admin 설정 Backend API
- **전환 조건**: 11-1 전체 Task 완료 및 최종 검증 통과

### Phase 11 내 우선순위

| 순위 | Phase ID | Phase 명 | 상태 |
|------|----------|----------|------|
| **1** | **11-1** | **DB 스키마·마이그레이션** | ✅ 완료 |
| 2 | 11-2 | Admin 설정 Backend API | ⏳ 대기 |
| 3 | 11-3 | Admin UI | ⏳ 대기 |
| 4 | 11-4 | 통합 테스트·운영 준비 | ⏳ 대기 |

---

## 공통 절차 (Task별 적용)

각 Task는 다음 순서로 진행한다. **검증 통과 후에만** 다음 Task로 이동한다.

1. **영향도 검증** — 해당 테이블의 Backend/Frontend 사용처 조사·기록
2. **백업** — `./scripts/backup/backup.sh --postgres-only`
3. **마이그레이션·시딩 개발** — 스크립트 작성·실행
4. **단계별 테스트 검증** — Plan §7 해당 Task 검증 항목 수행
5. **통과 시** — Task report 작성, 다음 Task 착수

---

## Task 목록 (세부 단계·검증 포함)

### 11-1-1: schemas, templates, prompt_presets 테이블 설계·마이그레이션 ✅

**우선순위**: 11-1 내 1순위
**예상 작업량**: 1일
**의존성**: 없음
**상태**: ✅ 완료

#### 영향도 검증 (개발 착수 전)

- [x] 해당 테이블(schemas, templates, prompt_presets) Backend 사용처 조사 — Phase 11-1 시점에는 없음, 기록만
- [x] 해당 테이블 Frontend 사용처 조사 — 없음, 기록만
- [x] 조사 결과 task 문서에 기록 (`phase-11-1/tasks/`)

#### 백업

- [x] 마이그레이션 실행 직전: Docker 내 `pg_dump` 실행
- [x] 백업 ID·경로 확인

#### 개발

- [x] SQL 스크립트로 마이그레이션 파일 작성 (`scripts/db/migrate_phase11_1_1.sql`)
- [x] 초기 시딩 데이터 정의 (`scripts/db/seed_phase11_1_1.sql`)
- [x] 마이그레이션·시딩 실행

#### 단계별 테스트 검증

- [x] `schemas`, `templates`, `prompt_presets` 테이블이 DB에 존재하는지 확인
- [x] 시딩 데이터 행 수가 기대값과 일치하는지 확인 (schemas 6, templates 3, prompt_presets 4)
- [x] 기존 기능(대시보드, 검색, 지식, Reasoning Lab 등) 회귀 없음 확인
- [x] Task 계획·report 문서화 (`phase11-1-1-task-test-report.md`)

---

### 11-1-2: rag_profiles, context_rules, policy_sets 테이블 설계·마이그레이션 ✅

**우선순위**: 11-1 내 2순위
**예상 작업량**: 1일
**의존성**: 11-1-1 검증 통과 후
**상태**: ✅ 완료

#### 영향도 검증 (개발 착수 전)

- [x] 해당 테이블(rag_profiles, context_rules, policy_sets) Backend 사용처 조사 — 없음, 기록
- [x] 해당 테이블 Frontend 사용처 조사 — 없음, 기록
- [x] FK 관계(policy_sets → projects, templates, prompt_presets, rag_profiles) 영향 범위 정리

#### 백업

- [x] 마이그레이션 실행 직전: Docker 내 `pg_dump` 실행
- [x] 백업 ID·경로 확인

#### 개발

- [x] SQL 마이그레이션 파일 작성 (`scripts/db/migrate_phase11_1_2.sql`)
- [x] policy_sets → templates, prompt_presets, rag_profiles, projects FK 관계 반영
- [x] 초기 시딩 (`scripts/db/seed_phase11_1_2.sql`) · 마이그레이션 실행

#### 단계별 테스트 검증

- [x] `rag_profiles`, `context_rules`, `policy_sets` 테이블 존재 및 FK 관계 확인
- [x] 시딩·제약 조건 오류 없음 확인 (rag_profiles 3, context_rules 4, policy_sets 2)
- [x] 기존 기능 회귀 없음 확인
- [x] Task 계획·report 문서화 (`phase11-1-2-task-test-report.md`)

---

### 11-1-3: audit_logs, 시딩, 관계 검증 ✅

**우선순위**: 11-1 내 3순위
**예상 작업량**: 0.5~1일
**의존성**: 11-1-2 검증 통과 후
**상태**: ✅ 완료

#### 영향도 검증 (개발 착수 전)

- [x] audit_logs 테이블 Backend/Frontend 사용처 조사 — 없음, 기록
- [x] 전체 Admin 설정 테이블(7종) 관계도 확인

#### 백업

- [x] 마이그레이션 전 Docker 내 `pg_dump` 실행
- [x] 백업 ID·경로 확인

#### 개발

- [x] audit_logs 테이블 마이그레이션 작성 (`scripts/db/migrate_phase11_1_3.sql`)
- [x] 전체 테이블 관계 검증 (FK 4개·인덱스 16개)
- [x] 초기 시딩 스크립트 (`scripts/db/seed_phase11_1_3.sql`) 실행·검증

#### 단계별 테스트 검증

- [x] `audit_logs` 테이블 존재 확인
- [x] 전체 Admin 설정 테이블(7종) 관계·인덱스 검증 (16 인덱스, 4 FK)
- [x] 초기 시딩 스크립트 실행 결과·행 수 검증 (총 25행)
- [x] 기존 서비스 회귀 확인 (system info, search, knowledge 모두 200)
- [x] Task 계획·report 문서화 (`phase11-1-3-task-test-report.md`)
