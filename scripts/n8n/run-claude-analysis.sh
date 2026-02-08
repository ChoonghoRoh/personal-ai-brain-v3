#!/bin/bash

# Phase 8-2-1: 현재 상태 분석
# README.md 기반으로 프로젝트 현재 상태를 분석하여 current-state.md 생성

cd /Users/map-rch/WORKS/personal-ai-brain-v2

echo "🚀 분석 시작: $(date '+%H:%M:%S')"
echo "⏱️  예상 시간: 2-5분"
echo "☕ 잠시만 기다려주세요..."
echo ""

# Claude Code CLI 실행 (한 번만!)
time claude "
1. README.md 전체 읽기 및 프로젝트 구조 파악
2. backend 폴더 전체 코드 분석:
   - 주요 라우터 (routers/)
   - 서비스 레이어 (services/)
   - 모델 (models/)
   - 미들웨어 (middleware/)
3. 현재 구현 상태 정리:
   - ✅ 완성된 기능 목록
   - 🔄 진행 중인 기능
   - ❌ 미구현 기능
   - 📋 Phase 8 준비 상태 (n8n, PostgreSQL workflow_* 테이블 등)
4. docs/phases/current-state.md 파일 생성
   - 형식: 요약 1페이지 + 상세 2페이지 (전체 4페이지 이내)
   - 포함 내용:
     * 프로젝트 개요
     * 구현 완료 기능
     * 진행 중 기능
     * 미구현 기능
     * Phase 8 준비 상태
" && {
    echo ""
    echo "✅ 완료: $(date '+%H:%M:%S')"
    echo "📄 결과 확인: cat docs/phases/current-state.md"
} || {
    echo ""
    echo "❌ 에러 발생: $(date '+%H:%M:%S')"
}