# Task 13-3-3: [E2E] 메뉴 간 이동·404 시나리오 E2E

**우선순위**: 13-3 내 3순위
**예상 작업량**: 소 (0.5일)
**의존성**: Task 13-3-1, 13-3-2 이후 권장
**상태**: TODO

---

## 1. 목표

메뉴 간 이동(사용자↔Admin 지식↔Admin 설정) 및 404 에러 경로 E2E 테스트.

## 2. 테스트 시나리오

### 2.1 메뉴 간 이동

- 사용자(/search) → Admin 지식(/admin/groups) → 헤더 전환 확인
- Admin 지식(/admin/labels) → Admin 설정(/admin/settings/templates) → 헤더 전환 확인
- Admin 설정(/admin/settings/presets) → 사용자(/reason) → 헤더 전환 확인
- 전체 순회: 사용자 → Admin 지식 → Admin 설정 → 사용자

### 2.2 404 시나리오

- /admin/unknown → 404 응답
- /admin/settings/unknown → 404 응답
- /dashbord (오타) → 404 응답

## 3. 참조

- Phase 13 Master Plan §E-3, E-4
- 메뉴 간 이동 시나리오 (5개), 라우팅·에러 시나리오 (3개)
