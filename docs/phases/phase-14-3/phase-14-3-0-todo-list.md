# Phase 14-3: UI 전체 레이아웃·좌측 LNB — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 14 내 3순위 (P1)
**예상 작업량**: 2일
**시작일**: 2026-02-16
**완료일**: 2026-02-16

**기준 문서**: `phase-14-master-plan-guide.md` §5.5, §8.4

---

## Task 목록

### 14-3-1: [FE] 와이드 레이아웃 + LNB 기반 app-layout 구조 ✅

**우선순위**: 1순위
**상태**: ✅ 완료

- [x] layout-component.js에 `.app-layout` 그리드 구조 (260px LNB + 1fr main)
- [x] `initLayout()`에서 .container를 .app-layout으로 자동 래핑 + LNB placeholder
- [x] container max-width: none (full-width within grid column)
- [x] 기존 CSS max-width 혼재 정리 (logs.css, knowledge.css, knowledge-detail.css)
- [x] 반응형 디자인: 1024px (220px LNB), 768px (모바일 드로어)

### 14-3-2: [FE] LNB 컴포넌트 + header 정리 ✅

**우선순위**: 2순위
**상태**: ✅ 완료

- [x] header-component.js에 LNB 코드 통합 (별도 파일 불필요)
- [x] 다크 사이드바 디자인 (#1e293b) + 메뉴 그룹 3개
- [x] 활성 메뉴 하이라이트 (파란색 배경, 좌측 border)
- [x] 설정 그룹 녹색 계열 스타일링
- [x] 권한별 메뉴 표시/숨김 (Phase 14-1 `data-menu-group` 연동)
- [x] header → top-bar 심플화 (페이지 제목 + 부제목만)
- [x] 기존 HTML 파일 변경 없음 (JS DOM 조작으로 자동 적용)

### 14-3-3: [TEST] 레이아웃·LNB 검증 ✅

**우선순위**: 3순위
**상태**: ✅ 완료

- [x] 18개 페이지 전체 200 OK 확인
- [x] pytest 79개 회귀 확인 — 회귀 없음 (5 failed, 3 errors 기존 동일)
