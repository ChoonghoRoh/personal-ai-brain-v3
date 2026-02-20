# Phase 17-7 Todo List: 대시보드 디자인 리뉴얼

> **상태**: 완료 (소급 생성)
> **완료일**: 2026-02-19

## Task 17-7-1: [FE] 대시보드 6단 레이아웃 재구성

- [x] dashboard.html 6단 구조 전면 재구성
- [x] 1단: 시스템 상태 한줄 요약 (🟢/🟡/🔴 + PostgreSQL/Qdrant/Redis/Ollama)
- [x] 2단: 등록 지식 현황 (총문서/총청크/총라벨/프로젝트 4카드)
- [x] 3단: Reasoning 가이드 (설계설명/리스크/다음단계/히스토리 4모드 + 시작 버튼)
- [x] 4단: 주요 기능 바로가기 (Knowledge Studio + Knowledge Admin 2카드)
- [x] 5단: 최근 업데이트 문서 카드뷰 (이름 + 폴더 경로)
- [x] 6단: 활동 분석 (문서유형 도넛 + 7일 트렌드)

## Task 17-7-2: [FE] CSS 전면 재작성

- [x] system-status-bar 스타일
- [x] knowledge-cards 스타일
- [x] reasoning-guide 스타일
- [x] quick-links 스타일
- [x] recent-docs-grid 카드뷰 스타일
- [x] dashboard-charts 스타일

## Task 17-7-3: [FE] JS 렌더 함수 교체

- [x] renderSystemStatusBar() 구현
- [x] renderKnowledgeCards() 구현
- [x] renderRecentDocsCards() 구현
- [x] 기존 삭제 영역 코드 제거

## Task 17-7-4: [FE] API 병렬 호출 + 차트 재사용

- [x] dashboard-api.js: 4 API 병렬 호출 (/system/status, /health/ready, /statistics, /trends)
- [x] Chart.js + statistics-charts.js 로드
- [x] test 함수 제거

## Task 17-7-5: [FE] 삭제 영역 정리

- [x] 최근 작업 (#recent-work) 제거 (로그 페이지로 이관)
- [x] 자동화 상태 (#automation-status) 제거
- [x] 문서 목록 (#documents-list) 제거 (검색 페이지로 이관)
- [x] 시스템 상태 상세 (renderSystemStatus) 제거 → 한줄 요약으로 대체

## Gate 결과

| Gate | 결과 |
|------|------|
| G1 계획 리뷰 | PASS |
| G2 FE 코드 리뷰 | PASS |
| G3 테스트 | PASS (import OK, 회귀 26/26) |
| G4 최종 | PASS |
