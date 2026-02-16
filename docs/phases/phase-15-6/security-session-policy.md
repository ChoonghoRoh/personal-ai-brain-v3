# Phase 15-6-4: 보안·세션 정책 문서

**작성일**: 2026-02-16

---

## 1. 토큰 체계

### 1.1 Access Token

| 항목 | 값 |
|------|-----|
| 알고리즘 | HS256 |
| 만료 시간 | 30분 (JWT_EXPIRE_MINUTES) |
| 페이로드 | `sub`(username), `role`, `exp` |
| 저장 위치 | 클라이언트 `localStorage` (`auth_token`) |

### 1.2 Refresh Token (Phase 15-6-1)

| 항목 | 값 |
|------|-----|
| 알고리즘 | HS256 (동일 시크릿) |
| 만료 시간 | 7일 (REFRESH_TOKEN_EXPIRE_DAYS) |
| 페이로드 | `sub`, `role`, `exp`, `type=refresh`, `jti`(UUID) |
| 저장 위치 | 클라이언트 `localStorage` (`refresh_token`) |

### 1.3 갱신 흐름

```
[1] Access Token 만료
     │
     ▼
[2] 클라이언트: POST /api/auth/refresh { refresh_token }
     │
     ▼
[3] 서버: Refresh Token 검증 → 새 Access Token 발급
     │
     ▼
[4] 클라이언트: auth_token 갱신
```

---

## 2. 토큰 블랙리스트 (Phase 15-6-2)

### 2.1 구조

- **Redis 사용 시**: `token_blacklist:{token}` 키, TTL = Access Token 만료 시간
- **Redis 미사용 시**: 메모리 Set (프로세스 재시작 시 초기화)

### 2.2 로그아웃 흐름

```
[1] POST /api/auth/logout (Authorization: Bearer {token})
     │
     ▼
[2] 서버: token을 블랙리스트에 추가 (Redis SETEX)
     │
     ▼
[3] 이후 해당 토큰으로 요청 시 인증 실패
```

### 2.3 인증 미들웨어 검증 순서

1. `is_token_blacklisted(token)` 확인
2. `verify_jwt_token(token)` JWT 서명/만료 검증
3. 유효 시 `UserInfo` 반환

---

## 3. 비인증 리다이렉트 (Phase 15-6-3)

### 3.1 FE 리다이렉트 규칙

| 조건 | 동작 |
|------|------|
| `auth_enabled=true` + 비인증 + 공개 페이지 | 접근 허용 |
| `auth_enabled=true` + 비인증 + 보호 페이지 | `/login?return_to={path}` 리다이렉트 |
| `auth_enabled=false` (개발) | 모든 페이지 접근 허용 |

### 3.2 공개 페이지 목록

- `/` (홈)
- `/login` (로그인)
- `/dashboard` (대시보드)

### 3.3 API 응답 규칙

| 조건 | HTTP 응답 |
|------|-----------|
| API + 비인증 | 401 Unauthorized |
| API + 권한 부족 | 403 Forbidden |
| HTML + 비인증 | FE에서 리다이렉트 처리 |

---

## 4. Redis 설정

| 항목 | 환경변수 | 기본값 |
|------|---------|--------|
| URL | `REDIS_URL` | None (비활성) |
| 블랙리스트 키 프리픽스 | - | `token_blacklist:` |
| TTL | - | Access Token 만료 시간 |
