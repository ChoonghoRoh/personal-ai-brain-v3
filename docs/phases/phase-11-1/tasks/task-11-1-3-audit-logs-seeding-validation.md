# Task 11-1-3: audit_logs, 시딩, 관계 검증

**우선순위**: 11-1 내 3순위  
**예상 작업량**: 0.5~1일  
**의존성**: 11-1-2 검증 통과 후  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-1-0-todo-list.md](../phase-11-1-0-todo-list.md)  
**Plan**: [phase-11-1-0-plan.md](../phase-11-1-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**audit_logs** 테이블 마이그레이션을 작성하고, Phase 11-1 전체 **7종 Admin 설정 테이블**의 관계(FK·인덱스)·초기 시딩 스크립트를 검증한다. Phase 10 회귀 테스트 유지 확인 후 Phase 11-2로 전달한다.

### 1.2 영향도 (Phase 11-1 시점)

| 항목 | 내용 |
|------|------|
| Backend 사용처 | 없음 (Phase 11-2에서 사용 예정) |
| Frontend 사용처 | 없음 (Phase 11-3에서 사용 예정) |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| audit_logs 마이그레이션 | audit_logs 테이블 CREATE |
| 초기 시딩 스크립트 (필요 시) | 관계 검증·시딩 실행 |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| (없음) | 기존 테이블 스키마 변경 없음 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 영향도 검증 (개발 착수 전)

- [ ] audit_logs 테이블 Backend/Frontend 사용처 조사 — 없음, 기록
- [ ] 전체 Admin 설정 테이블(7종) 관계도 확인

### 3.2 백업

- [ ] 마이그레이션 실행 직전: `./scripts/backup/backup.sh --postgres-only`
- [ ] 백업 ID·경로 확인

### 3.3 개발

- [ ] audit_logs 테이블 마이그레이션 작성
- [ ] 전체 테이블 관계 검증 (FK·인덱스)
- [ ] 초기 시딩 스크립트 실행·검증

### 3.4 단계별 테스트 검증 (통과 후 Phase 11-2 전달)

- [ ] `audit_logs` 테이블 존재 확인
- [ ] 전체 Admin 설정 테이블(7종) 관계·인덱스 검증
- [ ] 초기 시딩 스크립트 실행 결과·행 수 검증
- [ ] Phase 10 회귀 테스트(Reasoning Lab·E2E) 유지 확인
- [ ] Task 계획·report 문서화

---

## 4. 참조

- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Admin DB 스키마(SQL) 상세
- [phase-11-1-0-plan.md](../phase-11-1-0-plan.md) §6.3·§7.4 — Task 11-1-3 검증 항목
