-- workflow_tasks에 task_num 추가 (고유 Task 번호: 8-1-1, 1-1-2 형식)
-- phase_slug(8-1)만으로는 Phase 내 여러 Task 구분 불가. task_num으로 Task 단위 고유 식별.
--
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge -f - < scripts/db/migrate_workflow_tasks_task_num.sql

ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS task_num VARCHAR(50);

COMMENT ON COLUMN workflow_tasks.task_num IS '고유 Task 번호 (예: 8-1-1, 1-1-2). phase_slug-index 형식. UNIQUE.';

CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_tasks_task_num ON workflow_tasks(task_num);
