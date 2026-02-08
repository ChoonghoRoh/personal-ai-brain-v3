# Task 11-1-2: rag_profiles, context_rules, policy_sets 테이블 설계·마이그레이션

**우선순위**: 11-1 내 2순위  
**예상 작업량**: 1일  
**의존성**: 11-1-1 검증 통과 후  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-1-0-todo-list.md](../phase-11-1-0-todo-list.md)  
**Plan**: [phase-11-1-0-plan.md](../phase-11-1-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

Admin 설정 중 **RAG 프로필(rag_profiles)·컨텍스트 규칙(context_rules)·정책 세트(policy_sets)** 3종 테이블의 DB 스키마를 설계하고, 마이그레이션·초기 시딩을 구축한다. policy_sets → templates 등 FK 관계를 반영하며, 기존 테이블은 변경하지 않는다.

### 1.2 영향도 (Phase 11-1 시점)

| 항목 | 내용 |
|------|------|
| Backend 사용처 | 없음 (Phase 11-2에서 사용 예정) |
| Frontend 사용처 | 없음 (Phase 11-3에서 사용 예정) |
| FK 관계 | policy_sets → templates 등 (신규 테이블 간 또는 신규→기존 참조만) |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| Alembic 마이그레이션 또는 SQL/스크립트 | rag_profiles, context_rules, policy_sets 테이블 CREATE |
| 시딩 스크립트/데이터 | 초기 데이터, FK 관계 반영 |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| (없음) | 기존 테이블 스키마 변경 없음 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 영향도 검증 (개발 착수 전)

- [ ] 해당 테이블(rag_profiles, context_rules, policy_sets) Backend 사용처 조사 — 없음, 기록
- [ ] 해당 테이블 Frontend 사용처 조사 — 없음, 기록
- [ ] FK 관계(policy_sets → templates 등) 영향 범위 정리

### 3.2 백업

- [ ] 마이그레이션 실행 직전: `./scripts/backup/backup.sh --postgres-only`
- [ ] 백업 ID·경로 확인

### 3.3 개발

- [ ] Alembic/SQL 마이그레이션 파일 작성 (rag_profiles, context_rules, policy_sets)
- [ ] policy_sets → templates 등 FK 관계 반영
- [ ] 초기 시딩·마이그레이션 실행

### 3.4 단계별 테스트 검증 (통과 후에만 11-1-3 착수)

- [ ] `rag_profiles`, `context_rules`, `policy_sets` 테이블 존재 및 FK 관계 확인
- [ ] 시딩·제약 조건 오류 없음 확인
- [ ] 기존 기능 회귀 없음 확인
- [ ] Task 계획·report 문서화

---

## 4. 참조

- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Admin DB 스키마(SQL) 상세
- [phase-11-1-0-plan.md](../phase-11-1-0-plan.md) §6.2·§7.3 — Task 11-1-2 검증 항목
