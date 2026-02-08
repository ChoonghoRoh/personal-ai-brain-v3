# Task 11-1-1 Test Report — schemas, templates, prompt_presets

**Task ID**: 11-1-1
**상태**: ✅ 완료
**실행일**: 2026-02-06
**작성자**: Claude (자동)

---

## 1. 실행 내역

### 1.1 영향도 검증

- Backend 사용처: 없음 (신규 테이블, Phase 11-2에서 API 구현 예정)
- Frontend 사용처: 없음 (기존 `templates` 참조는 Jinja2 HTML 템플릿이며 Admin DB 테이블과 무관)

### 1.2 백업

- Docker 내 `pg_dump` 실행 완료
- 스키마 + 데이터 백업 저장

### 1.3 마이그레이션

- **파일**: `scripts/db/migrate_phase11_1_1.sql`
- **실행 명령**: `docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_1.sql`
- **결과**: CREATE TABLE × 3, CREATE INDEX × 4 성공

### 1.4 시딩

- **파일**: `scripts/db/seed_phase11_1_1.sql`
- **결과**: schemas 6행, templates 3행, prompt_presets 4행 삽입

### 1.5 SQLAlchemy 모델

- **파일**: `backend/models/admin_models.py` — `AdminSchema`, `AdminTemplate`, `AdminPromptPreset` 클래스
- **import**: `backend/models/__init__.py`에 `admin_models` 추가

---

## 2. 검증 결과

| 검증 항목 | 결과 | 비고 |
|-----------|------|------|
| schemas 테이블 존재 | ✅ | PK + role_key UNIQUE |
| templates 테이블 존재 | ✅ | idx_templates_status, idx_templates_type |
| prompt_presets 테이블 존재 | ✅ | idx_prompt_presets_task, idx_prompt_presets_status |
| schemas 시딩 행 수 | ✅ | 6행 (background, constraint, decision, rationale, evidence, open_questions) |
| templates 시딩 행 수 | ✅ | 3행 (decision_view, summary, report) |
| prompt_presets 시딩 행 수 | ✅ | 4행 (summary, decision, report, search) |
| 인덱스 수 | ✅ | 총 8개 (PK 3 + UNIQUE 1 + 커스텀 4) |
| 기존 서비스 회귀 | ✅ | system info, search, knowledge 정상 |

---

## 3. 산출물

| 산출물 | 경로 |
|--------|------|
| SQL 마이그레이션 | `scripts/db/migrate_phase11_1_1.sql` |
| SQL 시딩 | `scripts/db/seed_phase11_1_1.sql` |
| SQLAlchemy 모델 | `backend/models/admin_models.py` |
| Task 문서 | `docs/phases/phase-11-1/tasks/task-11-1-1-schemas-templates-presets.md` |
| Test Report | 본 문서 |
