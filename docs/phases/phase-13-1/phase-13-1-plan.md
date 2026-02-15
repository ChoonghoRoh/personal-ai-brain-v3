# Phase 13-1 Plan — Frontend 메뉴·헤더 보완

**작성일**: 2026-02-16
**Phase**: 13-1 (1순위)
**목표**: header-component 활성 해석 순서 문서화, NAV_MENU 제거, 지식/설정 그룹핑 UI, Admin 공통 shell 검증
**기준 문서**: [phase-13-master-plan.md](../phase-13-master-plan.md)

---

## 목표

Web 서비스 메뉴 개편의 Frontend 보완 작업 4건:
1. header-component 활성 해석 순서(user → settings → admin) 코드·문서 명시, NAV_MENU deprecated 제거
2. Admin 영역에 "지식 관리" / "설정 관리" 그룹 레이블 또는 구분 UI 추가
3. Admin 지식 6페이지·설정 5페이지 공통 shell(header-placeholder, admin-common, admin-styles) 검증·통일
4. (선택) 404 전용 HTML 페이지 생성, 활성 메뉴 aria-current 접근성 보완

## Task 구성

| Task | 도메인 | 목표 | 변경 파일 | 예상 |
|------|--------|------|----------|------|
| 13-1-1 | [FE] | header-component 활성 해석 순서 문서화·NAV_MENU 제거 | header-component.js, layout-component.js | 0.5일 |
| 13-1-2 | [FE] | 지식 vs 설정 그룹핑 UI 보완 | header-component.js 또는 admin 레이아웃 | 0.5일 |
| 13-1-3 | [FE] | Admin 공통 shell 검증·불일치 시 통일 | Admin HTML 11페이지 | 0.5일 |
| 13-1-4 | [FE] | (선택) 404 전용 HTML·활성 메뉴 접근성 보완 | 404.html, header 스크립트 | 0.5일 |

## 구현 순서

1. 13-1-1 (선행 — NAV_MENU 정리 후 다른 Task 진행)
2. 13-1-2, 13-1-3 (병렬 가능)
3. 13-1-4 (선택, 13-2-2와 연동 시 13-2 후)

## 의존성

- 13-1-1 → 13-1-2 (활성 해석 순서 확정 후 그룹핑)
- 13-1-3: 독립 (13-1-1과 병렬 가능)
- 13-1-4: 13-2-2(Backend HTML 404)와 연동 시 조율

## 검증 방법

- Grep 검증: `NAV_MENU` 참조처 0건(제거) 또는 deprecated 1곳만
- Admin 지식 6페이지·설정 5페이지 공통 shell 동일 패턴 확인
- 메뉴 활성 하이라이트 DOM 검증(active/current 클래스 또는 aria-current)
