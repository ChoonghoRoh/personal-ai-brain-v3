# Task 13-1-2: [FE] 지식 vs 설정 그룹핑 UI 보완

**우선순위**: 13-1 내 2순위
**예상 작업량**: 소 (0.5일)
**의존성**: Task 13-1-1 완료 후
**상태**: TODO

**기반 문서**: `phase-13-1-todo-list.md`
**Plan**: `phase-13-1-plan.md`

---

## 1. 개요

### 1.1 목표

Admin 영역에서 ADMIN_MENU(지식 관리 6개)와 SETTINGS_MENU(설정 관리 5개)를 시각적으로 그룹화하여, 사용자가 "지식 관리"와 "설정 관리"를 명확히 구분할 수 있도록 UI를 보완한다.

### 1.2 관련 시나리오

- Admin 지식 메뉴 진입 시나리오 (8개)
- Admin 설정 메뉴 진입 시나리오 (8개)

---

## 2. 파일 변경 계획

| 파일 | 변경 내용 |
|------|----------|
| `web/src/js/layout-component.js` 또는 header-component | 그룹 레이블 렌더링 추가 |
| `web/src/css/admin-styles.css` (필요 시) | 그룹 구분 스타일 |

---

## 3. 작업 체크리스트

- [ ] 그룹 레이블 도입 방안 결정 (레이블 텍스트 vs 구분선 vs 서브헤더)
- [ ] header-component 또는 admin 레이아웃에 그룹 구분 구현
- [ ] 지식 6개·설정 5개 그룹별 정상 렌더링 확인
- [ ] 반응형·다크모드 대응 확인

---

## 4. 참조

- Phase 13 Master Plan §13-1-2
- web-service-menu-restructuring-plan.md
