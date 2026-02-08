# Task 11-1-2 Test Report — rag_profiles, context_rules, policy_sets

**Task ID**: 11-1-2
**상태**: ✅ 완료
**실행일**: 2026-02-06
**작성자**: Claude (자동)

---

## 1. 실행 내역

### 1.1 영향도 검증

- Backend 사용처: 없음 (신규 테이블, Phase 11-2에서 API 구현 예정)
- Frontend 사용처: 없음 (Phase 11-3에서 Admin UI 구현 예정)
- FK 관계: policy_sets → projects(integer), templates(UUID), prompt_presets(UUID), rag_profiles(UUID)

### 1.2 백업

- Docker 내 `pg_dump` 스키마 + 데이터 백업 실행 완료

### 1.3 마이그레이션

- **파일**: `scripts/db/migrate_phase11_1_2.sql`
- **실행**: `docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_2.sql`
- **결과**: CREATE TABLE × 3, CREATE INDEX × 2 성공

### 1.4 시딩

- **파일**: `scripts/db/seed_phase11_1_2.sql`
- **결과**: rag_profiles 3행, context_rules 4행, policy_sets 2행 삽입
- policy_sets는 기존 templates/prompt_presets/rag_profiles의 실제 ID를 동적 참조하여 삽입

### 1.5 SQLAlchemy 모델

- **파일**: `backend/models/admin_models.py` — `AdminRagProfile`, `AdminContextRule`, `AdminPolicySet` 클래스
- policy_sets의 project_id는 Integer FK (projects.id가 Integer PK이므로 master-plan-sample의 UUID FK에서 수정)

---

## 2. 검증 결과

| 검증 항목 | 결과 | 비고 |
|-----------|------|------|
| rag_profiles 테이블 존재 | ✅ | PK |
| context_rules 테이블 존재 | ✅ | PK |
| policy_sets 테이블 존재 | ✅ | PK + idx_policy_sets_project, idx_policy_sets_active |
| rag_profiles 시딩 행 수 | ✅ | 3행 (기본, 정밀, 대용량) |
| context_rules 시딩 행 수 | ✅ | 4행 (개발, 회의록, 기획서, 보고서) |
| policy_sets 시딩 행 수 | ✅ | 2행 (전역 기본, 요약 전용) |
| FK 제약 조건 | ✅ | 4개 FK (projects, templates, prompt_presets, rag_profiles) |
| policy_sets FK 참조 정상 | ✅ | has_template, has_preset, has_rag 모두 true |
| 인덱스 수 | ✅ | 5개 (PK 3 + 커스텀 2) |
| 기존 서비스 회귀 | ✅ | system info 200 |

---

## 3. 산출물

| 산출물 | 경로 |
|--------|------|
| SQL 마이그레이션 | `scripts/db/migrate_phase11_1_2.sql` |
| SQL 시딩 | `scripts/db/seed_phase11_1_2.sql` |
| SQLAlchemy 모델 | `backend/models/admin_models.py` |
| Task 문서 | `docs/phases/phase-11-1/tasks/task-11-1-2-rag-profiles-context-policy.md` |
| Test Report | 본 문서 |
