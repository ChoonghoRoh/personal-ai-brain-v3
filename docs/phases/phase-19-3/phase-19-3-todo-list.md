# Phase 19-3 Todo List: 키워드 그룹 관리 UI 리뉴얼

> **Phase**: 19-3
> **상태**: PLANNED
> **작성일**: 2026-02-22

---

## Task 체크리스트

- [ ] Task 19-3-1: [FE] CSS 분리 (Lv2 리팩토링) — admin-groups.css(975줄) → 기능별 5개 파일 + HTML CSS 링크 업데이트 (Owner: frontend-dev)
- [ ] Task 19-3-2: [FE] D&D 제거 + 폴더형 트리 전환 — 폴더 아이콘 + 우클릭 메뉴 "부모 변경" 추가 (Owner: frontend-dev) [blocked by: 19-3-1]
- [ ] Task 19-3-3: [FE] 클릭 즉시 피드백 + 노드 이동 성능 — 스피너, 낙관적 UI(백업/복구) (Owner: frontend-dev) [blocked by: 19-3-2]
- [ ] Task 19-3-4: [FE] 바로 수정 모드 — 그룹 선택 즉시 인라인 편집 폼 + crud.js 구조 정리 (Owner: frontend-dev) [blocked by: 19-3-2]
- [ ] Task 19-3-5: [FE] 트리 헤더 + 검색 통합 — 검색+깊이 필터 컴팩트 배치, 반응형 CSS (Owner: frontend-dev) [blocked by: 19-3-4]
- [ ] Task 19-3-6: [TEST] 회귀 테스트 — 트리 렌더링, 노드 이동, CRUD, 검색, 반응형 동작 확인 (Owner: frontend-dev) [blocked by: 19-3-5]

---

## 500줄 규정 체크포인트

- [ ] 19-3-1 완료 후: 분리된 5개 CSS 파일 각각 500줄 미만 확인
- [ ] 19-3-2 완료 후: keyword-group-treeview.js 500줄 이내 확인
- [ ] 19-3-4 완료 후: keyword-group-crud.js 500줄 이내 확인
- [ ] 19-3-5 완료 후: 신규/변경 파일 전체 500줄 미만 확인
