-- Phase 11-1-2: rag_profiles, context_rules, policy_sets 초기 시딩 데이터
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/seed_phase11_1_2.sql

BEGIN;

-- 1. rag_profiles 초기 데이터 (3행)
INSERT INTO rag_profiles (name, description, chunk_size, chunk_overlap, top_k, score_threshold, use_rerank, rerank_model, filter_priority, version, status)
VALUES
    (
        '기본 RAG 프로필',
        '표준 RAG 검색 프로필. 일반적인 문서 검색에 적합.',
        1000, 200, 5, 0.70,
        false, NULL,
        '{"project": 10, "date": 5, "author": 3}'::jsonb,
        1, 'published'
    ),
    (
        '정밀 검색 프로필',
        '높은 정확도가 필요한 검색용. 청크 크기를 줄이고 임계값을 높임.',
        500, 100, 10, 0.85,
        true, 'cross-encoder/ms-marco-MiniLM-L-6-v2',
        '{"project": 10, "date": 3, "author": 5}'::jsonb,
        1, 'published'
    ),
    (
        '대용량 문서 프로필',
        '긴 문서나 보고서 검색에 최적화. 청크 크기를 키우고 top_k를 줄임.',
        2000, 400, 3, 0.60,
        false, NULL,
        '{"project": 8, "date": 7, "author": 2}'::jsonb,
        1, 'draft'
    )
ON CONFLICT DO NOTHING;

-- 2. context_rules 초기 데이터 (4행)
INSERT INTO context_rules (rule_name, document_type, domain_tags, classification_logic, allow_manual_override, priority, is_active)
VALUES
    (
        '개발 문서 자동 분류',
        'technical_doc',
        ARRAY['개발', '기술'],
        '{"keywords": ["API", "데이터베이스", "프론트엔드", "백엔드", "코드"], "folder_pattern": "*/dev/*"}'::jsonb,
        true, 10, true
    ),
    (
        '회의록 자동 분류',
        'meeting_note',
        ARRAY['회의', '미팅'],
        '{"keywords": ["회의록", "미팅노트", "참석자", "안건", "결정사항"], "folder_pattern": "*/meetings/*"}'::jsonb,
        true, 8, true
    ),
    (
        '기획서 자동 분류',
        'planning_doc',
        ARRAY['기획', '전략'],
        '{"keywords": ["기획서", "요구사항", "목표", "일정", "마일스톤"], "folder_pattern": "*/planning/*"}'::jsonb,
        true, 9, true
    ),
    (
        '보고서 자동 분류',
        'report',
        ARRAY['보고', '분석'],
        '{"keywords": ["보고서", "분석", "결과", "통계", "성과"], "folder_pattern": "*/reports/*"}'::jsonb,
        true, 7, true
    )
ON CONFLICT DO NOTHING;

-- 3. policy_sets 초기 데이터 (2행) — 전역 기본 정책
-- templates, prompt_presets의 실제 ID를 참조
INSERT INTO policy_sets (name, description, project_id, user_group, template_id, prompt_preset_id, rag_profile_id, priority, is_active)
SELECT
    '전역 기본 정책',
    '모든 프로젝트에 적용되는 기본 설정 정책',
    NULL,
    NULL,
    t.id,
    pp.id,
    rp.id,
    0,
    true
FROM
    (SELECT id FROM templates WHERE name = '기본 의사결정 문서' LIMIT 1) t,
    (SELECT id FROM prompt_presets WHERE name = '의사결정 프리셋' LIMIT 1) pp,
    (SELECT id FROM rag_profiles WHERE name = '기본 RAG 프로필' LIMIT 1) rp
ON CONFLICT DO NOTHING;

INSERT INTO policy_sets (name, description, project_id, user_group, template_id, prompt_preset_id, rag_profile_id, priority, is_active)
SELECT
    '요약 전용 정책',
    '요약 작업에 최적화된 설정 정책',
    NULL,
    NULL,
    t.id,
    pp.id,
    rp.id,
    1,
    true
FROM
    (SELECT id FROM templates WHERE name = '요약 보고서' LIMIT 1) t,
    (SELECT id FROM prompt_presets WHERE name = '요약 프리셋' LIMIT 1) pp,
    (SELECT id FROM rag_profiles WHERE name = '정밀 검색 프로필' LIMIT 1) rp
ON CONFLICT DO NOTHING;

COMMIT;
