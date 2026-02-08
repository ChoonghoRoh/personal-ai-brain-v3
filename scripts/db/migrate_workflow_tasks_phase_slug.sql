-- workflow_tasks에 phase_slug 추가 (Phase 식별을 workflow_phases.id 대신 phase 번호로)
-- phase_id FK 없이 Phase 그룹/필터 가능. 실행 로직에는 phase_id를 쓰지 않으므로 phase_id=NULL, phase_slug만 넣어도 동작.
--
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge -f - < scripts/db/migrate_workflow_tasks_phase_slug.sql
--
-- FK 오류 나면: phase_id에 DEFAULT가 걸려 있을 수 있음. 그때만 실행:
--   ALTER TABLE workflow_tasks ALTER COLUMN phase_id DROP DEFAULT;

ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS phase_slug VARCHAR(50);

COMMENT ON COLUMN workflow_tasks.phase_slug IS 'Phase 식별자 (예: 8-0, 1-1, Testphase1-1). workflow_phases.id 없이 Phase별 그룹/필터용.';

CREATE INDEX IF NOT EXISTS idx_workflow_tasks_phase_slug ON workflow_tasks(phase_slug);
