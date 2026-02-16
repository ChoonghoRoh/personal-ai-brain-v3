# Phase 14-1-0 Plan — 권한·메뉴 보완

**Phase ID**: 14-1
**Phase 명**: 권한·메뉴 보완
**Z**: 0 (초기 설계)
**기준 문서**: `phase-14-master-plan-guide.md`

---

## 1. Phase Goal

통합 메뉴 설계 보고서의 권한 분리와 Phase 13 QC 보완 항목을 반영하여, 역할(role) 기반 메뉴 표시/숨김과 Backend API 권한 검증을 구현한다.

---

## 2. Scope

### 2.1 In Scope

| Task ID | Task 명 | 도메인 | 예상 |
|---------|---------|--------|------|
| 14-1-1 | 역할 스키마·의존성 설계 | [BE] | 중 |
| 14-1-2 | "지식 관리" 그룹 레이블 적용 | [FE] | 소 |
| 14-1-3 | Admin API 권한 적용 + 403 응답 규격 | [BE] | 중 |
| 14-1-4 | 권한 기반 메뉴 표시 | [FE] | 중 |
| 14-1-5 | 권한 검증 통합 테스트 | [TEST] | 중 |

### 2.2 Out of Scope

- 사용자(user) 테이블 생성 및 회원 CRUD (Phase 14-5)
- 로그인 폼 UI (Phase 14-5)
- API Swagger 태그 그룹화 (Phase 14-2)
- UI 레이아웃·LNB (Phase 14-3)

---

## 3. Task 개요

| Task ID | Task 명 | 예상 | 의존성 |
|---------|---------|------|--------|
| 14-1-1 | [BE] 역할 스키마·의존성 설계 | 중 | 없음 |
| 14-1-2 | [FE] "지식 관리" 그룹 레이블 | 소 | 없음 |
| 14-1-3 | [BE] Admin API 권한 적용 + 403 | 중 | 14-1-1 |
| 14-1-4 | [FE] 권한 기반 메뉴 표시 | 중 | 14-1-1 |
| 14-1-5 | [TEST] 권한 검증 통합 테스트 | 중 | 14-1-3, 14-1-4 |

**진행 순서**: 14-1-1 + 14-1-2 (병렬) → 14-1-3 + 14-1-4 (병렬) → 14-1-5

---

## 4. Validation / Exit Criteria

- [ ] UserInfo에 role 필드 추가, JWT claim에 role 포함
- [ ] require_admin_knowledge, require_admin_system 의존성 함수 동작
- [ ] AUTH_ENABLED=false 시 테스트용 role 처리 (기본 admin)
- [ ] header-component "지식 관리" 그룹 레이블 적용
- [ ] /api/admin/* (지식)에 require_admin_knowledge 적용
- [ ] /api/admin/settings/* (설정)에 require_admin_system 적용
- [ ] 권한 부족 시 403 Forbidden + detail 메시지
- [ ] 비인증/일반 사용자에게 Admin·설정 메뉴 미노출
- [ ] 기존 69개 E2E 회귀 테스트 유지

---

## 5. 참고 문서

- `docs/phases/phase-14-master-plan-guide.md` (§2, §5, §8.2)
- `docs/phases/phase-14-1/phase-14-1-0-todo-list.md`
- `backend/middleware/auth.py`
- `web/public/js/components/header-component.js`
