-- Phase 11-1-3: audit_logs 테이블 생성
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_3.sql

BEGIN;

-- audit_logs: 변경 이력
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    changed_by VARCHAR(100) NOT NULL,
    change_reason TEXT,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_table ON audit_logs(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date ON audit_logs(created_at);

COMMIT;
