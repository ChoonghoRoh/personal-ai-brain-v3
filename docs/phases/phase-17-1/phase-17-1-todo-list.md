# Phase 17-1 Todo List — 키워드 그룹 3단 레이아웃 리뉴얼

**Phase**: 17-1
**기준**: [phase-17-1-plan.md](phase-17-1-plan.md)

---

- [x] Task 17-1-1: [BE] 그룹 목록 페이지네이션 API (Owner: backend-dev)
  - `backend/routers/knowledge/labels.py` page/size 쿼리 파라미터 추가
  - `backend/routers/knowledge/labels_handlers.py` 페이지네이션 로직 + total 응답
  - 완료 기준: GET /api/labels/groups?page=1&size=20 → { items, total, page, size }

- [x] Task 17-1-2: [FE] 3단 레이아웃 HTML 구조 (Owner: frontend-dev)
  - `web/src/pages/admin/groups.html` 전면 개편 — 3단 그리드 컨테이너
  - 모달 HTML 완전 제거
  - 상단에 "새 그룹" 버튼 우측 배치
  - 완료 기준: 3단 영역 (groups-list / group-detail / keyword-list) DOM 구조

- [x] Task 17-1-3: [FE] 상세 패널 인라인 편집 (Owner: frontend-dev)
  - `web/public/js/admin/keyword-group-crud.js` 모달→인라인 전환
  - 그룹 선택 시 상세 패널에 편집 폼 표시
  - 수정/삭제 버튼 상세 패널 내 배치
  - 완료 기준: 모달 없이 상세 패널에서 CRUD 동작

- [x] Task 17-1-4: [FE] 키워드 목록 3단 영역 이동 (Owner: frontend-dev)
  - `web/public/js/admin/keyword-group-matching.js` 키워드 렌더링 → 3단 영역
  - 모달 내부 키워드 목록 → 독립 패널
  - 완료 기준: 3단 키워드 영역에서 키워드 목록 정상 표시

- [x] Task 17-1-5: [FE] 페이지네이션 + 자동 선택 (Owner: frontend-dev)
  - `web/public/js/admin/keyword-group-ui.js` 페이지네이션 UI + 이벤트
  - 최초 진입 시 1번째 그룹 자동 선택
  - 페이지 전환 시 그룹 목록 갱신
  - 완료 기준: 하단 페이지네이션 동작 + 초기 자동 선택

- [x] Task 17-1-6: [FE] CSS 3단 그리드 (Owner: frontend-dev)
  - `web/public/css/admin/admin-groups.css` 3단 그리드 레이아웃
  - 반응형 처리 (필요 시)
  - 완료 기준: 3단 그리드 정상 표시, 각 영역 스크롤 독립
