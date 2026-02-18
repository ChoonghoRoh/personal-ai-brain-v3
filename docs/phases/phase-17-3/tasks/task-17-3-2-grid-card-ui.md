# Task 17-3-2: [FE] 추천 문서 그리드 카드 UI

**우선순위**: 17-3 내 2순위
**예상 작업량**: 중간
**의존성**: 없음
**담당 팀원**: frontend-dev
**상태**: 완료

---

## §1. 개요

추천 문서 영역을 단순 텍스트 리스트에서 그리드 카드 UI로 전환한다. 각 카드에 문서 제목, 폴더 경로, 파일 크기, 수정일을 표시한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/search.html` | recommended-items → rec-grid 클래스 추가 |
| 수정 | `web/public/js/search/search.js` | renderRecommendedCards() 함수 추가, loadRecommended() 리팩토링 |

## §3. 작업 체크리스트 (Done Definition)

- [x] rec-grid 컨테이너로 카드 렌더링
- [x] rec-card 구조: title + path + meta (size, date)
- [x] escapeHtml 적용 (XSS 방지)
- [x] 카드 클릭 시 openDocument() 호출
- [x] 빈 결과 시 "조건에 맞는 문서가 없습니다." 안내

## §4. 참조

- [Phase 17 개발 요구사항 §6](../../../planning/260218-0830-phase17-개발-요구사항.md)
