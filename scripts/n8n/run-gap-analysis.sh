#!/bin/bash

# Phase 8-2-2: Gap 분석
# current-state.md와 목표 상태를 비교하여 격차 분석

cd /Users/map-rch/WORKS/personal-ai-brain-v2

# current-state.md가 있는지 확인
if [ ! -f "docs/phases/current-state.md" ]; then
    echo "❌ 오류: docs/phases/current-state.md 파일이 없습니다."
    echo "먼저 Phase 8-2-1을 실행해주세요: ./scripts/n8n/run-claude-analysis.sh"
    exit 1
fi

# Claude Code CLI 실행
claude "
1. docs/phases/current-state.md 읽기
2. README.md의 목표 상태 확인
3. Gap 분석 수행:
   - 현재 상태 vs 목표 상태 비교
   - 누락된 기능 식별
   - 우선순위별 Gap 목록 작성
   - 각 Gap에 대한 해결 방안 제시
4. docs/phases/gap-analysis.md 파일 생성
   - 형식: 요약 1페이지 + 상세 Gap 목록 (전체 4페이지 이내)
   - 포함 내용:
     * Gap 개요
     * 우선순위별 Gap 목록 (High/Medium/Low)
     * 각 Gap 상세 설명
     * 해결 방안 제안
"

echo "✅ gap-analysis.md 생성 완료"
echo "📄 결과 확인: cat docs/phases/gap-analysis.md"
