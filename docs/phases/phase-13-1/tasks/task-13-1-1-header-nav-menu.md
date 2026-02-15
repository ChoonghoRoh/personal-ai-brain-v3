# Task 13-1-1: [FE] header-component 활성 해석 순서 문서화·NAV_MENU 제거

**우선순위**: 13-1 내 1순위 (선행)
**예상 작업량**: 소 (0.5일)
**의존성**: 없음
**상태**: TODO

**기반 문서**: `phase-13-1-todo-list.md`
**Plan**: `phase-13-1-plan.md`

---

## 1. 개요

### 1.1 목표

header-component.js의 활성 메뉴 해석 순서(user → settings → admin)를 코드 주석 및 문서에 명시하고, deprecated된 `NAV_MENU` 변수의 참조처를 제거하여 메뉴 상수 체계를 정리한다.

### 1.2 관련 시나리오

- 공통 시나리오 S-01: 메뉴 상수(USER_MENU, ADMIN_MENU, SETTINGS_MENU) 존재 확인
- 공통 시나리오 S-02: 활성 메뉴 하이라이트 정확성

---

## 2. 파일 변경 계획

### 2.1 수정

| 파일 | 변경 내용 |
|------|----------|
| `web/src/js/layout-component.js` | NAV_MENU 참조 제거 |
| `web/public/js/components/layout-component.js` | NAV_MENU 참조 제거 (빌드 산출물) |
| `web/src/js/header-component.js` (존재 시) | 활성 해석 순서 주석 추가, NAV_MENU 삭제 |

---

## 3. 작업 체크리스트

- [ ] NAV_MENU 참조처 전수 grep
- [ ] header-component.js 활성 해석 순서 코드 주석 추가
- [ ] NAV_MENU 참조 제거·변수 삭제
- [ ] Grep 검증: NAV_MENU 0건(제거) 또는 deprecated 1곳만
- [ ] 페이지 로드 확인 (메뉴 정상 렌더링)

---

## 4. 참조

- Phase 13 Master Plan §13-1-1
- web-service-menu-restructuring-scenarios.md S-01, S-02
