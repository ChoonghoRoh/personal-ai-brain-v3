-- Phase 11-1-1: schemas, templates, prompt_presets 초기 시딩 데이터
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/seed_phase11_1_1.sql

BEGIN;

-- 1. schemas 초기 데이터 (6행)
INSERT INTO schemas (role_key, display_name, description, is_required, output_length_limit, display_order)
VALUES
    ('background',      '배경 상황',   '의사결정이 이루어진 맥락과 배경을 설명합니다',                   true,  500, 1),
    ('constraint',      '제약 조건',   '의사결정 시 고려된 제약사항과 한계를 명시합니다',                false, 300, 2),
    ('decision',        '핵심 판단',   '내린 결정의 핵심 내용을 명확히 기술합니다',                    true,  400, 3),
    ('rationale',       '판단 근거',   '해당 결정을 내린 이유와 논리를 설명합니다',                    true,  600, 4),
    ('evidence',        '증거 자료',   '판단을 뒷받침하는 구체적인 증거와 출처를 제시합니다',             true,  500, 5),
    ('open_questions',  '미해결 질문', '여전히 남아있는 불확실성과 추가 검토 사항',                      false, 300, 6)
ON CONFLICT (role_key) DO NOTHING;

-- 2. templates 초기 데이터 (3행)
INSERT INTO templates (name, description, template_type, content, output_format, version, status, created_by)
VALUES
    (
        '기본 의사결정 문서',
        '표준 의사결정 문서 템플릿',
        'decision_view',
        E'# {{title}}\n\n## 배경 상황\n{{background}}\n\n## 제약 조건\n{{constraint}}\n\n## 핵심 판단\n{{decision}}\n\n## 판단 근거\n{{rationale}}\n\n## 증거 자료\n{{evidence}}\n\n## 미해결 질문\n{{open_questions}}',
        'markdown',
        1, 'published', 'system'
    ),
    (
        '요약 보고서',
        '간단한 요약 보고서 템플릿',
        'summary',
        E'# {{title}} 요약\n\n**핵심 판단**: {{decision}}\n\n**근거**: {{rationale}}\n\n**증거**: {{evidence}}',
        'markdown',
        1, 'published', 'system'
    ),
    (
        '상세 분석 보고서',
        '상세 분석 보고서 템플릿',
        'report',
        E'# {{title}} — 상세 분석\n\n## 1. 개요\n{{background}}\n\n## 2. 분석\n### 2.1 제약사항\n{{constraint}}\n\n### 2.2 핵심 판단\n{{decision}}\n\n## 3. 근거 및 증거\n### 3.1 판단 근거\n{{rationale}}\n\n### 3.2 증거 자료\n{{evidence}}\n\n## 4. 후속 과제\n{{open_questions}}',
        'markdown',
        1, 'draft', 'system'
    )
ON CONFLICT DO NOTHING;

-- 3. prompt_presets 초기 데이터 (4행)
INSERT INTO prompt_presets (name, task_type, model_name, temperature, top_p, max_tokens, system_prompt, constraints, version, status)
VALUES
    (
        '요약 프리셋',
        'summary',
        'qwen2.5:7b',
        0.5, 0.9, 2000,
        '당신은 문서 요약 전문가입니다. 주어진 문서를 핵심 내용 중심으로 간결하게 요약하세요. 한국어로 답변하세요.',
        ARRAY['추측 금지', '근거 없으면 모른다고 명시', '원문에 없는 내용 추가 금지'],
        1, 'published'
    ),
    (
        '의사결정 프리셋',
        'decision',
        'qwen2.5:7b',
        0.7, 0.9, 4000,
        '당신은 의사결정 지원 전문가입니다. 주어진 맥락을 분석하고, 구조화된 판단 문서를 작성하세요. 한국어로 답변하세요.',
        ARRAY['추측 금지', '근거 없으면 모른다고 명시', '편향 배제'],
        1, 'published'
    ),
    (
        '보고서 프리셋',
        'report',
        'qwen2.5:7b',
        0.6, 0.9, 6000,
        '당신은 분석 보고서 작성 전문가입니다. 주어진 자료를 바탕으로 구조화된 보고서를 작성하세요. 한국어로 답변하세요.',
        ARRAY['추측 금지', '출처 명시 필수', '객관적 서술'],
        1, 'published'
    ),
    (
        '검색 프리셋',
        'search',
        'qwen2.5:7b',
        0.3, 0.9, 1000,
        '당신은 정보 검색 전문가입니다. 사용자 질문의 핵심 키워드를 추출하고, 관련 문서를 정확하게 찾아 답변하세요. 한국어로 답변하세요.',
        ARRAY['검색 결과에 없는 정보 생성 금지', '불확실한 정보는 언급하지 않기'],
        1, 'published'
    )
ON CONFLICT DO NOTHING;

COMMIT;
