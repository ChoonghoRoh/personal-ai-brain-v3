# Phase 15-5 Todo List: 회원 관리 시스템 완성

**Phase**: 15-5
**G1 판정**: PASS
**작성일**: 2026-02-16

---

- [x] Task 15-5-1: [DB] users 테이블 실제 생성 및 마이그레이션 (Owner: backend-dev)
  - `scripts/migrations/004_create_users_table.sql` 작성
  - CREATE TABLE IF NOT EXISTS users (9개 컬럼)
  - 인덱스 3개 (username, role, is_active)
  - 테이블/컬럼 코멘트 추가

- [x] Task 15-5-2: [BE] 회원 가입/프로필 수정/비밀번호 변경 CRUD API (Owner: backend-dev)
  - POST `/api/auth/register` -- 회원 가입 (인증 불필요)
  - GET `/api/auth/profile` -- 프로필 조회 (require_auth)
  - PUT `/api/auth/profile` -- 프로필 수정 (require_auth)
  - POST `/api/auth/change-password` -- 비밀번호 변경 (require_auth)
  - middleware/auth.py register 경로 인증 제외 추가

- [x] Task 15-5-3: [FE] Admin 전용 사용자 목록/권한(Role) 할당 UI (Owner: frontend-dev)
  - `web/src/pages/admin/users.html` 사용자 관리 페이지
  - `web/public/css/admin/admin-users.css` 스타일
  - `web/public/js/admin/users.js` 사용자 CRUD + 역할 할당 JS
  - LNB 시스템 관리 그룹에 "사용자 관리" 메뉴 추가
  - `_HTML_ROUTES`에 /admin/users 라우트 등록

- [x] Task 15-5-4: [DOC] 회원 관리 API/권한 매핑 정리 (Owner: backend-dev)
  - `user-management-api.md` 작성 (API 엔드포인트, 권한 매핑, 비밀번호 정책, 스키마)
  - 셀프 서비스 API 4개 + Admin CRUD 6개 엔드포인트 정리
  - 역할 계층 (user/admin_knowledge/admin_system) 매핑
  - 메뉴 접근 권한 매트릭스
