# Task 15-5-3: [FE] Admin 전용 사용자 목록/권한(Role) 할당 UI

**우선순위**: 15-5 내 3순위
**의존성**: 15-5-2 완료 후
**담당 팀원**: frontend-dev
**상태**: DONE

---

## §1. 개요

Admin(admin_system 역할) 전용 사용자 관리 페이지를 구현한다. `/admin/users` 경로에서 사용자 목록 조회, 역할(Role) 변경, 사용자 생성/수정/비활성화, 비밀번호 초기화 기능을 제공한다. LNB(좌측 네비게이션) 시스템 관리 그룹에 "사용자 관리" 메뉴를 추가한다.

---

## §2. 파일 변경 계획

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `web/src/pages/admin/users.html` | 신규 | 사용자 관리 페이지 HTML 템플릿 |
| `web/public/css/admin/admin-users.css` | 신규 | 사용자 관리 페이지 전용 스타일 |
| `web/public/js/admin/users.js` | 신규 | 사용자 CRUD + 역할 할당 JS 로직 |
| `web/public/js/components/header-component.js` | 수정 | SYSTEM_MENU에 사용자 관리 메뉴 추가 |
| `backend/main.py` | 수정 | `_HTML_ROUTES`에 /admin/users 라우트 등록 |

---

## §3. 작업 체크리스트

- [x] HTML 페이지 작성 (`users.html`)
  - 사용자 목록 테이블 (username, display_name, email, role, is_active, last_login_at)
  - 사용자 생성 모달 (username, password, display_name, email, role)
  - 사용자 수정 모달 (display_name, email, role, is_active)
  - 비밀번호 초기화 기능
  - 검색/필터 (역할별, 상태별)
- [x] CSS 스타일 작성 (`admin-users.css`)
  - 기존 Admin 페이지 스타일과 일관성 유지
  - 테이블 레이아웃, 모달, 상태 배지 스타일
- [x] JS 로직 작성 (`users.js`)
  - GET /api/admin/users -- 목록 조회 (필터/페이징)
  - POST /api/admin/users -- 사용자 생성
  - PUT /api/admin/users/{id} -- 사용자 수정 (역할/상태)
  - DELETE /api/admin/users/{id} -- 비활성화 (soft delete)
  - POST /api/admin/users/{id}/reset-password -- 비밀번호 초기화
- [x] LNB 메뉴 추가 (`header-component.js`)
  - SYSTEM_MENU 배열에 `{ path: '/admin/users', label: '사용자 관리', icon: '...' }` 추가
  - 최소 역할: admin_system
- [x] HTML 라우트 등록 (`main.py`)
  - `_HTML_ROUTES`에 `("/admin/users", "admin/users.html", "사용자 관리")` 추가

---

## §4. 참조

- `web/src/pages/admin/users.html` -- 사용자 관리 페이지
- `web/public/css/admin/admin-users.css` -- 사용자 관리 CSS
- `web/public/js/admin/users.js` -- 사용자 관리 JS
- `web/public/js/components/header-component.js` -- LNB 컴포넌트 (SYSTEM_MENU)
- `backend/routers/admin/user_crud.py` -- Admin CRUD API (Phase 14-5-3, 변경 없음)
- `docs/phases/phase-15-5/user-management-api.md` -- Section 1.2 (Admin CRUD API)
- `docs/phases/phase-15-5/user-management-api.md` -- Section 2.2 (메뉴 접근 권한)
