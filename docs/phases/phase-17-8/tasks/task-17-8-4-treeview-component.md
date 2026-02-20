# Task 17-8-4: [FE] 트리뷰 컴포넌트 (접기/펼치기 + D&D)

**우선순위**: 17-8 내 2순위 (17-8-1 이후 병렬)
**예상 작업량**: 큰
**의존성**: 17-8-1
**상태**: 완료

---

## §1. 개요

키워드 그룹 관리 페이지에 트리뷰 컴포넌트를 추가한다.
접기/펼치기 + 드래그 앤 드롭으로 노드 이동을 지원한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 신규 | `web/public/js/knowledge/keyword-group-treeview.js` | 트리뷰 컴포넌트 |
| 수정 | `web/src/pages/knowledge/groups.html` | 트리뷰 영역 추가 |
| 수정 | `web/public/css/knowledge/admin-groups.css` | 트리뷰 스타일 |

## §3. 작업 체크리스트

- [x] keyword-group-treeview.js 신규 생성
- [x] 트리 노드 접기/펼치기 UI 구현
- [x] 드래그 앤 드롭으로 노드 이동 (move API 호출)
- [x] groups.html에 트리뷰 영역 HTML 추가
- [x] admin-groups.css 트리뷰 스타일 추가
