# Task 15-6-2: [BE] 로그아웃 시 토큰 블랙리스트 처리

**우선순위**: 15-6 내 2순위
**의존성**: 없음 (15-6-1과 병렬 가능)
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

로그아웃 시 서버 측에서 해당 Access Token을 즉시 무효화하여, 이후 해당 토큰으로의 요청을 차단한다. Redis를 1순위 저장소로 사용하고, Redis 미연결 시 메모리 Set 기반 폴백을 제공한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/middleware/auth.py` | 수정 | `blacklist_token()`, `is_token_blacklisted()`, `_get_redis()`, 메모리 폴백 Set |
| `backend/routers/auth/auth.py` | 수정 | `POST /api/auth/logout`에서 `blacklist_token()` 호출 |
| `backend/config.py` | 수정 | `REDIS_URL` 환경변수 로드 확인 |

## §3. 작업 체크리스트 (Done Definition)

### Redis 블랙리스트
- [x] `_get_redis()` — Redis 클라이언트 lazy init, `REDIS_URL` 기반
- [x] `blacklist_token(token, expires_in_seconds)` — `SETEX token_blacklist:{token} TTL "1"`
- [x] `is_token_blacklisted(token)` — `EXISTS token_blacklist:{token}` 확인
- [x] `BLACKLIST_PREFIX = "token_blacklist:"` 상수

### 메모리 폴백
- [x] `_memory_blacklist: set[str]` — Redis 미연결 시 사용
- [x] `blacklist_token()` — Redis 실패 시 메모리 Set에 추가
- [x] `is_token_blacklisted()` — Redis 실패 시 메모리 Set 조회

### 로그아웃 API 연동
- [x] `POST /api/auth/logout` — Authorization 헤더에서 토큰 추출
- [x] `blacklist_token(token, expires_in_seconds=JWT_EXPIRE_MINUTES * 60)` 호출
- [x] 로그아웃 로그 기록

### 인증 미들웨어 통합
- [x] `get_current_user()` — JWT 검증 전 `is_token_blacklisted()` 우선 체크
- [x] 블랙리스트에 있으면 `None` 반환 (인증 실패)

## §4. 참조

- `backend/middleware/auth.py` — 블랙리스트 함수, 인증 미들웨어
- `backend/routers/auth/auth.py` — 로그아웃 API
- `backend/config.py` — `REDIS_URL` 환경변수
- `docs/phases/phase-15-6/security-session-policy.md` 2 — 블랙리스트 정책
