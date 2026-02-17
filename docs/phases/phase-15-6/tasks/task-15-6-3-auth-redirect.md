# Task 15-6-3: [FS] 비인증 접근 시 로그인 페이지 강제 리다이렉트

**우선순위**: 15-6 내 3순위
**의존성**: 없음 (15-6-1, 15-6-2와 병렬 가능)
**담당 팀원**: frontend-dev
**상태**: DONE

---

## §1. 개요

인증이 활성화된 환경(`auth_enabled=true`)에서 비인증 사용자가 보호 페이지에 접근할 때 `/login?return_to={path}` 형태로 로그인 페이지로 강제 리다이렉트한다. 공개 페이지(/, /login, /dashboard)는 예외 처리하며, API 요청은 기존 401 Unauthorized 응답을 유지한다. Phase 14 권장사항을 반영한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/public/js/components/header-component.js` | 수정 | `fetchUserRole()` 내 비인증 감지 시 리다이렉트 로직 강화 |
| `backend/middleware/auth.py` | 수정 | `AUTH_EXCLUDE_PATHS`, `AUTH_EXCLUDE_PREFIXES` 정리 |

## §3. 작업 체크리스트 (Done Definition)

### FE 리다이렉트 로직
- [x] `fetchUserRole()` — `GET /api/auth/me` 호출 후 `auth_enabled=true` + 비인증 감지
- [x] 보호 페이지 접근 시 `window.location.href = '/login?return_to=' + encodeURIComponent(path)` 리다이렉트
- [x] 공개 페이지 예외 처리: `/`, `/login`, `/dashboard`

### 리다이렉트 규칙 정리
- [x] `auth_enabled=true` + 비인증 + 공개 페이지 -> 접근 허용
- [x] `auth_enabled=true` + 비인증 + 보호 페이지 -> `/login?return_to={path}` 리다이렉트
- [x] `auth_enabled=false` (개발 환경) -> 모든 페이지 접근 허용

### BE 인증 제외 경로
- [x] `AUTH_EXCLUDE_PATHS` — 정적 경로 (/, /health, /docs, /login, /dashboard 등)
- [x] `AUTH_EXCLUDE_PREFIXES` — 프리픽스 경로 (/static, /document/, /admin/)
- [x] API 비인증 요청 시 401 Unauthorized 유지

## §4. 참조

- `web/public/js/components/header-component.js` — `fetchUserRole()`, 메뉴 권한 로직
- `backend/middleware/auth.py` — `AUTH_EXCLUDE_PATHS`, `is_auth_excluded()`
- `docs/phases/phase-15-6/security-session-policy.md` 3 — 리다이렉트 정책
