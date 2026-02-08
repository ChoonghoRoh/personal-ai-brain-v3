# 데이터베이스 구조

**수정 시**: 스키마·테이블 추가·변경 시 `docs/db/` 문서를 갱신하고, 이 파일의 링크만 유지.

---

## 요약

- **PostgreSQL**: 지식 메타데이터(projects, documents, knowledge_chunks, labels, relations 등), workflow(workflow_phases, workflow_plans, workflow_tasks, workflow_test_results, workflow_approvals).
- **Qdrant**: 벡터 임베딩(청크), 의미 검색.

---

## 문서 위치 (단일 소스)

| 구분 | 경로 | 비고 |
|------|------|------|
| 스키마·일반 | [docs/db/database-schema.md](../db/database-schema.md) | 있으면 사용. 없으면 아래 조합 참고. |
| workflow 공통 | [docs/db/workflow-tables-common.md](../db/workflow-tables-common.md) | workflow_* 테이블 공통 컬럼·규약 |
| workflow_tasks | [docs/db/workflow_tasks-table-columns.md](../db/workflow_tasks-table-columns.md) | 컬럼·용도·마이그레이션 |
| DDL 조각 | `scripts/db/workflow_common_ddl.sql` | workflow 신규 테이블 참고용 |
| 백엔드 모델 | `backend/models/models.py`, `backend/models/workflow_common.py` | SQLAlchemy·공통 상수 |

---

## 마이그레이션

- workflow_tasks: `scripts/db/migrate_workflow_tasks_phase_slug.sql`, `migrate_workflow_tasks_task_num.sql`, `migrate_workflow_tasks_plan_md_path.sql`
- 기타: `scripts/db/` 하위 스크립트 참고.
