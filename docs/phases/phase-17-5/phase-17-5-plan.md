# Phase 17-5 Plan: 로그 통계 개선

## 목표
통계 대시보드의 상단 카드 클릭→하단 필터링 연동 + 테이블 조회 영역(검색/필터/정렬/페이지네이션) 추가

## Task 구조

| Task | 도메인 | 내용 | 변경 파일 |
|------|--------|------|----------|
| 17-5-3 | [BE] | 통계 리스트 API (필터/페이지네이션) | `statistics.py`, `statistics_service.py` |
| 17-5-1 | [FE] | 카드 클릭→하단 필터링 연동 | `statistics.html`, `statistics.js` |
| 17-5-2 | [FE] | 테이블 조회 영역 (검색·필터·정렬) | `statistics.js`, `statistics.css` |

## 의존성
- 17-5-3(BE) → 17-5-1, 17-5-2(FE)에서 API 호출

## 핵심 설계

### BE: 4개 리스트 API 추가
- `GET /api/system/statistics/documents/list?page=&size=&type=&q=`
- `GET /api/system/statistics/chunks/list?page=&size=&status=&q=`
- `GET /api/system/statistics/labels/list?page=&size=&label_type=&q=`
- `GET /api/system/statistics/usage/list?page=&size=&mode=&from_date=&to_date=`

### FE: 카드→필터 연동 + 조회 영역
- Summary card에 cursor:pointer + active 상태 추가
- 카드 클릭 시 하단에 해당 카테고리 리스트 표시
- 검색/필터/정렬/페이지네이션 컨트롤
