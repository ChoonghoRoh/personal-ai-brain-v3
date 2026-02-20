# Phase 17-5 Todo List: 로그 통계 개선

> **상태**: 완료 (소급 생성)
> **완료일**: 2026-02-19

## Task 17-5-3: [BE] 통계 API 필터링 파라미터 추가

- [x] `GET /api/system/statistics/documents/list` 엔드포인트 추가
- [x] `GET /api/system/statistics/chunks/list` 엔드포인트 추가
- [x] `GET /api/system/statistics/labels/list` 엔드포인트 추가
- [x] `GET /api/system/statistics/usage/list` 엔드포인트 추가
- [x] 공통 응답 형식 (items, total, page, size, total_pages) 적용
- [x] page/size/sort_by/sort_order 공통 파라미터 처리

## Task 17-5-1: [FE] 상단 카드 클릭 → 하단 필터링 연동

- [x] summary-card에 cursor:pointer + data-category 속성 추가
- [x] 카드 클릭 시 active 상태 토글
- [x] 하단 filtered-list-section HTML 추가
- [x] loadFilteredList(category, page) → API 호출 → 테이블 렌더링

## Task 17-5-2: [FE] 통계 테이블 조회 영역 (검색·필터·정렬)

- [x] 검색 입력 (debounce 300ms)
- [x] 유형/상태 필터 드롭다운 (카테고리별 다른 옵션)
- [x] 컬럼 헤더 클릭 정렬 (asc/desc 토글)
- [x] 페이지네이션 (이전/다음 + 페이지 번호)
- [x] 초기화 버튼

## Gate 결과

| Gate | 결과 |
|------|------|
| G1 계획 리뷰 | PASS |
| G2 BE 코드 리뷰 | PASS |
| G2 FE 코드 리뷰 | PASS |
| G3 테스트 | PASS (import OK, 회귀 26/26) |
| G4 최종 | PASS |
