# Task 17-3-4: [FE] search.css 그리드 스타일 + 반응형

**우선순위**: 17-3 내 4순위
**예상 작업량**: 중간
**의존성**: 17-3-2, 17-3-3 (HTML 구조 확정 후)
**담당 팀원**: frontend-dev
**상태**: 완료

---

## §1. 개요

추천 문서 그리드 카드와 조회 컨트롤의 CSS 스타일을 구현한다. 반응형 레이아웃을 포함하여 768px 이하에서 1단 레이아웃으로 전환한다. 검색 모드 토글 스타일도 포함한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/public/css/search.css` | rec-grid, rec-card, rec-controls, mode-btn 스타일 + 반응형 |

## §3. 작업 체크리스트 (Done Definition)

- [x] rec-grid: auto-fill minmax(280px, 1fr) 그리드
- [x] rec-card: 패딩 16px, 호버 시 border-color + box-shadow 변화
- [x] rec-card-title, rec-card-path, rec-card-meta 스타일
- [x] rec-controls: flex gap 8px 레이아웃
- [x] rec-search-input, rec-select 인풋 스타일
- [x] mode-btn: pill 형태 토글 버튼, active 시 파란색 배경
- [x] 반응형 @media (max-width: 768px): 1단 전환

## §4. 참조

- [Phase 17 개발 요구사항 §6](../../../planning/260218-0830-phase17-개발-요구사항.md)
