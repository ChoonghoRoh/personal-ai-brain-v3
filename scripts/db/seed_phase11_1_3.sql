-- Phase 11-1-3: audit_logs 초기 시딩 + 전체 Admin 테이블 시딩 검증
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/seed_phase11_1_3.sql

BEGIN;

-- audit_logs 초기 데이터: Phase 11-1 마이그레이션 기록 (3행)
INSERT INTO audit_logs (table_name, record_id, action, changed_by, change_reason, old_values, new_values)
VALUES
    (
        'schemas',
        '00000000-0000-0000-0000-000000000001'::uuid,
        'create',
        'system',
        'Phase 11-1-1 초기 시딩: 6종 Role 스키마 생성',
        NULL,
        '{"count": 6, "roles": ["background","constraint","decision","rationale","evidence","open_questions"]}'::jsonb
    ),
    (
        'templates',
        '00000000-0000-0000-0000-000000000002'::uuid,
        'create',
        'system',
        'Phase 11-1-1 초기 시딩: 3종 템플릿 생성',
        NULL,
        '{"count": 3, "types": ["decision_view","summary","report"]}'::jsonb
    ),
    (
        'prompt_presets',
        '00000000-0000-0000-0000-000000000003'::uuid,
        'create',
        'system',
        'Phase 11-1-1 초기 시딩: 4종 프롬프트 프리셋 생성',
        NULL,
        '{"count": 4, "types": ["summary","decision","report","search"]}'::jsonb
    )
ON CONFLICT DO NOTHING;

COMMIT;
