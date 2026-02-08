#!/bin/bash

# Phase 8-2-3: Plan 생성
# Gap 분석 결과를 바탕으로 구체적인 실행 계획 생성

cd /Users/map-rch/WORKS/personal-ai-brain-v2

# gap-analysis.md가 있는지 확인
if [ ! -f "docs/phases/gap-analysis.md" ]; then
    echo "❌ 오류: docs/phases/gap-analysis.md 파일이 없습니다."
    echo "먼저 Phase 8-2-2를 실행해주세요: ./scripts/n8n/run-gap-analysis.sh"
    exit 1
fi

# Claude Code CLI 실행
claude "
1. docs/phases/gap-analysis.md 읽기
2. docs/phases/current-state.md 참고
3. 구체적인 실행 계획 생성:
   - Gap 해결을 위한 단계별 작업 계획
   - 각 작업의 우선순위 및 의존성
   - 예상 소요 시간
   - 필요한 리소스 및 도구
4. docs/phases/phase-8-plan.md 파일 생성
   - 형식: 요약 1페이지 + 상세 계획 (전체 5페이지 이내)
   - 포함 내용:
     * 계획 개요
     * 단계별 작업 목록
     * 우선순위 및 의존성
     * 예상 일정
     * 리스크 및 대응 방안
"

echo "✅ phase-8-plan.md 생성 완료"
echo "📄 결과 확인: cat docs/phases/phase-8-plan.md"
