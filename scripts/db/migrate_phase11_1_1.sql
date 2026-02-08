-- Phase 11-1-1: schemas, templates, prompt_presets 테이블 생성
-- 실행: docker exec pab-postgres psql -U brain -d knowledge -f /app/scripts/db/migrate_phase11_1_1.sql
-- 또는: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_1.sql

BEGIN;

-- 1. schemas: Role 스키마 정의
CREATE TABLE IF NOT EXISTS schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_key VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT false,
    output_length_limit INTEGER,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. templates: 판단 문서 템플릿
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    output_format VARCHAR(20) DEFAULT 'markdown',
    citation_rule TEXT,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_templates_status ON templates(status);
CREATE INDEX IF NOT EXISTS idx_templates_type ON templates(template_type);

-- 3. prompt_presets: 프롬프트 프리셋
CREATE TABLE IF NOT EXISTS prompt_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    model_name VARCHAR(50),
    temperature DECIMAL(3,2) DEFAULT 0.7,
    top_p DECIMAL(3,2) DEFAULT 0.9,
    max_tokens INTEGER DEFAULT 4000,
    system_prompt TEXT NOT NULL,
    constraints TEXT[],
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prompt_presets_task ON prompt_presets(task_type);
CREATE INDEX IF NOT EXISTS idx_prompt_presets_status ON prompt_presets(status);

COMMIT;
