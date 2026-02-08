-- workflow 공통 컬럼 DDL 조각 (신규 workflow 테이블 생성 시 복사·수정용)
-- 실행만으로는 테이블이 생성되지 않음. phases/plans/tasks/test_results DDL에 참고용으로 사용.
-- 문서: docs/db/workflow-tables-common.md

-- 공통 패턴 (테이블별로 default·컬럼명 조정)
-- id          SERIAL PRIMARY KEY,
-- status      VARCHAR(20) DEFAULT 'pending',   -- phases/plans: 'draft', tasks: 'pending'
-- created_at  TIMESTAMP DEFAULT NOW(),
-- completed_at TIMESTAMP,                       -- plans: approved_at, test_results: tested_at 등

-- 인덱스 공통 권장
-- CREATE INDEX idx_<table>_status ON <table>(status);
-- CREATE INDEX idx_<table>_parent_id ON <table>(phase_id);  -- 또는 task_id
