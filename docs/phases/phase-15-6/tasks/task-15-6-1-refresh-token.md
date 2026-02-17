# Task 15-6-1: [BE] 토큰 만료 처리 및 Refresh Token 도입

**우선순위**: 15-6 내 1순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

JWT Access Token(30분) 만료 후에도 사용자 세션을 유지할 수 있도록 Refresh Token(7일)을 도입한다. 로그인 시 Access Token과 함께 Refresh Token을 발급하고, Access Token 만료 시 Refresh Token으로 새 Access Token을 발급하는 갱신 API를 구현한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/middleware/auth.py` | 수정 | `create_refresh_token()`, `verify_refresh_token()` 함수 추가, `REFRESH_TOKEN_EXPIRE_DAYS=7` 상수 |
| `backend/routers/auth/auth.py` | 수정 | `POST /api/auth/refresh` 갱신 엔드포인트, 로그인 응답에 `refresh_token` 포함 |
| `web/public/js/auth/login.js` | 수정 | 로그인 응답에서 `refresh_token`을 `localStorage`에 저장 |

## §3. 작업 체크리스트 (Done Definition)

### Refresh Token 생성/검증
- [x] `create_refresh_token(data)` — HS256, 7일 만료, `type=refresh`, `jti=UUID`
- [x] `verify_refresh_token(token)` — `type=refresh` 클레임 검증, TokenData 반환
- [x] `REFRESH_TOKEN_EXPIRE_DAYS = 7` 상수 정의
- [x] `TokenResponse` 모델에 `refresh_token: Optional[str]` 필드 추가

### 로그인 시 발급
- [x] `POST /api/auth/login` — 응답에 `refresh_token` 포함
- [x] `create_refresh_token(data={"sub": username, "role": role})` 호출

### 갱신 API
- [x] `POST /api/auth/refresh` 엔드포인트 구현
- [x] `RefreshRequest` 스키마: `{ refresh_token: str }`
- [x] Refresh Token 검증 -> 새 Access Token 발급
- [x] `AUTH_EXCLUDE_PATHS`에 `/api/auth/refresh` 추가 (인증 불필요)

### FE 저장
- [x] `login.js` — `data.refresh_token` 존재 시 `localStorage.setItem('refresh_token', ...)` 저장

## §4. 참조

- `backend/middleware/auth.py` — 토큰 생성/검증 함수
- `backend/routers/auth/auth.py` — 인증 API 라우터
- `web/public/js/auth/login.js` — 로그인 FE
- `docs/phases/phase-15-6/security-session-policy.md` 1.2, 1.3 — Refresh Token 정책
