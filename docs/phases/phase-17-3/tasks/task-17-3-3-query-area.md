# Task 17-3-3: [FE] 추천 문서 조회 영역 (검색·폴더 필터·정렬)

**우선순위**: 17-3 내 3순위
**예상 작업량**: 중간
**의존성**: 없음
**담당 팀원**: frontend-dev
**상태**: 완료

---

## §1. 개요

추천 문서 영역 상단에 조회 컨트롤을 추가한다. 문서 이름/경로 실시간 검색, 폴더 필터 드롭다운, 정렬 옵션, 표시 건수 제한을 제공하여 사용자가 원하는 문서를 빠르게 찾을 수 있도록 한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/search.html` | rec-controls 영역 추가 (검색 input, 폴더 select, 정렬 select, 건수 select) |
| 수정 | `web/public/js/search/search.js` | filterRecommended(), populateFolderFilter() 함수 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [x] rec-search-input: 문서 이름/경로 실시간 필터링 (oninput)
- [x] rec-folder: 1단계 폴더 기준 드롭다운 자동 생성
- [x] rec-sort: 최신순/이름순/크기순 정렬
- [x] rec-limit: 5/10/20건 제한
- [x] allDocuments 전체 fetch 후 클라이언트사이드 필터링 방식
- [x] 각 컨트롤 변경 시 filterRecommended() 자동 호출

## §4. 참조

- [Phase 17 개발 요구사항 §6](../../../planning/260218-0830-phase17-개발-요구사항.md)
