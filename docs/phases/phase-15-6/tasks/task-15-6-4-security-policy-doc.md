# Task 15-6-4: [DOC] 보안·세션 정책 문서화

**우선순위**: 15-6 내 4순위
**의존성**: 15-6-1, 15-6-2, 15-6-3 (구현 완료 후 작성)
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Phase 15-6에서 도입한 Refresh Token, 토큰 블랙리스트, 비인증 리다이렉트의 보안·세션 정책을 `security-session-policy.md` 문서로 정리한다. 토큰 체계, 블랙리스트 구조, 리다이렉트 규칙, Redis 설정을 포함한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `docs/phases/phase-15-6/security-session-policy.md` | 신규 | 보안·세션 정책 전체 문서 |

## §3. 작업 체크리스트 (Done Definition)

### 문서 구성
- [x] 1. 토큰 체계
  - Access Token: HS256, 30분, `sub`/`role`/`exp`
  - Refresh Token: HS256, 7일, `sub`/`role`/`exp`/`type=refresh`/`jti`
  - 갱신 흐름 다이어그램
- [x] 2. 토큰 블랙리스트
  - Redis 구조: `token_blacklist:{token}`, TTL
  - 메모리 폴백: `set[str]`
  - 로그아웃 흐름 다이어그램
  - 인증 미들웨어 검증 순서
- [x] 3. 비인증 리다이렉트
  - FE 리다이렉트 규칙 테이블
  - 공개 페이지 목록
  - API 응답 규칙 테이블
- [x] 4. Redis 설정
  - 환경변수 (`REDIS_URL`), 키 프리픽스, TTL

## §4. 참조

- `backend/middleware/auth.py` — 구현 코드 (정책의 근거)
- `backend/routers/auth/auth.py` — API 엔드포인트
- `docs/phases/phase-15-master-plan.md` 6.2 — Phase 15-6 마스터 정의
