-- workflow_tasks에 plan_md_path 추가 (Phase 8-2-7: 경로 기반 Task 실행)
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge -f - < scripts/db/migrate_workflow_tasks_plan_md_path.sql
-- 또는 psql 접속 후 \i scripts/db/migrate_workflow_tasks_plan_md_path.sql

ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS plan_md_path VARCHAR(500);

COMMENT ON COLUMN workflow_tasks.plan_md_path IS 'Task Plan .md 파일 경로 (workspace 기준 상대경로, 예: docs/phases/tasks/task-1-plan.md). 있으면 Backend가 이 경로만 Claude CLI에 전달.';
