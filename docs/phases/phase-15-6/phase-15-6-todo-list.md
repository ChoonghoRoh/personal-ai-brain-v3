# Phase 15-6 Todo List: 보안 및 세션 관리 강화

**Phase**: 15-6
**G1 판정**: PASS
**작성일**: 2026-02-16

---

- [x] Task 15-6-1: [BE] 토큰 만료 처리 및 Refresh Token 도입 (Owner: backend-dev)
  - Refresh Token 생성 함수 (`create_refresh_token`, `verify_refresh_token`)
  - 로그인 시 refresh_token 발급 (`POST /api/auth/login` 응답에 포함)
  - `POST /api/auth/refresh` 갱신 API
  - `REFRESH_TOKEN_EXPIRE_DAYS = 7`, `type=refresh`, `jti`(UUID) 페이로드

- [x] Task 15-6-2: [BE] 로그아웃 시 토큰 블랙리스트 처리 (Owner: backend-dev)
  - Redis 블랙리스트 (`token_blacklist:{token}`, SETEX TTL)
  - 메모리 Set 폴백 (Redis 미연결 시)
  - `blacklist_token()`, `is_token_blacklisted()` 함수
  - `POST /api/auth/logout` 에서 블랙리스트 등록
  - 인증 미들웨어 `get_current_user()`에서 블랙리스트 우선 체크

- [x] Task 15-6-3: [FS] 비인증 접근 시 로그인 페이지 강제 리다이렉트 (Owner: frontend-dev)
  - FE `fetchUserRole()`에서 비인증 + 보호 페이지 감지 시 리다이렉트
  - `/login?return_to={path}` 형태로 원래 경로 전달
  - 공개 페이지(/, /login, /dashboard) 제외
  - BE `AUTH_EXCLUDE_PATHS`, `AUTH_EXCLUDE_PREFIXES` 정리

- [x] Task 15-6-4: [DOC] 보안·세션 정책 문서화 (Owner: backend-dev)
  - `security-session-policy.md` 작성
  - 토큰 체계 (Access Token, Refresh Token)
  - 블랙리스트 구조 (Redis + 메모리)
  - 리다이렉트 규칙 (공개 페이지, 보호 페이지, API 응답)
  - Redis 설정 (환경변수, 키 프리픽스, TTL)
