# Task 17-5-1: [FE] 상단 카드 클릭 → 하단 필터링 연동

**우선순위**: 17-5 내 2순위
**예상 작업량**: 중간
**의존성**: 17-5-3 (API)
**상태**: 대기

---

## §1. 개요

4개 상단 요약 카드(문서/청크/라벨/사용량)를 클릭하면 하단에 해당 카테고리의 상세 목록이 표시되도록 한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/admin/statistics.html` | filtered-list-section HTML 추가 |
| 수정 | `web/public/js/admin/statistics.js` | 카드 클릭 핸들러 + loadFilteredList() |

## §3. 작업 체크리스트

- [ ] summary-card에 cursor:pointer + data-category 속성 추가
- [ ] 카드 클릭 시 active 상태 토글 + 하단 목록 전환
- [ ] filtered-list-section: 카테고리 탭 + 테이블 + 페이지네이션
- [ ] loadFilteredList(category, page) → API 호출 → 테이블 렌더링
