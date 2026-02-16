# Phase 14-5: 사용자 검증·로그인·회원관리 — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 14 내 5순위 (P1~P2)
**기준 문서**: `phase-14-master-plan-guide.md` §6, §8.6

---

## Task 목록

### 14-5-1: [DOC] 사용자 검증·로그인·회원관리 요구사항 및 단계별 플랜 문서 ✅

**우선순위**: 1순위
**상태**: ✅ 완료

- [x] 현재 인증 시스템 분석 (middleware/auth.py, routers/auth/auth.py, config.py)
- [x] 요구사항 정의 (Authentication, Login/Logout, User Management)
- [x] DB 스키마 설계 (users, refresh_tokens 테이블)
- [x] API 설계 (로그인·회원관리 엔드포인트)
- [x] FE 인증 플로우 설계 (로그인 페이지, 401 리다이렉트, LNB 로그아웃)
- [x] 보안 고려사항 (bcrypt, JWT, Rate Limiting)
- [x] 구현 단계별 플랜 (5단계)
- [x] On-Premise·단일 사용자 호환 방안

### 14-5-2: [BE] 로그인/로그아웃·토큰 갱신 API 보강 ✅

**우선순위**: 2순위
**상태**: ✅ 완료
**선행**: 14-5-1

- [x] User 모델 생성 (backend/models/user_models.py) + init_db()로 자동 생성
- [x] passlib[bcrypt] + bcrypt<5 의존성 추가 (requirements.txt)
- [x] POST /api/auth/login 구현 (bcrypt 검증, last_login_at 갱신)
- [x] 초기 admin 계정 시드 (_seed_admin_user in main.py on_startup)
- [x] config.py: ADMIN_DEFAULT_USERNAME, ADMIN_DEFAULT_PASSWORD 환경변수
- [x] 로그인 성공/실패 curl 검증 (admin/admin1234 → JWT 발급, 잘못된 비번 → 401)
- [x] pytest 79 passed, 5 failed, 3 errors — 기존 baseline 동일 (회귀 없음)
- [x] 16개 페이지 200 OK 확인

### 14-5-3: [BE] 회원(사용자) CRUD·목록·역할 관리 API ✅

**우선순위**: 3순위
**상태**: ✅ 완료
**선행**: 14-5-2

- [x] GET /api/admin/users — 목록 조회 (검색·역할·활성 필터, 페이지네이션)
- [x] GET /api/admin/users/{id} — 단건 조회
- [x] POST /api/admin/users — 생성 (username, password, role, display_name, email)
- [x] PUT /api/admin/users/{id} — 수정 (역할 변경, 비활성화, 표시명·이메일)
- [x] DELETE /api/admin/users/{id} — 비활성화 (soft delete)
- [x] POST /api/admin/users/{id}/reset-password — 비밀번호 초기화
- [x] 엣지 케이스: 409 중복 username, 404 없는 사용자, 비활성 사용자 로그인 차단
- [x] admin/__init__.py에 users 라우터 등록 (admin_system 권한 일괄 적용)
- [x] openapi_tags에 "Admin - Users" 태그 추가
- [x] pytest 79 passed — 회귀 없음
