-- Task Plan and Test Plan Generation 워크플로우용: workflow_phases에 Phase 등록
-- workflow_tasks.phase_id는 workflow_phases(id) FK이므로, INSERT 전에 해당 phase가 있어야 함.
--
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge -f - < scripts/db/insert_workflow_phase_for_generation.sql
-- 또는: psql -U brain -d knowledge -f scripts/db/insert_workflow_phase_for_generation.sql
--
-- 실행 후 n8n SET_PhaseContext의 phase_id는 아래 조회 결과의 id로 설정:
--   SELECT id, phase_name, status FROM workflow_phases ORDER BY id;

-- Testphase1-1 (phase_dir_id = Testphase1-1 인 경우)
INSERT INTO workflow_phases (phase_name, status, created_at)
SELECT 'Testphase1-1', 'draft', NOW()
WHERE NOT EXISTS (SELECT 1 FROM workflow_phases WHERE phase_name = 'Testphase1-1');

-- phase-8-0 (phase_dir_id = phase-8-0 인 경우)
INSERT INTO workflow_phases (phase_name, status, created_at)
SELECT 'phase-8-0', 'draft', NOW()
WHERE NOT EXISTS (SELECT 1 FROM workflow_phases WHERE phase_name = 'phase-8-0');

-- 사용할 phase_id 확인용 (실행 후 출력)
SELECT id, phase_name, status FROM workflow_phases ORDER BY id;
