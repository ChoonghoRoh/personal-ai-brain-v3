# Phase 14-1: 권한·메뉴 보완 — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 14 내 1순위 (P0)
**예상 작업량**: 2일
**시작일**: 2026-02-16
**완료일**: 2026-02-16

**기준 문서**: `phase-14-master-plan-guide.md`
**Plan**: `phase-14-1-0-plan.md`

---

## Phase 진행 정보

- **현재 Phase**: 14-1 권한·메뉴 보완 — 역할 기반 메뉴 표시/숨김과 BE API 권한 검증 구현
- **이전 Phase**: Phase 13 완료 (69 E2E, 98.5%)
- **다음 Phase**: 14-2 API 문서(Swagger) 고도화

---

## Task 목록

### 14-1-1: [BE] 역할 스키마·의존성 설계 ✅

**우선순위**: 1순위
**예상 작업량**: 중
**의존성**: 없음
**상태**: ✅ 완료

- [x] UserInfo 모델에 role 필드 추가 (user/admin_knowledge/admin_system)
- [x] JWT claim에 role 포함 (토큰 생성·검증)
- [x] require_admin_knowledge 의존성 함수 구현
- [x] require_admin_system 의존성 함수 구현
- [x] AUTH_ENABLED=false 시 기본 role=admin_system (개발 편의)
- [x] /api/auth/status 응답에 role 포함

### 14-1-2: [FE] "지식 관리" 그룹 레이블 적용 ✅

**우선순위**: 2순위 (14-1-1과 병렬 가능)
**예상 작업량**: 소
**의존성**: 없음
**상태**: ✅ 완료

- [x] header-component.js line 119 "관리자 메뉴" → "지식 관리" 변경

### 14-1-3: [BE] Admin API 권한 적용 + 403 응답 규격 ✅

**우선순위**: 3순위
**예상 작업량**: 중
**의존성**: 14-1-1 완료 후
**상태**: ✅ 완료

- [x] /api/admin/* 라우터에 require_admin_system 적용 (router-level dependency)
- [x] 403 Forbidden 응답 규격 정의 (detail 메시지)
- [x] AUTH_EXCLUDE_PREFIXES `/admin/` — dead code 확인 (is_auth_excluded 미사용)

### 14-1-4: [FE] 권한 기반 메뉴 표시 ✅

**우선순위**: 4순위 (14-1-3과 병렬 가능)
**예상 작업량**: 중
**의존성**: 14-1-1 완료 후
**상태**: ✅ 완료

- [x] /api/auth/status API에서 userRole 조회 (fetchUserRole)
- [x] ROLE_HIERARCHY, MENU_REQUIRED_ROLE 상수 추가
- [x] role에 따라 ADMIN_MENU·SETTINGS_MENU 표시/숨김 (applyMenuPermissions)
- [x] 메뉴 그룹 비어있으면 그룹 전체 숨김

### 14-1-5: [TEST] 권한 검증 통합 테스트 ✅

**우선순위**: 5순위
**예상 작업량**: 중
**의존성**: 14-1-3, 14-1-4 완료 후
**상태**: ✅ 완료

- [x] pytest: Admin API 권한 검증 테스트 (401/403) — 11/11 PASS
- [x] pytest: 역할별 접근 제어 검증 (user→403, admin_knowledge→403, admin_system→200)
- [x] 기존 pytest 79개 회귀 확인 — 회귀 없음
- [x] tests/test_auth_permissions.py 신규 생성 (11개 테스트 케이스)
