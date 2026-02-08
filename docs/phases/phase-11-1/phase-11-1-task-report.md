# Phase 11-1 Task Report — DB 스키마·마이그레이션

**Phase ID**: 11-1
**상태**: ✅ 완료
**시작일**: 2026-02-06
**완료일**: 2026-02-06

---

## 1. Phase 목표

Admin 설정을 저장할 **7종 테이블(schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs)**의 DB 스키마·마이그레이션·시딩을 구축한다.

---

## 2. Task 실행 요약

| Task ID | Task 명 | 상태 | 테이블 | 시딩 행 수 |
|---------|---------|------|--------|-----------|
| 11-1-1 | schemas, templates, prompt_presets | ✅ 완료 | 3개 | 13행 (6+3+4) |
| 11-1-2 | rag_profiles, context_rules, policy_sets | ✅ 완료 | 3개 | 9행 (3+4+2) |
| 11-1-3 | audit_logs, 전체 검증, 시딩 | ✅ 완료 | 1개 | 3행 |
| **합계** | | | **7개** | **25행** |

---

## 3. 산출물 목록

### 3.1 DB 산출물

| 파일 | 용도 |
|------|------|
| `scripts/db/migrate_phase11_1_1.sql` | schemas, templates, prompt_presets 테이블 생성 |
| `scripts/db/seed_phase11_1_1.sql` | 11-1-1 초기 시딩 (13행) |
| `scripts/db/migrate_phase11_1_2.sql` | rag_profiles, context_rules, policy_sets 테이블 생성 |
| `scripts/db/seed_phase11_1_2.sql` | 11-1-2 초기 시딩 (9행) |
| `scripts/db/migrate_phase11_1_3.sql` | audit_logs 테이블 생성 |
| `scripts/db/seed_phase11_1_3.sql` | 11-1-3 초기 시딩 (3행) |

### 3.2 코드 산출물

| 파일 | 용도 |
|------|------|
| `backend/models/admin_models.py` | SQLAlchemy ORM 모델 (7 클래스) |
| `backend/models/__init__.py` | admin_models import 추가 |

### 3.3 문서 산출물

| 파일 | 용도 |
|------|------|
| `docs/phases/phase-11-1/phase-11-1-0-plan.md` | Phase 11-1 계획서 |
| `docs/phases/phase-11-1/phase-11-1-0-todo-list.md` | Todo List |
| `docs/phases/phase-11-1/tasks/task-11-1-1-*.md` | Task 11-1-1 실행 계획 |
| `docs/phases/phase-11-1/tasks/task-11-1-2-*.md` | Task 11-1-2 실행 계획 |
| `docs/phases/phase-11-1/tasks/task-11-1-3-*.md` | Task 11-1-3 실행 계획 |
| `docs/phases/phase-11-1/phase11-1-1-task-test-report.md` | Task 11-1-1 검증 결과 |
| `docs/phases/phase-11-1/phase11-1-2-task-test-report.md` | Task 11-1-2 검증 결과 |
| `docs/phases/phase-11-1/phase11-1-3-task-test-report.md` | Task 11-1-3 종합 검증 결과 |
| `docs/phases/phase-11-1/phase-11-1-task-report.md` | Phase 11-1 통합 리포트 (본 문서) |

---

## 4. 기술 사항

### 4.1 설계 결정

| 항목 | 결정 | 사유 |
|------|------|------|
| PK 타입 | UUID (gen_random_uuid()) | Admin 설정 테이블의 ID는 UUID로 통일하여 마이크로서비스 확장성 확보 |
| policy_sets.project_id | Integer FK | 기존 projects.id가 Integer PK이므로 Sample의 UUID FK에서 수정 |
| 마이그레이션 방식 | Raw SQL | 프로젝트 기존 관행에 따라 Alembic 대신 SQL 스크립트 사용 |
| 시딩 충돌 처리 | ON CONFLICT DO NOTHING | 반복 실행 안전성 확보 |

### 4.2 테이블 관계도

```
schemas (독립)
templates (독립) ←─── policy_sets.template_id
prompt_presets (독립) ←─── policy_sets.prompt_preset_id
rag_profiles (독립) ←─── policy_sets.rag_profile_id
context_rules (독립)
policy_sets ──→ projects.id (FK, nullable)
audit_logs (독립, 참조용)
```

---

## 5. 다음 단계

**Phase 11-2**: Admin 설정 Backend API

| Task ID | Task 명 | 의존성 |
|---------|---------|--------|
| 11-2-1 | Schema·Template·PromptPreset CRUD API | Phase 11-1 완료 |
| 11-2-2 | RAG Profile·Policy Set CRUD API | Phase 11-1 완료 |
| 11-2-3 | 버전 관리·Publish/Rollback·Audit Log API | 11-2-1, 11-2-2 |
| 11-2-4 | 정책 해석(resolve) API·Reasoning 연동 | 11-2-3 |
