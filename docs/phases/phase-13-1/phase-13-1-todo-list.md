# Phase 13-1 Todo List — Frontend 메뉴·헤더 보완

**Phase**: 13-1
**작성일**: 2026-02-16

---

## Task 13-1-1 [FE] header-component 활성 해석 순서 문서화·NAV_MENU 제거

- [ ] header-component.js 활성 해석 순서(user → settings → admin) 코드 주석 추가
- [ ] 활성 해석 순서 문서화 (plan 또는 별도 docs)
- [ ] `NAV_MENU` 참조처 grep 후 모든 참조 제거
- [ ] `NAV_MENU` 변수 삭제 또는 deprecated 주석 유지 결정·적용
- [ ] layout-component.js NAV_MENU 참조 제거 (존재 시)
- [ ] Grep 검증: `NAV_MENU` 참조 0건 또는 deprecated 1곳만

## Task 13-1-2 [FE] 지식 vs 설정 그룹핑 UI 보완

- [ ] Admin 영역 "지식 관리" / "설정 관리" 그룹 레이블 도입 방안 결정
- [ ] header-component.js 또는 admin 레이아웃에 그룹 구분 UI 구현
- [ ] 지식 메뉴 6개·설정 메뉴 5개 그룹별 렌더링 확인
- [ ] 그룹 레이블 스타일링·반응형 검증

## Task 13-1-3 [FE] Admin 공통 shell 검증·불일치 시 통일

- [ ] Admin 지식 6페이지 공통 shell 구성 확인:
  - [ ] groups.html
  - [ ] labels.html (또는 keyword-groups.html)
  - [ ] chunk-create.html
  - [ ] approval.html
  - [ ] chunk-labels.html
  - [ ] statistics.html
- [ ] Admin 설정 5페이지 공통 shell 구성 확인:
  - [ ] templates.html
  - [ ] presets.html
  - [ ] rag-profiles.html
  - [ ] policy-sets.html
  - [ ] audit-logs.html
- [ ] 공통 요소 검증: header-placeholder, admin-common.js, admin-styles.css
- [ ] 불일치 발견 시 통일 패치 적용
- [ ] 검증 체크리스트 작성

## Task 13-1-4 [FE] (선택) 404 전용 HTML·활성 메뉴 접근성 보완

- [ ] 404.html 페이지 생성 (메뉴 구조 포함)
- [ ] 활성 메뉴에 aria-current="page" 적용
- [ ] active/current CSS 클래스 일관성 확인
- [ ] 백엔드 404 HTML 응답 연동 (13-2-2 완료 후)
