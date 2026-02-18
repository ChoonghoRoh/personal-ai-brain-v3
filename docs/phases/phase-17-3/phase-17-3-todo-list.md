# Phase 17-3 Todo List — 검색 메뉴 + 추천 문서 개선

**Phase**: 17-3
**기준**: [phase-17-3-plan.md](phase-17-3-plan.md)

---

- [x] Task 17-3-1: [BE] hybrid_search.py 파일명 ILIKE 검색 추가 (Owner: backend-dev)
  - `backend/services/search/hybrid_search.py` 수정
  - Document JOIN 추가 (KnowledgeChunk.document_id == Document.id)
  - keyword_search ILIKE 조건에 Document.file_path 포함
  - match_count 계산에 filepath_lower 포함
  - 완료 기준: 파일명 키워드로 검색 시 해당 청크 결과 반환

- [x] Task 17-3-2: [FE] 추천 문서 그리드 카드 UI (Owner: frontend-dev)
  - `web/src/pages/search.html` 수정 — rec-grid 컨테이너 추가
  - `web/public/js/search/search.js` 수정 — renderRecommendedCards() 함수 추가
  - 카드 표시 항목: 제목(name), 폴더 경로, 파일 크기(KB), 수정일
  - 완료 기준: 추천 문서가 그리드 카드 형태로 렌더링

- [x] Task 17-3-3: [FE] 추천 문서 조회 영역 (Owner: frontend-dev)
  - `web/src/pages/search.html` 수정 — rec-controls 영역 추가
  - `web/public/js/search/search.js` 수정 — filterRecommended(), populateFolderFilter() 함수 추가
  - 검색: 문서 이름/경로 실시간 필터링
  - 폴더 필터: 1단계 폴더 기준 드롭다운
  - 정렬: 최신순/이름순/크기순
  - 건수 제한: 5/10/20건
  - 완료 기준: 각 필터·정렬 조합이 정상 동작

- [x] Task 17-3-4: [FE] search.css 그리드 스타일 + 반응형 (Owner: frontend-dev)
  - `web/public/css/search.css` 수정
  - rec-grid: grid-template-columns auto-fill minmax(280px, 1fr)
  - rec-card: 호버 효과 + 메타 정보 영역
  - rec-controls: flex 레이아웃
  - 검색 모드 토글: mode-btn 스타일 (보너스)
  - 반응형: 768px 이하 1단 전환
  - 완료 기준: 카드·컨트롤·반응형 스타일 정상 렌더링
