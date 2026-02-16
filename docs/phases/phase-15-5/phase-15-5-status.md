# Phase 15-5 Status: 회원 관리 시스템

**상태**: DONE
**완료일**: 2026-02-16

## 완료 항목

| Task | 내용 | 상태 |
|------|------|------|
| 15-5-1 | [BE] users 테이블 마이그레이션 SQL | DONE |
| 15-5-2 | [BE] 회원 가입·프로필·비밀번호 변경 CRUD API | DONE |
| 15-5-3 | [FE] Admin 사용자 목록·권한 할당 UI | DONE |
| 15-5-4 | [DOC] 회원 관리 API·권한 매핑 정리 | DONE |

## 산출물

### Backend
- `scripts/migrations/004_create_users_table.sql` — users 테이블 마이그레이션
- `backend/routers/auth/auth.py` — 셀프 서비스 API 추가 (register, profile, change-password)
- `backend/routers/admin/user_crud.py` — Admin CRUD (기존 Phase 14-5-3, 변경 없음)
- `backend/middleware/auth.py` — register 경로 인증 제외 추가

### Frontend
- `web/src/pages/admin/users.html` — 사용자 관리 페이지
- `web/public/css/admin/admin-users.css` — 사용자 관리 CSS
- `web/public/js/admin/users.js` — 사용자 관리 JS
- `web/public/js/components/header-component.js` — LNB 시스템 관리 그룹 추가
- `backend/main.py` — /admin/users HTML 라우트 추가

### Documentation
- `docs/phases/phase-15-5/user-management-api.md` — API·권한 매핑 문서
