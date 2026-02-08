#!/bin/bash
# Phase 8-2 전체 실행 스크립트
# Phase 8-2-1부터 8-2-3까지 순차 실행 및 PostgreSQL 저장

set -e  # 에러 발생 시 중단

cd /Users/map-rch/WORKS/personal-ai-brain-v2

echo "=========================================="
echo "Phase 8-2: 코드 분석 및 Plan 생성"
echo "=========================================="
echo ""

# Phase 8-2-1: 현재 상태 분석
echo "=== Phase 8-2-1: 현재 상태 분석 ==="
./scripts/n8n/run-claude-analysis.sh

if [ ! -f "docs/phases/current-state.md" ]; then
    echo "❌ 오류: current-state.md 생성 실패"
    exit 1
fi

echo "✅ current-state.md 생성 완료"
echo ""

# PostgreSQL 저장
echo "📊 PostgreSQL에 저장 중..."
psql -h localhost -U brain -d knowledge << EOF
INSERT INTO workflow_phases (
    phase_name, 
    status, 
    current_state_md, 
    created_at
) VALUES (
    'Phase-8-Current-State',
    'completed',
    '$(cat docs/phases/current-state.md | sed "s/'/''/g")',
    NOW()
) RETURNING id, phase_name, created_at;
EOF

echo "✅ Phase 8-2-1 완료"
echo ""

# Phase 8-2-2: Gap 분석
echo "=== Phase 8-2-2: Gap 분석 ==="
./scripts/n8n/run-gap-analysis.sh

if [ ! -f "docs/phases/gap-analysis.md" ]; then
    echo "❌ 오류: gap-analysis.md 생성 실패"
    exit 1
fi

echo "✅ gap-analysis.md 생성 완료"
echo ""

# PostgreSQL 업데이트
echo "📊 PostgreSQL 업데이트 중..."
psql -h localhost -U brain -d knowledge << EOF
UPDATE workflow_phases 
SET gap_analysis_md = '$(cat docs/phases/gap-analysis.md | sed "s/'/''/g")',
    status = 'gap_analyzed'
WHERE phase_name = 'Phase-8-Current-State'
RETURNING id, phase_name, status;
EOF

echo "✅ Phase 8-2-2 완료"
echo ""

# Phase 8-2-3: Plan 생성
echo "=== Phase 8-2-3: Plan 생성 ==="
./scripts/n8n/generate-plan.sh

if [ ! -f "docs/phases/phase-8-plan.md" ]; then
    echo "❌ 오류: phase-8-plan.md 생성 실패"
    exit 1
fi

echo "✅ phase-8-plan.md 생성 완료"
echo ""

# PostgreSQL 저장
echo "📊 PostgreSQL에 저장 중..."
psql -h localhost -U brain -d knowledge << EOF
INSERT INTO workflow_plans (
    phase_id,
    version,
    content,
    status,
    created_at
) VALUES (
    (SELECT id FROM workflow_phases WHERE phase_name = 'Phase-8-Current-State'),
    1,
    '$(cat docs/phases/phase-8-plan.md | sed "s/'/''/g")',
    'draft',
    NOW()
) RETURNING id, version, status;
EOF

echo "✅ Phase 8-2-3 완료"
echo ""

echo "=========================================="
echo "✅ Phase 8-2 전체 완료!"
echo "=========================================="
echo ""
echo "생성된 파일:"
echo "  - docs/phases/current-state.md"
echo "  - docs/phases/gap-analysis.md"
echo "  - docs/phases/phase-8-plan.md"
echo ""
echo "PostgreSQL 확인:"
echo "  SELECT * FROM workflow_phases WHERE phase_name = 'Phase-8-Current-State';"
echo "  SELECT * FROM workflow_plans WHERE phase_id = (SELECT id FROM workflow_phases WHERE phase_name = 'Phase-8-Current-State');"
