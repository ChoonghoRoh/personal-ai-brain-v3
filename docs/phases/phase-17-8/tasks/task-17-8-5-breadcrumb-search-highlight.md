# Task 17-8-5: [FE] Breadcrumb + 검색 시 트리 하이라이트

**우선순위**: 17-8 내 3순위 (최종)
**예상 작업량**: 중간
**의존성**: 17-8-4
**상태**: 완료

---

## §1. 개요

트리 노드 선택 시 Breadcrumb(경로) 표시와 검색 시 매칭 노드 하이라이트 기능을 구현한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/public/js/knowledge/keyword-group-treeview.js` | Breadcrumb 렌더 + 하이라이트 |
| 수정 | `web/public/js/knowledge/keyword-group-search.js` | 검색 결과 트리 연동 |
| 수정 | `web/public/css/knowledge/admin-groups.css` | Breadcrumb + 하이라이트 스타일 |

## §3. 작업 체크리스트

- [x] Breadcrumb 컴포넌트 (루트→현재 경로 표시)
- [x] 검색 시 매칭 노드 하이라이트 CSS 클래스 적용
- [x] 트리 자동 펼침 (검색 결과 노드까지 경로 열기)
- [x] keyword-group-search.js와 treeview 연동
