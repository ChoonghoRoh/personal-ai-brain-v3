# Phase 15-6 Plan: 보안 및 세션 관리 강화

**Phase**: 15-6
**작성일**: 2026-02-16
**상태**: G1 PASS

---

## 1. 목표

JWT Access Token 만료 후에도 사용자 세션을 유지할 수 있도록 **Refresh Token**을 도입하고, 로그아웃 시 서버 측에서 토큰을 즉시 무효화하는 **블랙리스트** 메커니즘을 구현하며, 비인증 사용자가 보호 페이지에 접근할 때 **로그인 페이지로 강제 리다이렉트**하는 보안 흐름을 완성한다.

---

## 2. 범위

### 포함

| 항목 | 내용 |
|------|------|
| Refresh Token | Access Token 만료 시 `POST /api/auth/refresh`로 갱신, 7일 만료 |
| 토큰 블랙리스트 | 로그아웃 시 Redis에 토큰 등록, 인증 미들웨어에서 차단 |
| 메모리 폴백 | Redis 미연결 시 메모리 Set 기반 블랙리스트 |
| 비인증 리다이렉트 | FE `fetchUserRole()`에서 비인증 감지 시 `/login?return_to=` 리다이렉트 |
| 보안 정책 문서 | 토큰 체계, 블랙리스트, 리다이렉트 규칙 문서화 |

### 제외

| 항목 | 사유 |
|------|------|
| Refresh Token Rotation | 현 단계에서는 단순 갱신, Rotation은 추후 고려 |
| Redis Sentinel/Cluster | 단일 인스턴스로 충분, 인프라 고도화는 15-7/15-8 |
| SSO/LDAP/OAuth 연동 | 로컬 우선 아키텍처, 추후 확장 예정 |
| HTTPS/TLS 설정 | 인프라 레벨, 15-7 Docker Production에서 검증 |

---

## 3. 설계 결정

### 3.1 Refresh Token

| 항목 | 결정 |
|------|------|
| 알고리즘 | HS256 (Access Token과 동일 시크릿) |
| 만료 기간 | **7일** (`REFRESH_TOKEN_EXPIRE_DAYS`) |
| 페이로드 | `sub`, `role`, `exp`, `type=refresh`, `jti`(UUID) |
| 저장 위치 | 클라이언트 `localStorage` (`refresh_token`) |
| 갱신 API | `POST /api/auth/refresh` (Refresh Token -> 새 Access Token) |

### 3.2 블랙리스트 저장소

| 우선순위 | 저장소 | 조건 |
|---------|--------|------|
| 1순위 | **Redis** | `REDIS_URL` 설정 시 `SETEX token_blacklist:{token} TTL` |
| 2순위 | **메모리 Set** | Redis 미연결 시 fallback (프로세스 재시작 시 초기화) |

### 3.3 비인증 리다이렉트 방식

- **FE 기반**: `fetchUserRole()` 호출 -> `auth_enabled=true` + 비인증 + 보호 페이지 -> `/login?return_to={path}` 리다이렉트
- **공개 페이지**: `/`, `/login`, `/dashboard` 는 리다이렉트 제외
- **API 응답**: HTML 요청은 FE 리다이렉트, API 요청은 401 Unauthorized 유지

---

## 4. 리스크

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Redis 미연결 시 블랙리스트 초기화 | 프로세스 재시작 시 메모리 블랙리스트 소멸 | Access Token TTL이 짧아(30분) 영향 제한적 |
| Refresh Token 탈취 | 7일간 세션 유지 가능 | jti 기반 개별 무효화 가능, Rotation 추후 도입 |
| localStorage XSS 노출 | 토큰 탈취 가능 | CSP 헤더 적용, httpOnly 쿠키 전환은 추후 고려 |

---

## 5. 참조

| 문서 | 용도 |
|------|------|
| `docs/phases/phase-15-master-plan.md` 6.2 | Phase 15-6 마스터 플랜 정의 |
| `docs/phases/phase-15-6/security-session-policy.md` | 보안 정책 상세 문서 |
| `backend/middleware/auth.py` | 인증 미들웨어 (Refresh Token, 블랙리스트) |
| `backend/routers/auth/auth.py` | 인증 API (로그인, 로그아웃, 갱신) |
| `web/public/js/components/header-component.js` | FE 리다이렉트 로직 |
| `web/public/js/auth/login.js` | FE refresh_token 저장 |
