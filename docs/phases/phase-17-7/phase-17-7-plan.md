# Phase 17-7: 대시보드 디자인 리뉴얼

## 목표

대시보드를 6단 레이아웃으로 전면 재구성하고, 통계 메뉴 차트를 재사용한다.

## 변경 파일

| 구분 | 파일 | 변경 내용 |
|------|------|-----------|
| 수정 | `web/src/pages/dashboard.html` | 6단 구조 전면 재구성, Chart.js + statistics-charts.js 로드 |
| 수정 | `web/public/css/dashboard.css` | 전면 재작성 (system-status-bar, knowledge-cards, reasoning-guide, quick-links, recent-docs-grid, dashboard-charts) |
| 수정 | `web/public/js/dashboard/dashboard.js` | 렌더 함수 교체 (renderSystemStatusBar, renderKnowledgeCards, renderRecentDocsCards), 삭제 영역 코드 제거 |
| 수정 | `web/public/js/dashboard/dashboard-api.js` | 4 API 병렬 호출 (/system/status, /health/ready, /statistics, /trends), test 함수 제거 |

## 6단 구조

1. **시스템 상태 한줄 요약**: 🟢/🟡/🔴 + PostgreSQL/Qdrant/Redis/Ollama
2. **등록 지식 현황**: 총문서/총청크/총라벨/프로젝트 4카드
3. **Reasoning 가이드**: 설계설명/리스크/다음단계/히스토리 4모드 + 시작 버튼
4. **주요 기능 바로가기**: Knowledge Studio + Knowledge Admin 2카드
5. **최근 업데이트 문서**: 카드뷰 (이름 + 폴더 경로)
6. **활동 분석**: 문서유형 도넛 + 7일 트렌드 (statistics-charts.js 재사용)

## 삭제 영역

- 최근 작업 (#recent-work) → 로그 페이지로 이관
- 자동화 상태 (#automation-status) → 제거
- 문서 목록 (#documents-list) → 검색 페이지로 이관
- 시스템 상태 상세 (renderSystemStatus) → 한줄 요약으로 대체
