-- Phase 11-1-2: rag_profiles, context_rules, policy_sets 테이블 생성
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_2.sql

BEGIN;

-- 1. rag_profiles: RAG 검색 파라미터 프로필
CREATE TABLE IF NOT EXISTS rag_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    chunk_size INTEGER DEFAULT 1000,
    chunk_overlap INTEGER DEFAULT 200,
    top_k INTEGER DEFAULT 5,
    score_threshold DECIMAL(3,2) DEFAULT 0.7,
    use_rerank BOOLEAN DEFAULT false,
    rerank_model VARCHAR(50),
    filter_priority JSONB,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. context_rules: 상황 분류 규칙
CREATE TABLE IF NOT EXISTS context_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(200) NOT NULL,
    document_type VARCHAR(50),
    domain_tags TEXT[],
    classification_logic JSONB,
    allow_manual_override BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. policy_sets: 설정 적용 정책
CREATE TABLE IF NOT EXISTS policy_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    project_id INTEGER REFERENCES projects(id),
    user_group VARCHAR(100),
    template_id UUID REFERENCES templates(id),
    prompt_preset_id UUID REFERENCES prompt_presets(id),
    rag_profile_id UUID REFERENCES rag_profiles(id),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    effective_from TIMESTAMP DEFAULT NOW(),
    effective_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_sets_project ON policy_sets(project_id);
CREATE INDEX IF NOT EXISTS idx_policy_sets_active ON policy_sets(is_active);

COMMIT;
