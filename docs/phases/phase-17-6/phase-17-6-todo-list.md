# Phase 17-6 Todo List: 통계 메뉴 4단 레이아웃 리뉴얼

> **상태**: 완료 (소급 생성)
> **완료일**: 2026-02-19

## Task 17-6-1: [FE] 통계 4단 레이아웃 재구성

- [x] statistics.html에 4단 `stats-tier` 래퍼 구조 적용
- [x] 1단: 요약 수치 (문서·청크·라벨·사용량 카드 4장)
- [x] 2단: 분포 차트 (문서유형 도넛 + 청크상태 바 + 라벨유형 도넛)
- [x] 3단: 트렌드 (일별 라인 차트, 7/14/30일 선택)
- [x] 4단: 상세 테이블 (인기 라벨 TOP10 + 프로젝트별 현황 2-col)
- [x] 서브타이틀 (.tier-header, .tier-subtitle) 추가

## Task 17-6-2: [FE] 시스템 상태 카드 제거 (17-7 이관)

- [x] statistics.html에서 시스템 상태 카드 섹션 제거
- [x] statistics.js에서 `updateSystemStatus()` 제거
- [x] `/system`, `/health` API 호출 코드 제거
- [x] statistics.css에서 미사용 system-status 스타일 제거

## Task 17-6-3: [FE] CSS 스타일 정리

- [x] `.stats-tier` 래퍼 스타일 추가
- [x] `.tier-header`, `.tier-subtitle` 스타일 추가
- [x] 4단 간 간격·배경 구분 스타일 적용

## Gate 결과

| Gate | 결과 |
|------|------|
| G1 계획 리뷰 | PASS |
| G2 FE 코드 리뷰 | PASS |
| G3 테스트 | PASS (import OK, 회귀 26/26) |
| G4 최종 | PASS |
