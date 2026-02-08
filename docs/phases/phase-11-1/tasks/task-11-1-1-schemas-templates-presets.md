# Task 11-1-1: schemas, templates, prompt_presets 테이블 설계·마이그레이션

**우선순위**: 11-1 내 1순위  
**예상 작업량**: 1일  
**의존성**: 없음  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-1-0-todo-list.md](../phase-11-1-0-todo-list.md)  
**Plan**: [phase-11-1-0-plan.md](../phase-11-1-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

Admin 설정 중 **Role 스키마(schemas)·판단 문서 템플릿(templates)·프롬프트 프리셋(prompt_presets)** 3종 테이블의 DB 스키마를 설계하고, 마이그레이션·초기 시딩을 구축한다. 기존 테이블은 변경하지 않는다.

### 1.2 영향도 (Phase 11-1 시점)

| 항목 | 내용 |
|------|------|
| Backend 사용처 | 없음 (Phase 11-2에서 API 구현 예정) |
| Frontend 사용처 | 없음 (Phase 11-3에서 사용 예정) |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| Alembic 마이그레이션 또는 SQL/스크립트 | schemas, templates, prompt_presets 테이블 CREATE |
| 시딩 스크립트/데이터 | 초기 데이터 (phase-11-master-plan-sample 참고) |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| (없음) | 기존 테이블 스키마 변경 없음 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 영향도 검증 (개발 착수 전)

- [ ] 해당 테이블(schemas, templates, prompt_presets) Backend 사용처 조사 — Phase 11-1 시점에는 없음, 기록만
- [ ] 해당 테이블 Frontend 사용처 조사 — 없음, 기록만
- [ ] 조사 결과 task 문서에 기록 (`phase-11-1/tasks/`)

### 3.2 백업

- [ ] 마이그레이션 실행 직전: `./scripts/backup/backup.sh --postgres-only`
- [ ] 백업 ID·경로 확인

### 3.3 개발

- [ ] Alembic 또는 SQL/스크립트로 마이그레이션 파일 작성 (schemas, templates, prompt_presets)
- [ ] 초기 시딩 데이터 정의 (phase-11-master-plan-sample 참고)
- [ ] 마이그레이션·시딩 실행

### 3.4 단계별 테스트 검증 (통과 후에만 11-1-2 착수)

- [ ] `schemas`, `templates`, `prompt_presets` 테이블이 DB에 존재하는지 확인
- [ ] 시딩 데이터 행 수가 기대값과 일치하는지 확인
- [ ] 기존 기능(대시보드, 검색, 지식, Reasoning Lab 등) 회귀 없음 확인
- [ ] Task 계획·report 문서화 (`phase-11-1/tasks/`, `phase-11-1/phase11-1-1-*-test-report.md`)

---

## 4. 참조

- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Admin DB 스키마(SQL) 상세
- [phase-11-1-0-plan.md](../phase-11-1-0-plan.md) §6.1·§7.2 — Task 11-1-1 검증 항목
