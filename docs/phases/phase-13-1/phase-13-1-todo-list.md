# Phase 13-1 Todo List — Frontend 메뉴·헤더 보완

**Phase**: 13-1
**작성일**: 2026-02-16
**완료일**: 2026-02-16

---

## Task 13-1-1 [FE] header-component 활성 해석 순서 문서화·NAV_MENU 제거

- [x] header-component.js 활성 해석 순서(user → settings → admin) 코드 주석 추가
- [x] 활성 해석 순서 문서화 (plan 또는 별도 docs)
- [x] `NAV_MENU` 참조처 grep 후 모든 참조 제거
- [x] `NAV_MENU` 변수 삭제 적용
- [x] layout-component.js NAV_MENU 참조 제거 (참조 없음 확인)
- [x] Grep 검증: `NAV_MENU` 참조 0건
- [x] 구버전 web/src/js/header-component.js 삭제

## Task 13-1-2 [FE] 지식 vs 설정 그룹핑 UI 보완

- [x] Admin 영역 "지식 관리" / "설정 관리" 그룹 레이블 — 이미 구현 확인
- [x] header-component.js menu-group-title 3개 그룹(사용자, 관리, 설정) 렌더링 확인
- [x] 그룹 레이블 스타일링 확인

## Task 13-1-3 [FE] Admin 공통 shell 검증·불일치 시 통일

- [x] Admin 지식 6페이지 공통 shell 구성 확인
- [x] Admin 설정 5페이지 공통 shell 구성 확인
- [x] statistics.html 불일치 발견 → 통일 패치 적용
- [x] 공통 요소 검증: header-placeholder, admin-common.js, admin-styles.css
- [x] statistics.js에서 renderHeader() 제거 (admin-common.js가 담당)

## Task 13-1-4 [FE] (선택) 404 전용 HTML·활성 메뉴 접근성 보완

- [x] 404.html 페이지 생성 (메뉴 구조 포함)
- [x] 백엔드 404 HTML 응답 연동 (13-2-2와 통합)
