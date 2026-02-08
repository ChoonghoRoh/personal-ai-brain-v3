-- Phase 11-5-6: reasoning_results 공유·조회 고도화 (expires_at, view_count, is_private)
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_5_6_reasoning_results.sql
-- 전제: reasoning_results 테이블 존재 (Phase 8/10에서 생성된 경우)

BEGIN;

ALTER TABLE reasoning_results
  ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS is_private INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_reasoning_results_expires_at ON reasoning_results(expires_at);

COMMIT;
